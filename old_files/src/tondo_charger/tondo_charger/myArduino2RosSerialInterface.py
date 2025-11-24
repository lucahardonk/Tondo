#!/usr/bin/env python3
import rclpy 
from rclpy.node import Node
import time
import serial
from std_srvs.srv import Trigger
from std_msgs.msg import Bool, Float32
import threading

arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, timeout=1) 
#usb-1a86_USB2.0-Serial-if00-port0




def string_to_float32_msg(input_string):
# Parse the input string into a float
    try:
        float_value = float(input_string)
    except ValueError:
        print("Invalid input string. Please provide a valid float value.")
        return None
        
    # Create a Float32 message and assign the parsed float value to its data field
    float32_msg = Float32()
    float32_msg.data = float_value
    return float32_msg




class ArduinoToSerialServer(Node):

    

    def __init__(self):
        super().__init__("ArduinoToSerialServer")
        self.lock_writeReadArduino = threading.Lock()
        self.get_logger().info("ArduinoToSerialServer has started!")
        #timers for data streams
        self.create_timer(1, self.check_inCharge_callback)
        self.create_timer(2, self.battery_voltage_callback)
        #publishers
        self.inChargeStatusPublish = self.create_publisher(Bool, "/Tondo/chargerAttached",10)
        self.batteryVoltagePublish = self.create_publisher(Float32, "/Tondo/batteryVoltage",10)
        #services to contro,l the charger
        self.srv = self.create_service(Trigger, '/Tondo/chargerService/charge', self.callback_charge)
        self.srv = self.create_service(Trigger, '/Tondo/chargerService/uncharge', self.callback_uncharge)
        self.srv = self.create_service(Trigger, '/Tondo/chargerService/buttonUp', self.callback_buttonUp)
        self.srv = self.create_service(Trigger, '/Tondo/chargerService/buttonDown', self.callback_buttonDown)


        arduino.reset_input_buffer()
        

    def writeReadArduino(self, comando,): 
        with self.lock_writeReadArduino:
            arduino.write(bytes(comando+'\n', 'utf-8'))
            time.sleep(0.01)
            answare = arduino.readline().decode('utf-8').rstrip()
            self.get_logger().info("arduino risponde a " + comando + " con " + answare) 
            return answare
            
    
       
    def check_inCharge_callback(self):
        try:
            response = self.writeReadArduino("charger_contact?")
            # Check if the response is a valid boolean string ('0' or '1')
            if response not in ['0', '1']:
                raise ValueError("Unexpected response: " + response)
            else:
                self.get_logger().info("Is charging?: " + str(response))            
                msg = Bool()
                msg.data = True if response == "1" else False
                self.inChargeStatusPublish.publish(msg)
        except Exception as e:
            self.get_logger().error(f"Failed to check charging status: {str(e)}")

    def battery_voltage_callback(self):
        try:
            response = self.writeReadArduino("battery")
            try:
                voltage = float(response)
            except ValueError:
                self.get_logger().error("Invalid response received for battery voltage. Expected a number.")
                return
            else:
                self.get_logger().info("Battery voltage: " + response)
                # Publish the battery voltage if it's a valid number
                voltage_msg = string_to_float32_msg(response)
                self.batteryVoltagePublish.publish(voltage_msg)
        except Exception as e:
            self.get_logger().error(f"Failed to read battery voltage: {str(e)}")
    #calbacks for using the charger services
    def callback_charge(self, request, response):
        try:
            # Service callback implementation
            self.get_logger().info("Starting charging!")
            self.writeReadArduino("charge")
            response.success = True
            response.message = "Charging started successfully"
        except Exception as e:
            self.get_logger().error(f"Failed to start charging: {str(e)}")
            response.success = False
            response.message = f"Failed to start charging: {str(e)}"
        return response

    def callback_uncharge(self, request, response):
        try:
            # Service callback implementation
            self.get_logger().info("Stop charging!")
            self.writeReadArduino("uncharge")
            response.success = True
            response.message = "Charging stopped successfully"
        except Exception as e:
            self.get_logger().error(f"Failed to stop charging: {str(e)}")
            response.success = False
            response.message = f"Failed to stop charging: {str(e)}"
        return response

    def callback_buttonUp(self, request, response):
        try:
            # Service callback implementation
            self.get_logger().info("Press buttonUp")
            self.writeReadArduino("up")
            response.success = True
            response.message = "ButtonUp pressed successfully"
        except Exception as e:
            self.get_logger().error(f"Failed to press buttonUp: {str(e)}")
            response.success = False
            response.message = f"Failed to press buttonUp: {str(e)}"
        return response
    
    def callback_buttonDown(self, request, response):
        try:
            # Service callback implementation
            self.get_logger().info("Button down pressed")
            self.writeReadArduino("down")
            response.success = True
            response.message = "Button down pressed successfully"
        except Exception as e:
            self.get_logger().error(f"Failed to press button down: {str(e)}")
            response.success = False
            response.message = f"Failed to press button down: {str(e)}"
        return response


def main(args=None):
    rclpy.init(args=args)
    node = ArduinoToSerialServer()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()



