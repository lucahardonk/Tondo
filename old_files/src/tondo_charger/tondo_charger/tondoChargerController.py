import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger
from std_msgs.msg import Bool, Float32
from functools import partial


class TondoChargerController(Node):

    def __init__(self):
        super().__init__("TondoChargerController")

        self.__battery_voltage = 24.0  # Private variable
        self.__in_charge = False  # Private variable
        self.__is_charging = False  # Private variable

        self.subscription_attached = self.create_subscription(Bool,'/Tondo/chargerAttached',self.attached_callback,10)
        #self.subscription_attached  # prevent unused variable warning

        self.subscription_voltage = self.create_subscription(Float32,'/Tondo/batteryVoltage',self.voltage_callback,10)
        #self.subscription_voltage  # prevent unused variable warning
        '''
        self.charge_service = self.create_client(Trigger, '/Tondo/chargerService/charge')
        self.uncharge_service = self.create_client(Trigger, '/Tondo/chargerService/uncharge')
        self.button_up_service = self.create_client(Trigger, '/Tondo/chargerService/buttonUp')
        self.button_down_service = self.create_client(Trigger, '/Tondo/chargerService/buttonDown')
        '''
    #getter e setter for private variables
    def set_is_charging(self, status):
        self.__is_charging = status

    def get_is_charging(self):
        return self.__is_charging

    def set_battery_voltage(self, voltage):
        self.__battery_voltage = voltage

    def get_battery_voltage(self):
        return self.__battery_voltage

    def set_in_charge(self, status):
        self.__in_charge = status

    def get_in_charge(self):
        return self.__in_charge

    # callbacks for the subscriptions
    def attached_callback(self, msg):
        if not isinstance(msg.data, bool):
            self.get_logger().error("Invalid data type received for charger status. Expected boolean.")
            return

        self.set_in_charge(msg.data)
        self.get_logger().info(f'Charger Attached: {msg.data}')

    def voltage_callback(self, msg):
        try:
            voltage = float(msg.data)
            if voltage <  10 or voltage >  30:
                self.get_logger().error("error reading, battery voltage out of range")
                return
        except ValueError:
            self.get_logger().error("Invalid data type received for battery voltage. Expected float.")
            return

        self.set_battery_voltage(voltage)
        self.get_logger().info(f'Battery Voltage: {voltage}')


    def chargingLogic(self):
        if(self.__in_charge):
            if (self.get_battery_voltage() >= 25):
                self.set_is_charging = False
            if(not self.__is_charging):
                if(self.get_battery_voltage() < 20):
                    self.call_charge_services()
                    self.set_is_charging(True)
    
    
    #charge service callback and future callback                
    def call_charge_services(self):
        client = self.create_client(Trigger, '/Tondo/chargerService/charge')
        while not client.wait_for_service(1.0):
            self.get_logger().warn("waiting for service...")

        request = Trigger.Request()

        future= client.call_async(request)
        future.add_done_callback(partial(self.charge_future_callback))

    def charge_future_callback(self,future):
        try:
            respose = future.result()
        except Exception as e:
            self.get_logger().error("service call failed: %r" %(e,))


def main(args=None):

    rclpy.init(args=args)
    node = TondoChargerController()

    try:
        while rclpy.ok():  # Keep running as long as ROS is operational
            # Call the charging logic function
            node.chargingLogic()
            # Spin once (handle ROS messages and services)
            rclpy.spin_once(node)
    finally:
        # Perform cleanup before exiting
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
