import ble # This is the file in the same folder, should be uploaded to Pico.
import uasyncio as asyncio
import time, sys
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
        self.idle_limit = 5  # max number of missed reads allowed
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
            
    async def dcfromidle(self): # disconnects if left idle for too long.
        while True:
            print("dc from idle entered")
            if self.success is True:
                prev_readcount = self.readcount
                await asyncio.sleep(3)
                curr_readcount = self.readcount
                if (prev_readcount == curr_readcount):
                    self.idle_time = self.idle_time + 1
                    print("increase timer")
            if self.idle_time == self.idle_limit and self.success is True:
                print("dc from idle")
                self.disconnect()
                self.idle_time = 0 # if disconnected, reset idle time
                await asyncio.sleep(1)
                while self.success is False:
                    self.connect() # reconnect attempt
                    print(f"Successful connection: {self.success}")
                    await asyncio.sleep_ms(10)
            await asyncio.sleep_ms(10)
        
    async def read(self):
        led_bt_incoming = Pin(27, Pin.OUT)
        led_pc_outgoing = Pin(2, Pin.OUT)
        while True:
            led_bt_incoming.off()
            if self.op.is_any(): # Read any received BLE comm.
                led_bt_incoming.on()
                str_data = self.op.read() # Data from BLE
#                 print(str_data[2:-1])
                self.readcount += 1;
                # now to send it to the PC
                led_bt_outgoing.on()
                print(str_data)
                await asyncio.sleep_ms(20)
                led_bt_outgoing.off()
            await asyncio.sleep_ms(30)
            
    async def send(self):
#         led_bt_outgoing = Pin(26, Pin.OUT)
        while True:
            if self.operation is True:
                self.op.send("test from yell")
            else:
                self.op.write("test from listen")
            await asyncio.sleep_ms(800)
            
    async def main(self, duration):
        asyncio.create_task(self.read())	# read task
        asyncio.create_task(self.send())	# send task
#         asyncio.create_task(self.dcfromidle()) # disconnect if idle task
        await asyncio.sleep(duration)		# sleeps for duration secs
    
    def run(self, runtime):
        try:
            asyncio.run(self.main(runtime)) # runs everything for __ seconds
        except KeyboardInterrupt:
            print('Interrupted')
        finally:
            asyncio.new_event_loop()  
            print('All set! There will be a clear state now.')


