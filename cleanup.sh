#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Performing emergency cleanup...${NC}"

# Source ROS workspace and Intera SDK
source devel/setup.bash
source intera.sh

# Function to check if ROS master is running
check_ros_master() {
    timeout 2 rostopic list > /dev/null 2>&1
    return $?
}

# Function to kill all ROS nodes except master
kill_ros_nodes() {
    echo "Stopping ROS nodes..."
    rosnode kill -a > /dev/null 2>&1
    sleep 2
}

# Function to ensure robot is disabled
disable_robot() {
    echo "Disabling robot..."
    rosrun intera_interface enable_robot.py -d > /dev/null 2>&1
}

# Function to open gripper (if possible)
open_gripper() {
    echo "Opening gripper..."
    rosrun robot_action open_gripper.py > /dev/null 2>&1
}

# Function to attempt safe neutral position
try_neutral() {
    echo "Attempting to return to neutral position..."
    rosrun robot_action goto_table_neutral.py > /dev/null 2>&1
}

# Main cleanup sequence
echo -e "\n${YELLOW}Starting cleanup sequence...${NC}"

# 1. Check if ROS is running
if check_ros_master; then
    echo -e "${GREEN}✓ ROS master is running${NC}"
    
    # 2. Try to open gripper
    open_gripper
    sleep 2
    
    # 3. Try to move to neutral position
    try_neutral
    sleep 2
    
    # 4. Disable robot
    disable_robot
    sleep 1
    
    # 5. Kill all ROS nodes
    kill_ros_nodes
    
else
    echo -e "${RED}✗ ROS master not running${NC}"
    echo "Starting ROS and attempting cleanup..."
    
    # Try to start roscore and retry
    roscore & 
    sleep 5
    
    if check_ros_master; then
        disable_robot
        kill_ros_nodes
    else
        echo -e "${RED}Failed to start ROS master${NC}"
    fi
fi

# Final cleanup
echo -e "\n${YELLOW}Cleaning up processes...${NC}"

# Kill any remaining robot-related processes
pkill -f "intera"
pkill -f "sawyer"
pkill -f "robot_action"
pkill -f "vision_processing"
pkill -f "speech_recognition"

# Kill roscore if we started it
pkill -f "roscore"
pkill -f "rosmaster"

echo -e "\n${GREEN}Cleanup complete!${NC}"
echo "The robot should now be in a safe state."
echo "Please verify physically that the robot is disabled and in a safe position."

exit 0