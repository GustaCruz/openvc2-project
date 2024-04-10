import io
import json
import logging
import os
import socketserver
from http import server
import threading
from threading import Condition
import base64
import libcamera
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep
from bmpReadings import read_sensor_data  # Import the function for reading sensor data
from gpsReadings import read_gps_data  # Import the function for reading GPS data

# Read the crosshair image and encode it to base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_image

# HTML page for the MJPEG streaming demo
CROSSHAIR_IMAGE_PATH = "/home/drewjefferies/Documents/spots/crosshair.png"
CROSSHAIR_IMAGE_BASE64 = encode_image_to_base64(CROSSHAIR_IMAGE_PATH)

PAGE = f"""\
<html>
<head>
<title>Drone FPV feed</title>
<style>
    body, html {{
        margin: 0;
        padding: 0;
        width: 100%;
        height: 100%;
        background-color: black;
        overflow: hidden;
        position: relative;
    }}
    #video-container {{
        width: 100%;
        height: 100%;
        position: relative;
    }}
    #video {{
        width: 100%;
        height: 100%;
        object-fit: contain;
    }}
    #crosshair {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 1; /* Ensure crosshair appears above the video */
    }}
    #sensor-values {{
        position: absolute;
        bottom: 10px;
        left: 10px;
        background-color: rgba(255, 255, 255, 0.7);
        padding: 10px;
        border-radius: 5px;
        z-index: 2; /* Ensure sensor values appear on top of crosshair */
    }}
    #gps-values {{
        position: absolute;
        bottom: 10px;
        right: 10px;
        background-color: rgba(255, 255, 255, 0.7);
        padding: 10px;
        border-radius: 5px;
        z-index: 2; /* Ensure GPS values appear on top of crosshair */
    }}
    #servo-controls {{
        position: absolute;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        background-color: rgba(255, 255, 255, 0.7);
        padding: 10px;
        border-radius: 5px;
        z-index: 2; /* Ensure servo controls appear on top of other elements */
    }}
</style>
</head>
<body>
    <div id="video-container">
        <img id="video" src="stream.mjpg">
        <img id="crosshair" src="data:image/png;base64,{CROSSHAIR_IMAGE_BASE64}" style="width: 50px; height: 50px;"> <!-- Adjust width and height as needed -->
    </div>
    <div id="sensor-values">
        <div id="temp">Temperature: </div>
        <div id="pressure">Pressure: </div>
        <div id="altitude">Altitude: </div>
    </div>
    <div id="gps-values">
        <div id="latitude">Latitude: </div>
        <div id="longitude">Longitude: </div>
    </div>
    <div id="servo-controls">
        <button onclick="moveServo('+5')">+5&deg;</button>
        <button onclick="moveServo('-5')">-5&deg;</button>
        <div id="servo-angle">Servo Angle: </div>
    </div>
<script>
    function moveServo(direction) {{
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "/move_servo?direction=" + direction, true);
        xhr.send();
    }}
    var source = new EventSource('/streamdata');
    source.onmessage = function(event) {{
        var data = JSON.parse(event.data);
        document.getElementById('temp').innerHTML = 'Temperature: ' + data.temp.toFixed(2) + '&deg;C'; // Display temperature with two decimal points
        document.getElementById('pressure').textContent = 'Pressure: ' + data.pressure.toFixed(2) + ' hPa'; // Display pressure with two decimal points
        document.getElementById('altitude').textContent = 'Altitude: ' + data.altitude.toFixed(2) + ' meters'; // Display altitude with two decimal points
        document.getElementById('servo-angle').innerHTML = 'Servo Angle: ' + data.servo_angle.toFixed(2) + '&deg;'; // Display servo angle
    }};
    var gpsSource = new EventSource('/gpsdata');
    gpsSource.onmessage = function(event) {{
        var gpsData = JSON.parse(event.data);
        document.getElementById('latitude').textContent = 'Latitude: ' + gpsData.lat.toFixed(6);
        document.getElementById('longitude').textContent = 'Longitude: ' + gpsData.long.toFixed(6);
    }};
</script>
</body>
</html>
"""

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.sensor_data = None
        self.gps_data = None
        self.servo_angle = None
        self.condition = Condition()
        # Create Servo instance and configure it
        factory = PiGPIOFactory()
        self.servo = Servo(12, min_pulse_width=0.45/1000, max_pulse_width=1.095/1000, pin_factory=factory)
        # Calibrate servo to the initial angle
        self.calibrate_servo()
    
            
    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

    def update_sensor_data(self, data):
        with self.condition:
            self.sensor_data = data
            self.condition.notify_all()

    def update_gps_data(self, data):
        with self.condition:
            self.gps_data = data
            self.condition.notify_all()
            
    def update_camera_angle(self,data):
        with self.condition:
            self.servo_angle = data
            self.condition.notify_all()
    
    def calibrate_servo(self):
    # Look-up table to map servo to correct angle
        self.angle_map_table = {
            # Degrees : Respective Pulse Width Value in microseconds
            0 : 0.45,
            5 : 0.485,
            8 : 0.50,
            10 : 0.525,
            15 : 0.55,
            16 : 0.57,
            17 : 0.575,
            20 : 0.60,
            25 : 0.635,
            30 : 0.675,
            35 : 0.70,
            40 : 0.745,
            45 : 0.77,
            50 : 0.8175,
            55 : 0.85,
            60 : 0.895,
            65 : 0.915,
            70 : 0.95,
            75 : 0.985,
            80 : 1.015,
            85 : 1.05,
            90 : 1.095
        }
        # Set servo to the desired initial angle
        self.servo_angle = 45
        pulse_width = self.angle_map_table.get(self.servo_angle, None)
        if pulse_width is not None:
            self.servo.pulse_width = pulse_width / 1000.0
            sleep(0.5)
            
    def move_servo(self, direction=None):
        if direction:
            # Move the servo by +/- 5 degrees
            if direction == '+5':
                self.servo_angle += 5
            elif direction == '-5':
                self.servo_angle -= 5
            # Limit servo angle within 0 to 90 degrees
            self.servo_angle = max(0, min(self.servo_angle, 90))
        # Map angle to pulse width and move servo
        pulse_width = self.angle_map_table.get(self.servo_angle, None)
        if pulse_width is not None:
            self.servo.pulse_width = pulse_width / 1000.0

