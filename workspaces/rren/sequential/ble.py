import bluetooth
import time
import struct
import micropython

NAME_FLAG = 0x09
SCAN_RESULT = 5
SCAN_DONE = 6
NAME_FLAG = 0x09
ADV_TYPE_UUID128_COMPLETE = 0x07
ADV_IND = 0x00
ADV_DIRECT_IND = 0x01

IRQ_CENTRAL_CONNECT = 1
IRQ_CENTRAL_DISCONNECT = 2
IRQ_GATTS_WRITE = 3
IRQ_GATTS_READ_REQUEST = 4
IRQ_SCAN_RESULT = 5
IRQ_SCAN_DONE = 6
IRQ_PERIPHERAL_CONNECT = 7
IRQ_PERIPHERAL_DISCONNECT = 8
IRQ_GATTC_SERVICE_RESULT = 9
IRQ_GATTC_SERVICE_DONE = 10
IRQ_GATTC_CHARACTERISTIC_RESULT = 11
IRQ_GATTC_CHARACTERISTIC_DONE = 12
IRQ_GATTC_DESCRIPTOR_RESULT = 13
IRQ_GATTC_DESCRIPTOR_DONE = 14
IRQ_GATTC_READ_RESULT = 15
IRQ_GATTC_READ_DONE = 16
IRQ_GATTC_WRITE_DONE = 17
IRQ_GATTC_NOTIFY = 18
IRQ_GATTC_INDICATE = 19

UART_SERVICE_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
UART_RX_CHAR_UUID = bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")
UART_TX_CHAR_UUID = bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")

FLAG_READ = 0x0002
FLAG_WRITE_NO_RESPONSE = 0x0004
FLAG_WRITE = 0x0008
FLAG_NOTIFY = 0x0010

UART_UUID = UART_SERVICE_UUID
UART_TX = (UART_TX_CHAR_UUID, FLAG_READ | FLAG_NOTIFY,)
UART_RX = (UART_RX_CHAR_UUID, FLAG_WRITE | FLAG_WRITE_NO_RESPONSE,)
UART_SERVICE = (UART_UUID,(UART_TX, UART_RX),)


