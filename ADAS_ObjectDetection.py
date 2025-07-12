#ADAS code CAMERA STOP

from picamera2 import Picamera2
import cv2
import numpy as np
import RPi.GPIO as GPIO
import time

# ==== Motor Setup ====
IN1, IN2 = 5, 6
IN3, IN4 = 13, 26
ENA, ENB = 18, 19

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

for pin in [IN1, IN2, IN3, IN4, ENA, ENB]:
    GPIO.setup(pin, GPIO.OUT)

pwm_left = GPIO.PWM(ENA, 1000)
pwm_right = GPIO.PWM(ENB, 1000)
pwm_left.start(0)
pwm_right.start(0)

# ✅ Updated Snippet: correct motor direction
def motor_control(left_speed, right_speed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwm_left.ChangeDutyCycle(left_speed)
    pwm_right.ChangeDutyCycle(right_speed)

def stop():
    pwm_left.ChangeDutyCycle(0)
    pwm_right.ChangeDutyCycle(0)
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)

# ==== Camera Setup ====
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(
    main={"size": (640, 480), "format": "XRGB8888"}
))
picam2.start()
time.sleep(2)

# ==== HSV Color Ranges ====
LOWER_RED1 = np.array([0, 100, 100])
UPPER_RED1 = np.array([10, 255, 255])
LOWER_RED2 = np.array([160, 100, 100])
UPPER_RED2 = np.array([180, 255, 255])

LOWER_GREEN = np.array([40, 70, 70])
UPPER_GREEN = np.array([80, 255, 255])

# ==== Color Detection Function ====
def detect_color(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask_red1 = cv2.inRange(hsv, LOWER_RED1, UPPER_RED1)
    mask_red2 = cv2.inRange(hsv, LOWER_RED2, UPPER_RED2)
    red_mask = cv2.bitwise_or(mask_red1, mask_red2)

    green_mask = cv2.inRange(hsv, LOWER_GREEN, UPPER_GREEN)

    red_area = cv2.countNonZero(red_mask)
    green_area = cv2.countNonZero(green_mask)

    return red_area, green_area

# ==== Main Loop ====
try:
    print("🚦 CODE 3: Red = STOP / Green = GO")

    while True:
        frame = picam2.capture_array()
        red_area, green_area = detect_color(frame)

        print(f"[COLOR] Red: {red_area} | Green: {green_area}")

        if red_area > 3000:
            print("🟥 RED DETECTED — STOP")
            stop()
        elif green_area > 3000:
            print("🟩 GREEN DETECTED — MOVING")
            motor_control(25, 25)
        else:
            print("❓ No strong signal — IDLE")
            stop()

        cv2.imshow("Cam View", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("\n[STOP] Interrupted")

finally:
    stop()
    pwm_left.stop()
    pwm_right.stop()
    GPIO.cleanup()
    picam2.stop()
    cv2.destroyAllWindows()
    print("[CLEANUP] All released")
