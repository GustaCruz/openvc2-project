import board
import busio
import digitalio
import adafruit_rfm69
import RPi.GPIO as GPIO
import time
import weatherAPI
import dataLogScript

# Global variables
sentPKT = 0
receivedPKT = 0
missedPKT = 0

# SPI and RFM69 setup
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.D5)
reset = digitalio.DigitalInOut(board.D25)
rfm69 = adafruit_rfm69.RFM69(spi, cs, reset, 915.0)

# Button GPIO pins
BUTTON1_PIN = 26
BUTTON2_PIN = 19

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Servo and weather data
servoAng = 50.00
apiPressure = None
pressure = None
lastCall = time.time()
apiCalled = False

#global variables for drone lat/lon
latStr = None
lonStr = None

# Packet processing functions
def split_packet(packet_text):
    values = packet_text.split("+")
    if len(values) == 5:
        return values
    else:
        print("Packet is corrupted, discarding")
        global missedPKT
        missedPKT += 1
        return [None] * 5

def send_control_data(servo_angle, pressure):
    global sentPKT
    controlData = f"{servo_angle}+{pressure}"
    rfm69.send(bytes(controlData, "utf-8"))
    sentPKT += 1
    print(f"Sending servo angle: {servo_angle}, pressure: {pressure}\n")

def receive_packet():
    global receivedPKT, missedPKT
    packet = rfm69.receive(timeout=0.1)
    if packet is None:
        return None
    try:
        packet_text = packet.decode('utf-8')
        receivedPKT += 1
        return packet_text
    except UnicodeDecodeError:
        missedPKT += 1
        return None

def update_pressure():
    global apiPressure, pressure, lastCall, apiCalled, latStr, lonStr
    currentTime = time.time()
    if (currentTime - lastCall) >= 10:
        if (latStr is not None) & (latStr != 'NF'):
            lastCall = currentTime
            apiPressure = weatherAPI.main(latStr, lonStr)
            if apiPressure is not None:
                pressure = apiPressure
                apiCalled = True

def handle_buttons():
    global servoAng
    button1_pressed = not GPIO.input(BUTTON1_PIN)
    button2_pressed = not GPIO.input(BUTTON2_PIN)
    if button1_pressed:
        servoAng = min(90.00, servoAng + 10.00)
    if button2_pressed:
        servoAng = max(0.00, servoAng - 10.00)


## MAIN LOOP ----------------------------
while True:
    handle_buttons()
    update_pressure()
    send_control_data(servoAng, pressure)
    
    packet_text = receive_packet()
    if packet_text:
        altStr, latStr, lonStr, angStr, dPressureStr = split_packet(packet_text)
        if altStr is not None:
            dataLogScript.log_data(altStr, latStr, lonStr, angStr, pressure, dPressureStr, sentPKT, receivedPKT, missedPKT)
            if apiCalled == False:
                if (latStr is not None) & (latStr != 'NF'):
                    lastCall = time.time()
                    apiPressure = weatherAPI.main(latStr, lonStr)
                    if apiPressure is not None:
                        pressure = apiPressure
                        apiCalled = True


