import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from std_msgs.msg import Float64MultiArray
import numpy as np

class JoySubscriber(Node):

    def __init__(self):
        super().__init__('joy_to_wheel')
        self.subscription = self.create_subscription(Joy,'/joy',self.joy_callback,10)
        self.publisher_joint0 = self.create_publisher(Float64MultiArray, '/joint0_velocity_controller/commands', 10)
        self.publisher_joint1 = self.create_publisher(Float64MultiArray, '/joint1_velocity_controller/commands', 10)
        self.__lever1 = 0.0
        self.__lever2 = 0.0

    def joy_callback(self, msg:Joy):
        self.__lever1 = self.remap_value(msg.axes[2])
        self.__lever2 = self.remap_value(msg.axes[5])
        self.publish_commands(msg.buttons[4], msg.buttons[5])


    def remap_value(self, value):
        return np.interp(value, [-1, 1], [6, 0])

    def publish_commands(self, left, right):
        msg = Float64MultiArray()
        if(left):
            msg.data = [5.0]
        else:
            msg.data = [(-1*self.__lever1)]
        
        self.publisher_joint0.publish(msg)
        if(right):
            msg.data = [-5.0]
        else:
            msg.data = [(self.__lever2)]
        self.publisher_joint1.publish(msg)
def main():
    rclpy.init()
    node = JoySubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
