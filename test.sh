#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default parameters
TEST_VISION=true
TEST_SPEECH=true
TEST_ROBOT=true
SAFETY_MODE=true

# Function to print usage
print_usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -h, --help           Show this help message"
    echo "  --no-vision          Skip vision system tests"
    echo "  --no-speech          Skip speech system tests"
    echo "  --no-robot           Skip robot movement tests"
    echo "  --no-safety          Disable safety mode (full speed)"
    echo "  --vision-only        Test only vision system"
    echo "  --speech-only        Test only speech system"
    echo "  --robot-only         Test only robot movement"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            print_usage
            exit 0
            ;;
        --no-vision)
            TEST_VISION=false
            shift
            ;;
        --no-speech)
            TEST_SPEECH=false
            shift
            ;;
        --no-robot)
            TEST_ROBOT=false
            shift
            ;;
        --no-safety)
            SAFETY_MODE=false
            shift
            ;;
        --vision-only)
            TEST_SPEECH=false
            TEST_ROBOT=false
            shift
            ;;
        --speech-only)
            TEST_VISION=false
            TEST_ROBOT=false
            shift
            ;;
        --robot-only)
            TEST_VISION=false
            TEST_SPEECH=false
            shift
            ;;
        *)
            echo "Unknown option: $1"
            print_usage
            exit 1
            ;;
    esac
done

# Check if Intera SDK is sourced
if ! command -v rosrun &> /dev/null; then
    echo -e "${YELLOW}Sourcing Intera SDK...${NC}"
    source intera.sh
fi

# Source ROS workspace
source devel/setup.bash

# Print test configuration
echo -e "${GREEN}Test Configuration:${NC}"
echo -e "Vision System: $([ "$TEST_VISION" == "true" ] && echo "Enabled" || echo "Disabled")"
echo -e "Speech System: $([ "$TEST_SPEECH" == "true" ] && echo "Enabled" || echo "Disabled")"
echo -e "Robot Movement: $([ "$TEST_ROBOT" == "true" ] && echo "Enabled" || echo "Disabled")"
echo -e "Safety Mode: $([ "$SAFETY_MODE" == "true" ] && echo "Enabled" || echo "Disabled")"
echo ""

# Confirm before proceeding
read -p "Press Enter to start tests or Ctrl+C to cancel..."

# Launch test system
roslaunch robot_action test_system.launch \
    test_vision:=$TEST_VISION \
    test_speech:=$TEST_SPEECH \
    test_robot:=$TEST_ROBOT \
    safety_mode:=$SAFETY_MODE

# Check for test results
if [ -d "src/robot_action/logs" ]; then
    LATEST_LOG=$(ls -t src/robot_action/logs/errors_*.log | head -n1)
    if [ -f "$LATEST_LOG" ]; then
        echo -e "\n${GREEN}Test Results:${NC}"
        cat "$LATEST_LOG"
    fi
fi