# This is the code for the "solo" Pico.
# It will handle the motors and servos.
# It will communicate with the "antenna" Pico (PC <-> Pico) via
#	bluetooth, in a sequential manner.

"""
    PLAN:
        # 1. Constantly look for connection. If no connection, keep searching.
        #		1a. Only move on if connection is successful.
        #		1b. Skip the check if there is an active connection.
        #		1c. (Extra) If time, add an auto-reconnect from idle.
        # 2. Read in data from the "antenna" Pico over Bluetooth. Blocking?
        # 3. Based on that data, change the state of the motors/servos.
        # 4. Send data to the "antenna" Pico over Bluetooth, reporting
        #	 the current state of the motors/servos.
    
"""

import ble_wrapper, ble
import time
from machine import Pin

def main():
    loop = 0 # DEBUG
    bluetooth  = ble_wrapper.BLEWrapper(False, 10)
    bluetooth_success = False
        
    while True:
        # 1. Constantly look for connection. If no connection, keep searching.
        #		1a. Only move on if connection is successful.
        #		1b. Skip the check if there is an active connection.
        #		1c. (Extra) If time, add an auto-reconnect from idle.
        bluetooth_success = bluetooth.ble_status()
        print(f"bt_success:{bluetooth_success}") # DEBUG
        if not bluetooth_success:
            bluetooth_success = bluetooth.ble_connect() # ble_connects returns a boolean
            print(f"Successful connection: {bluetooth_success}") # DEBUG        
        
        # 2. Read in data from the "antenna" Pico over Bluetooth.
        received_data = bluetooth.ble_read()
        print(f"received_data:{received_data}, loop:{loop}") # DEBUG
        bluetooth.ble_idle_disconnect(received_data) # Disconnect from idle to allow for reconnect in 1c.
        
        # 3. Based on that data, change the state of the motors/servos.
            # ADD CODE HERE [10/25/23]
#         motorservo_states = f"f0,r0,f2,r2,str,a0,a2,claw"
            # ERROR: Currently issue, cannot send too much data in one send operation.
            #		 Maybe in each loop, send less but more frequently? Reduce time.sleep in functions
            #		 But only send states a few at a time. RT Update not super important to dashboard.
            #		 Other fix is to see what send does vs write, and if write could just be send.
#         motorservo_states = '1,0,1,0,360,360,360,360'
        motorservo_states = '0'
        
        # 4. Send data to the "antenna" Pico over Bluetooth, reporting
        #	 the current state of the motors/servos.
        bluetooth.ble_send(motorservo_states)
        
#         time.sleep(0.5)
        loop += 1
main()
