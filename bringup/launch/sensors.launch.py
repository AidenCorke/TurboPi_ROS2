from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    
    # ===== Launch Descriptions =====
    # --- Ultrasonic Sensor ---
    ultrasonic = Node(
        package='sensors',
        executable='ultrasonic_sensor',
        name='ultrasonic_sensor',
        parameters=[{
            'frame_id': 'ultrasonic_link',
            'publish_rate': 20.0
        }],
        output='screen'
    )

    return LaunchDescription([
        ultrasonic,
    ])
