import json

import pymysql


DB_CONFIG = dict(
    host="localhost",
    user="root",
    password="1234",
    database="rosdb",
    charset="utf8"
)


class DB:

    def __init__(self, **config):
        self.config = config

    def connect(self):
        return pymysql.connect(**self.config)

    # LiDAR 데이터 저장
    def insert_lidar(self, ranges, action):
        sql = "INSERT INTO lidardata (ranges, action) VALUES (%s, %s)"
        ranges_json = json.dumps(ranges)

        with self.connect() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, (ranges_json, action))

                conn.commit()
                return True

            except Exception:
                conn.rollback()
                return False
