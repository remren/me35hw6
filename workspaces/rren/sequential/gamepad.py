from machine import Pin, I2C
import struct, time

class Gamepad:
    def __init__(self, i2c_bus=1, scl_pin=27, sda_pin=26, addr=0x50):
        self.i2c = I2C(i2c_bus, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=100000)
        self.addr = addr
        self.last_x, self.last_y, self.last_btn = 0, 0, [False] * 6
        self.BTN_CONST = [1 << 6, 1 << 2, 1 << 5, 1 << 1, 1 << 0, 1 << 16]
        self.current_button = None
        self.BTN_Value = ['x', 'y', 'A', 'B', 'select', 'start']
        self.BTN_Mask = 0
        for btn in self.BTN_CONST:
            self.BTN_Mask |= btn
        self.digital_setup()

    def digital_setup(self):
        cmd = bytearray(4)
        cmd[0:] = struct.pack(">I", self.BTN_Mask)
        buffer = bytearray([0x01, 0x03]) + cmd
        self.i2c.writeto(self.addr, buffer)
        buffer = bytearray([0x01, 0x0B]) + cmd
        self.i2c.writeto(self.addr, buffer)
        buffer = bytearray([0x01, 0x05]) + cmd
        self.i2c.writeto(self.addr, buffer)

    def digital_read(self, delay=0.008):
        buffer = bytearray([0x01, 0x04])
        buf = self.i2c.writeto(self.addr, buffer)
        time.sleep(delay)
        buf = self.i2c.readfrom(self.addr, 4)
        try:
            ret = struct.unpack(">I", buf)[0]
        except OverflowError:
            buf[0] = buf[0] & 0x3F
            ret = struct.unpack(">I", buf)[0]
        return ret & self.BTN_Mask

    def read_joystick(self, pin, delay=0.005):
        reply = self.i2c.writeto(self.addr, bytearray([0x09, 0x07 + pin]))
        time.sleep(delay)
        reply = self.i2c.readfrom(self.addr, 2)
        return struct.unpack('>H', reply)[0]

    def get_joystick_state(self):
        x = 1023 - self.read_joystick(14)
        y = 1023 - self.read_joystick(15)
        buttons = [not self.digital_read() & btn for btn in self.BTN_CONST]

        pressed_buttons = [name for name, btn in zip(self.BTN_Value, buttons) if btn]

        # Update the current_button variable
        if pressed_buttons:
            self.current_button = pressed_buttons[0]
        else:
            # Clear the current_button if no button is pressed
            self.current_button = None

        return x, y, pressed_buttons

    def readbuttons(self):
        x, y, _ = self.get_joystick_state()

        # Check if a new button is pressed or released
        if self.current_button != self.last_btn:
            if self.current_button:
                return self.current_button
            elif self.last_btn:
                return self.last_btn

        # Update the last_btn variable
        self.last_btn = self.current_button
        
    def readstick(self, tolerance=5):
        x, y, _ = self.get_joystick_state()

        if abs(x - self.last_x) > tolerance or abs(y - self.last_y) > tolerance:
            # Print joystick values when they change
            #print(f'Joystick: X={x}, Y={y}')
            self.last_x, self.last_y = x, y
        return [x,y]