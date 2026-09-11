from kafka import KafkaProducer
import json, time, random

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def publish_slot_event(distance, gate_status):
    event = {
        "timestamp": time.time(),
        "distance_cm": distance,
        "slot_status": "Free" if distance > 10 else "Occupied",
        "gate_status": gate_status
    }
    producer.send("parking-events", event)
    return event

# Simulate sensor readings if no real Pi attached (for demo/dev)
if __name__ == "__main__":
    while True:
        distance = random.uniform(2, 20)
        gate = "Open" if distance > 10 else "Closed"
        event = publish_slot_event(distance, gate)
        print("Published:", event)
        time.sleep(3)
