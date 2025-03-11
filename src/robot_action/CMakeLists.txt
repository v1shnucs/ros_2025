cmake_minimum_required(VERSION 3.0.2)
project(robot_action)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  intera_interface
  intera_motion_interface
  intera_core_msgs
  sensor_msgs
  message_generation
)

catkin_python_setup()

## Generate messages in the 'msg' folder
# add_message_files(
#   FILES
# )

## Generate services in the 'srv' folder
# add_service_files(
#   FILES
# )

## Generate added messages and services with any dependencies listed here
# generate_messages(
#   DEPENDENCIES
#   std_msgs
# )

catkin_package(
  CATKIN_DEPENDS
    rospy
    std_msgs
    intera_interface
    intera_motion_interface
    intera_core_msgs
    sensor_msgs
    message_runtime
)

include_directories(
  ${catkin_INCLUDE_DIRS}
)

## Install Python scripts
catkin_install_python(PROGRAMS
  src/scripts/act_gpt.py
  src/scripts/goto_table_neutral.py
  src/scripts/open_gripper.py
  src/scripts/close_gripper.py
  src/scripts/test_sequence.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

## Install launch files
install(DIRECTORY launch/
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/launch
  FILES_MATCHING PATTERN "*.launch"
)

## Install config files
install(DIRECTORY config/
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/config
  FILES_MATCHING PATTERN "*.yaml"
)
