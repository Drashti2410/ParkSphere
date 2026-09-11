# ParkSphere — Smart IoT Parking Gate System

An intelligent automated parking gate controller that manages vehicle access based on real-time slot availability. The system uses ultrasonic and IR sensors to detect vehicles and automatically opens/closes the gate accordingly, with remote control via PubNub cloud messaging.

On top of the original hardware demo, ParkSphere now includes a **production-style ingestion and analytics layer**: a Kafka event stream, a database-backed history store, a FastAPI service, and a live web dashboard — the pieces you'd add if this scaled from one Raspberry Pi to hundreds of parking gates.

## Features

### Hardware / real-time control
- 🚗 **Automatic Gate Control** - Opens when car arrives and parking slot is free
- 📏 **Real-time Distance Measurement** - Ultrasonic sensor monitors slot occupancy
- 🚨 **IR Vehicle Detection** - Detects vehicle presence at gate entrance
- 💡 **LED Indicator** - Visual status display for parking slot availability
- 🔔 **Buzzer Alert** - Audio warning when vehicle is too close
- 📡 **Remote Gate Control** - Open/close gate via PubNub messaging
- 📊 **Cloud Integration** - Live status updates to PubNub

### Streaming, storage & dashboard
- 🔁 **Kafka Event Stream** - Every sensor reading is published to a `parking-events` topic as a durable, replayable log
- 🗄️ **Event History Store** - A Kafka consumer persists every event to a SQLite database
- ⚡ **FastAPI Service** - REST endpoints for health, recent history, and occupancy stats
- 📈 **Live Dashboard** - Simple browser dashboard polling the API for real-time status
- 🐳 **Dockerized API** - The API service ships as a container
- ✅ **CI Pipeline** - GitHub Actions runs tests and builds the Docker image on every push

## Architecture

```
Raspberry Pi (sensors)
      │
      ├──► PubNub  ───────────────► Remote gate control (low-latency, demo)
      │
      └──► Kafka producer ──► "parking-events" topic ──► Kafka consumer ──► SQLite DB
                                                                                │
                                                                                ▼
                                                                          FastAPI (reads DB)
                                                                                │
                                                                                ▼
                                                                        Dashboard (browser)
```

**Design choice:** PubNub stays as the real, working hardware demo — it's what actually drives the physical Raspberry Pi gate. Kafka is added as the durable ingestion layer: the API only ever reads from the database, never from Kafka directly, so the read path stays decoupled from the broker's uptime (a Kafka outage never takes the dashboard down, only pauses new writes).

## Tech Stack

- **Hardware Controller**: Raspberry Pi (BCM GPIO)
- **Language**: Python 3
- **GPIO Library**: RPi.GPIO
- **IoT Platform**: PubNub (real-time remote gate control)
- **Sensors**: HC-SR04 Ultrasonic Sensor, IR Motion Sensor
- **Actuators**: Servo Motor (SG90), LED, Buzzer
- **Event Streaming**: Apache Kafka + Zookeeper (via `kafka-python`)
- **API**: FastAPI + Uvicorn
- **Database**: SQLite via SQLAlchemy
- **Dashboard**: Static HTML/JS (fetches the API directly)
- **Testing**: pytest + httpx (FastAPI `TestClient`)
- **Containerization**: Docker
- **CI/CD**: GitHub Actions

## Hardware Requirements

| Component | Specifications |
|-----------|----------------|
| Raspberry Pi | Any model with GPIO pins |
| Ultrasonic Sensor | HC-SR04 (Trig: GPIO23, Echo: GPIO24) |
| IR Sensor | Motion/Proximity detector (GPIO17) |
| Servo Motor | SG90 or similar (GPIO12) |
| LED | Standard LED (GPIO18) |
| Buzzer | 5V Buzzer (GPIO20) |
| Power Supply | 5V PSU for RPi & components |
| Cables | Jumper wires, breadboard |

## GPIO Pin Configuration

```
TRIG   = GPIO 23  (Ultrasonic Trigger)
ECHO   = GPIO 24  (Ultrasonic Echo)
IR     = GPIO 17  (IR Sensor)
LED    = GPIO 18  (Status LED)
SERVO  = GPIO 12  (Gate Servo Motor)
BUZZER = GPIO 20  (Alert Buzzer)
```

## System Logic

### Slot Detection
- **Free Slot**: Distance > 10 cm → LED ON
- **Occupied Slot**: Distance ≤ 10 cm → LED OFF

### Gate Control
1. **Opening Condition**: IR detects car (IR=0) AND slot is free
   - Gate opens automatically
   - LED indicates free slot

2. **Closing Condition**: Car passes gate (IR=1)
   - Gate closes automatically

3. **Remote Override**:
   - `force_open` command opens gate remotely
   - `force_close` command closes gate remotely

### Alerts
- **Buzzer Activation**: Triggers when distance < 5 cm (too close warning)

## Installation

### Prerequisites (Raspberry Pi hardware)
```bash
# Install required packages on Raspberry Pi
sudo apt-get update
sudo apt-get install python3-pip
sudo pip3 install -r requirements.txt
```

### Prerequisites (streaming + API stack, any dev machine)
```bash
pip install -r requirements.txt
docker-compose up -d   # starts Kafka + Zookeeper
```

### Running the hardware script
```bash
# Run with sudo (required for GPIO access)
sudo python3 "Python Script.py"
```

## Running the Full Stack

The streaming/API stack runs independently of the physical hardware — use the simulated producer if you don't have a Pi attached.

