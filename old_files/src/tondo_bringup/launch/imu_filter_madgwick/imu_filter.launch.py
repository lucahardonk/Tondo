import os
import launch
import launch.actions
import launch.substitutions
import launch_ros.actions
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    print ("my imu madgwick")

    config_dir = os.path.join(get_package_share_directory('tondo_bringup'), 'config/imu_filter_madgwick')

    return launch.LaunchDescription(
        [
            launch_ros.actions.Node(
                package='imu_filter_madgwick',
                executable='imu_filter_madgwick_node',
                name='imu_filter',
                output='screen',
                parameters=[
                    os.path.join(config_dir, 'imu_filter.yaml'),
                    {'stateless': False},
                    {'use_mag': False},
                    {'publish_tf': False},  # Set publish_tf to false here
                    {'reverse_tf': False},
                    {'fixed_frame': 'odom'},
                    {'constant_dt': 0.0},
                    {'publish_debug_topics': False},
                    {'world_frame': 'enu'},
                    {'gain': 0.1},
                    {'zeta': 0.0},
                    {'mag_bias_x': 0.0},
                    {'mag_bias_y': 0.0},
                    {'mag_bias_z': 0.0},
                    {'orientation_stddev': 0.0}
                ],
                remappings=[
                    ('/imu/data_raw', '/camera/imu')
                ]
            )
        ]
    )

