import serial
import time

# open a serial connection
s = serial.Serial("COM6", 115200)

# blink the led
while True:
    # s.write(b"on\n")
    # time.sleep(1)
    # s.write(b"off\n")
    # time.sleep(1)
    s.write(b"i\n")
    test = s.readline()
    print(test)
    time.sleep(0.5)