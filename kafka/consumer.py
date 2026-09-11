from kafka import KafkaConsumer
import json
from api.db import save_event

consumer = KafkaConsumer(
    "parking-events",
    bootstrap_servers="localhost:9092",
    group_id="parking-db-writer",
    value_deserializer=lambda v: json.loads(v.decode("utf-8"))
)

print("Listening for parking events...")
for msg in consumer:
    event = msg.value
    save_event(event["distance_cm"], event["slot_status"], event["gate_status"])
    print("Saved:", event)
