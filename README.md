# 😴 RestAware – Real-Time Drowsiness Detection & Alert System

**A Raspberry Pi-based drowsiness monitoring system using eye-blink detection and NeoPixel LED alerts. Streams real-time video to a remote machine and sends alerts upon detecting sleepy behavior.**

---

## 🚀 Project Overview

RestAware is a lightweight and efficient blink-detection system designed for:

- Detecting prolonged eye closures (aka sleepy blinks)
- Sending **visual alerts** using **NeoPixel LEDs**
- Streaming real-time video to a connected remote laptop
- Automatically turning off alerts after a defined timeout

Primarily built using:
- Raspberry Pi + **Picamera2**
- **OpenCV** for eye detection
- **NeoPixel LEDs** for visual alert
- **Socket streaming** to send video & alerts to a host machine

---

## 🛠️ Hardware Requirements

- **Raspberry Pi 4 / 3B+**
- **Camera Module (OV5647 supported)**
- **NeoPixel LED Ring (WS2812, 16 LEDs)**
- **Breadboard & resistors (10k pull-ups for I2C)**
- **Power Supply for LEDs**

### 🔧 Hardware Notes
- **MPU6050 / IR Camera**: If using additional sensors, add 10kΩ I2C pull-up resistors.
- **NeoPixels** require sufficient 5V power and careful ground alignment.
- Camera should be placed ~2-3 cm from the eyes for consistent detection.

---

## 🧠 How It Works

- Uses Haar cascades (`haarcascade_eye_tree_eyeglasses.xml`) for eye detection
- Detects **blinks longer than 0.6 seconds** as "sleepy"
- Maintains a timestamped queue of sleepy blinks
- If **≥ 3 sleepy blinks in 2 minutes**, triggers a **NeoPixel alert**
- Sends "ALERT" message via socket to remote laptop
- NeoPixel alert resets after 30 seconds

---

## 💻 Software Requirements

- Raspberry Pi OS (bookworm / bullseye recommended)
- Python 3.9+
- Required Python packages:
```bash
pip install opencv-python picamera2 neopixel adafruit-blinka
