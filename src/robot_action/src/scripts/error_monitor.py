#!/usr/bin/env python2

import rospy
from std_msgs.msg import String
import json
import os
from datetime import datetime

class ErrorMonitor:
    def __init__(self):
        rospy.init_node('error_monitor')
        
        # Create log directory
        self.log_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'logs'
        )
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        # Initialize error counts
        self.error_counts = {
            'vision': 0,
            'speech': 0,
            'robot': 0,
            'system': 0
        }
        
        # Subscribe to error topics
        rospy.Subscriber('/vision/grid_state', String, 
                        lambda msg: self.log_error(msg, 'vision'))
        rospy.Subscriber('/audio/status_ros', String, 
                        lambda msg: self.log_error(msg, 'speech'))
        rospy.Subscriber('/robot/status', String, 
                        lambda msg: self.log_error(msg, 'robot'))
        rospy.Subscriber('/speak_errors', String, 
                        lambda msg: self.log_error(msg, 'speech'))
        
        # Status publisher
        self.status_pub = rospy.Publisher(
            '/system/error_status',
            String,
            queue_size=10
        )
        
        # Log file setup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = os.path.join(self.log_dir, f'errors_{timestamp}.log')
        self.write_log("Error monitoring started")
        
        rospy.loginfo("Error monitor initialized")

    def write_log(self, message):
        """Write message to log file with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            with open(self.log_file, 'a') as f:
                f.write(f"[{timestamp}] {message}\n")
        except Exception as e:
            rospy.logerr("Failed to write to log file: %s", str(e))

    def log_error(self, msg, system):
        """Process and log error messages"""
        try:
            data = json.loads(msg.data)
            
            # Check if message contains error
            if any(err in data.get('status', '').lower() 
                  for err in ['error', 'fail', 'timeout']):
                self.error_counts[system] += 1
                
                error_msg = (f"[{system.upper()}] Error: "
                           f"{data.get('details', 'No details provided')}")
                
                # Log to file
                self.write_log(error_msg)
                
                # Log to ROS
                rospy.logerr(error_msg)
                
                # Publish error status
                self.publish_status()
                
        except json.JSONDecodeError:
            # Handle plain text error messages
            if 'error' in msg.data.lower():
                self.error_counts[system] += 1
                self.write_log(f"[{system.upper()}] Error: {msg.data}")
                rospy.logerr("%s error: %s", system.upper(), msg.data)
                self.publish_status()
                
        except Exception as e:
            rospy.logerr("Error processing message: %s", str(e))

    def publish_status(self):
        """Publish current error status"""
        try:
            status = {
                'error_counts': self.error_counts,
                'total_errors': sum(self.error_counts.values()),
                'timestamp': rospy.Time.now().to_sec()
            }
            
            status_msg = String()
            status_msg.data = json.dumps(status)
            self.status_pub.publish(status_msg)
            
        except Exception as e:
            rospy.logerr("Error publishing status: %s", str(e))

    def on_shutdown(self):
        """Cleanup on node shutdown"""
        total_errors = sum(self.error_counts.values())
        summary = (f"\nTest session completed with {total_errors} total errors:\n" +
                  "\n".join(f"- {sys}: {count}" 
                          for sys, count in self.error_counts.items()))
        
        self.write_log(summary)
        rospy.loginfo(summary)

def main():
    try:
        monitor = ErrorMonitor()
        rospy.on_shutdown(monitor.on_shutdown)
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
    except Exception as e:
        rospy.logerr("Error monitor failed: %s", str(e))

if __name__ == '__main__':
    main()