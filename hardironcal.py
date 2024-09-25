import board
import busio
import adafruit_lis3mdl

# Initialize I2C and sensor
i2c = busio.I2C(board.GP5, board.GP4)  
sensor = adafruit_lis3mdl.LIS3MDL(i2c)

x_min, x_max = float('inf'), float('-inf')
y_min, y_max = float('inf'), float('-inf')

while True:
    mag_x, mag_y, _ = sensor.magnetic
    x_min = min(x_min, mag_x)
    x_max = max(x_max, mag_x)
    y_min = min(y_min, mag_y)
    y_max = max(y_max, mag_y)

    print(f"x_min: {x_min}, x_max: {x_max}, y_min: {y_min}, y_max: {y_max}")
