from gpiozero import Servo
from math import sin,radians
from time import sleep
#importing Pi GPIO to access hardware PWM signals(eliminates jitter)
from gpiozero.pins.pigpio import PiGPIOFactory


#creating factory object for servo
factory = PiGPIOFactory()
servo = Servo(12, min_pulse_width=0.45/1000,max_pulse_width=1.095/1000,pin_factory=factory)


#look up table to map servo to correct angle
angle_map_table = {
    #Degrees : Respective Pulse Width Value in microsec
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

#Function maps servo to corrected angle according to PWM lookup table
def map_servo(angle,servo):
    pulse_width = angle_map_table.get(angle,None)
    
    if pulse_width is not None:
        print("Angle: ", angle, "degrees which maps to: ",pulse_width,"us")
        servo.pulse_width = pulse_width / 1000.0
    else:
        print("Angle was not found in lookup table")

while True:
    for angle in range(0,91,5):
        map_servo(angle,servo)
        print("Servo moved to: ", angle, " degrees.")
        print()
        sleep(2)
    sleep(1)

