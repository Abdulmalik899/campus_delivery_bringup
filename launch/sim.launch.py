from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    description= FindPackageShare('campus_delivery_robot')
    here= FindPackageShare('campus_delivery_bringup')
    model= PathJoinSubstitution([description, 'urdf', 'campus_delivery_bot.urdf.xacro'])
    world=LaunchConfiguration('world')
    gz_launch = PathJoinSubstitution(
        [FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py'])
    robot_description = ParameterValue(Command(['xacro ', model]), value_type=str)

    return LaunchDescription([
        DeclareLaunchArgument('world', default_value='empty.sdf', 
                              description='A file in worlds/, or one of Gazebo\'s own worlds'),

        DeclareLaunchArgument('gui', default_value='true', choices=['true', 'false'],
                              description='Open the Gazebo window'),
        DeclareLaunchArgument('rviz', default_value='true', choices=['true', 'false'],
                              description='Start RViz'),
        DeclareLaunchArgument('x', default_value='0.0'),
        DeclareLaunchArgument('y', default_value='0.0'),
        DeclareLaunchArgument('z', default_value='0.1', description='Height to drop form'),
        DeclareLaunchArgument('yaw', default_value='0.0', description='Heading, radians'),


        AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH',
                                  PathJoinSubstitution([here, 'worlds'])),
        IncludeLaunchDescription(
            gz_launch, condition=IfCondition(LaunchConfiguration('gui')),
            launch_arguments={'gz_args': ['-r ', world]}.items()),
        IncludeLaunchDescription(  # no window: server only, drawing sensors off-screen
            gz_launch, condition=UnlessCondition(LaunchConfiguration('gui')),
            launch_arguments={'gz_args': ['-r -s --headless-rendering ', world]}.items()),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description, 'use_sim_time': True}],
        ),
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=['-topic', 'robot_description', '-name', 'campus_delivery_robot',
                       '-x', LaunchConfiguration('x'), '-y', LaunchConfiguration('y'),
                       '-z', LaunchConfiguration('z'), '-Y', LaunchConfiguration('yaw')],
        ),
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            parameters=[{'config_file': PathJoinSubstitution([here, 'config', 'bridge.yaml']),
                         'use_sim_time': True}]
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', PathJoinSubstitution([here, 'rviz', 'sim.rviz'])],
            parameters=[{'use_sim_time': True}],
            condition=IfCondition(LaunchConfiguration('rviz')),
        )                                           
    ])