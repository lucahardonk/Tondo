import os
from pathlib import Path
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from openai import OpenAI

class TelegramSubscriber(Node):

    def __init__(self):
        super().__init__('telegram_subscriber')
        self.subscription = self.create_subscription(String, 'telegram/in', self.message_callback, 10)
        self.publisher = self.create_publisher(String, 'chatter/out/file', 10)
        self.openai_client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
        self.file_path = str(Path.home() / 'my_tondo_ws' / 'src' / 'tondo_lam' / 'tondo_lam' / 'tondo_chatter_response' / 'response_file.txt')

    def message_callback(self, msg):
        # Extract text from the message
        user_message = msg.data
        # Use OpenAI to generate response
        completion = self.openai_client.chat.completions.create(
            model="TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF",
            messages=[
                {"role": "system", "content": "You are a kind and helpful assistant called Tondo"},
                {"role": "user", "content": user_message},
                
            ],
            temperature=0.7,
        )
        # Publish the generated response
        response = completion.choices[0].message.content
        # Write response to file
        self.write_to_file(response)
        response = self.file_path # instead of pubblishing a large file, users will be notified where to find the text file
        self.publish_response(response)
        

    def publish_response(self, response):
        response_msg = String()
        response_msg.data = response
        self.publisher.publish(response_msg)

    def write_to_file(self, response):
        with open(self.file_path, 'w') as f:
            f.write(response)

def main():
    rclpy.init()
    node = TelegramSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

