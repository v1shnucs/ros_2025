#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Checking system setup..."

# Check ROS installation
echo -n "Checking ROS installation: "
if command -v roscore >/dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}Not found${NC}"
    echo "Please install ROS"
    exit 1
fi

# Check Python dependencies
echo "Checking Python dependencies..."
DEPS=("tensorflow" "numpy" "google-cloud-speech" "sounddevice" "opencv-python" "pyttsx3")
for dep in "${DEPS[@]}"; do
    echo -n "  $dep: "
    if python -c "import $dep" 2>/dev/null; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${RED}Not found${NC}"
        echo "Please run: pip install $dep"
    fi
done

# Check file permissions
echo "Checking file permissions..."

# Check launch files
echo -n "  Launch files: "
if [ -x "src/launch/full_system.launch" ]; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${YELLOW}Fixing...${NC}"
    chmod +x src/launch/full_system.launch
fi

# Check scripts
SCRIPTS=(
    "src/robot_action/src/scripts/act_gpt.py"
    "src/robot_action/src/scripts/goto_table_neutral.py"
    "src/robot_action/src/scripts/open_gripper.py"
    "src/robot_action/src/scripts/close_gripper.py"
    "src/robot_action/src/scripts/test_sequence.py"
    "src/gpt_vision/src/scripts/vision_processing.py"
    "src/gpt_vision/src/scripts/grid_state_publisher.py"
    "src/audio/src/scripts/speech_recognition.py"
    "src/audio/src/scripts/speak_gpt.py"
)

for script in "${SCRIPTS[@]}"; do
    echo -n "  $script: "
    if [ -x "$script" ]; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${YELLOW}Fixing...${NC}"
        chmod +x "$script"
    fi
done

# Check credentials
echo -n "Checking Google Cloud credentials: "
if [ -f "src/audio/credentials/surf-test-426821-4c653702a368.json" ]; then
    echo -e "${GREEN}Found${NC}"
    # Check permissions
    PERMS=$(stat -c "%a" "src/audio/credentials/surf-test-426821-4c653702a368.json")
    if [ "$PERMS" != "600" ]; then
        echo -e "${YELLOW}Fixing credentials permissions...${NC}"
        chmod 600 "src/audio/credentials/surf-test-426821-4c653702a368.json"
    fi
else
    echo -e "${RED}Not found${NC}"
    echo "Please ensure Google Cloud credentials are in place"
fi

# Check OpenAI API key
echo -n "Checking OpenAI API key: "
if [ -f ".env" ] && grep -q "OPENAI_API_KEY" ".env"; then
    echo -e "${GREEN}Found${NC}"
else
    echo -e "${RED}Not found${NC}"
    echo "Please set up your OpenAI API key in .env file"
fi

# Check shell scripts
SHELL_SCRIPTS=("start_system.sh" "quick_test.sh" "setup_permissions.sh")
for script in "${SHELL_SCRIPTS[@]}"; do
    echo -n "Checking $script: "
    if [ -x "$script" ]; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${YELLOW}Fixing...${NC}"
        chmod +x "$script"
    fi
done

echo ""
echo "Setup check complete!"
echo "If any items were marked in ${RED}red${NC}, please fix them before running the system."
echo "Items marked in ${YELLOW}yellow${NC} were automatically fixed."
echo "Items marked in ${GREEN}green${NC} are ready to use."