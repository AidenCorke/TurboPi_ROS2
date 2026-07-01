from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    # ===== Define Package and Parameter Paths =====
    # --- Package Paths ---
    bringup_dir = get_package_share_directory('bringup')
    config_dir = os.path.join(bringup_dir, 'config')

    # --- Parameter Paths ---
    motor_params = os.path.join(config_dir, 'motor_driver.yaml')
    kinematics_params = os.path.join(config_dir, 'kinematics.yaml')


    # ===== Launch Descriptions =====
    # --- Motor Driver Node ---
    motor_driver = Node(
        package='base',
        executable='motor_driver',
        name='motor_driver',
        output='screen',
        parameters=[motor_params]
    )
    
    # --- Wheel Kinematics Node ---
    mecanum_kinematics = Node(
        package='base',
        executable='mecanum_kinematics',
        name='mecanum_kinematics',
        output='screen',
        parameters=[kinematics_params]
    )
    
    # --- Dead Reckoning Odom Node ---
    odom = Node(
        package='base',
        executable='dead_reckoning_odom',
        name='dead_reckoning_dom',
        output='screen',
    )    

    return LaunchDescription([
        motor_driver,
        mecanum_kinematics,
        odom,
    ])
