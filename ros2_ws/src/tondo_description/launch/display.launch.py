from launch import LaunchDescription
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command
import os
from ament_index_python.packages import get_package_share_path
from launch_ros.actions import Node


def generate_launch_description():

    urdf_path = os.path.join(get_package_share_path('tondo_description'), 'urdf' ,'tondo_urdf.urdf.xacro')
    rviz_config_path = os.path.join(get_package_share_path('tondo_description'), 'rviz' ,'rviz_config.rviz')

    robot_description  = ParameterValue(Command(['xacro ', urdf_path]) , value_type=str)

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[
            {'robot_description' : robot_description},
            {'use_sim_time': False}  # Make sure it runs correctly with simulation time
        ],
        remappings=[
            ('/tf', '/static_tf')  # Prevent `robot_state_publisher` from overriding odom updates
        ]
    )

    joint_state_publisher_node = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher"
    )


    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_node
    ])
