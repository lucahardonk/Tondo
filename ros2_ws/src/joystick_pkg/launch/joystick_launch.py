import launch
import launch_ros.actions

def generate_launch_description():
    return launch.LaunchDescription([
        launch_ros.actions.Node(
            package="joy",
            executable="joy_node",
            name="joy_node"
        ),
        launch_ros.actions.Node(
            package="joystick_pkg",
            executable="diff_drive_joystick",
            name="diff_drive_joystick"
        )
    ])
