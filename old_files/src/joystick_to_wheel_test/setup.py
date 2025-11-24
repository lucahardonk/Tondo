from setuptools import find_packages, setup

package_name = 'joystick_to_wheel_test'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='nuc',
    maintainer_email='nuc@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        	"joy_to_wheel = joystick_to_wheel_test.joystick_to_wheel:main",
            "left_joistick_cmdvel = joystick_to_wheel_test.left_joystick_cmd_vel_publisher:main",
            "left_joystick_diffbot_base_cmdvel_unstamped = joystick_to_wheel_test.left_joystick_diffbot_base_controller_cmd_vel_unstamped:main"
        ],
    },
)
