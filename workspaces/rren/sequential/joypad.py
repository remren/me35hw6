# Borrowing from Lydia's code in "Talking in Sentences"

# from https://github.com/adafruit/Adafruit_CircuitPython_seesaw/blob/main/examples/seesaw_gamepad_qt.py

from machine import Pin, I2C
import struct, time
import time

GamePad = 0x50

ADC_BASE = 0x09
ADC_OFFSET = 0x07
GPIO_BASE = 0x01
GPIO_BULK = 0x04
GPIO_DIRCLR_BULK = 0x03
GPIO_PULLENSET = 0x0B
GPIO_BULK_SET = 0x05

BTN_CONST = [1 << 6, 1 << 2, 1 << 5, 1 << 1, 1 << 0, 1 << 16]
BTN_Value = ['x','y','A','B','select','start']
BTN_Mask = 0
for btn in BTN_CONST:
    BTN_Mask |=  btn

class Joypad:
    def __init__(self, i2c_slot, scl_pin, sda_pin):
        self.i2c = I2C(i2c_slot, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=100000)
        print(f"Gamepad Scan:{[hex(i) for i in self.i2c.scan()]}")
        
    def digital_setup(self):
        cmd = bytearray(4)
        cmd[0:] = struct.pack(">I", BTN_Mask)
        buffer = bytearray([GPIO_BASE, GPIO_DIRCLR_BULK]) + cmd
        reply = self.i2c.writeto(GamePad,buffer)
        buffer = bytearray([GPIO_BASE, GPIO_PULLENSET]) + cmd
        reply = self.i2c.writeto(GamePad,buffer)
        buffer = bytearray([GPIO_BASE, GPIO_BULK_SET]) + cmd
        reply = self.i2c.writeto(GamePad,buffer)
        
    def digital_read(self, delay=0.008):
        '''Get the values of all the pins on the "B" port as a bitmask'''
        buffer = bytearray([GPIO_BASE, GPIO_BULK])   
        buf = self.i2c.writeto(GamePad,buffer)
        time.sleep(delay)
        buf = self.i2c.readfrom(GamePad,4)
        try:
            ret = struct.unpack(">I", buf)[0]
        except OverflowError:
            buf[0] = buf[0] & 0x3F
            ret = struct.unpack(">I", buf)[0]
        return ret & BTN_Mask
    
    def get_buttons(self):
        buttons = [not self.digital_read() & btn for btn in BTN_CONST]
        return buttons
    
    def read_joystick(self, pin, delay = 0.008):
        '''Read an analog signal from the game pad - define both the pin and a delay between write and read'''
        reply = self.i2c.writeto(GamePad,bytearray([ADC_BASE, ADC_OFFSET + pin]))
        time.sleep(delay)
        reply = self.i2c.readfrom(GamePad,2)
        return struct.unpack('>H',reply)[0]
    
# test = Joypad(1, 27, 26)
# test.digital_setup()
# while True:
# # digital_read(): 1000 0000 0011 0011 1
# # Index:		  0
# # Info:			  St          XA   YB Sl
#     buttons = [not test.digital_read() & btn for btn in BTN_CONST]
# #     print(buttons)
# #     print(f"X:{buttons[0]}, Y:{buttons[1]}, A:{buttons[2]}, B:{buttons[3]}")
#     print(f"X:{test.read_joystick(14)}, Y:{test.read_joystick(15)} - X:{buttons[0]}, Y:{buttons[1]}, A:{buttons[2]}, B:{buttons[3]}")
#     time.sleep(0.1)
