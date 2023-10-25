# Heavily inspired from the brilliance of Julia and Chris
import gamepad
import mqtt
import time
import wifi_connect
from secrets import Tufts_Wireless as wifi

mygamepad = gamepad.Gamepad()

direction = 'STP'
xpos = 0
turning = False

def whenCalled(topic, msg):
    print((topic.decode(), msg.decode()))
    time.sleep(.1)

def MQTTConnect():
    try:
        global client
        client = mqtt.MQTTClient('VroomControl', '10.243.82.33', keepalive=1000)
        client.connect()
        print("We are in! Hello MQTT Broker...")
        #client.set_callback(whenCalled)
    except OSError as e:
        print('Failed')
        

def handle_movement(direction_x, direction_y,xpos,turning):
    default_speed = 100
    stick = mygamepad.readstick()
    if stick != None:
        xpos = round(((stick[0] - 523)/100),0)
		#if statments below assess direction based on joystick threshold of (x, y < 505) and (x, y > 525) 
    if direction_y > 525 and (direction_x > 505 and direction_x < 525): #forwards
        rspeedmod = 1
        lspeedmod = 1
        turning = False
    elif direction_y < 505 and (direction_x > 505 and direction_x < 525): #backwards
        rspeedmod = -1
        lspeedmod = -1
        turning = False
    elif direction_x > 525 and (direction_y > 505 and direction_y < 525): #right
        rspeedmod = -1
        lspeedmod = 1
        turning = True
    elif direction_x < 505 and (direction_y > 505 and direction_y < 525): #left
        rspeedmod = 1
        lspeedmod = -1
        turning = True
    else:
        rspeedmod = 0
        lspeedmod = 0
        turning = False
    if turning == True:
        if xpos>0:
            rspeedmod2 = 1-(abs(xpos)/7)
            lspeedmod2 = 1
        elif xpos<0:
            lspeedmod2 = 1-(abs(xpos)/7)
            rspeedmod2 = 1
        else:
            lspeedmod2 = 1
            rspeedmod2 = 1
    else:
        rspeedmod2 = 1
        lspeedmod2 = 1
    rspeed = int(default_speed*rspeedmod*rspeedmod2)
    lspeed = int(default_speed*lspeedmod*lspeedmod2)
    #print(lspeed,rspeed)
    return direction,xpos,turning,lspeed,rspeed

def main():
    buttonread = mygamepad.readbuttons()
    buttondictionary = {'x': 'FWD', 'B': 'BWD','A': 'RSPIN','y': 'LSPIN'}
    direction = buttondictionary.get(buttonread, 'STP')
    curr_xy = mygamepad.get_joystick_state()
    direction_x = curr_xy[0]
    direction_y = curr_xy[1]
    vals = handle_movement(direction_x, direction_y, xpos,turning)
    lspeed = vals[3]
    rspeed = vals[4]
    print("LSPEED = %s"% (lspeed*-1), "RSPEED = %s" %rspeed)
    time.sleep(1)
    client.publish('joystick_left',str(lspeed))
    client.publish('joystick_right',str(rspeed))
    
MQTTConnect()
while True:
    main()