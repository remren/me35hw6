# This is code for the "antenna" Pico.
# It will communicate both PC <-> Pico and Pico <-> Pico.
#	- PC <-> Pico is done over Serial.
#	- Pico <-> Pico is done over Bluetooth.
# All code will be done in a sequential manner.

"""
    PLAN:
        # 1. Check for data sent over stdin, data from the UI on the PC.
        # 2. Based on data from stdin, connect or disconnect over Bluetooth.
        #		2a. As this is PC <-> Pico, this is the blocking step.
        #		2b. This means, don't move past this step without a successful connection.
        # 3. Once Bluetooth connection is established, read controller data.
        # 		3a. Process controller data (Doug's code?).
        # 4. Send processed controller data over Bluetooth to the "solo" Pico.
        # 5. Receive data about status of motors/servos from "solo" Pico.

"""

import time, sys, uselect
import ble_wrapper, ble

from machine import Pin

import joypad

# gets inputs from control pad, then converts them into simple forms to send?
def get_buttons(device):
    buttons = device.get_buttons()
    return buttons

# A non-blocking check for data from the PC over stdin, using spoll.
def frompc_stdin():
    led_incoming_from_pc = Pin(1, Pin.OUT)
    spoll = uselect.poll()	# Assuming spoll = Select Poll
    spoll.register(sys.stdin, uselect.POLLIN)
    data = ""
    
        # Use of uselect.poll() to make sys.stdin non-blocking!
        # Awesome! https://forum.micropython.org/viewtopic.php?t=7325
        # Need to read further documentation. Polls the stdin stream.
            # Unsure if in this instance poll() goes to timeout as it =0.
    led_incoming_from_pc.on()
    if spoll.poll(0):
        data = sys.stdin.readline()
    led_incoming_from_pc.off()
    return data

def main():
    loop = 0 # DEBUG
    datafrompc = None
    bluetooth  = ble_wrapper.BLEWrapper(True, 50)
    bluetooth_success = False
    
    led_action_from_pc = Pin(2, Pin.OUT)
    
    controller = joypad.Joypad(1, 27, 26) # I2C Line, SCL, SDA
        
    try:
        while True:
            # 1. Check for data sent over stdin, data from the UI on the PC.
            buffer = str(frompc_stdin())
            if len(buffer):
                datafrompc = buffer.strip()
#                 print(f"datafrompc:{datafrompc.strip()}, loop:{loop}") # DEBUG

            # 2. Based on data from stdin, connect or disconnect over Bluetooth.
            #		2a. As this is PC <-> Pico, this is the blocking step.
            #		2b. This means, don't send/read over Bluetooth without a successful connection.
            bluetooth_success = bluetooth.ble_status()
            if (datafrompc == "join") and bluetooth_success is False:
                led_action_from_pc.on()
#                 print("now joining") # DEBUG
                bluetooth_success = bluetooth.ble_connect()
#                 print("After Step 2") # DEBUG
                led_action_from_pc.off()
            elif (datafrompc == "quit") and bluetooth_success is True:
                led_action_from_pc.on()
#                 print("now disconnecting") # DEBUG
                bluetooth.ble_disconnect()
                led_action_from_pc.off()
                
            # 3. Once Bluetooth connection is established, read controller data.
            # 		3a. Process controller data (Doug's code?).
#             controller_data = f"lrastart - {loop}
                            #    X   Y   X Y A B St Sl
#             controller_data = "1024,1024,0,0,0,0,0,0"
            button_data = get_buttons(controller)
            button_string = ""
            for value in button_data:
                if value:
                    button_string = button_string + str(1)
                else:
                    button_string = button_string + str(0)
                button_string = button_string + ','
            controller_data = f"{controller.read_joystick(14)},{controller.read_joystick(15)},{button_string[:-1]}"
            print(controller_data)
            
            # 4. Send processed controller data over Bluetooth to the "solo" Pico.
            bluetooth.ble_send(controller_data)
            
            # 5. Receive data about status of motors/servos from "solo" Pico.
            received_data = bluetooth.ble_read()
            
            # 6. Send data from "solo" Pico to PC via print() statement.
            if received_data is not None:
                print(f"$$${received_data}") # $$$ Will be parsed in the UI.
            
            time.sleep(0.3)
            loop += 1
    except KeyboardInterrupt:
        print("KeyboardInterupt!")
    finally:
        print("All set. Ready for new slate.")
    
main()
    
