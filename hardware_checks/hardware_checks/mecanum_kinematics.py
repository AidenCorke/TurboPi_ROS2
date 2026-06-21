##########################################
# ===== Mecanum Kinematic =====
'''
This file subscribes to /cmd_vel topic and computes the velocities for each motor converting velocites bases on mecanum wheel kinematics, and publishes them on the /wheel_speeds topic. 

Author: Aiden Corke
'''
##########################################

# ===== Imports =====
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32MultiArray
import time

# ===== Class =====
class MecanumKinematics(Node):

    # === Node Setup ===
    def __init__(self):
        super().__init__('mecanum_kinematics')  # Define node name using underlying Node class

        # ----- Declare Parameters -----
         # --- Geometry Parameters --- 
        self.declare_parameters(
            namespace='',
            parameters=[
                ('wheelbase', 0.1380),          # meters
                ('track_width', 0.1410),         # meters
                ('wheel_diameter', 0.065),      # meters
            ]
        )
         # --- Motion Limit Parameters --- 
        self.declare_parameters(
            namespace='',
            parameters=[
                ('max_vx', 1.0),            # m/s
                ('max_vy', 1.0),            # m/s
                ('max_wz', 1.0),            # rad/s
                ('max_wheel_speed', 1.0),   # m/s    
                ('max_wheel_accel', 1.5),   # m/s^2            
            ]
        )

        # ----- Assign Parameters as Class Attributes -----
        # --- Geometry parameters ---
        self.wheelbase = self.get_parameter('wheelbase').value
        self.track_width = self.get_parameter('track_width').value
        self.wheel_diameter = self.get_parameter('wheel_diameter').value

        # --- Motion Limit parameters ---
        self.max_vx = self.get_parameter('max_vx').value
        self.max_vy = self.get_parameter('max_vy').value
        self.max_wz = self.get_parameter('max_wz').value
        self.max_wheel_speed = self.get_parameter('max_wheel_speed').value
        self.max_wheel_accel = self.get_parameter('max_wheel_accel').value

        self.prev_speeds = [0.0, 0.0, 0.0, 0.0]
        self.prev_time = time.time()

        # ----- Subscriptions -----
        self.cmd_vel_sub = self.create_subscription(
            Twist,                  # Message 
            '/cmd_vel',             # Topic 
            self.cmd_vel_callback,  # Callback 
            10,                     # Timer
        )

        # ----- Publishers -----
        self.wheel_pub = self.create_publisher(
            Float32MultiArray,  # message
            '/wheel_speeds',    # topic
            10                  # timer
        )


    # === Functions ===

    def cmd_vel_callback(self, msg: Twist):
        """This is the main kinematic and motion limiting function. It converts vel commands to wheel speeds to be sent to the motors while limiting speeds and acceleration to set limits."""
        # --- Setup --
        now = time.time()
        dt = max(now-self.prev_time, 1e-3)  # avoid zero dt
        self.prev_time = now

        # --- Define velocity messages ---
        vx = msg.linear.x  
        vy = msg.linear.y  
        wz = msg.angular.z 

        # --- Clamp Velocity Input Speeds ---
        vx = self.clamp(vx, -self.max_vx, self.max_vx)
        vy = self.clamp(vy, -self.max_vy, self.max_vy)
        wz = self.clamp(wz, -self.max_wz, self.max_wz)

        # --- Mecanum kinematic equations ---
        v1 = (vx - vy - wz * (self.wheelbase + self.track_width) / 2)   # Front left
        v2 = (vx + vy - wz * (self.wheelbase + self.track_width) / 2)   # Front right
        v3 = (vx + vy + wz * (self.wheelbase + self.track_width) / 2)   # Rear left
        v4 = (vx - vy + wz * (self.wheelbase + self.track_width) / 2)   # Rear right

        raw_speeds = [v1,v2,v3,v4]

        # --- Clamp wheel speeds ---
        clamped_speeds = [
            self.clamp(s, -self.max_wheel_speed, self.max_wheel_speed)
            for s in raw_speeds
        ]

        # --- Acceleration Limiting ---
        max_delta = self.max_wheel_accel * dt
        limited_speeds = []
        for i, target in enumerate(clamped_speeds):
            prev = self.prev_speeds[i]
            delta = target - prev
            delta = self.clamp(delta, -max_delta, max_delta)
            new_speed = prev + delta
            limited_speeds.append(new_speed)

        self.prev_speeds = limited_speeds

        # --- Publish ---
        msg_out = Float32MultiArray()
        msg_out.data = limited_speeds
        self.wheel_pub.publish(msg_out)

        self.get_logger().debug(
            f"cmd_vel -> raw: {raw_speeds}, limited: {limited_speeds}"
        )


    def clamp(self, value, min_val, max_val):
        """This function checks a value against a max and min limit returning either the value or the limit."""
        return max(min(value, max_val), min_val)


def main(args=None):
    rclpy.init(args=args)
    mecanum_kinematics = MecanumKinematics()
    rclpy.spin(mecanum_kinematics)
    mecanum_kinematics.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()