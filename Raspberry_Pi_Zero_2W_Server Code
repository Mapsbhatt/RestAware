from picamera2 import Picamera2
import cv2
import socket
import pickle
import struct
import time
import board
import neopixel
import os
import sys
from collections import deque

# Ensure the script is run with sudo
if not os.geteuid() == 0:
    print("This script must be run as root! Use 'sudo python3 <script>'")
    sys.exit(1)

# NeoPixel Configuration
NEO_PIXEL_PIN = board.D18  # GPIO18 for NeoPixel
NUM_PIXELS = 16  # Number of NeoPixel LEDs
BRIGHTNESS = 0.2  # Brightness level (0.0 to 1.0)

# Initialize NeoPixel
pixels = neopixel.NeoPixel(NEO_PIXEL_PIN, NUM_PIXELS, brightness=BRIGHTNESS, auto_write=False)

# Function to control NeoPixel for alert
def trigger_alert():
    for i in range(NUM_PIXELS):
        pixels[i] = (0, 0, 255)  # Set to blue light
    pixels.show()

# Function to reset NeoPixel
def reset_neopixel():
    for i in range(NUM_PIXELS):
        pixels[i] = (0, 0, 0)  # Turn off NeoPixel
    pixels.show()

# Blink detection parameters
blink_start_time = None
blink_threshold = 0.6  # Threshold in seconds for detecting sleepiness
sleepy_blinks = deque()  # Store timestamps of sleepy blinks
alert_blink_threshold = 3  # Number of sleepy blinks required to trigger an alert
alert_time_window = 120  # Time window in seconds (2 minutes)
last_alert_time = None  # Timestamp of the last alert
neopixel_active = False  # Flag to track if NeoPixel is currently active

# Load Haar cascade for eye detection
eyesCascade = cv2.CascadeClassifier("haarcascade_eye_tree_eyeglasses.xml")

# Initialize Picamera2 with OV5647-specific settings
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(
    main={"size": (320, 240)}  # Lower resolution for better performance
))

# Adjust settings to let more light in
picam2.set_controls({
    "FrameDurationLimits": (33333, 33333),  # Lower frame rate (~30 FPS)
    "ExposureTime": 20000,  # Increase exposure time (20ms)
    "AnalogueGain": 4.0    # Amplify signal (gain)
})
picam2.start()

# Set up server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 8485))
server_socket.listen(5)
print("Waiting for connection...")
conn, addr = server_socket.accept()
print(f"Connected to {addr}")

try:
    while True:
        # Capture frame
        frame = picam2.capture_array()

        # Flip the frame
        frame = cv2.flip(frame, -1)  # Flip both horizontally and vertically

        # Convert to grayscale for Haar cascade
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Preprocess the grayscale image (equalize histogram for better IR contrast)
        gray = cv2.equalizeHist(gray)

        # Detect eyes directly
        eyes = eyesCascade.detectMultiScale(
            gray,
            scaleFactor=1.2,  # Larger scale factor for close-up detection
            minNeighbors=3,   # Number of neighbors required for a detection
            minSize=(90, 90)  # Adjust based on close-up eye size
        )

        # Draw rectangles around detected eyes and track blinks
        if len(eyes) > 0:  # Eyes detected
            for (x, y, w, h) in eyes:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (100, 255, 255), 2)

            # End blink tracking if previously started
            if blink_start_time:
                blink_duration = time.time() - blink_start_time
                if blink_duration < blink_threshold:
                    print(f"Normal blink detected. Duration: {blink_duration:.2f} seconds")
                else:
                    print(f"Sleepy blink detected! Duration: {blink_duration:.2f} seconds")
                    sleepy_blinks.append(time.time())  # Add timestamp of sleepy blink
                blink_start_time = None
        else:  # No eyes detected (possible blink)
            if blink_start_time is None:  # Start tracking blink
                blink_start_time = time.time()

        # Remove sleepy blinks older than the alert window
        current_time = time.time()
        while sleepy_blinks and (current_time - sleepy_blinks[0] > alert_time_window):
            sleepy_blinks.popleft()

        # Trigger alert if enough sleepy blinks occur within the time window
        if len(sleepy_blinks) >= alert_blink_threshold:
            if not neopixel_active:  # Only trigger if NeoPixel is not already active
                print(f"ALERT: {len(sleepy_blinks)} sleepy blinks detected in {alert_time_window} seconds!")
                trigger_alert()  # Turn on NeoPixel as alert
                last_alert_time = current_time  # Record alert time
                neopixel_active = True  # Set NeoPixel as active

                # Send alert message to laptop
                alert_message = b"ALERT"
                alert_message = struct.pack("Q", len(alert_message)) + alert_message
                conn.sendall(alert_message)

            sleepy_blinks.clear()  # Reset sleepy blinks after alert

        # Turn off NeoPixel if 30 seconds have passed since the last alert
        if neopixel_active and last_alert_time and (current_time - last_alert_time > 30):
            print("Turning off alert after 30 seconds.")
            reset_neopixel()
            neopixel_active = False  # Reset NeoPixel active state
            last_alert_time = None

        # Compress the frame as JPEG for streaming
        _, encoded_frame = cv2.imencode('.jpg', frame)
        data = pickle.dumps(encoded_frame)
        message = struct.pack("Q", len(data)) + data

        # Send the compressed frame
        conn.sendall(message)
finally:
    # Cleanup resources
    picam2.stop()
    reset_neopixel()  # Ensure NeoPixel is off
    conn.close()
    server_socket.close()
