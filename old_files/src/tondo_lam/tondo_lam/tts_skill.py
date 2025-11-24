import os
import subprocess
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import re

class Tts_node(Node):

    def __init__(self):
        super().__init__('tts_node')
        self.subscription = self.create_subscription(String, '/chatter/out/file', self.file_callback, 10)
        self.say_text = ""
        self.change_dir = '/home/nuc/piper/piper'
        self.tts_command_part1 = "echo '"
        self.tts_command_part2 = "' | ./piper --model en_GB-jenny_dioco-medium.onnx --output-raw | aplay -r 22050 -f S16_LE -t raw -"
        

    def file_callback(self, msg):
        file_path = msg.data
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
            
            file_content_filtered = text_filter(file_content)
            self.say_text = file_content_filtered
            self.get_logger().info(f"File content:\n{self.say_text}")
            # Change the current working directory to ~/piper/piper
            os.chdir(self.change_dir)
            
            try:
                # Open a new terminal window and execute the command
                long_command =  self.tts_command_part1 + self.say_text + self.tts_command_part2
                process = subprocess.Popen(["bash", "-c", f"cd {self.change_dir} && {long_command} "])
                process.wait()
            except Exception as e:
                self.get_logger().error(f"Error running terminal command: {e}")
        else:
            self.get_logger().warning(f"File '{file_path}' does not exist.")

def text_filter(text):
    pattern = r"[']|[-]"
    # Replace ' and - with space
    modified_text = re.sub(pattern, " ", text)
    #print(modified_text)
    return modified_text

def main():
    rclpy.init()
    node = Tts_node()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

