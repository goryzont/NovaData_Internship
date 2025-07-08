from kafka import KafkaProducer
import json
import time
import random

import os
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

producer = KafkaProducer(
    bootstrap_servers=f'{os.environ.get('HOST')}:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

users = ["alice", "bob", "carol", "dave"]

while True:
    data = {
        "user": random.choice(users),
        "event": "login",
        "timestamp": time.time()
    }
    producer.send("user_events", value=data)
    print("Sent:", data)
    time.sleep(1)