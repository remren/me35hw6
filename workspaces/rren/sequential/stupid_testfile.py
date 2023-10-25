import ble_wrapper
import time

test = ble_wrapper.BLEWrapper(True)
test.ble_connect()
time.sleep(5)
test.ble_disconnect()
