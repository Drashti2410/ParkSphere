# Smart IoT Parking Gate System

An intelligent automated parking gate controller that manages vehicle access based on real-time slot availability. The system uses ultrasonic and IR sensors to detect vehicles and automatically opens/closes the gate accordingly, with remote control capabilities via PubNub cloud messaging.

## Features

- 🚗 **Automatic Gate Control** - Opens when car arrives and parking slot is free
- 📏 **Real-time Distance Measurement** - Ultrasonic sensor monitors slot occupancy
- 🚨 **IR Vehicle Detection** - Detects vehicle presence at gate entrance
- 💡 **LED Indicator** - Visual status display for parking slot availability
- 🔔 **Buzzer Alert** - Audio warning when vehicle is too close
- 📡 **Remote Gate Control** - Open/close gate via PubNub messaging
- 📊 **Cloud Integration** - Live status updates to PubNub

## Tech Stack

- **Hardware Controller**: Raspberry Pi (BCM GPIO)
- **Language**: Python 3
- **GPIO Library**: RPi.GPIO
- **IoT Platform**: PubNub (Real-time messaging)
- **Sensors**: HC-SR04 Ultrasonic Sensor, IR Motion Sensor
- **Actuators**: Servo Motor (SG90), LED, Buzzer

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

### Prerequisites
```bash
# Install required packages on Raspberry Pi
sudo apt-get update
sudo apt-get install python3-pip
sudo pip3 install pubnub
```

### Running the Script
```bash
# Run with sudo (required for GPIO access)
sudo python3 "Python Script.py"
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

## Usage

1. Power on the Raspberry Pi
2. Ensure all sensors and actuators are properly connected
3. Run the script with GPIO privileges
4. Monitor output for distance readings and gate status
5. Use PubNub interface for remote control (optional)

## Project Structure

```
IOTFInalProjectGRP7/
├── Python Script.py      # Main controller script
├── README.md            # Project documentation
└── [Additional files]
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

## Future Enhancements

- Mobile app integration for real-time notifications
- Machine learning for traffic pattern analysis
- Multiple gate support for larger facilities
- RFID/License plate integration for vehicle identification
- Database logging for analytics

## License

[Add your license here]

## Authors

Group 7

---

**Note**: Ensure proper safety measures are in place when deploying in production environments. Test thoroughly before deployment.
