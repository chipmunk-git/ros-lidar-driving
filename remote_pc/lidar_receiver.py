import os

import roslibpy
from dotenv import load_dotenv


load_dotenv()

ROS_PC_IP = os.getenv('ROS_PC_IP')  # .env 파일을 작성하거나 실행 전 환경변수로 ROS PC IP 지정
ROSBRIDGE_PORT = 9090


def lidar_callback(message):
    ranges = message['ranges']

    print(f'LiDAR 데이터 수신 - ranges: {len(ranges)}개')


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