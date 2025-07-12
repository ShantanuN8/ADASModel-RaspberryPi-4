# 🚗 Raspberry Pi ADAS Robot Car

This project implements an **Advanced Driver Assistance System (ADAS)** using Raspberry Pi, ultrasonic sensors, and a camera. It mimics smart automotive features like obstacle detection, lane changes, adaptive cruise control, and traffic light responses.

---

## 🧠 Features Implemented

| Code   | Feature                           | Description                                                              |
|--------|-----------------------------------|--------------------------------------------------------------------------|
| 1 | Smart Lane Change Detection       | Scans left/right using ultrasonic sensors and changes lane accordingly. |
| 2 | Adaptive Cruise Control (ACC)     | Adjusts car speed based on object distance using ultrasonic sensor.     |
| 3 | Traffic Light Recognition         | Uses camera to detect red/green lights and decides stop/go.             |
| 4 | Lane Width / Side Safety Detection| Stops the car if the lane is too narrow using side ultrasonic sensors.  |

---

## ⚙️ Hardware Requirements

- Raspberry Pi (3B/4)
- Raspberry Pi Camera Module v2
- L298N Motor Driver
- 4x DC Motors + wheels
- 3x Ultrasonic sensors (front, front-left, front-right)
- Breadboard, jumper wires, resistors
- 3x 3.7V Li-ion batteries (connected in series)
- Voltage divider for ECHO pin to GPIO

---

## 🔌 Wiring Summary

| Component            | GPIO Pins Used                      |
|----------------------|--------------------------------------|
| Front Ultrasonic     | TRIG: GPIO 23, ECHO: GPIO 24         |
| Left Side US (CODE 4)| TRIG: GPIO 20, ECHO: GPIO 21         |
| Right Side US (CODE 4)| TRIG: GPIO 17, ECHO: GPIO 27        |
| Motor Left           | IN1: GPIO 5, IN2: GPIO 6, ENA: GPIO 18 |
| Motor Right          | IN3: GPIO 13, IN4: GPIO 26, ENB: GPIO 19 |
| Pi Camera            | CSI interface (enabled via config)  |

---

## 🧩 Installation Steps

1. **Flash Raspberry Pi OS**
   - Use Raspberry Pi Imager to flash OS onto SD card.
   - Recommended: Raspberry Pi OS Lite or Full (32-bit).

2. **Enable Interfaces**
   ```bash
   sudo raspi-config
