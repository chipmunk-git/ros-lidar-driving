import json

import pandas as pd
import pymysql

from db_helper import DB_CONFIG


df = pd.DataFrame()

conn = pymysql.connect(**DB_CONFIG)

cursor = conn.cursor()

cursor.execute("SELECT ranges, action FROM lidardata")

rows = cursor.fetchall()

for r in rows:
    ranges = json.loads(r[0])
    action = r[1]

    row = pd.DataFrame([{i: v for i, v in enumerate(ranges)}])
    row['action'] = action
    df = pd.concat([df, row], ignore_index=True)

print(df)

df.to_csv('output.csv', index=False)

cursor.close()
conn.close()