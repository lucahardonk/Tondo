import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import TwistStamped
import numpy as np

class JoyToTwist(Node):

    def __init__(self):
        super().__init__('left_joy_to_twist')
        self.subscription = self.create_subscription(Joy, '/joy', self.joy_callback, 10)
        self.publisher_cmd_vel = self.create_publisher(TwistStamped, '/cmd_vel', 10)

    def joy_callback(self, msg: Joy):
        if(msg.buttons[4]):
            linear_x = self.remap_value(msg.axes[1])
            angular_z = self.remap_value(msg.axes[0])
            self.publish_twist(linear_x, angular_z)
        else:
            self.publish_twist(0., 0.)

    def remap_value(self, value):
	    old_min = -1
	    old_max = 1
	    new_min = -3
	    new_max = 3
	    #print("Input value:", value)
	    remapped_value = ((value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min
	    #print("Remapped value:", remapped_value)
	    return remapped_value





    def publish_twist(self, linear_x, angular_z):
        twist_msg = TwistStamped()
        twist_msg.twist.linear.x = linear_x
        twist_msg.twist.angular.z = angular_z
        self.publisher_cmd_vel.publish(twist_msg)

def main():
    rclpy.init()
    node = JoyToTwist()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

