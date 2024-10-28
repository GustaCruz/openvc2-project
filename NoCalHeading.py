import board
import busio
import adafruit_lis3mdl
import math

# Initialize I2C and LIS3MDL sensor
i2c = busio.I2C(board.GP5, board.GP4)
sensor = adafruit_lis3mdl.LIS3MDL(i2c)

def calculate_heading(x, y):
    # Calculate the heading in degrees
    heading = math.atan2(y, x) * (180 / math.pi)
    if heading < 0:
        heading += 360
    return heading

while True:
    mag_data = sensor.magnetic  # Get magnetic data (x, y, z)
    x, y, z = mag_data

    heading = calculate_heading(x, y)
    print(f"Heading: {heading:.2f} degrees")

    time.sleep(0.5)
