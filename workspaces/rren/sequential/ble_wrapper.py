import ble
import time

class BLEWrapper:
    def __init__(self, mode, max_idle_attempts):
        self.bluetooth = None
        self.mode = mode
        self.advertisement_str = "phooey" # What will be broadcast over Bluetooth to begin connection.
        self.bluetooth_success = False    # Indicates a successful Bluetooth connection.
        
        self.bluetooth_data    = ""
        self.prev_bluetooth_data = ""
        self.max_idle_attempts = max_idle_attempts # Maximum number of attempts allowed before disconnect.
        self.idle_attempts     = 0
        self.msg               = ""
        
    # Blocking loop to ensure connection. self.mode is boolean, where
    #	True	=> Yell
    #	False	=> Listen
    # The mode has no major affect on send or receive functionality.
    # Yell and Listen are essentially identical, except that Listen will have
    # its message repeat.
    def ble_connect(self):
        try:
            if self.mode: # True  => Yell
                self.bluetooth = ble.Yell(self.advertisement_str) # Establishes connection by broadcasting advertisement_str
                print("NOTICE: before connect_up() - If you do not pass this message for some time, reconnect Pico.")
            else:         # False => Listen
                self.bluetooth = ble.Listen(self.advertisement_str)
            if self.bluetooth.connect_up(): # Checks connection, connect_up() is blocking.
                self.bluetooth_success = True
        except Exception as e: # If any error occurs, attempt a disconnect.
            self.ble_disconnect()
            print(e)
        return self.bluetooth_success
    
    # Will disconnect any established connection.
    def ble_disconnect(self):
        if self.bluetooth is not None:
            self.bluetooth.disconnect()
            self.bluetooth_success = False
            print("DISCONNECT!")
            self.bluetooth = None
    
    # Returns bluetooth_success, if a Bluetooth connection is presently established.
    def ble_status(self):
        return self.bluetooth_success

    # Reads in any received Bluetooth communication after established connection.
    def ble_read(self):
        if self.bluetooth_success and self.bluetooth.is_any():
            time.sleep_ms(25)
            self.bluetooth_data = self.bluetooth.read()
            return self.bluetooth_data[2:-1] # Parsing leading b' and closing '
        
    # Checks if any new reads have occured. If no reads have occured after a set time,
    # the function will call on ble_disconnect(), allowing for connection to be restablished.
    def ble_idle_disconnect(self, data):
        if data is None and self.bluetooth_success is True:
            self.idle_attempts += 1
            print(f"idle attempts:{self.idle_attempts}") # DEBUG
        else:
            self.idle_attempts = 0
            print("Reset idle attempts!") # DEBUG

        if self.idle_attempts > self.max_idle_attempts:
            self.idle_attempts = 0
            self.ble_disconnect()
    
    # Sends some string to other party in established Bluetooth connection.
    def ble_send(self, msg):
        if self.bluetooth_success:
            if self.mode: # True  => Yell
                time.sleep_ms(100)
                self.bluetooth.send(msg)
                time.sleep_ms(25)
            if self.mode is False:         # False => Listen
                time.sleep_ms(100)	# For some reason, this sleep is ABSOLUTELY VITAL.
                                    # If a NoneType error occurs, it is likey from this
                                    # being too short of a sleep. 600ms seems okay?
                self.bluetooth.write(msg)
                time.sleep_ms(25)


                
