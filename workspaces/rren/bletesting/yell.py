import time
import ble

LINE = "me mum"

def run():
        try:
            while True:
                yeller()
#                 time.sleep(1)
#                 print("wha")
#             asyncio.run(self.main(runtime)) # runs everything for __ seconds
        except KeyboardInterrupt:
            print('Ctrl+C Interrupted')
        finally:
            print('All set! There will be a clear state now.')
            
def yeller():
    try:
        # any operator is either Yell or Listen
        op = ble.Yell(LINE) # will establish a connecting using the LINE
        if op.connect_up(): # once connection is established, begin send/receive
            while True:
                time.sleep(1)
                op.send("OI MATE")
                print("sent msg")
                if op.is_any(): # read from BLE comms
                    print("read something!")
                    print(op.read())
                    time.sleep(1)
                
                print("about to wait")
                time.sleep(5)
                print("done waiting")
    except Exception as e:
        op.disconnect()
        print(e)

run()