#!/bin/bash

# Source ROS workspace
source devel/setup.bash

# Check environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY is not set"
    exit 1
fi

if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "Error: GOOGLE_APPLICATION_CREDENTIALS is not set"
    exit 1
fi

# Source Intera SDK
source intera.sh

echo "Starting robot system..."

# Launch main system
roslaunch full_system.launch