class Listen:   # central
    def __init__(self, name = None, verbose = False): 
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        self._ble.irq(self._irq)
        self.name = name
        self._reset()
        self.buffer_ref = self.buffer  # Allocation occurs here
        self.string = ''
        self.verbose = verbose
        
    def printIt(self, data):
        if self.verbose:
            print(data)

    def _reset(self):
        # Cached name and address from a successful scan.
        self._name = None
        self._addr_type = None
        self._addr = None
        self.addresses = set()
        self._scan_callback = None
        self._conn_callback = None
        self._read_callback = None
        self._notify_callback = None
        self._conn_handle = None
        self._start_handle = None
        self._end_handle = None
        self._tx_handle = None
        self._rx_handle = None
        self.is_connected = False 
        self.scanning = False 
        self.found = False      

    def _irq(self, event, data):
        if event == IRQ_SCAN_RESULT: #check to see if it is a serialperipheral
            if self.uart_scan(data):
                self._ble.gap_scan(None)#stop scanning

        elif event == IRQ_SCAN_DONE:  # close everything
            self.scanning = False
            if self._scan_callback: #if there is a callback, run it then kill it
                if self._addr:
                    # Found a device during the scan (and the scan was explicitly stopped).
                    self._scan_callback(self._addr_type, self._addr, self._name) #run done_scan
                    self._scan_callback = None
                else:
                    # Scan timed out.
                    self._scan_callback(None, None, None)

        elif event == IRQ_PERIPHERAL_CONNECT:  # ask for services
            self.printIt('Connect successful.')
            conn_handle, addr_type, addr = data
            if addr_type == self._addr_type and addr == self._addr:
                self.is_connected = True
                self._conn_handle = conn_handle
                self._ble.gattc_discover_services(self._conn_handle)
    
        elif event == IRQ_PERIPHERAL_DISCONNECT:
            self.printIt('disconnected')
            # Disconnect (either initiated by us or the remote end).
            conn_handle, _, _ = data
            if conn_handle == self._conn_handle:
                # If it was initiated by us, it'll already be reset.
                self._reset()
    
        elif event == IRQ_GATTC_SERVICE_RESULT:  # read the service
            self.printIt('Connected device returned a service.')
            conn_handle, start_handle, end_handle, uuid = data
            if conn_handle == self._conn_handle and uuid == UART_SERVICE_UUID:
                self._start_handle, self._end_handle = start_handle, end_handle
            
        elif event == IRQ_GATTC_SERVICE_DONE:  #ask for characteristics
            self.printIt('Service query complete.')
            if self._start_handle and self._end_handle:
                self._ble.gattc_discover_characteristics(self._conn_handle, self._start_handle, self._end_handle)
            else:
                self.printIt("Failed to find uart service.")
            
        elif event == IRQ_GATTC_CHARACTERISTIC_RESULT:  #check that it has Rx and Tx
            self.printIt('Connected device returned a characteristic.')
            conn_handle, def_handle, value_handle, properties, uuid = data
            if conn_handle == self._conn_handle and uuid == UART_RX_CHAR_UUID:
                self._rx_handle = value_handle
            if conn_handle == self._conn_handle and uuid == UART_TX_CHAR_UUID:
                self._tx_handle = value_handle
        
        elif event == IRQ_GATTC_CHARACTERISTIC_DONE:  #got the info - run the connection callback
            self.printIt('Characteristic query complete.')
            if self._tx_handle is not None and self._rx_handle is not None:
                # We've finished connecting and discovering device, fire the connect callback.
                if self._conn_callback:
                    self._conn_callback()
                else:
                    self.printIt("Failed to find uart rx characteristic.")
        
        elif event == IRQ_GATTC_WRITE_DONE:
            conn_handle, value_handle, status = data
            self.printIt("TX complete")
    
        elif event == IRQ_GATTC_NOTIFY:
            conn_handle, value_handle, notify_data = data
            if conn_handle == self._conn_handle and value_handle == self._tx_handle:
                if self._notify_callback:
                    self._notify_callback(notify_data)
                        
    def uart_scan(self, data):
        addr_type, addr, adv_type, rssi, adv_data = data
        if adv_type in (ADV_IND, ADV_DIRECT_IND) and UART_SERVICE_UUID in self.decode_services(adv_data):
            # Found a potential device, remember it and stop scanning.
            self._addr_type = addr_type
            self._addr = bytes(addr)  # Note: addr buffer is owned by caller so need to copy it.
            name = self.decode_name(adv_data)
            if bytes(addr) not in self.addresses:
                self.addresses.add(bytes(addr))
            if self.name == '':
                self._name = name or "?"
                self.printIt("type: %s, addr: %s, name: %s, rssi: %d"%(addr_type, str(bytes(addr)), self.name, rssi))
            else:
                if self.name == name:  # we found the right one and are done
                    self._name = name
                    self.found = True
                    return True
                else:
                    self._name = name or "?"
                    return False
                    
    def decode_field(self, payload, adv_type):
        i = 0
        result = []
        while i + 1 < len(payload):
            if payload[i + 1] == adv_type:
                result.append(payload[i + 2 : i + payload[i] + 1])
            i += 1 + payload[i]
        return result

    def decode_name(self,payload):
        n = self.decode_field(payload, NAME_FLAG)
        return str(n[0], "utf-8") if n else ""

    def decode_services(self, payload):
        services = []
        ADV_TYPE_UUID16_COMPLETE = (0x3)
        ADV_TYPE_UUID32_COMPLETE = (0x5)
        ADV_TYPE_UUID128_COMPLETE = (0x7)
        try:
            for u in self.decode_field(payload, ADV_TYPE_UUID16_COMPLETE):
                services.append(bluetooth.UUID(struct.unpack("<h", u)[0]))
            for u in self.decode_field(payload, ADV_TYPE_UUID32_COMPLETE):
                services.append(bluetooth.UUID(struct.unpack("<d", u)[0]))
            for u in self.decode_field(payload, ADV_TYPE_UUID128_COMPLETE):
                services.append(bluetooth.UUID(u))
        except:
            pass
        return services

    # Find a device advertising the environmental sensor service.
    def scan(self, callback=None, duration = 2000):
        self._addr_type = None
        self._addr = None
        self.addresses = set()
        self.scanning = True
        self._scan_callback = callback  #where to go when done
        #run for 2 sec, with checking every 30 ms for 30 ms
        return self._ble.gap_scan(duration, 30000, 30000)

    def wait_for_scan(self):
        while self.scanning:
            print('.',end='')
            time.sleep(0.1)

    def stop_scan(self):
        self._addr_type = None
        self._addr = None
        self._scan_callback = None
        self._ble.gap_scan(None)
        self.scanning = False

    # Connect to the specified device (otherwise use cached address from a scan).
    def connect(self, addr_type=None, addr=None, callback=None):
        self._addr_type = addr_type or self._addr_type
        self._addr = addr or self._addr
        self._conn_callback = callback
        if self._addr_type is None or self._addr is None:
            return False
        self._ble.gap_connect(self._addr_type, self._addr)
        return True

    def wait_for_connection(self):
        while not self.is_connected:
            print('.',end='')
            time.sleep(0.1)

    # Disconnect from current device.
    def disconnect(self):
        if not self._conn_handle:
            return
        self._ble.gap_disconnect(self._conn_handle)
        self._reset()

    def connect_up(self):
        self.scan(duration = 5000)
        self.wait_for_scan()
        if self.found:
            self.connect()
            self._notify_callback = self.rx # Set handler for when data is received over the UART.
            self.wait_for_connection()
            return True
        else:
            return False
            
    def rx(self, data):
        micropython.schedule(self.buffer_ref, data)

    def write(self, v, response=False):
        if not self.is_connected:
            return
        return self._ble.gattc_write(self._conn_handle, self._rx_handle, v, 1 if response else 0)
