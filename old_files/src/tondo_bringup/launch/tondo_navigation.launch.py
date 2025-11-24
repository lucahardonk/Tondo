import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess

def generate_launch_description():
    slam_params_file = "/home/nuc/my_tondo_ws/src/tondo_bringup/config/slam_toolbox/config/mapper_params_online_async.yaml"
    nav2_params_file = "/home/nuc/my_tondo_ws/src/tondo_bringup/config/nav2_bringup/params/nav2_params.yaml"

    slam_toolbox_launch = ExecuteProcess(
        cmd=["ros2", "launch", "slam_toolbox", "online_async_launch.py", f"slam_params_file:={slam_params_file}"],
        output='screen',
    )

    nav2_bringup_launch = ExecuteProcess(
        cmd=["ros2", "launch", "nav2_bringup", "navigation_launch.py", f"params_file:={nav2_params_file}", "use_sim_time:=false"],
        output='screen',
    )

    return LaunchDescription([
        slam_toolbox_launch,
        nav2_bringup_launch
    ])

