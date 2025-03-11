#!/usr/bin/env python
import rospy
from std_msgs.msg import String
import json

class GridState:
    def __init__(self):
        self.state = {}
        self.last_update = None
        self.state_lock = False

    def update(self, new_state):
        """Update the grid state"""
        self.state = new_state
        self.last_update = rospy.Time.now()

    def get_state(self):
        """Get current grid state"""
        return {
            'state': self.state,
            'timestamp': self.last_update.to_sec() if self.last_update else None
        }

    def get_object_at_square(self, square):
        """Get object info for a specific square"""
        if str(square) in self.state:
            return self.state[str(square)]
        return None

class GridStatePublisher:
    def __init__(self):
        rospy.init_node('grid_state_publisher', anonymous=True)
        
        # Initialize GridState
        self.grid_state = GridState()
        
        # Publishers
        self.state_pub = rospy.Publisher(
            '/vision/grid_state_processed',
            String,
            queue_size=1
        )
        
        # Subscribers
        self.vision_sub = rospy.Subscriber(
            '/vision/grid_state',
            String,
            self.vision_callback
        )
        
        # Service response publishers
        self.query_response_pub = rospy.Publisher(
            '/vision/query_response',
            String,
            queue_size=1
        )
        
        # Subscribe to query requests
        self.query_sub = rospy.Subscriber(
            '/vision/query_request',
            String,
            self.handle_query
        )
        
        rospy.loginfo("Grid state publisher initialized")

    def vision_callback(self, msg):
        """Handle incoming grid state from vision system"""
        try:
            state_data = json.loads(msg.data)
            self.grid_state.update(state_data)
            
            # Publish processed state
            self.publish_current_state()
            
        except json.JSONDecodeError as e:
            rospy.logerr(f"Error decoding grid state: {str(e)}")
        except Exception as e:
            rospy.logerr(f"Error processing grid state: {str(e)}")

    def publish_current_state(self):
        """Publish current grid state"""
        try:
            state_msg = String()
            state_msg.data = json.dumps(self.grid_state.get_state())
            self.state_pub.publish(state_msg)
        except Exception as e:
            rospy.logerr(f"Error publishing grid state: {str(e)}")

    def handle_query(self, msg):
        """Handle specific queries about the grid state"""
        try:
            query = json.loads(msg.data)
            response = {}
            
            if query.get('type') == 'square':
                # Query about specific square
                square = query.get('square')
                if square:
                    response = self.grid_state.get_object_at_square(square)
            
            elif query.get('type') == 'object':
                # Query about specific object type
                color = query.get('color')
                shape = query.get('shape')
                
                # Search for matching objects
                matches = []
                for square, data in self.grid_state.state.items():
                    if ((not color or data['color'] == color) and
                        (not shape or data['shape'] == shape)):
                        matches.append({
                            'square': square,
                            'data': data
                        })
                response = {'matches': matches}
            
            # Publish response
            response_msg = String()
            response_msg.data = json.dumps(response)
            self.query_response_pub.publish(response_msg)
            
        except json.JSONDecodeError as e:
            rospy.logerr(f"Error decoding query: {str(e)}")
        except Exception as e:
            rospy.logerr(f"Error handling query: {str(e)}")

def main():
    try:
        publisher = GridStatePublisher()
        
        # Spin to keep the node alive
        rospy.spin()
        
    except rospy.ROSInterruptException:
        pass
    except Exception as e:
        rospy.logerr(f"Grid state publisher error: {str(e)}")

if __name__ == '__main__':
    main()