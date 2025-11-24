import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist
from std_srvs.srv import Empty
from threading import Timer

class JoyToTwist(Node):

    def __init__(self):
        super().__init__('left_joy_to_cmd_vel_unstamped')
        self.subscription = self.create_subscription(Joy, '/joy', self.joy_callback, 10)
        self.publisher_cmd_vel = self.create_publisher(Twist, 'cmd_vel_joy', 10)
        self.max_vel = 6
        self.motor_running = True  # Flag per tracciare lo stato del motore
        self.button_pressed = False  # Flag per tracciare lo stato del pulsante
        self.debounce_timer = None  # Timer per debounce
        self.last_0_speed = False  # manda l'ultimo mesaggio per sicureza a 0
        self.get_logger().info("started node as left_joy_to_cmd_vel_unstamped")

    def joy_callback(self, msg: Joy):
        if msg.buttons[6]:
            self.last_0_speed = True
            linear_x = self.remap_value(msg.axes[1])
            angular_z = self.remap_value(msg.axes[0])
            self.publish_twist(linear_x, angular_z)
        elif msg.buttons[1] and not self.button_pressed:  # Controlla se il pulsante è stato premuto e non è già premuto
            self.button_pressed = True
            self.debounce_timer = Timer(0.5, self.reset_button_pressed)  # Imposta un timer di 0.5 secondi
            self.debounce_timer.start()
            if self.motor_running:
                self.stop_motor_service_call()
            else:
                self.start_motor_service_call()
        elif self.last_0_speed:
            self.publish_twist(0., 0.)

    def reset_button_pressed(self):
        self.button_pressed = False

    def remap_value(self, value):
        old_min = -1
        old_max = 1
        new_min = -(self.max_vel)
        new_max = self.max_vel
        remapped_value = ((value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min
        return remapped_value

    def publish_twist(self, linear_x, angular_z):
        twist_msg = Twist()
        twist_msg.linear.x = linear_x
        twist_msg.angular.z = angular_z
        self.publisher_cmd_vel.publish(twist_msg)

    def stop_motor_service_call(self):
        self.get_logger().info('Servizio /stop_motor chiamato')
        self.motor_running = False
        stop_motor_client = self.create_client(Empty, '/stop_motor')
        if stop_motor_client.wait_for_service(timeout_sec=1.0):
            request = Empty.Request()
            future = stop_motor_client.call_async(request)
            future.add_done_callback(self.stop_motor_callback)
        else:
            self.get_logger().error('Servizio /stop_motor non disponibile')

    def stop_motor_callback(self, future):
        if future.result() is not None:
            self.get_logger().info('Servizio /stop_motor richiamato con successo')
        else:
            self.get_logger().error('Chiamata al servizio /stop_motor fallita')

    def start_motor_service_call(self):
        self.get_logger().info('Servizio /start_motor chiamato')
        self.motor_running = True
        start_motor_client = self.create_client(Empty, '/start_motor')
        if start_motor_client.wait_for_service(timeout_sec=1.0):
            request = Empty.Request()
            future = start_motor_client.call_async(request)
            future.add_done_callback(self.start_motor_callback)
        else:
            self.get_logger().error('Servizio /start_motor non disponibile')

    def start_motor_callback(self, future):
        if future.result() is not None:
            self.get_logger().info('Servizio /start_motor richiamato con successo')
        else:
            self.get_logger().error('Chiamata al servizio /start_motor fallita')

def main():
    rclpy.init()
    node = JoyToTwist()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
