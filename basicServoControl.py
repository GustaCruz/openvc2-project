from gpiozero import Servo
from math import sin,radians
from time import sleep
#importing Pi GPIO to access hardware PWM signals(eliminates jitter)
from gpiozero.pins.pigpio import PiGPIOFactory


#creating factory object for servo
factory = PiGPIOFactory()
servo = Servo(12, min_pulse_width=0.5/1000,max_pulse_width=2.5/1000,pin_factory=factory)


while True:
    servo.min()
    sleep(.5)
    
    servo.mid()
    sleep(.5)
    
    servo.max()
    sleep(.5)
    
