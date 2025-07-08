import psycopg2
from kafka import KafkaProducer
import json
import time
import random

import os
from dotenv import load_dotenv
dotenv_path ='/home/vova/Рабочий стол/NovaData_Личный_проект/.env'
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

producer = KafkaProducer(
    bootstrap_servers=f'{os.environ.get('HOST')}:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)


conn = psycopg2.connect(
    dbname="test_db", user="admin", password="admin", host=f"{os.environ.get('HOST')}", port=5432
)
cursor = conn.cursor()

cursor.execute("SELECT username, event_type, extract(epoch FROM event_time) FROM user_logins")
rows = cursor.fetchall()

for row in rows:
    data = {
        "user": row[0],
        "event": row[1],
        "timestamp": float(row[2])  # преобразуем Decimal → float
    }
    producer.send("user_events", value=data)
    print("Sent:", data)
    time.sleep(0.5)