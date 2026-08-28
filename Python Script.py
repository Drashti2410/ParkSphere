from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
from pubnub.callbacks import SubscribeCallback
import RPi.GPIO as GPIO
import time

# =========================
# PubNub Setup
# =========================
pnconfig = PNConfiguration()
pnconfig.subscribe_key = "sub-c-d2cf210c-9365-4938-ac72-9627d63ef60d"
pnconfig.publish_key = "pub-c-3a406da1-b0a2-4010-b78f-2334b59a131d"
pnconfig.uuid = "pubnub-devtools-user"

pubnub = PubNub(pnconfig)
channel = "group_7"

# =========================
# GPIO Setup
# =========================
TRIG = 23
ECHO = 24
IR = 17
LED = 18
SERVO = 12
BUZZER = 20

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(IR, GPIO.IN)
GPIO.setup(LED, GPIO.OUT)
GPIO.setup(SERVO, GPIO.OUT)
GPIO.setup(BUZZER, GPIO.OUT)

servo = GPIO.PWM(SERVO, 50)
servo.start(0)

remote_command = "none"
gate_open = False   # 🔥 IMPORTANT STATE

# =========================
# Ultrasonic Function
# =========================
def distance():
    GPIO.output(TRIG, False)
    time.sleep(0.05)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    timeout = time.time()

    while GPIO.input(ECHO) == 0:
        start = time.time()
        if start - timeout > 0.05:
            return -1

    timeout = time.time()

    while GPIO.input(ECHO) == 1:
        end = time.time()
        if end - timeout > 0.05:
            return -1

    duration = end - start
    return round(duration * 17150, 2)

# =========================
# Servo Functions (FIXED)
# =========================
def open_gate():
    servo.ChangeDutyCycle(7)
    time.sleep(1)
    servo.ChangeDutyCycle(0)

def close_gate():
    servo.ChangeDutyCycle(2)
    time.sleep(1)
    servo.ChangeDutyCycle(0)

# =========================
# PubNub Listener
# =========================
class MySubscribeCallback(SubscribeCallback):
    def message(self, pubnub, message):
        global remote_command
        msg = message.message

        if "command" in msg:
            remote_command = msg["command"]
            print("Remote:", remote_command)

pubnub.add_listener(MySubscribeCallback())
pubnub.subscribe().channels(channel).execute()

# =========================
# MAIN LOOP
# =========================
try:
    print("🚀 FINAL SYSTEM (CORRECT LOGIC)")

    while True:
        d = distance()
        print("Distance:", d)

        if d == -1:
            print("⚠️ Sensor Error")
            continue

        # -------- SLOT STATUS --------
        slot_free = d > 10

        # LED
        GPIO.output(LED, slot_free)

        # Buzzer
        if d < 5:
            GPIO.output(BUZZER, True)
            print("🔔 Too Close!")
        else:
            GPIO.output(BUZZER, False)

        # -------- IR → GATE CONTROL (FIXED LOGIC) --------
        ir_val = GPIO.input(IR)
        print("IR:", ir_val)

        # 🔥 Gate opens ONLY when car arrives AND slot is free
        if ir_val == 0 and not gate_open:
            print("🚗 Car at gate")

            if slot_free:
                print("🅿️ Slot FREE → OPEN")
                open_gate()
                gate_open = True
                gate_status = "Open"
            else:
                print("❌ Slot FULL → KEEP CLOSED")
                gate_status = "Closed"

        # 🔥 Gate closes when car leaves
        elif ir_val == 1 and gate_open:
            print("🚫 Car passed → CLOSE")
            close_gate()
            gate_open = False
            gate_status = "Closed"

        else:
            gate_status = "Idle"

        # -------- REMOTE OVERRIDE --------
        if remote_command == "force_open":
            open_gate()
            gate_open = True
            gate_status = "Open (Remote)"

        elif remote_command == "force_close":
            close_gate()
            gate_open = False
            gate_status = "Closed (Remote)"

        print(f"Slot: {'Free' if slot_free else 'Occupied'} | Gate: {gate_status}")

        # Send to PubNub
        pubnub.publish().channel(channel).message({
            "slot": "Free" if slot_free else "Occupied",
            "distance": d,
            "gate": gate_status
        }).sync()

        time.sleep(1)

except KeyboardInterrupt:
    print("Stopping...")

finally:
    servo.stop()
    GPIO.cleanup()