import time
import board
import busio
import adafruit_gps


def read_gps_data(output):

    import serial
    uart = serial.Serial("/dev/serial0", baudrate=9600, timeout=10)
    
    gps = adafruit_gps.GPS(uart, debug=False) # Use UART/pyserial

    # sending message configuration commands to GPS
    gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
    gps.send_command(b"PMTK220,1000")
    last_print = time.monotonic()
    
    while True:
        # setting zero values for lat/lon
        latitude = 0
        longitude = 0

        # update gps and read in lat/lon values
        gps.update()
        latitude = gps.latitude
        longitude = gps.longitude

        
        output.update_gps_data({'lat' : latitude, 'long' : longitude})

        
        