# Class to handle HTTP requests
class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # Redirect root path to index.html
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            # Serve the HTML page
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            # Set up MJPEG streaming
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        elif self.path == '/streamdata':
            # Serve sensor data as a stream
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        sensor_data = output.sensor_data
                        servo_angle = output.servo_angle
                    if sensor_data and servo_angle:
                        sensor_data["servo_angle"] = servo_angle
                        self.wfile.write(f"data: {json.dumps(sensor_data)}\n\n".encode())
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        elif self.path == '/gpsdata':
            # Serve GPS data as a stream
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        gps_data = output.gps_data
                    if gps_data:
                        self.wfile.write(f"data: {json.dumps(gps_data)}\n\n".encode())
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        elif self.path.startswith('/move_servo'):
            # Move the servo by a specified angle
            params = self.path.split('?')[1]
            direction = params.split('=')[1]
            output.move_servo(direction)
            self.send_response(200)
            self.end_headers()
        else:
            # Handle 404 Not Found
            self.send_error(404)
            self.end_headers()

# Class to handle streaming server
class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

# Create Picamera2 instance and configure it
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
config["transform"] = libcamera.Transform(hflip=1, vflip=1)
picam2.configure(config)
output = StreamingOutput()
picam2.start_recording(JpegEncoder(), FileOutput(output))

try:
    # Set up and start the streaming server
    address = ('10.0.0.200', 5000)
    server = StreamingServer(address, StreamingHandler)
    
    # Update sensor and GPS data in separate threads
    def update_sensor_data_thread():
        while True:
            output.update_sensor_data(read_sensor_data(output))
    threading.Thread(target=update_sensor_data_thread, daemon=True).start()
    
    def update_gps_data_thread():
        while True:
            read_gps_data(output)
    threading.Thread(target=update_gps_data_thread, daemon=True).start()

    server.serve_forever()
finally:
    # Stop recording when the script is interrupted
    picam2.stop_recording()

