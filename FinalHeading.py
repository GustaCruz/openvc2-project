import board
import busio
import math
import adafruit_lis3mdl
import time

# Pins
i2c = busio.I2C(board.GP5, board.GP4)

# Initialize LIS3MDL magnetometer
lis3mdl = adafruit_lis3mdl.LIS3MDL(i2c)

# Hard-iron calibration settings (Change values to Magnetic offset values in MotionCal!)
hard_iron = [-32.34, -1.19, 6.25]

# Soft-iron calibration settings (Change these to Magnetic Mapping values from MotionCal!)
soft_iron = [
    [0.993, 0.040, -0.002],
    [0.040, 1.003, -0.009],
    [-0.002, -0.009, 1.006]
]

# Magnetic declination (Already Calculated)
mag_decl = -1.233

def calibrate_magnetometer():
    # Read magnetometer data
    mag_data = lis3mdl.magnetic

    # Apply hard-iron offsets
    hi_cal = [mag_data[0] - hard_iron[0],
              mag_data[1] - hard_iron[1],
              mag_data[2] - hard_iron[2]]

    # Apply soft-iron scaling
    mag_data_calibrated = [
        (soft_iron[0][0] * hi_cal[0] + soft_iron[0][1] * hi_cal[1] + soft_iron[0][2] * hi_cal[2]),
        (soft_iron[1][0] * hi_cal[0] + soft_iron[1][1] * hi_cal[1] + soft_iron[1][2] * hi_cal[2]),
        (soft_iron[2][0] * hi_cal[0] + soft_iron[2][1] * hi_cal[1] + soft_iron[2][2] * hi_cal[2])
    ]

    # Calculate heading
    heading = -1 * (math.atan2(mag_data_calibrated[0], mag_data_calibrated[1]) * 180) / math.pi

    # Apply magnetic declination
    heading += mag_decl

    # Convert heading to 0..360 degrees
    if heading < 0:
        heading += 360

    return heading

while True:
    heading = calibrate_magnetometer()

    # Print heading to console
    print(f"Heading: {heading:.2f}°")

    # Delay for 100 milliseconds
    time.sleep(0.1)
