import cv2
import socket
import struct
import pickle
from playsound import playsound  # Library to play sound files

# Set up client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.163.157', 8485))  # Replace with your Raspberry Pi's IP address
print("Connected to the server.")

data = b""
payload_size = struct.calcsize("Q")

try:
    while True:
        # Receive the message size
        while len(data) < payload_size:
            packet = client_socket.recv(4 * 1024)
            if not packet:
                raise ConnectionError("Connection closed by the server.")
            data += packet

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q", packed_msg_size)[0]

        # Receive the full frame data
        while len(data) < msg_size:
            packet = client_socket.recv(4 * 1024)
            if not packet:
                raise ConnectionError("Connection closed by the server.")
            data += packet

        # Check if it's an alert signal
        if b"ALERT" in data[:msg_size]:  # Check for the "ALERT" keyword
            print("Sleep alert received!")
            try:
                playsound('/Users/mananbhatt/Downloads/Johns Hopkins University.m4a')  # Play a beep sound (replace with your sound file path)
            except Exception as e:
                print(f"Error playing sound: {e}")  # Handle sound playback errors gracefully
            data = data[msg_size:]  # Remove the alert message from the buffer
            continue

        # Deserialize and decode the frame
        frame_data = data[:msg_size]
        data = data[msg_size:]

        encoded_frame = pickle.loads(frame_data)
        frame = cv2.imdecode(encoded_frame, cv2.IMREAD_COLOR)

        # Display the frame
        cv2.imshow("Stream", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    client_socket.close()
    cv2.destroyAllWindows()