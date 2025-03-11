#!/usr/bin/env python2

import rospy
from std_msgs.msg import String
import subprocess
import json
import os
import signal

class SpeechBridge:
    def __init__(self):
        rospy.init_node('speech_bridge')
        
        # Publishers that will be used by ROS nodes
        self.speech_pub = rospy.Publisher('/audio/speech_text_ros', String, queue_size=10)
        self.status_pub = rospy.Publisher('/audio/status_ros', String, queue_size=10)
        
        # Subscribe to control commands from ROS nodes
        rospy.Subscriber('/audio/control_ros', String, self.control_callback)
        
        # Process management
        self.py3_process = None
        self.start_python3_node()
        
        rospy.loginfo("Speech bridge initialized")
        
    def start_python3_node(self):
        """Start the Python 3 speech recognition node"""
        try:
            script_path = os.path.join(os.path.dirname(__file__), 'speech_recognition.py')
            self.py3_process = subprocess.Popen(['python3', script_path])
            rospy.loginfo("Started Python 3 speech recognition node")
        except Exception as e:
            rospy.logerr("Failed to start Python 3 node: %s", str(e))

    def control_callback(self, msg):
        """Forward control messages to Python 3 node"""
        try:
            # Forward the message to the Python 3 node's topic
            control_pub = rospy.Publisher('/audio/control', String, queue_size=10)
            control_pub.publish(msg)
        except Exception as e:
            rospy.logerr("Error forwarding control message: %s", str(e))

    def cleanup(self):
        """Clean up processes on shutdown"""
        if self.py3_process:
            self.py3_process.terminate()
            try:
                self.py3_process.wait(timeout=5)
            except:
                self.py3_process.kill()
            rospy.loginfo("Python 3 node terminated")

def main():
    bridge = None
    try:
        bridge = SpeechBridge()
        
        # Subscribe to Python 3 node topics
        rospy.Subscriber('/audio/speech_text', String,
                        lambda msg: bridge.speech_pub.publish(msg))
        rospy.Subscriber('/audio/status', String,
                        lambda msg: bridge.status_pub.publish(msg))
        
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
    except Exception as e:
        rospy.logerr("Speech bridge error: %s", str(e))
    finally:
        if bridge:
            bridge.cleanup()

if __name__ == '__main__':
    main()