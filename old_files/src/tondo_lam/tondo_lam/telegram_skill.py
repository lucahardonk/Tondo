import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import telepot
from telepot.loop import MessageLoop

class TelegramPublisher(Node):

    def __init__(self, token):
        super().__init__('telegram_publisher')
        self.publisher = self.create_publisher(String, 'telegram/in', 10)
        self.bot = telepot.Bot(token)
        MessageLoop(self.bot, self.handle_message).run_as_thread()

    def handle_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type == 'text':
            text = msg['text']
            self.publish_message(text)

    def publish_message(self, text):
        msg = String()
        msg.data = text
        self.publisher.publish(msg)

def main():
    # Replace 'YOUR_TELEGRAM_TOKEN' with your actual Telegram bot token
    token = '6544009520:AAE_IkrWDfbpoAOsnxLcsFiKtqLfu8dioXw'
    rclpy.init()
    node = TelegramPublisher(token)
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

