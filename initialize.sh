#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting system initialization...${NC}"

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

# 1. Make all scripts executable
echo -e "\n${YELLOW}1. Setting file permissions...${NC}"
echo "Making scripts executable..."
chmod +x src/robot_action/src/scripts/*.py
chmod +x src/gpt_vision/src/scripts/*.py
chmod +x src/audio/src/scripts/*.py
chmod +x src/launch/*.launch
chmod +x *.sh
check_status

# 2. Set up credentials
echo -e "\n${YELLOW}2. Setting up credentials...${NC}"
echo "Securing Google Cloud credentials..."
chmod 600 src/audio/credentials/*.json
check_status

# 3. Create necessary directories
echo -e "\n${YELLOW}3. Creating required directories...${NC}"
mkdir -p src/gpt_vision/src/test_images
mkdir -p src/audio/credentials
mkdir -p src/robot_action/logs
check_status

# 4. Build ROS workspace
echo -e "\n${YELLOW}4. Building ROS workspace...${NC}"
echo "Running catkin_make..."
catkin_make
check_status

# 5. Source environment
echo -e "\n${YELLOW}5. Sourcing environment...${NC}"
source devel/setup.bash
source intera.sh
check_status

# 6. Verify ROS installation
echo -e "\n${YELLOW}6. Verifying ROS installation...${NC}"
if command -v roscore >/dev/null 2>&1; then
    echo -e "${GREEN}✓ ROS is properly installed${NC}"
else
    echo -e "${RED}✗ ROS installation not found${NC}"
    exit 1
fi

# 7. Check Python dependencies
echo -e "\n${YELLOW}7. Checking Python dependencies...${NC}"
DEPS=("tensorflow" "numpy" "google-cloud-speech" "sounddevice" "opencv-python" "pyttsx3")
for dep in "${DEPS[@]}"; do
    echo -n "Checking $dep ... "
    if python -c "import $dep" 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        echo "Please install $dep: pip install $dep"
    fi
done

# 8. Verify robot connection
echo -e "\n${YELLOW}8. Verifying robot connection...${NC}"
echo "Checking robot state..."
rosrun intera_interface enable_robot.py -s
check_status

# 9. Start core services
echo -e "\n${YELLOW}9. Starting core services...${NC}"
echo "Starting ROS master..."
roscore &
sleep 5
check_status

echo "Starting robot services..."
rosrun intera_interface joint_trajectory_action_server.py &
sleep 2
check_status

# 10. Final checks
echo -e "\n${YELLOW}10. Performing final checks...${NC}"

# Check if critical files exist
CRITICAL_FILES=(
    "src/robot_action/src/scripts/act_gpt.py"
    "src/gpt_vision/src/scripts/vision_processing.py"
    "src/audio/src/scripts/speech_recognition.py"
    "src/launch/full_system.launch"
    "src/audio/credentials/surf-test-426821-4c653702a368.json"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "Checking $file ... ${GREEN}✓${NC}"
    else
        echo -e "Checking $file ... ${RED}✗${NC}"
    fi
done

echo -e "\n${GREEN}Initialization complete!${NC}"
echo -e "\nYou can now:"
echo "1. Run quick hardware test:    ./quick_test.sh"
echo "2. Run full system test:       ./test.sh"
echo "3. Start the full system:      ./start_system.sh"
echo "4. Clean up in emergency:      ./cleanup.sh"

exit 0