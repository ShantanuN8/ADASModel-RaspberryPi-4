#ADAS code side safety 

import RPi.GPIO as GPIO
import time

# ==== SENSOR PINS ====
LEFT_TRIG = 20
LEFT_ECHO = 21
RIGHT_TRIG = 17
RIGHT_ECHO = 27

# ==== MOTOR PINS ====
IN1, IN2 = 5, 6
IN3, IN4 = 13, 26
ENA, ENB = 18, 19

# ==== SETUP ====
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

for pin in [IN1, IN2, IN3, IN4, ENA, ENB, LEFT_TRIG, RIGHT_TRIG]:
    GPIO.setup(pin, GPIO.OUT)
for pin in [LEFT_ECHO, RIGHT_ECHO]:
    GPIO.setup(pin, GPIO.IN)

pwm_left = GPIO.PWM(ENA, 1000)
pwm_right = GPIO.PWM(ENB, 1000)
pwm_left.start(0)
pwm_right.start(0)

# ==== PARAMETERS ====
MIN_SIDE_DISTANCE = 7    # cm
MOVE_SPEED = 30
FORWARD_INVERT = True

# ==== FUNCTIONS ====
def get_distance(trig, echo):
    GPIO.output(trig, False)
    time.sleep(0.01)
    GPIO.output(trig, True)
    time.sleep(0.00001)
    GPIO.output(trig, False)

    start = time.time()
    timeout = start + 0.03
    while GPIO.input(echo) == 0 and time.time() < timeout:
        start = time.time()

    stop = start
    timeout = stop + 0.03
    while GPIO.input(echo) == 1 and time.time() < timeout:
        stop = time.time()

    duration = stop - start
    distance = duration * 17150
    return round(distance, 1) if 0 < distance < 400 else 400

def motor_control(ls, rs):
    if FORWARD_INVERT:
        ls, rs = -ls, -rs

    GPIO.output(IN1, GPIO.HIGH if ls > 0 else GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW if ls > 0 else GPIO.HIGH if ls < 0 else GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH if rs > 0 else GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW if rs > 0 else GPIO.HIGH if rs < 0 else GPIO.LOW)

    pwm_left.ChangeDutyCycle(abs(ls))
    pwm_right.ChangeDutyCycle(abs(rs))
    print(f"[MOTOR] L:{ls}%  R:{rs}%")

def stop():
    pwm_left.ChangeDutyCycle(0)
    pwm_right.ChangeDutyCycle(0)
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    print("🛑 STOPPED — One side too close")

# ==== MAIN LOOP ====
try:
    print("🚘 CODE 4: Side Safety Stop Active")
    while True:
        left_dist = get_distance(LEFT_TRIG, LEFT_ECHO)
        right_dist = get_distance(RIGHT_TRIG, RIGHT_ECHO)

        print(f"[SIDE] Left: {left_dist} cm | Right: {right_dist} cm")

        if left_dist < MIN_SIDE_DISTANCE or right_dist < MIN_SIDE_DISTANCE:
            stop()
        else:
            motor_control(MOVE_SPEED, MOVE_SPEED)

        time.sleep(0.2)

except KeyboardInterrupt:
    print("\n[STOP] Interrupted")

finally:
    stop()
    pwm_left.stop()
    pwm_right.stop()
    GPIO.cleanup()
    print("[CLEANUP] All GPIO released")
