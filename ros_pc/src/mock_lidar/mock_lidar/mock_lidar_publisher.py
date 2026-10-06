import math
import random

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


ANGLE_MIN_DEG = 0
ANGLE_MAX_DEG = 359
ANGLE_INCREMENT_DEG = 1
NUM_POINTS = 360
RANGE_MIN = 0.12
RANGE_MAX = 3.5


def create_empty_scan():
    ranges = [RANGE_MAX for _ in range(NUM_POINTS)]
    intensities = [100.0 for _ in range(NUM_POINTS)]

    scan = {
        'angle_min': math.radians(ANGLE_MIN_DEG),
        'angle_max': math.radians(ANGLE_MAX_DEG),
        'angle_increment': math.radians(ANGLE_INCREMENT_DEG),
        'range_min': RANGE_MIN,
        'range_max': RANGE_MAX,
        'ranges': ranges,
        'intensities': intensities
    }

    return scan


# 벽 만들기
def make_the_wall(ranges, center_deg, width_deg):
    half_width = width_deg // 2

    for offset in range(-half_width, half_width + 1):
        index = (center_deg + offset) % NUM_POINTS
        ranges[index] = 0.4


def pattern_front_wall(scan):
    make_the_wall(scan['ranges'], center_deg=0, width_deg=40)


def pattern_left_wall(scan):
    make_the_wall(scan['ranges'], center_deg=90, width_deg=30)


def pattern_right_wall(scan):
    make_the_wall(scan['ranges'], center_deg=270, width_deg=30)


def generate_single_scan(pattern_name):
    scan = create_empty_scan()

    if pattern_name == 'front_wall':
        pattern_front_wall(scan)
    elif pattern_name == 'left_wall':
        pattern_left_wall(scan)
    elif pattern_name == 'right_wall':
        pattern_right_wall(scan)

    return scan


AVAILABLE_PATTERNS = [
    'front_wall',
    'left_wall',
    'right_wall'
]


class MockLidarPublisher(Node):

    def __init__(self):
        super().__init__('mock_lidar_publisher')

        # LiDAR 모의 데이터 Publisher 생성
        self.publisher_ = self.create_publisher(
            LaserScan,
            '/mock_scan',
            10
        )

        # 2초마다 LiDAR 모의 데이터 발행
        self.timer = self.create_timer(2.0, self.publish_scan)

    def publish_scan(self):
        pattern_name = random.choice(AVAILABLE_PATTERNS)
        scan = generate_single_scan(pattern_name)

        # LaserScan 메시지 생성
        msg = LaserScan()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'laser'
        msg.angle_min = scan['angle_min']
        msg.angle_max = scan['angle_max']
        msg.angle_increment = scan['angle_increment']
        msg.range_min = scan['range_min']
        msg.range_max = scan['range_max']
        msg.ranges = scan['ranges']
        msg.intensities = scan['intensities']

        self.publisher_.publish(msg)

        self.get_logger().info(
            f'LiDAR 모의 데이터 발행 - pattern: {pattern_name}'
        )


def main(args=None):
    rclpy.init(args=args)

    mock_lidar_publisher = MockLidarPublisher()

    rclpy.spin(mock_lidar_publisher)

    mock_lidar_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()