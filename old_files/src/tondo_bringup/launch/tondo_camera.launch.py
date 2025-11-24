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

    # Construct the path to rs_launch.py
    rs_launch_file = PathJoinSubstitution([
        get_package_share_directory('realsense2_camera'),
        'launch',
        'rs_launch.py'
    ])

    # Include the rs_launch.py file in the launch description
    launch_realsense_camera = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(rs_launch_file),
        launch_arguments={
            'enable_accel': 'true',
            'enable_gyro': 'true',
            'unite_imu_method': '1'
        }.items(),
    )
    
    # run imu_correction_node
    intel_imu_correction_node = Node(
        package="intel_imu_correction",
        executable="imu_correction_node",
        name="imu_correction_node",
        output="log"
    )
    
    
    # Define the path to the imu_filter_launch_file 
    imu_filter_launch_file = PathJoinSubstitution([
        '/home/nuc/my_tondo_ws/src',
        'tondo_bringup/launch/imu_filter_madgwick',
        'imu_filter.launch.py'
    ])

    # Include the rplidar_a1_launch.py file in the launch description
    launch_imu_filter = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(imu_filter_launch_file)
    )




    nodes = [
        launch_realsense_camera,
        intel_imu_correction_node,
        launch_imu_filter
    ]

    return LaunchDescription(nodes)

