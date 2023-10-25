import sys # save as main!
from machine import Pin
import time

led = Pin(0, Pin.OUT)
led_ltp = Pin(1, Pin.OUT)
# led_ltp(1)
led_afp = Pin(2, Pin.OUT)
led_bti = Pin(27, Pin.OUT)
led_bto = Pin(26, Pin.OUT)
# led_afp(1)

def led_on():
    led(1)

def led_off():
    led(0)


while True:
    # read a command from the host
#     v = sys.stdin.readline().strip()

    # perform the requested action
#     if v.lower() == "on":
#         led_on()
#     elif v.lower() == "off":
#         led_off()
        
    led_ltp(0)
    led_afp(0)
    led_bti(0)
    led_bto(0)
    time.sleep(0.4)
    led_ltp(1)
    led_afp(1)
    led_bti(1)
    led_bto(1)
    time.sleep(0.4)
        
    print("hello")
