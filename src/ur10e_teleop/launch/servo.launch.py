from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    servo_yaml = os.path.join(
        get_package_share_directory('ur10e_teleop'),
        'config',
        'ur_servo.yaml'
    )

    servo_node = Node(
        package='moveit_servo',
        executable='servo_node_main',
        name='servo_node',
        parameters=[servo_yaml, {'use_sim_time': True}],
        output='screen',
    )

    return LaunchDescription([servo_node])
