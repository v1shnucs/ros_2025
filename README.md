# Sawyer Robot Table Object Manipulation

A ROS-based system for intelligent table object manipulation using the Sawyer robot with vision and speech capabilities.

## System Components

- Vision System: Object detection using dual neural network models
- Speech Interface: Google Cloud Speech-to-Text integration
- GPT Integration: Natural language processing using GPT-3.5-turbo-instruct
- Robot Control: Precise movement and gripper control for object manipulation

## Prerequisites

- ROS (same version as current setup)
- Python 2.7
- Sawyer Robot with intera_sdk
- RealSense Camera
- Google Cloud Speech-to-Text credentials
- OpenAI API key

## Installation

1. Clone the repository into your ROS workspace:
```bash
cd ~/ros_ws/src
git clone [repository-url]
```

2. Install Python dependencies:
```bash
pip install tensorflow==2.16.1
pip install numpy==1.26.3
pip install pandas==2.1.4
pip install sounddevice
pip install google-cloud-speech
```

3. Set up environment variables:
```bash
# Add to ~/.bashrc
export OPENAI_API_KEY='your-key-here'
export GOOGLE_APPLICATION_CREDENTIALS='path-to-credentials.json'
```

4. Build the workspace:
```bash
cd ~/ros_ws
catkin_make
```

## Configuration

1. Camera Settings:
- Edit `src/gpt_vision/config/camera_params.yaml` for camera parameters
- Default resolution: 1920x1080, processing size: 230x440

2. Robot Positions:
- Predefined positions in `src/robot_action/src/scripts/act_gpt.py`
- 12 grid positions for precise object manipulation
- Neutral position defined for safe movement

## Usage

1. Start the system:
```bash
roslaunch full_system.launch
```

2. The system supports:
- Natural language commands
- Grid-based object manipulation (12 squares)
- Automatic state tracking and verification
- Error recovery and status reporting

3. Example commands:
```
"What objects do you see on the table?"
"Pick up the red triangle in square 1"
"Place it in square 5"
```

## File Structure

```
src/
├── gpt_vision/
│   ├── models/           # Neural network models
│   ├── config/          # Camera and vision settings
│   └── scripts/         # Vision processing
├── audio/
│   └── scripts/         # Speech recognition
├── robot_action/
│   └── scripts/         # Robot control
└── launch/             # Launch files
```

## Components

### Vision System
- Dual model approach for reliable object detection
- Real-time state tracking
- Image quality verification

### Speech System
- Google Cloud Speech-to-Text integration
- Confidence-based recognition
- Error handling and retries

### Robot Control
- Precise positioning system
- Safe movement paths
- Gripper control
- Status monitoring

## Common Operations

1. Starting the System:
```bash
source devel/setup.bash
roslaunch full_system.launch
```

2. Checking System Status:
```bash
rostopic echo /robot/status     # Robot status
rostopic echo /vision/grid_state # Table state
```

3. Manual Control:
```bash
# Open gripper
rosrun robot_action open_gripper.py

# Close gripper
rosrun robot_action close_gripper.py

# Move to neutral
rosrun robot_action goto_table_neutral.py
```

## Troubleshooting

1. Vision Issues:
- Check camera connection
- Verify lighting conditions
- Ensure proper table view

2. Speech Recognition:
- Check microphone connection
- Verify Google Cloud credentials
- Check internet connection

3. Robot Control:
- Verify robot initialization
- Check joint limits
- Monitor gripper status

## Contributing

1. Follow ROS coding standards
2. Maintain existing motion parameters
3. Test thoroughly before committing
4. Update documentation as needed

## License

[Your License Information]

## Authors

[Your Information]