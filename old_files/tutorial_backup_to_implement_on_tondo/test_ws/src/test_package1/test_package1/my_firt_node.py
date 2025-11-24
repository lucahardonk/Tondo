#!/user/bin/env python3

import rclpy
from rclpy.node import Node #oop ros


class MyNode(Node): #inherits all ros functionalities 
    def __init__(self): # constructor
        super().__init__("first_node") # tra "" the node name visible to ros
        self.get_logger().info("hello from ros2")  #logging message [type] [time] [message]
        self.create_timer(1.0, self.timer_callback)  #timer for periodical events

    def timer_callback(self):
        self.get_logger().info("hello") # what does the timer every time isa called



def main(args=None):
    rclpy.init(args=args) # initializes ros comunication
    #all the node code

    node = MyNode()#creation of our node

    rclpy.spin(node)# keep the node alive and all callbacks will run

    rclpy.shutdown() # shutdown ros comunication



if __name__ == '__main__':
    main() 