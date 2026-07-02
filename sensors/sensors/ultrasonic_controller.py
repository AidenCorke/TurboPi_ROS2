##########################################
# ===== Sonar Control =====
'''
This file contains control logic for ultrasonic sensor, based on manufacturer code.

Author: Aiden Corke
'''
##########################################

# ===== Imports =====
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Range
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
from sensors.ultrasonic_sensor import UltrasonicSensor

# ===== Class / Node =====
class UtrasonicController(Node):

    # === Node Setup ===
    def __init__(self):
        super().__init__('ultrasonic_controller')
        
        # ----- Declare Parameters -----
        # --- Publishing Rate ---
        self.declare_parameter('frame_id', 'ultrasonic_link')
        self.declare_parameter('pub_rate', 20.0)
        
        # ----- Extract Parameters -----
        self.frame_id = self.get_parameter('frame_id').value
        rate = self.get_parameter('pub_rate').value
        
        # --- Sensor Class ---
        self.sonar = UltrasonicSensor()
        
        # ----- Publishers -----
        self.pub = self.create_publisher(
            Range,
            '/ultrasonic/range',
            10,
        )
        
        self.tf = TransformBroadcaster(self)
        
        self.get_logger().info("Ultrasonic sensor active...")
        
        # ----- Timer -----
        self.timer = self.create_timer(
            1.0 / rate,
            self.update,
            )
    
    # === Functions ===
    def update(self,):
        '''Main function extracting and constructing range message.'''
        # ----- Range Message ------
        # --- Extract Range Value ---
        dist_mm = self.sonar.getDistance()
        
        # --- Create Message ---        
        msg = Range()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.frame_id
        msg.radiation_type = Range.ULTRASOUND
        msg.field_of_view = 0.5  # radians
        msg.min_range = 0.02
        msg.max_range = 5.0

        msg.range = dist_mm / 1000.0  # convert mm → meters

        # --- Publish Message ---
        self.pub.publish(msg)        
        
        # ----- TF Message -----
        # --- Publish TF ---
        t = TransformStamped()
        t.header.stamp = msg.header.stamp
        t.header.frame_id = 'base_link'
        t.child_frame_id = self.frame_id

        # --- Adjust based on mount position ---
        t.transform.translation.x = 0.10
        t.transform.translation.y = 0.0
        t.transform.translation.z = 0.05
        t.transform.rotation.w = 1.0

        # --- Send TF Message ---
        self.tf.sendTransform(t)        
        
def main(args=None):
    rclpy.init(args=args)
    node = UtrasonicController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()        