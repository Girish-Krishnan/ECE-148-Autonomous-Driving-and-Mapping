source_ros2
echo """sick: 0
livox: 0
bpearl: 0
rp_lidar: 0
ld06: 1
webcam: 0
intel: 0
oakd: 0
zed: 0
artemis: 0
ublox: 0
vesc_with_odom: 1
vesc_without_odom: 0
adafruit: 0
adafruit_servo: 0
adafruit_continuous_servo: 0
esp32: 0
stm32: 0
bldc_sensor: 0
bldc_no_sensor: 0""" > src/ucsd_robocar_hub2/ucsd_robocar_nav2_pkg/config/car_config.yaml

echo """# sensors/hardware
all_components: 1
simulator: 0

# camera navigation
camera_nav_calibration: 0
camera_nav: 0

# recording data 
rosbag_launch: 0

# TODO: Obstacle Avoidance
simple_obstacle_detection_launch: 0

# rviz
sensor_visualization: 1

# control
manual_joy_control_launch: 0
f1tenth_vesc_joy_launch: 1
pid_launch: 0
lqr_launch: 0
lqg_launch: 0
lqg_w_launch: 0
mpc_launch: 0

# path planner
path_nav: 0
tube_follower_launch: 0
curve_localizer_launch: 0""" > src/ucsd_robocar_hub2/ucsd_robocar_nav2_pkg/config/node_config.yaml

build_ros2

source_ros1
roslaunch ucsd_robocar_nav1_pkg ros_racer_mapping_launch.launch