#!/bin/bash

# Make all Python scripts executable
chmod +x src/gpt_vision/src/scripts/*.py
chmod +x src/audio/src/scripts/*.py
chmod +x src/robot_action/src/scripts/*.py

# Set permissions for credential files
chmod 600 src/audio/credentials/*.json

# Make launch files executable
chmod +x src/launch/*.launch
chmod +x start_system.sh

echo "Permissions set successfully"

# Additional setup steps
echo "Creating necessary directories if they don't exist..."
mkdir -p src/gpt_vision/src/test_images
mkdir -p src/audio/credentials

echo "Setup complete!"