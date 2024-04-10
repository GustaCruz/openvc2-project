# bmp388i2c.py
import time
import board
import adafruit_bmp3xx

def read_sensor_data(output):
    # create i2c object
    i2c = board.I2C()
    # use i2c object to intialize bmp
    bmp = adafruit_bmp3xx.BMP3XX_I2C(i2c)

    # setting up oversampling and sea level pressure
    # Eventually we will call the weather API code to import a current sea level press. value
    bmp.pressure_oversampling = 8
    bmp.temperature_oversampling = 2
    bmp.sea_level_pressure = 1022
    
    # reading temp, pressure, and altitude
    # we can remove the temp and pressure, don't really need those readings
    temperature = bmp.temperature
    pressure = bmp.pressure
    altitude = bmp.altitude
    
    # Update sensor data in StreamingOutput
    output.update_sensor_data({'temp': temperature, 'pressure': pressure, 'altitude': altitude})  
 
   
