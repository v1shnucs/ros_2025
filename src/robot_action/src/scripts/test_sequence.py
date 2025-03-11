#!/usr/bin/env python2

import rospy
from std_msgs.msg import String
import json
import time
from intera_interface import Limb
import goto_table_neutral

class SystemTester:
    def __init__(self):
        rospy.init_node('system_tester')
        
        # Publishers
        self.audio_control_pub = rospy.Publisher('/audio/control_ros', String, queue_size=1)
        self.vision_request_pub = rospy.Publisher('/vision/request_state', String, queue_size=1)
        
        # Subscribers
        rospy.Subscriber('/vision/grid_state', String, self.vision_callback)
        rospy.Subscriber('/audio/speech_text_ros', String, self.speech_callback)
        rospy.Subscriber('/robot/status', String, self.robot_status_callback)
        
        # State tracking
        self.current_grid_state = None
        self.last_speech = None
        self.robot_status = None
        self.test_complete = False
        
        # Test timeouts
        self.VISION_TIMEOUT = 5.0  # seconds
        self.SPEECH_TIMEOUT = 10.0
        self.ROBOT_TIMEOUT = 15.0
        
        rospy.loginfo("System tester initialized")

    def wait_for_condition(self, condition_func, timeout, error_msg):
        """Wait for a condition with timeout"""
        start_time = rospy.Time.now()
        rate = rospy.Rate(10)  # 10Hz check rate
        
        while not rospy.is_shutdown():
            if condition_func():
                return True
            
            if (rospy.Time.now() - start_time).to_sec() > timeout:
                rospy.logerr(error_msg)
                return False
                
            rate.sleep()
        
        return False

    def check_robot_enabled(self):
        """Verify robot is enabled and responding"""
        try:
            limb = Limb()
            return limb.is_enabled()
        except Exception as e:
            rospy.logerr("Robot check failed: %s", str(e))
            return False

    def vision_callback(self, msg):
        """Handle vision system state updates"""
        try:
            self.current_grid_state = json.loads(msg.data)
            rospy.loginfo("Received grid state update")
        except Exception as e:
            rospy.logerr("Error processing vision state: %s", str(e))

    def speech_callback(self, msg):
        """Handle speech recognition results"""
        try:
            self.last_speech = json.loads(msg.data)
            rospy.loginfo("Received speech: %s", 
                         self.last_speech.get('text', ''))
        except Exception as e:
            rospy.logerr("Error processing speech: %s", str(e))

    def robot_status_callback(self, msg):
        """Handle robot status updates"""
        try:
            self.robot_status = json.loads(msg.data)
            rospy.loginfo("Robot status: %s", 
                         self.robot_status.get('status', ''))
        except Exception as e:
            rospy.logerr("Error processing robot status: %s", str(e))

    def test_vision_system(self):
        """Test vision system functionality"""
        rospy.loginfo("Testing vision system...")
        
        # Clear previous state
        self.current_grid_state = None
        
        # Request vision update
        self.request_vision_update()
        
        # Wait for vision response
        success = self.wait_for_condition(
            lambda: self.current_grid_state is not None,
            self.VISION_TIMEOUT,
            "Vision system test timed out"
        )
        
        if success:
            rospy.loginfo("Vision system test passed")
        else:
            rospy.logerr("Vision system test failed")
        
        return success

    def test_speech_system(self):
        """Test speech recognition system"""
        rospy.loginfo("Testing speech system...")
        
        # Clear previous speech
        self.last_speech = None
        
        # Start listening
        self.start_listening()
        
        # Wait for speech input
        success = self.wait_for_condition(
            lambda: self.last_speech is not None,
            self.SPEECH_TIMEOUT,
            "Speech recognition test timed out"
        )
        
        # Stop listening regardless of result
        self.stop_listening()
        
        if success:
            rospy.loginfo("Speech system test passed")
        else:
            rospy.logwarn("Speech system test - no speech detected")
        
        return success

    def test_robot_movement(self):
        """Test basic robot movement"""
        rospy.loginfo("Testing robot movement...")
        
        # Check if robot is enabled
        if not self.check_robot_enabled():
            rospy.logerr("Robot not enabled")
            return False
        
        try:
            # Try moving to neutral position
            goto_table_neutral.goto_table_neutral()
            
            # Wait for completion or error
            success = self.wait_for_condition(
                lambda: (self.robot_status and 
                        self.robot_status.get('status') == 'complete'),
                self.ROBOT_TIMEOUT,
                "Robot movement test timed out"
            )
            
            if success:
                rospy.loginfo("Robot movement test passed")
            else:
                rospy.logerr("Robot movement test failed")
            
            return success
            
        except Exception as e:
            rospy.logerr("Robot movement test failed: %s", str(e))
            return False

    def request_vision_update(self):
        """Request current table state"""
        msg = String()
        msg.data = json.dumps({"action": "update"})
        self.vision_request_pub.publish(msg)
        rospy.loginfo("Requested vision update")

    def start_listening(self):
        """Start speech recognition"""
        msg = String()
        msg.data = json.dumps({"action": "start"})
        self.audio_control_pub.publish(msg)
        rospy.loginfo("Started listening")

    def stop_listening(self):
        """Stop speech recognition"""
        msg = String()
        msg.data = json.dumps({"action": "stop"})
        self.audio_control_pub.publish(msg)
        rospy.loginfo("Stopped listening")

    def run_test_sequence(self):
        """Run through test sequence"""
        rospy.loginfo("Starting test sequence")
        overall_success = True

        try:
            # Test 1: Vision System
            if not self.test_vision_system():
                overall_success = False
            
            # Test 2: Speech System
            if not self.test_speech_system():
                overall_success = False
            
            # Test 3: Robot Movement
            if not self.test_robot_movement():
                overall_success = False

            if overall_success:
                rospy.loginfo("All tests completed successfully")
            else:
                rospy.logwarn("Some tests failed - check logs for details")
            
            return overall_success

        except Exception as e:
            rospy.logerr("Test sequence failed: %s", str(e))
            return False
        finally:
            self.test_complete = True
            # Ensure robot is in safe state
            try:
                goto_table_neutral.goto_table_neutral()
            except:
                pass

def main():
    try:
        tester = SystemTester()
        
        # Run test sequence
        result = tester.run_test_sequence()
        
        if result:
            rospy.loginfo("System test completed successfully")
        else:
            rospy.logerr("System test failed")
            
    except rospy.ROSInterruptException:
        pass
    except Exception as e:
        rospy.logerr("Error in system test: %s", str(e))

if __name__ == '__main__':
    main()