```bash
docker-compose up -d                # 1. Kafka + Zookeeper
uvicorn api.main:app --reload       # 2. FastAPI service (http://localhost:8000)
python kafka/consumer.py            # 3. Consumer: writes events to the DB
python kafka/producer.py            # 4. Producer: simulates sensor events (or drives real Pi readings)
```

Then open [`dashboard/index.html`](dashboard/index.html) directly in a browser, or serve it:
```bash
cd dashboard && python -m http.server
```

## PubNub Configuration

The system publishes to channel: `group_7`

### Published Messages
```json
{
  "slot": "Free|Occupied",
  "distance": 15.5,
  "gate": "Open|Closed|Idle|Open (Remote)|Closed (Remote)"
}
```

### Remote Control Commands
Subscribe to channel `group_7` and publish:
```json
{
  "command": "force_open"
}
```
or
```json
{
  "command": "force_close"
}
```

## Kafka Configuration

Events are published to the `parking-events` topic (see [`kafka/producer.py`](kafka/producer.py)):

```json
{
  "timestamp": 1737849600.123,
  "distance_cm": 8.4,
  "slot_status": "Free|Occupied",
  "gate_status": "Open|Closed"
}
```

[`kafka/consumer.py`](kafka/consumer.py) subscribes as consumer group `parking-db-writer` and persists every event to SQLite via [`api/db.py`](api/db.py).

## API Endpoints

Served by [`api/main.py`](api/main.py) (FastAPI, default `http://localhost:8000`):

| Endpoint | Description |
|----------|--------------|
| `GET /health` | Liveness check — `{"status": "ok"}` |
| `GET /history?limit=50` | Most recent parking events from the database |
| `GET /stats` | Occupancy stats — total events and percent occupied |

The API only reads from the database — it never queries Kafka directly, so its uptime isn't coupled to the broker.

## Dashboard

[`dashboard/index.html`](dashboard/index.html) is a lightweight static page that polls `/stats` and `/history` every 3 seconds and renders live occupancy and recent events. No build step — open it directly in a browser once the API is running.

## Testing

```bash
pytest tests/
```

[`tests/test_api.py`](tests/test_api.py) covers the health check, the shape of `/stats`, and the `limit` behavior of `/history` using FastAPI's `TestClient`.

## Docker & CI

- [`Dockerfile`](Dockerfile) builds the FastAPI service into a container (`uvicorn api.main:app`).
- [`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs `pytest` and builds the Docker image on every push.

```bash
docker build -t parksphere-api .
docker run -p 8000:8000 parksphere-api
```

## Usage

1. Power on the Raspberry Pi
2. Ensure all sensors and actuators are properly connected
3. Run the script with GPIO privileges
4. Monitor output for distance readings and gate status
5. Use PubNub interface for remote control (optional)
6. Optionally bring up Kafka + the API/dashboard stack to see durable event history and live occupancy stats

## Project Structure

```
ParkSphere/
├── Python Script.py          # Main hardware controller script (PubNub + GPIO)
├── kafka/
│   ├── producer.py           # Publishes sensor/simulated events to the "parking-events" topic
│   └── consumer.py           # Persists events from Kafka into the database
├── api/
│   ├── main.py                # FastAPI app: /health, /history, /stats
│   └── db.py                  # SQLAlchemy models + DB access helpers
├── dashboard/
│   └── index.html             # Live status dashboard (polls the API)
├── tests/
│   └── test_api.py            # pytest tests for the API
├── docker-compose.yml          # Local Kafka + Zookeeper cluster
├── Dockerfile                  # Container build for the API service
├── requirements.txt             # Full dev/hardware dependencies
├── requirements-api.txt        # Minimal dependencies for the API container
├── .github/workflows/ci.yml    # CI: tests + Docker build
└── README.md
```

## System States

- **Idle**: No vehicle at gate, slot status displayed
- **Car Detected**: Vehicle at gate entrance (IR=0)
- **Gate Open**: Access granted, vehicle entering
- **Gate Closed**: Slot occupied or vehicle leaving
- **Remote Override**: Manual gate control via PubNub

## Error Handling

- **Sensor Timeout** (-1): Returns error message if sensor fails to respond
- **Keyboard Interrupt**: Gracefully stops system and cleans up GPIO
- **GPIO Cleanup**: Ensures all pins are reset on exit

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Sensor reads -1 | Check sensor wiring and power supply |
| Gate doesn't open | Verify servo motor connections and PWM signal |
| No PubNub updates | Check internet connection and API keys |
| LED not lighting | Check GPIO pin and LED polarity |
| Producer/consumer can't connect | Confirm `docker-compose up -d` is running and port 9092 is reachable |
| `/history` or `/stats` returns empty | Make sure the consumer is running so events are actually written to the DB |
| API container won't build | Rebuild with `docker build -t parksphere-api .` and check `requirements-api.txt` |

## Future Enhancements

- Mobile app integration for real-time notifications
- Machine learning for traffic pattern analysis
- Multiple gate support for larger facilities (Kafka partitions per gate)
- RFID/License plate integration for vehicle identification
- Swap SQLite for a networked database (Postgres) for multi-instance deployments

## Interview Notes

- **Why two messaging systems?** PubNub was the fastest path to a working IoT demo on real hardware. Kafka is what this would become in production — a durable, replayable event log that many consumers (DB writer, analytics, alerting) can read independently, and that scales to many gates via partitions and consumer groups.
- **What changed along the way:** the first version of the API queried Kafka directly on every request, which coupled the API's uptime to the broker and added latency. The fix was the standard event-sourcing split: the consumer writes to the database, and the API only ever reads from the database.

## License

[Add your license here]

## Authors

Group 7

---

**Note**: Ensure proper safety measures are in place when deploying in production environments. Test thoroughly before deployment.
