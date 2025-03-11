#!/usr/bin/env python

import rospy
from intera_motion_interface import (
    MotionTrajectory,
    MotionWaypoint,
    MotionWaypointOptions
)
from intera_interface import Limb

def goto_table_neutral():
    """
    goto_table_neutral primes arm to execute goto_square
    """
    try:
        limb = Limb()
        traj = MotionTrajectory(limb=limb)

        # Keep exact same neutral position and parameters
        args = {
            'speed_ratio': 0.5,
            'accel_ratio': 0.5,
            'timeout': None,
            'joint_angles': [
                0.18966015625,      # j0
                0.347060546875,     # j1
                -1.9490498046875,   # j2
                1.6227490234375,    # j3
                1.8296552734375,    # j4
                1.9532705078125,    # j5
                2.10231640625       # j6
            ]
        }

        # Configure waypoint options
        wpt_opts = MotionWaypointOptions(
            max_joint_speed_ratio=args['speed_ratio'],
            max_joint_accel=args['accel_ratio']
        )
        waypoint = MotionWaypoint(options=wpt_opts.to_msg(), limb=limb)

        # Get current joint angles
        joint_angles = limb.joint_ordered_angles()

        if len(args['joint_angles']) != len(joint_angles):
            rospy.logerr('The number of joint_angles must be %d', len(joint_angles))
            return None

        # Add current position waypoint
        waypoint.set_joint_angles(joint_angles=joint_angles)
        traj.append_waypoint(waypoint.to_msg())

        # Add neutral position waypoint
        waypoint.set_joint_angles(joint_angles=args['joint_angles'])
        traj.append_waypoint(waypoint.to_msg())

        # Execute trajectory
        result = traj.send_trajectory(timeout=args['timeout'])
        if result is None:
            rospy.logerr('Trajectory FAILED to send')
            return

        if result.result:
            rospy.loginfo('Successfully moved to table neutral position')
        else:
            rospy.logerr('Motion controller failed to complete trajectory with error %s',
                     result.errorId)

    except rospy.ROSInterruptException:
        rospy.logerr('Keyboard interrupt detected. Exiting before trajectory completion.')
    except Exception as e:
        rospy.logerr('Error: %s', str(e))

def main():
    """Main function to run the node"""
    try:
        rospy.init_node('goto_table_neutral', anonymous=True)
        rospy.loginfo("goto_table_neutral node initialized")
        goto_table_neutral()
    except rospy.ROSInterruptException:
        pass
    except Exception as e:
        rospy.logerr("Error: %s", str(e))

if __name__ == '__main__':
    main()