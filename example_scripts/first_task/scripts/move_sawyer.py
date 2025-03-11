#!/usr/bin/env python

import sys
import copy
import rospy
import moveit_commander
from geometry_msgs.msg import Pose
from math import pi
from std_msgs.msg import String
from moveit_commander.conversions import pose_to_list
import argparse
from intera_motion_interface import (
    MotionTrajectory,
    MotionWaypoint,
    MotionWaypointOptions
)
from intera_motion_msgs.msg import TrajectoryOptions
from geometry_msgs.msg import PoseStamped
import PyKDL
from tf_conversions import posemath
from intera_interface import Limb

# Initialize the move_group API
moveit_commander.roscpp_initialize(sys.argv)

# Initialize the rosoppy node
rospy.init_node('move_sawyer', anonymous=True)

# Connect the right arm move group
group = moveit_commander.MoveGroupCommander("right_hand")

# Create a Pose object for the target positon
target_pose = Pose()
target_pose.position.x = 0.5 # replace all with corresponding values
target_pose.position.y = 0.5
target_pose.position.z = 0.5 

# Set the target pose 
group.set_pose_target(target_pose)

# Plan and execute the motion
plan = group.plan()
group.execute(plan, wait = True)
