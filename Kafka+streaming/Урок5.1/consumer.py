# consumer_to_clickhouse.py
from kafka import KafkaConsumer
import json
import clickhouse_connect

import os
from dotenv import load_dotenv
dotenv_path ='/home/vova/Рабочий стол/NovaData_Личный_проект/.env'
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

consumer = KafkaConsumer(
    "user_events",
    bootstrap_servers=f'{os.environ.get('HOST')}:9092',
    group_id='users',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

client = clickhouse_connect.get_client(host=f'{os.environ.get('HOST')}', port=8123, username='user', password='strongpassword')

client.command("""
CREATE TABLE IF NOT EXISTS user_logins (
    username String,
    event_type String,
    event_time DateTime
) ENGINE = MergeTree()
ORDER BY event_time
""")

for message in consumer:
    data = message.value
    print("Received:", data)
    client.command(
        f"INSERT INTO user_logins (username, event_type, event_time) VALUES ('{data['user']}', '{data['event']}', toDateTime({data['timestamp']}))"
    )
