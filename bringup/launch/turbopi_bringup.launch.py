from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # ===== Define Package and Parameter Paths =====
    # --- Package Paths ---
    launch_dir = PathJoinSubstitution(
        [FindPackageShare('bringup'),'launch']
        )

    # ===== Launch Descriptions =====
    # --- Base Launch ---
    base = IncludeLaunchDescription(
        PathJoinSubstitution([launch_dir,'base.launch.py'])
    )
    
    # --- Sensors Launch ---
    sensors = IncludeLaunchDescription(
        PathJoinSubstitution([launch_dir,'sensors.launch.py'])
    )

    return LaunchDescription([
        base,
        sensors,
    ])