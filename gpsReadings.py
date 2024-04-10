import time
import board
import busio
import adafruit_gps


def read_gps_data(output):
    
    import serial
    uart = serial.Serial("/dev/serial0", baudrate=9600, timeout=10)
    
    gps = adafruit_gps.GPS(uart, debug=False) # Use UART/pyserial
    
    gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
    gps.send_command(b"PMTK220,1000")
    last_print = time.monotonic()
    
    while True:
        latitude = 0
        longitude = 0
        gps.update()
        latitude = gps.latitude
        longitude = gps.longitude
        
        output.update_gps_data({'lat' : latitude, 'long' : longitude})

        
        