#ADAS codes lane change 

import RPi.GPIO as GPIO
import time

# ==== GPIO SETUP ====
TRIG = 23
ECHO = 24

IN1, IN2 = 5, 6     # Left motor
IN3, IN4 = 13, 26   # Right motor
ENA, ENB = 18, 19   # PWM

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Setup Motor and Sensor Pins
for pin in [IN1, IN2, IN3, IN4, ENA, ENB, TRIG]:
    GPIO.setup(pin, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

pwm_left = GPIO.PWM(ENA, 1000)
pwm_right = GPIO.PWM(ENB, 1000)
pwm_left.start(0)
pwm_right.start(0)

# ==== PARAMETERS ====
FORWARD_SPEED = 30
TURN_SPEED = 35
LANE_SHIFT_TIME = 0.7
SAFE_DISTANCE = 20
FORWARD_INVERT = True

# ==== MOVEMENT ====

def motor_control(ls, rs):
    if FORWARD_INVERT:
        ls, rs = -ls, -rs

    GPIO.output(IN1, GPIO.HIGH if ls > 0 else GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW if ls > 0 else GPIO.HIGH if ls < 0 else GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH if rs > 0 else GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW if rs > 0 else GPIO.HIGH if rs < 0 else GPIO.LOW)

    pwm_left.ChangeDutyCycle(abs(ls))
    pwm_right.ChangeDutyCycle(abs(rs))

def stop():
    pwm_left.ChangeDutyCycle(0)
    pwm_right.ChangeDutyCycle(0)
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)

def move_forward():
    motor_control(FORWARD_SPEED, FORWARD_SPEED)

def turn_left():
    motor_control(-TURN_SPEED//2, TURN_SPEED)
    time.sleep(LANE_SHIFT_TIME)
    stop()

def turn_right():
    motor_control(TURN_SPEED, -TURN_SPEED//2)
    time.sleep(LANE_SHIFT_TIME)
    stop()

def forward_short():
    move_forward()
    time.sleep(0.5)
    stop()

# ==== ULTRASONIC ====

def get_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.01)

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
    distance = duration * 17150
    return round(distance, 1) if 0 < distance < 400 else 400

# ==== OBSTACLE AVOIDANCE LOGIC ====

def check_and_shift():
    stop()
    print("🟥 Object Ahead — Checking LEFT")
    turn_left()
    time.sleep(0.2)
    left_dist = get_distance()
    print(f"⬅️ LEFT Check: {left_dist} cm")

    if left_dist > SAFE_DISTANCE:
        print("✅ LEFT is clear — Shifting")
        forward_short()
        turn_right()
    else:
        print("❌ LEFT blocked — Checking RIGHT")
        turn_right()  # Center again
        time.sleep(0.2)
        turn_right()  # Shift to right
        time.sleep(0.2)
        forward_short()
        turn_left()

# ==== MAIN LOOP ====

try:
    print("🚘 CODE 1: Lane Shift Smart Check")

    while True:
        dist = get_distance()
        print(f"[DISTANCE] Front: {dist} cm")

        if dist > SAFE_DISTANCE:
            move_forward()
        else:
            check_and_shift()

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n[STOP] Interrupted")

finally:
    stop()
    pwm_left.stop()
    pwm_right.stop()
    GPIO.cleanup()
    print("[CLEANUP] GPIO released")
