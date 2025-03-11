#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting quick hardware test sequence...${NC}"

# Source ROS workspace and Intera SDK
echo -e "\n${YELLOW}Setting up environment...${NC}"
source devel/setup.bash
source intera.sh

# Function to check command status
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Success${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed${NC}"
        return 1
    fi
}

# 1. Check robot status
echo -e "\n${YELLOW}1. Checking robot status...${NC}"
rosrun intera_interface enable_robot.py -s
check_status
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Robot not responding. Please check connection.${NC}"
    exit 1
fi

# 2. Check robot information
echo -e "\n${YELLOW}2. Getting robot information...${NC}"
echo "Robot State:"
rosrun intera_interface enable_robot.py -s | grep "Robot State:"

echo "Joint States:"
rostopic echo /robot/joint_states -n 1 > /dev/null
check_status

# 3. Enable robot
echo -e "\n${YELLOW}3. Enabling robot...${NC}"
rosrun intera_interface enable_robot.py -e
check_status
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to enable robot.${NC}"
    exit 1
fi

# 4. Check camera
echo -e "\n${YELLOW}4. Testing RealSense camera...${NC}"
echo "Checking camera topics..."
rostopic list | grep "/camera/color"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Camera topics found${NC}"
    
    echo "Checking camera feed..."
    timeout 2 rostopic echo /camera/color/image_raw -n 1 > /dev/null
    check_status
else
    echo -e "${RED}✗ Camera topics not found${NC}"
fi

# 5. Test gripper
echo -e "\n${YELLOW}5. Testing gripper...${NC}"
echo "Opening gripper..."
rosrun robot_action open_gripper.py
check_status

sleep 2

echo "Closing gripper..."
rosrun robot_action close_gripper.py
check_status

sleep 2

echo "Opening gripper again..."
rosrun robot_action open_gripper.py
check_status

# 6. Test neutral position
echo -e "\n${YELLOW}6. Testing neutral position movement...${NC}"
rosrun robot_action goto_table_neutral.py
check_status

# 7. Check available topics
echo -e "\n${YELLOW}7. Checking critical ROS topics...${NC}"
REQUIRED_TOPICS=(
    "/robot/joint_states"
    "/robot/state"
    "/camera/color/image_raw"
    "/vision/grid_state"
    "/audio/speech_text_ros"
    "/robot/status"
)

for topic in "${REQUIRED_TOPICS[@]}"; do
    echo -n "Checking $topic ... "
    rostopic info $topic > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
    fi
done

# 8. Final status
echo -e "\n${YELLOW}8. Checking final robot state...${NC}"
rosrun intera_interface enable_robot.py -s
check_status

# Return to neutral and disable robot
echo -e "\n${YELLOW}Cleaning up...${NC}"
echo "Returning to neutral position..."
rosrun robot_action goto_table_neutral.py

echo "Disabling robot..."
rosrun intera_interface enable_robot.py -d
check_status

echo -e "\n${GREEN}Quick test sequence completed!${NC}"
echo "Check the output above for any error messages marked with ✗"
echo "For detailed testing, use: ./test.sh"

exit 0