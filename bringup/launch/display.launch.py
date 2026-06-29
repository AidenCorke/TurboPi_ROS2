from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    # ===== Pathing =====
    # --- Package Paths ---
    description_dir = get_package_share_directory('description')
    
    # --- Config / Parameter Paths ---
    urdf_path = os.path.join(description_dir, 'urdf', 'robot.urdf.xacro')
    rviz_config = os.path.join(description_dir, 'rviz', 'display.rviz')

    # ===== Launch Arguments =====
    # --- Model Path ---
    arg_model = DeclareLaunchArgument(
        'model',
        default_value=urdf_path,
        description='Absolute path to robot URDF'
    )
    
    # ===== Launch Descriptions =====
    # --- Robot State Publisher ---
    robot_state_pub = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': False,
            'robot_description': LaunchConfiguration('model')
        }]         
    )
    
    # --- Joint State Publisher ---
    joint_state_pub = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen'        
    )
    
    # --- RViz ---
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config]        
    )


    return LaunchDescription([
        arg_model,
        robot_state_pub,
        joint_state_pub,
        rviz,
    ])
