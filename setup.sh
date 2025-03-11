#!/bin/bash

echo "Setting up ROS workspace permissions..."

# Make main scripts executable
chmod +x src/robot_action/src/scripts/*.py
chmod +x src/gpt_vision/src/scripts/*.py
chmod +x src/audio/src/scripts/*.py

# Set permissions for launch files
chmod +x src/launch/*.launch

# Secure Google Cloud credentials
chmod 600 src/audio/credentials/*.json

# Make utility scripts executable
chmod +x *.sh

# Make all Python files readable
find . -name "*.py" -exec chmod 644 {} \;

# Create necessary directories if they don't exist
mkdir -p src/gpt_vision/src/test_images
mkdir -p src/audio/credentials

echo "Permissions set successfully"
echo "Running sanity checks..."

# Check if core files are executable
for script in src/robot_action/src/scripts/act_gpt.py \
             src/robot_action/src/scripts/goto_table_neutral.py \
             src/gpt_vision/src/scripts/vision_processing.py \
             src/audio/src/scripts/speech_recognition.py \
             src/audio/src/scripts/speak_gpt.py \
             src/audio/src/scripts/speech_bridge.py; do
    if [ -x "$script" ]; then
        echo "✓ $script is executable"
    else
        echo "✗ $script is not executable"
    fi
done

# Check credentials file
creds_file="src/audio/credentials/surf-test-426821-4c653702a368.json"
if [ -f "$creds_file" ]; then
    perms=$(stat -c "%a" "$creds_file")
    if [ "$perms" = "600" ]; then
        echo "✓ Credentials file has correct permissions"
    else
        echo "✗ Credentials file has incorrect permissions: $perms"
    fi
else
    echo "✗ Credentials file not found"
fi

echo "Setup complete!"