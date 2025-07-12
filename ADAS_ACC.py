ADAS code ACC 

import RPi.GPIO as GPIO
import time
from collections import deque

# ==== GPIO PIN SETUP ====
TRIG = 23
ECHO = 24

IN1, IN2 = 5, 6         # Left Motor
IN3, IN4 = 13, 26       # Right Motor
ENA, ENB = 18, 19       # PWM Pins

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

motor_pins = [IN1, IN2, IN3, IN4, ENA, ENB]
for pin in motor_pins:
    GPIO.setup(pin, GPIO.OUT)

pwm_left = GPIO.PWM(ENA, 1000)
pwm_right = GPIO.PWM(ENB, 1000)
pwm_left.start(0)
pwm_right.start(0)

# ==== ACC PARAMETERS ====
FORWARD_INVERT = True  # Set to True if your motors run backward

MAX_DIST = 400
BUFFER_SIZE = 5

# === Tweaked Distance Zones (cm) ===
STOP_DIST   = 15
SLOW_DIST   = 25
CRUISE_DIST = 45

# === Slower, smoother Speed Zones (PWM %) ===
STOP_SPEED   = 0
SLOW_SPEED   = 20
CRUISE_SPEED = 30
FAST_SPEED   = 40

distance_buffer = deque(maxlen=BUFFER_SIZE)

# ==== FUNCTIONS ====

def get_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    start = time.time()
    timeout = start + 0.03
    while GPIO.input(ECHO) == 0 and time.time() < timeout:
        start = time.time()

    stop = start
    timeout = stop + 0.03
    while GPIO.input(ECHO) == 1 and time.time() < timeout:
        stop = time.time()

    duration = stop - start
    distance = (duration * 34300) / 2
    return round(distance, 1) if 0 < distance < MAX_DIST else MAX_DIST

def smoothed_distance():
    d = get_distance()
    distance_buffer.append(d)
    return round(sum(distance_buffer) / len(distance_buffer), 1)

def motor_control(ls, rs):
    if FORWARD_INVERT:
        ls, rs = -ls, -rs

    ls = max(-100, min(100, ls))
    rs = max(-100, min(100, rs))

    # Left
    GPIO.output(IN1, GPIO.HIGH if ls > 0 else GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW if ls > 0 else GPIO.HIGH if ls < 0 else GPIO.LOW)
    pwm_left.ChangeDutyCycle(abs(ls))

    # Right
    GPIO.output(IN3, GPIO.HIGH if rs > 0 else GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW if rs > 0 else GPIO.HIGH if rs < 0 else GPIO.LOW)
    pwm_right.ChangeDutyCycle(abs(rs))

    print(f"[MOTOR] L:{ls}%  R:{rs}%")

def stop():
    motor_control(0, 0)

# ==== MAIN LOOP ====
try:
    print("🚗 CODE 2: Adaptive Cruise Control – FINAL TWEAKED")

    while True:
        dist = smoothed_distance()
        print(f"[DISTANCE] Front (smoothed): {dist} cm")

        if dist <= STOP_DIST:
            print("🟥 STOP — Too Close")
            stop()

        elif dist <= SLOW_DIST:
            print("🟧 SLOW")
            motor_control(SLOW_SPEED, SLOW_SPEED)

        elif dist <= CRUISE_DIST:
            print("🟨 CRUISE")
            motor_control(CRUISE_SPEED, CRUISE_SPEED)

        else:
            print("🟩 FAST CRUISE")
            motor_control(FAST_SPEED, FAST_SPEED)

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n[STOP] Interrupted")

finally:
    stop()
    pwm_left.stop()
    pwm_right.stop()
    GPIO.cleanup()
    print("[CLEANUP] GPIO Released")
