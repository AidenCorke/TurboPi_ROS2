##########################################
# ===== Motor Driver =====
'''
This file contains a node for sending and receiving motor commands.
Author: Aiden Corke
'''
##########################################

# ===== Imports =====
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import time
import serial
import struct

# ===== CRC-8 Table from SDK =====
crc8_table = [
    0,94,188,226,97,63,221,131,194,156,126,32,163,253,31,65,
    157,195,33,127,252,162,64,30,95,1,227,189,62,96,130,220,
    35,125,159,193,66,28,254,160,225,191,93,3,128,222,60,98,
    190,224,2,92,223,129,99,61,124,34,192,158,29,67,161,255,
    70,24,250,164,39,121,155,197,132,218,56,102,229,187,89,7,
    219,133,103,57,186,228,6,88,25,71,165,251,120,38,196,154,
    101,59,217,135,4,90,184,230,167,249,27,69,198,152,122,36,
    248,166,68,26,153,199,37,123,58,100,134,216,91,5,231,185,
    140,210,48,110,237,179,81,15,78,16,242,172,47,113,147,205,
    17,79,173,243,112,46,204,146,211,141,111,49,178,236,14,80,
    175,241,19,77,206,144,114,44,109,51,209,143,12,82,176,238,
    50,108,142,208,83,13,239,177,240,174,76,18,145,207,45,115,
    202,148,118,40,171,245,23,73,8,86,180,234,105,55,213,139,
    87,9,235,181,54,104,138,212,149,203,41,119,244,170,72,22,
    233,183,85,11,136,214,52,106,43,117,151,201,74,20,246,168,
    116,42,200,150,21,75,169,247,182,232,10,84,215,137,107,53
]

def crc8(data: bytes) -> int:
    """
    
    """
    check = 0
    for b in data:
        check = crc8_table[check ^ b]
    return check & 0xFF

# ===== Motor Packet Builder =====
def build_motor_packet(speeds):
    """
    speeds = [duty1, duty2, duty3, duty4]
    """
    func = 3 # PACKET_FUNC_MOTOR

    # ----- Build Data Payload -----
    data = [0x05, len(speeds)]
    for motor_id, duty in enumerate(speeds, start=1):
        data.extend(struct.pack("<Bf", int(motor_id - 1), float(duty)))

    # ----- Build Packet -----
    packet = [0xAA, 0x55, func, len(data)]
    packet.extend(data)

    # ----- Compute Checksum -----
    checksum = crc8(bytes(packet[2::]))
    packet.append(checksum)

    return bytes(packet)

# ===== Class / Node =====
class MotorDriver(Node):
    
    # === Node Setup ===
    def __init__(self):
        super().__init__('motor_driver')

        # ----- Serial Port Parameters -----
        # --- Declare Parameters ---
        self.declare_parameters(
            namespace='',
            parameters=[
                ('port', '/dev/ttyAMA0'),       # Serial port
                ('baud', 1000000),               # Baudrate
                ('rate', 30.0),                 # Packet Rate (Hz)
            ]
        )
        # --- Store Parameters ---
        port = self.get_parameter('port').value
        baud = self.get_parameter('baud').value
        self.rate = self.get_parameter('rate').value

        # ----- Open Serial Port -----
        try:
            self.ser = serial.Serial(port, baudrate=baud, timeout=0.01)
            self.get_logger().info(f"Opened serial {port} at {baud}")
        except Exception as e:
            self.get_logger().error(f"Failed to open serial port: {e}")
            self.ser = None

        # ----- Wheel Speeds -----
        self.speeds = [0.0, 0.0, 0.0, 0.0]
        self.sub = self.create_subscription(
            Float32MultiArray,      # Message
            '/wheel_speeds',        # Topic
            self.wheel_callback,    # Callback
            10,                     # Timer
        )

        # ----- Packet Rate -----
        self.timer = self.create_timer(1.0 / self.rate, self.send_packet)






    # === Functions ===

    def wheel_callback(self, msg):
        """Checks length of message and stores as attribute if correct length."""
        if len(msg.data) == 4:
            self.speeds = list(msg.data)
            self.get_logger().info(f"Recieved wheel speeds: {self.speeds}")

    def send_packet(self):
        """Send packets to builder or raises error if fails."""

        if self.ser is None:
            return
        
        packet = build_motor_packet(self.speeds)
        #self.get_logger().info(f"Sending packet: {packet.hex()}")
        try:
            self.ser.write(packet)
        except Exception as e:
            self.get_logger().error(f"Serial write failed: {e}")

        '''
        # ----- Board Response Check -----
        resp = self.ser.read(64)
        if resp:
            self.get_logger().info(f"Received from board: {resp.hex()}")
        '''
            
def main(args=None):
    rclpy.init(args=args)
    node = MotorDriver()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
