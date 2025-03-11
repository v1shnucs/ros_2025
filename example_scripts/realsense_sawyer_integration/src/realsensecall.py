#Q/usr/bin/env python

import rospyfrom sensor_msgs.msg import Image

def depth_image_callback(msg):
    #for processing depth info
    pass

def main():
    rospy.init_node('realsense_saywer_intergration')
    rospy.Subscriber('/camera/depth/image_rect_raw', Image, depth_image_callback)
    #other control and setup for saywer here
    rospy.spin()

if __name__ == '__main__':
    main()