# # I tried copying the send function from class Yell, but it looks like Listen is missing a few
# # things that Yell has.
#     def write(self, data):
#         for conn_handle in self._connections:
#                 self._ble.gatts_notify(conn_handle, self._handle_tx, data)

    def buffer(self, value):
        self.string += str(bytes(value))

    def is_any(self):
        return len(self.string)
        
    def read(self):
        temp = self.string
        self.string = ''
        return temp
#----------------------------------------------------------------------------------------------------------------------------------                
class Yell:  #peripheral
    def __init__(self, name = 'Pico'):
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        # register a UART service
        ((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services((UART_SERVICE,))
        services = [UART_UUID]
        self._connections = set()
        self._write_callback = None 
        self._ble.irq(self._irq)   
        self._write_callback = None  
        self.name = name  
        self.buffer_ref = self.buffer  # Allocation occurs here
        self.string = ''
        print('waiting...')
                
    def advertise(self, callback = None, interval_us=10000):
        self._write_callback = callback
        short = self.name[:8]
        payload = struct.pack("BB", len(short) + 1, NAME_FLAG) + short  # byte length, byte type, value
        value = bytes(UART_UUID)
        payload += struct.pack("BB", len(value) + 1,ADV_TYPE_UUID128_COMPLETE) + value

        self._ble.gap_advertise(interval_us, adv_data=payload)
        
    def stop_advertising(self):
        self._ble.gap_advertise(None)
        
    def _irq(self, event, data):  # Track connections so we can send notifications.
        if event == IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            print("New connection", conn_handle)
            self._connections.add(conn_handle)
            self.stop_advertising() #only have one connection
            
        elif event == IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            print("Disconnected", conn_handle)
            self._connections.remove(conn_handle)
            self._write_callback = None
            
        elif event == IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            value = self._ble.gatts_read(value_handle)
            if value_handle == self._handle_rx and self._write_callback:
                self._write_callback(value)

    def is_connected(self):
        return len(self._connections) > 0
        
    def wait_for_connection(self, timeout = -1):
        start =  time.ticks_ms()
        done = False
        while not done:
            done = self.is_connected()
            if not done and timeout >= 0:
                done = (time.ticks_ms()-start) >= timeout
            time.sleep(0.1)
        return self.is_connected()
        
    def disconnect(self):
        for conn_handle in self._connections:
            self._ble.gap_disconnect(conn_handle)
            
    def connect_up(self, timeout = -1):
        self.advertise(self.rx)
        success = self.wait_for_connection(timeout)
        self.stop_advertising()
        return success
    
    def rx(self, data):
        micropython.schedule(self.buffer_ref, data)

    def send(self, data):
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._handle_tx, data)

    def buffer(self, value):
        self.string += str(bytes(value))

    def is_any(self):
        return len(self.string)
        
    def read(self):
        temp = self.string
        self.string = ''
        return temp
        
def heard(data):
    print(str(bytes(data)))

# def action(mode = 'P'): 
#     if mode == 'P':
#         try:
#             p = Yell('Fred')
#             if p.():
#                 time.sleep(2)
# 
#                 p.send("test from p")
#                 if p.is_any():
#                     print(p.read())
#                 time.sleep(1)
#         except Exception as e:
#             print(e)
#         finally:
#             print('closing up yell')
#             p.disconnect()
#     else:    
#         try:   
#             L = Listen('Fred')
#             if L.connect_up():
#                 time.sleep(4)
#                 print(L.read())
#                 L.write('test from l')
#                 time.sleep(20)
#                 print(L.is_any())
#                 print(L.read())
#         except Exception as e:
#             print(e)
#         finally:
#             print('closing up listen')
#             L.disconnect()
