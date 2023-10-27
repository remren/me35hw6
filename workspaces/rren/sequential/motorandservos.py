from machine import PWM, Pin
import time

# Setup motors pins as PWM pins to send to motor driver
right_motor_f = PWM(Pin(8))
right_motor_b = PWM(Pin(9))
left_motor_f = PWM(Pin(20))
left_motor_b = PWM(Pin(21))
# TURN EM ALL OFF
left_motor_f.duty_u16(0)
left_motor_b.duty_u16(0)
right_motor_f.duty_u16(0)
right_motor_b.duty_u16(0)

left_motor_f.freq(5000)
left_motor_b.freq(5000)
right_motor_f.freq(5000)
right_motor_b.freq(5000)
on_duty_r = int(65_535)
on_duty_l = int(65_535)

servo_a = PWM(Pin(7))
servo_a.freq(50)
servo_b = PWM(Pin(8))
servo_b.freq(50)
servo_claw = PWM(Pin(9))
servo_claw.freq(50)

def setAngle(angle):
    angle = (int(angle))/30
    angle+=33
    print("angle",angle)
    return int(((angle/180)*8000)+1000)

try:
    while True:
        for i in range(0, 1300 ):
            servo_a.duty_u16(setAngle(i))
            servo_b.duty_u16(setAngle(i))
            servo_claw.duty_u16(setAngle(i))
            right_motor_f.duty_u16(on_duty_l)
            right_motor_b.duty_u16(0)
            left_motor_f.duty_u16(on_duty_l)
            left_motor_b.duty_u16(0)
            time.sleep(0.1)
except KeyboardInterrupt:
    left_motor_f.duty_u16(0)
    left_motor_b.duty_u16(0)
    right_motor_f.duty_u16(0)
    right_motor_b.duty_u16(0)
    print("baller")
