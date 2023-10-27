import uasyncio as asyncio
import time, sys
import uselect
from machine import Pin

async def sendpc():
    while True:
        print("information!")
        await asyncio.sleep_ms(500)
        
async def readpc():
    led1 = Pin(1, Pin.OUT)
    datafrompc = None
    spoll = uselect.poll()	# Assuming spoll = Select Poll
    spoll.register(sys.stdin, uselect.POLLIN)
    while True:
        # Use of uselect.poll() to make sys.stdin non-blocking!
        # Awesome! https://forum.micropython.org/viewtopic.php?t=7325
        # Need to read further documentation. Polls the stdin stream.
            # Unsure if in this instance poll() goes to timeout as it =0.
        if spoll.poll(0):
            datafrompc = sys.stdin.readline()
        print(f"augh:{datafrompc}")
        if datafrompc is not None:
            led1.on()
        else:
            led1.off()
        datafrompc = None
        await asyncio.sleep_ms(250)

async def main(duration):
    asyncio.create_task(readpc())	# read task
    asyncio.create_task(sendpc())	# send task
    await asyncio.sleep(duration)		# sleeps for duration secs

def run(runtime):
    try:
        print("run")
        asyncio.run(main(runtime)) # runs everything for __ seconds
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        asyncio.new_event_loop()  
        print('All set! There will be a clear state now.')

run(9999)