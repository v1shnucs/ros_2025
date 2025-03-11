#!/usr/bin/env python
import rospy
from sensor_msgs.msg import Image
from apriltag_ros.msg import AprilTagDetectionArray
import cv2
from cv_bridge import CvBridge, CvBridgeError

class AprilTagDetector:
    def __init__(self):
        self.bridge = CvBridge()
        self.image_sub = rospy.Subscriber("/camera/color/image_raw", Image, self.image_callback)
        self.tag_detections_sub = rospy.Subscriber("/tag_detections", AprilTagDetectionArray, self.detections_callback)
        self.detections = []

    def image_callback(self, data):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
            
            # Draw detection results on the image
            for detection in self.detections:
                for corner in detection.corners:
                    cv2.circle(cv_image, (int(corner.x), int(corner.y)), 5, (0, 255, 0), 2)
                center = detection.center
                cv2.putText(cv_image, str(detection.id[0]), (int(center.x), int(center.y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            # Display the image with detected tags
            cv2.imshow("Image", cv_image)
            cv2.waitKey(1)
        except CvBridgeError as e:
            rospy.logerr(e)

    def detections_callback(self, data):
        self.detections = data.detections
        # Log detection IDs to the ROS console
        for detection in data.detections:
            rospy.loginfo("Detected tag ID: %d", detection.id[0])

def main():
    rospy.init_node('apriltag_detector', anonymous=True)
    AprilTagDetector()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        rospy.loginfo("Shutting down")
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()



