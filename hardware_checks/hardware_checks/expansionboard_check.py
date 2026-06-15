import rclpy
from rclpy.node import Node
import serial
import time

class TurboPiHardware(Node):
    def __init__(self):
        super().__init__('turbopi_hardware')

        # Open UART
        self.ser = serial.Serial(
            port='/dev/ttyAMA0',
            baudrate=115200,
            timeout=0.1
        )

        self.get_logger().info("TurboPi hardware interface started")

        # Timer to send test command
        self.timer = self.create_timer(1.0, self.test_command)

    def test_command(self):
        # Example packet (placeholder)
        packet = bytes([0x55, 0xAA, 0x01, 0x00, 0x01])
        self.ser.write(packet)
        self.get_logger().info("Sent test packet")

        # Read response
        data = self.ser.read(32)
        if data:
            self.get_logger().info(f"Received: {data}")

def main(args=None):
    rclpy.init(args=args)
    node = TurboPiHardware()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
