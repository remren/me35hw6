import ble_wrapper
import time

test = ble_wrapper.BLEWrapper(False)
test.ble_connect()
time.sleep(5)
test.ble_disconnect()