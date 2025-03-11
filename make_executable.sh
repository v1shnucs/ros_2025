#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Making scripts executable..."

# Make shell scripts executable
chmod +x *.sh
echo -e "${GREEN}✓${NC} Shell scripts"

# Make Python scripts executable
chmod +x src/robot_action/src/scripts/*.py
chmod +x src/gpt_vision/src/scripts/*.py
chmod +x src/audio/src/scripts/*.py
echo -e "${GREEN}✓${NC} Python scripts"

# Make launch files executable
chmod +x src/launch/*.launch
chmod +x src/robot_action/launch/*.launch
echo -e "${GREEN}✓${NC} Launch files"

# Set restricted permissions for credentials
chmod 600 src/audio/credentials/*.json
echo -e "${GREEN}✓${NC} Credentials file permissions"

echo "Verifying permissions..."

# Check shell scripts
for script in *.sh; do
    if [ -x "$script" ]; then
        echo -e "${GREEN}✓${NC} $script is executable"
    else
        echo -e "${RED}✗${NC} $script is not executable"
    fi
done

# Check Python scripts
for dir in "robot_action" "gpt_vision" "audio"; do
    if [ -d "src/$dir/src/scripts" ]; then
        for script in src/$dir/src/scripts/*.py; do
            if [ -x "$script" ]; then
                echo -e "${GREEN}✓${NC} $script is executable"
            else
                echo -e "${RED}✗${NC} $script is not executable"
            fi
        done
    fi
done

# Check credentials
cred_file="src/audio/credentials/surf-test-426821-4c653702a368.json"
if [ -f "$cred_file" ]; then
    perms=$(stat -c "%a" "$cred_file")
    if [ "$perms" = "600" ]; then
        echo -e "${GREEN}✓${NC} Credentials have correct permissions"
    else
        echo -e "${RED}✗${NC} Credentials have incorrect permissions: $perms"
    fi
else
    echo -e "${RED}✗${NC} Credentials file not found"
fi

echo "Setup complete!"
echo "You can now run ./initialize.sh to start the system setup"