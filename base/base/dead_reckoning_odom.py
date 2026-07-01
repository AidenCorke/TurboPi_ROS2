##########################################
# ===== Mecanum Kinematic =====
'''
This file contains open loop odometry logic node. Using velocity commands to create dead reckoning positional estimation.

Author: Aiden Corke
'''
##########################################

# ===== Imports =====
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped
import math
import time

# ===== Class / Node =====
class DeadReckonOdom(Node):

    # === Node Setup ===
    def __init__(self):
        super().__init__('dead_reckoning_odom')
        
        # ----- Declare Parameters -----
        # --- Publishing Rate ---
        self.declare_parameter('publish_rate',50.0)
        
        # ----- Extract Parameters -----
        # --- Publishing Params ---
        rate = self.get_parameter('publish_rate').value
        
        # --- Initial Velocity & Positional Params ---
        self.vx = 0.0
        self.vy = 0.0
        self.wz = 0.0
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0        
        
        # ----- Subscriptions -----
        self.cmd_vel_sub = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10,
        )
        
        # ----- Publishers -----
        # --- Odometry Publisher ---
        self.odom_pub = self.create_publisher(
            Odometry,
            '/odom',
            10,
        )
        # --- TF Broadcaster ---
        self.tf_broadcaster = TransformBroadcaster(self)
        
        # ----- Timer -----
        self.last_time = self.get_clock().now()
        self.timer = self.create_timer(1.0 / rate, self.update)        


    # === Functions ===

    # ----- Update Odometry -----
    def update(self):
        now = self.get_clock().now()
        dt = (now - self.last_time).nanoseconds / 1e9
        self.last_time = now

        # --- Integrate Motion ---
        self.x += self.vx * math.cos(self.theta) * dt - self.vy * math.sin(self.theta) * dt
        self.y += self.vx * math.sin(self.theta) * dt + self.vy * math.cos(self.theta) * dt
        self.theta += self.wz * dt

        # --- Publish Odometry ---
        odom = Odometry()
        odom.header.stamp = now.to_msg()
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_link'

        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.position.z = 0.0

        odom.pose.pose.orientation.z = math.sin(self.theta / 2.0)
        odom.pose.pose.orientation.w = math.cos(self.theta / 2.0)

        odom.twist.twist.linear.x = self.vx
        odom.twist.twist.linear.y = self.vy
        odom.twist.twist.angular.z = self.wz

        self.odom_pub.publish(odom)

        # --- Publish TF ---
        t = TransformStamped()
        t.header.stamp = now.to_msg()
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = 0.0
        t.transform.rotation.z = math.sin(self.theta / 2.0)
        t.transform.rotation.w = math.cos(self.theta / 2.0)

        self.tf_broadcaster.sendTransform(t)

def main(args=None):
    rclpy.init(args=args)
    node = DeadReckonOdom()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()        