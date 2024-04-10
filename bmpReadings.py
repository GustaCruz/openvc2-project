# bmp388i2c.py
import time
import board
import adafruit_bmp3xx

def read_sensor_data(output):
    i2c = board.I2C()
    bmp = adafruit_bmp3xx.BMP3XX_I2C(i2c)

    bmp.pressure_oversampling = 8
    bmp.temperature_oversampling = 2
    bmp.sea_level_pressure = 1022

    temperature = bmp.temperature
    pressure = bmp.pressure
    altitude = bmp.altitude
    
    # Update sensor data in StreamingOutput
    output.update_sensor_data({'temp': temperature, 'pressure': pressure, 'altitude': altitude})  
 
   
