import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from std_msgs.msg import Float64MultiArray
import numpy as np

class WheelVelocityCalculator(Node):
    def __init__(self):
        super().__init__('wheel_velocity_calculator')
        self.subscription = self.create_subscription(TwistStamped,'/cmd_vel',self.cmd_vel_callback,10)
        self.publisher_joint0 = self.create_publisher(Float64MultiArray, '/joint0_velocity_controller/commands', 10)
        self.publisher_joint1 = self.create_publisher(Float64MultiArray, '/joint1_velocity_controller/commands', 10)
        self.declare_parameter('wheel_diameter', 0.25)  # assuming wheel diameter of 0.1 meter
        self.declare_parameter('wheel_separation', 0.42)  # assuming wheel separation of 0.5 meter

    def cmd_vel_callback(self, msg):
        linear_x = msg.twist.linear.x
        angular_z = msg.twist.angular.z

        wheel_diameter = self.get_parameter('wheel_diameter').value
        wheel_separation = self.get_parameter('wheel_separation').value

        left_wheel_velocity = (-1)*(linear_x - angular_z * wheel_separation / 2) / (wheel_diameter / 2)
        right_wheel_velocity = (linear_x + angular_z * wheel_separation / 2) / (wheel_diameter / 2)

        # Create Float64MultiArray message for each joint
        left_msg = Float64MultiArray()
        left_msg.data = [left_wheel_velocity]  # assuming only velocity along one axis, so second value is 0.0
        right_msg = Float64MultiArray()
        right_msg.data = [right_wheel_velocity]  # assuming only velocity along one axis, so second value is 0.0

        self.publisher_joint0.publish(left_msg)
        self.publisher_joint1.publish(right_msg)

def main(args=None):
    rclpy.init(args=args)
    wheel_velocity_calculator = WheelVelocityCalculator()
    rclpy.spin(wheel_velocity_calculator)
    wheel_velocity_calculator.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
