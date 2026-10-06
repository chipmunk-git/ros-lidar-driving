import os

import numpy as np
import roslibpy
from dotenv import load_dotenv

from db_helper import DB, DB_CONFIG


load_dotenv()

ROS_PC_IP = os.getenv('ROS_PC_IP')  # .env 파일을 작성하거나 실행 전 환경변수로 ROS PC IP 지정
ROSBRIDGE_PORT = 9090

LINEAR_SPEED = 0.1
ANGULAR_SPEED = 0.5


def publish_action(cmd_vel_publisher, action):
    linear_x = 0.0
    angular_z = 0.0

    if action == 'go_forward':
        linear_x = LINEAR_SPEED

    elif action == 'turn_left':
        angular_z = ANGULAR_SPEED

    elif action == 'turn_right':
        angular_z = -ANGULAR_SPEED

    message = roslibpy.Message({
        'linear': {
            'x': linear_x,
            'y': 0.0,
            'z': 0.0
        },
        'angular': {
            'x': 0.0,
            'y': 0.0,
            'z': angular_z
        }
    })

    cmd_vel_publisher.publish(message)


def lidar_callback(message, cmd_vel_publisher, db):
    ranges = np.array(message['ranges'])

    # 방향별 거리 데이터
    front = np.r_[ranges[350:360], ranges[0:10]]
    left = ranges[80:100]
    right = ranges[260:280]

    front_dist = np.mean(front)
    left_dist = np.mean(left)
    right_dist = np.mean(right)

    # 주행 방향 결정
    safe_dist = 0.5

    if front_dist < safe_dist:
        action = 'turn_left' if left_dist > right_dist else 'turn_right'

    else:
        action = 'go_forward'

    print('front:', round(front_dist, 2))
    print('left :', round(left_dist, 2))
    print('right:', round(right_dist, 2))
    print('action:', action)

    # 주행 명령 발행
    publish_action(cmd_vel_publisher, action)

    # LiDAR 데이터 저장
    if db.insert_lidar(ranges.tolist(), action):
        print('데이터베이스 저장 완료')

    else:
        print('데이터베이스 저장 실패')


def main():
    client = roslibpy.Ros(
        host=ROS_PC_IP,
        port=ROSBRIDGE_PORT
    )

    lidar_listener = roslibpy.Topic(
        client,
        '/scan',
        'sensor_msgs/LaserScan'
    )

    cmd_vel_publisher = roslibpy.Topic(
        client,
        '/cmd_vel',
        'geometry_msgs/Twist'
    )

    # 데이터베이스 객체 생성
    db = DB(**DB_CONFIG)

    cmd_vel_publisher.advertise()

    lidar_listener.subscribe(
        lambda message: lidar_callback(message, cmd_vel_publisher, db)
    )

    try:
        client.run_forever()

    except KeyboardInterrupt:
        pass

    finally:
        lidar_listener.unsubscribe()
        cmd_vel_publisher.unadvertise()
        client.terminate()


if __name__ == '__main__':
    main()