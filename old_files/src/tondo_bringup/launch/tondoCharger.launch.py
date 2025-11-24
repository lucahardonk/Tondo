from launch import LaunchDescription
from launch_ros.actions import Node




def generate_launch_description():
    ld = LaunchDescription()

    arduino2serialinterface_node= Node(
        package="tondoCharger",
        executable="arduinoMegaToRosSerial"
    )

    tondoChargerController_node= Node(
        package="tondoCharger",
        executable="tondoChargerController"
    )

    

    ld.add_action(arduino2serialinterface_node)
    ld.add_action(tondoChargerController_node)


    return ld
