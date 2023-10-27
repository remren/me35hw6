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
from machine import PWM, Pin

# Setup motors pins as PWM pins to send to motor driver
right_motor_f = PWM(Pin(8))
right_motor_b = PWM(Pin(9))
left_motor_f = PWM(Pin(21))
left_motor_b = PWM(Pin(20))
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

arm_motor_a = PWM(Pin(7))
arm_motor_a.freq(50)

def setAngle(angle):
    angle = (int(angle))/30
    angle+=33
    return int(((angle/180)*8000)+1000)

def main():
    loop = 0 # DEBUG
    bluetooth  = ble_wrapper.BLEWrapper(False, 10)
    bluetooth_success = False
    right_motor_status = 0
    left_motor_status = 0
        
    while True:
        left_motor_f.duty_u16(on_duty_l)
        left_motor_b.duty_u16(0)
        # 1. Constantly look for connection. If no connection, keep searching.
        #		1a. Only move on if connection is successful.
        #		1b. Skip the check if there is an active connection.
        #		1c. (Extra) If time, add an auto-reconnect from idle.
        bluetooth_success = bluetooth.ble_status()
#         print(f"bt_success:{bluetooth_success}") # DEBUG
        if not bluetooth_success:
            bluetooth_success = bluetooth.ble_connect() # ble_connects returns a boolean
            print(f"Successful connection: {bluetooth_success}") # DEBUG
            time.sleep(0.1)
        
        # 2. Read in data from the "antenna" Pico over Bluetooth.
        received_data = bluetooth.ble_read()
#         print(f"received_data:{received_data}, loop:{loop}") # DEBUG
        bluetooth.ble_idle_disconnect(received_data) # Disconnect from idle to allow for reconnect in 1c.
        
        right_motor_f.duty_u16(0)
        right_motor_b.duty_u16(0)
        # 3. Based on that data, change the state of the motors/servos.
            # ADD CODE HERE [10/25/23]
        if received_data is not None:
            inputs = received_data.split(",")
            if len(inputs) <= 9:
                if int(inputs[4]) == 0:
                    right_motor_f.duty_u16(0)
                    right_motor_b.duty_u16(0)
                    right_motor_status = 0
                if int(inputs[4]) == 1:
                    right_motor_f.duty_u16(on_duty_l)
                    right_motor_b.duty_u16(0)
                    right_motor_status = 1
                if int(inputs[5]) == 0:
                    left_motor_f.duty_u16(0)
                    left_motor_b.duty_u16(0)
                    left_motor_status = 0
                if int(inputs[5]) == 1:
                    left_motor_f.duty_u16(on_duty_l)
                    left_motor_b.duty_u16(0)
                    left_motor_status = 1
#                 if inputs[5]:
#                 else:
                    
                print(f"received{inputs}") # DEBUG
                # Act on inputs now that its correct length
            
#         motorservo_states = f"f0,r0,f2,r2,str,a0,a2,claw"
            # ERROR: Currently issue, cannot send too much data in one send operation.
            #		 Maybe in each loop, send less but more frequently? Reduce time.sleep in functions
            #		 But only send states a few at a time. RT Update not super important to dashboard.
            #		 Other fix is to see what send does vs write, and if write could just be send.
#         motorservo_states = '1,0,1,0,360,360,360,360'
#         motorandclaw_states = f"L:{loop % 3},R:{loop % 3},S:{loop % 3 + 360}" # Left Drive State, Right Drive State Servo for Arm
#         armservo_states = f"A:{loop % 3 + 360},B:{loop % 3 + 360}" # Arm Servo A (Base), Arm Servo B (Second)
        motorandclaw_states = f"L:{left_motor_status},R:{right_motor_status}"
        
        # 4. Send data to the "antenna" Pico over Bluetooth, reporting
        #	 the current state of the motors/servos.
        if loop: # on Odd loop iterations
            bluetooth.ble_send(str(motorandclaw_states))
            print(str(motorandclaw_states))
#         else:        # on Even loop iterations
#             bluetooth.ble_send(str(armservo_states))
#             print(str(armservo_states))
                    
#         time.sleep(0.5)
        loop += 1
main()