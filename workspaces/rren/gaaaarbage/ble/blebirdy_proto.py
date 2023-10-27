import ble # This is the file in the same folder, should be uploaded to Pico.
import uasyncio as asyncio
import time


class BLEBirdy: # "Bidirectional" to "Bidir" to "Birdy" lmao i hate myself
    def __init__(self, operation, line="DefaultLine"):
        self.line = line
        self.operation = operation	# operation can either be True or False.
                                    # True => Yell operator, False => Listen operator.
                                    # The operation type does not directly affect their
                                    # functionality.
        self.op = None # op stands for operator, either in Yell or Listen operations
        self.success = False
        
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
            self.op.disconnect()
        
    async def read(self):
        while True:
            print("entered read function")
            if self.op.is_any(): # Read any received BLE comm.
                print(self.op.read())
#                 self.op = self.op.decode()
#                 print(f" >> {self.op}", end='')
            await asyncio.sleep_ms(10)
            
    async def send(self):
        while True:
            print("entered send function")
            if self.operation is True:
                time.sleep(1)
                self.op.send("OI MATE")
            else:
                time.sleep(1)
                self.op.write("NAHHH FACK YOU")
            await asyncio.sleep_ms(10)
            
    async def main(self, duration):
        asyncio.create_task(self.read())			# read task
        asyncio.create_task(self.send())	# send task
        await asyncio.sleep(duration)		# sleeps for duration secs
    
    def run(self, runtime):
        try:
            asyncio.run(self.main(runtime)) # runs everything for __ seconds
        except KeyboardInterrupt:
            print('Interrupted')
        finally:
            asyncio.new_event_loop()  
            print('All set! There will be a clear state now.')

    
