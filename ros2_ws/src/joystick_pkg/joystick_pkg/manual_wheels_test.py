import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from std_msgs.msg import Float32
from std_srvs.srv import Empty

class ManualWheelsTest(Node):
    def __init__(self):
        super().__init__('manual_wheels_test')

        # Declare and get scale factor parameter
        self.declare_parameter('scale_factor', 1.0)
        self.scale_factor = self.get_parameter('scale_factor').value

        # Subscribe to /joy topic
        self.subscription = self.create_subscription(
            Joy,
            '/joy',
            self.joy_callback,
            10
        )

        # Publishers for wheel velocity commands
        self.left_wheel_pub = self.create_publisher(Float32, '/left_wheel/cmd_vel', 10)
        self.right_wheel_pub = self.create_publisher(Float32, '/right_wheel/cmd_vel', 10)

        # Create service clients
        self.start_motor_client = self.create_client(Empty, '/start_motor')
        self.stop_motor_client = self.create_client(Empty, '/stop_motor')

        # State tracking
        self.motor_running = False  # Track whether motor is running
        self.prev_button_state = 0  # Used to detect button press events

    def joy_callback(self, msg):
        # Toggle motor state when button 1 is pressed
        if msg.buttons[1] == 1 and self.prev_button_state == 0:  # Button press event
            self.toggle_motor()
        
        self.prev_button_state = msg.buttons[1]  # Store button state for next callback

        # Get joystick values (axes[1] for left wheel, axes[4] for right wheel)
        left_wheel_speed = msg.axes[1] * self.scale_factor
        right_wheel_speed = msg.axes[4] * self.scale_factor

        # Publish speeds
        self.publish_speed(self.left_wheel_pub, left_wheel_speed)
        self.publish_speed(self.right_wheel_pub, right_wheel_speed)

    def toggle_motor(self):
        """Toggles between starting and stopping the motor."""
        if self.motor_running:
            self.call_service(self.stop_motor_client, '/stop_motor')
            self.motor_running = False
        else:
            self.call_service(self.start_motor_client, '/start_motor')
            self.motor_running = True

    def call_service(self, client, service_name):
        """Calls an Empty service."""
        if client.wait_for_service(timeout_sec=1.0):
            request = Empty.Request()
            future = client.call_async(request)
            self.get_logger().info(f"Called {service_name}")
        else:
            self.get_logger().warn(f"Service {service_name} not available!")

    def publish_speed(self, publisher, speed):
        msg = Float32()
        msg.data = speed
        publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = ManualWheelsTest()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
