# Copyright 2020 ros2_control Development Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution, LaunchConfiguration

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
import os


def generate_launch_description():
    # Declare arguments
    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            "gui",
            default_value="true",
            description="Start RViz2 automatically with this launch file.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "use_mock_hardware",
            default_value="false",
            description="Start robot with mock hardware mirroring command to its states.",
        )
    )

    # Initialize Arguments
    gui = LaunchConfiguration("gui")
    use_mock_hardware = LaunchConfiguration("use_mock_hardware")
    
    odrive_diffbot_launch_file = PathJoinSubstitution([
        '/home/nuc/my_tondo_ws/src/odrive_ros2_control',
        'odrive_demo_bringup/launch',  # Replace 'path' with the correct directory path
        'odrive_diffbot.launch.py'
    ])
    
    
    # Include the odrive_diffbot_launch.py file in the launch description
    launch_odrive_diffbot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(odrive_diffbot_launch_file)
    )
    

    # Define the path to the twist_mux twist_mux_launch.py
    my_twist_mux_launch_file = PathJoinSubstitution([
        '/home/nuc/my_tondo_ws/src',
        'twist_mux/launch',  # Replace 'path' with the correct directory path
        'twist_mux_launch.py'
    ])

    # Include the rplidar_a1_launch.py file in the launch description
    launch_my_twist_mux = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(my_twist_mux_launch_file)
    )
    
    # Define the path to the rplidar_a1_launch.py file
    rplidar_launch_file = PathJoinSubstitution([
        '/home/nuc/my_tondo_ws/src',
        'rplidar_ros/launch',  # Replace 'path' with the correct directory path
        'rplidar_a1_launch.py'
    ])

    # Include the rplidar_a1_launch.py file in the launch description
    launch_rplidar = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(rplidar_launch_file)
    )

   
    rviz_config_file = PathJoinSubstitution(
        [FindPackageShare("tondo_bringup"), "rviz", "rviz_config.rviz"]
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config_file],
        condition=IfCondition(gui)
    )
    '''maybe add to odrive lauch for ros2_control
    # Delay rviz start after `joint_state_broadcaster`
    delay_rviz_after_joint_state_broadcaster_spawner = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[rviz_node]
        )
    )

    # Delay start of robot_controller after `joint_state_broadcaster`
    delay_robot_controller_spawner_after_joint_state_broadcaster_spawner = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[robot_controller_spawner]
        )
    )
    '''
    # launch joy node
    joy_node = Node(
        package="joy",
        executable="joy_node",
        name="joy_node",
        output="log"
    )

    # launch left joystick to control the robot teleop
    left_joystick_node = Node(
        package="joystick_to_wheel_test",
        executable="left_joystick_diffbot_base_cmdvel_unstamped",
        name="left_joystick",
        output="log"
    )



    nodes = [
        launch_odrive_diffbot,
        launch_rplidar,
        #rviz_node,
        joy_node,
        left_joystick_node,
        launch_my_twist_mux
    ]

    return LaunchDescription(declared_arguments + nodes)

