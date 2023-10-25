import ble # This is the file in the same folder, should be uploaded to Pico.
import uasyncio as asyncio
import time, sys, uselect
from machine import Pin

class BLEHawk: # "Bidirectional" to "Bidir" to "Birdy" lmao i hate myself
    def __init__(self, operation, line="DefaultLine"):
        self.line = line
#         self.idle = idle_limit # maximum idle time in seconds, idle is defined by no reads.
        self.operation = operation	# operation can either be True or False.
                                    # True => Yell operator, False => Listen operator.
                                    # The operation type does not directly affect their
                                    # functionality.
        self.op = None # op stands for operator, either in Yell or Listen operations
        self.success = False
        
        self.idle_time  = 0		# time spent idling in seconds
        self.idle_limit = 2  # max number of missed reads allowed
        self.readcount = 0		# keeps track number of read or write functions done.
        
    def connect(self): # Connects one Pico to another Pico
        try:
            # Attempts to connect via bluetooth!
            if self.operation is True:
                self.op = ble.Yell(self.line) # establishes connection using the message in self.line
            else:
                self.op = ble.Listen(self.line) # establishes connection using the message in self.line
            if self.op.connect_up(): # Checks connection, connect_up() is currently blocking, should get around?
                self.success = True
            return self.success
        except Exception as e: # if any error occurs, disconnect if possible
            self.disconnect()
            print(e)
            
    def disconnect(self): # Disconnect the established connection, if possible
        if self.op is not None and self.success is True:
            self.success = False
            self.op.disconnect()
        
    async def read(self):
        led_bt_incoming = Pin(27, Pin.OUT)
        led_pc_outgoing = Pin(2, Pin.OUT)
        while True:
            if self.op is not None:
                if self.op.is_any(): # Read any received BLE comm.
                    led_bt_incoming.on()
                    led_pc_outgoing.on()
                    await asyncio.sleep_ms(25)
                    str_data = self.op.read()
                    led_bt_incoming.off()
                    led_pc_outgoing.off()
                    await asyncio.sleep_ms(25)
                    print(str_data[2:-1]) # SEND TO PC USING THIS PRINT
                    self.readcount += 1;
                
    async def send(self):
        led_bt_outgoing = Pin(26, Pin.OUT)
        while True:
            if self.operation is True and self.op is not None:
                led_bt_outgoing.on()
                await asyncio.sleep_ms(25)
                # Put controller detection stuff here!
                # Then send it!
                self.op.send("OI MATE")
                led_bt_outgoing.off()
                await asyncio.sleep_ms(25)
            else:
                led_bt_outgoing.on()
                await asyncio.sleep_ms(25)
                self.op.write("NAHHH FACK YOU")
                led_bt_outgoing.off()
                await asyncio.sleep_ms(25) 
                
    async def readpc(self):
        led_pc_incoming = Pin(1, Pin.OUT)
        datafrompc = None
        spoll = uselect.poll()	# Assuming spoll = Select Poll
        spoll.register(sys.stdin, uselect.POLLIN)
        while True:
            # Use of uselect.poll() to make sys.stdin non-blocking!
            # Awesome! https://forum.micropython.org/viewtopic.php?t=7325
            # Need to read further documentation. Polls the stdin stream.
                # Unsure if in this instance poll() goes to timeout as it =0.
            print("readpc entered")
            if spoll.poll(0):
                datafrompc = sys.stdin.readline()
            print(f"augh:{datafrompc}")
            await asyncio.sleep_ms(500)
            if datafrompc is not None:
                led_pc_incoming.on()
            else:
                led_pc_incoming.off()
            if datafrompc == "join":
                self.connect()
            if datafrompc == "quit":
                self.disconnect()
            datafrompc = None
            await asyncio.sleep_ms(250)
            
    async def main(self, duration):
        asyncio.create_task(self.read())	# read task
        asyncio.create_task(self.send())	# send task
        asyncio.create_task(self.readpc())  # read from pc usb
        await asyncio.sleep(duration)		# sleeps for duration secs
    
    def run(self, runtime):
        try:
            print("run")
            asyncio.run(self.main(runtime)) # runs everything for __ seconds
        except KeyboardInterrupt:
            print('Interrupted')
        finally:
            asyncio.new_event_loop()  
            print('All set! There will be a clear state now.')


