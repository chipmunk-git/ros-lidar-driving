import os

import numpy as np
import roslibpy
from dotenv import load_dotenv


load_dotenv()

ROS_PC_IP = os.getenv('ROS_PC_IP')  # .env 파일을 작성하거나 실행 전 환경변수로 ROS PC IP 지정
ROSBRIDGE_PORT = 9090


def lidar_callback(message):
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


def main():
    client = roslibpy.Ros(
        host=ROS_PC_IP,
        port=ROSBRIDGE_PORT
    )

    lidar_listener = roslibpy.Topic(
        client,
        '/mock_scan',
        'sensor_msgs/LaserScan'
    )

    lidar_listener.subscribe(lidar_callback)

    try:
        client.run_forever()

    except KeyboardInterrupt:
        pass

    finally:
        lidar_listener.unsubscribe()
        client.terminate()


if __name__ == '__main__':
    main()