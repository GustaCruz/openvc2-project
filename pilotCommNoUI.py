import board
import busio
import digitalio
import adafruit_rfm69
import adafruit_gps
import RPi.GPIO as GPIO
import time
import dataLogScript
import serial

# Global variables
sentPKT = 0
receivedPKT = 0
missedPKT = 0

# SPI and RFM69 setup
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.D5)
reset = digitalio.DigitalInOut(board.D25)
rfm69 = adafruit_rfm69.RFM69(spi, cs, reset, 915.0)

#GPS uart-usb setup
uart = serial.Serial("/dev/serial0", baudrate=9600,timeout=10)
gps = adafruit_gps.GPS(uart, debug=False)
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
gps.send_command(b"PMTK220,1000")

# Button GPIO pins
button1 = 26
button2 = 19

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(button1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
prev_press = {button1: False, button2: False}

# Servo data
servoAng = 50.00

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

def send_control_data(servo_angle):
    global sentPKT
    controlData = f"{servo_angle}"
    rfm69.send(bytes(controlData, "utf-8"))
    sentPKT += 1
    print(f"Sending servo angle: {servo_angle}\n")

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

def handle_buttons():
    global servoAng, prev_press
    button1_pressed = not GPIO.input(button1)
    button2_pressed = not GPIO.input(button2)
    
    if button1_pressed != prev_press[button1]:
        if button1_pressed:
            servoAng = min(90.00, servoAng + 10.00)
    if button2_pressed != prev_press[button2]:
        if button2_pressed:
            servoAng = max(0.00, servoAng - 10.00)
        
def get_gps_data():
    """ Retrieve GPS data. """
    gps.update()
    if gps.has_fix:
        latitude = round(gps.latitude, 5)
        longitude = round(gps.longitude, 5)
        return str(latitude), str(longitude)
    else:
        return 'NF', 'NF'


## MAIN LOOP ----------------------------
while True:
    handle_buttons()
    pilotLat, pilotLon = get_gps_data()
    send_control_data(servoAng)
    
    #receive packet
    packet_text = receive_packet()
    #check if empty
    if packet_text:
        #split data into array of values
        altStr, latStr, lonStr, angStr, dPressureStr = split_packet(packet_text)
        #check if array is occupied
        if altStr is not None:
            #log data to csv
            dataLogScript.log_data(altStr, latStr, lonStr, pilotLat, pilotLon,
            angStr, dPressureStr, sentPKT, receivedPKT, missedPKT)
