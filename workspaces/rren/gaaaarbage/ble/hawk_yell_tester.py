import blehawk # should be uploaded

test = blehawk.BLEHawk(True, "hello!") # True => Yell operator
tester = False
try:
#     while not tester:
#         tester = test.connect()
#         print(f"Successful connection: {tester}")
    test.run(9999)
except KeyboardInterrupt:
    test.disconnect()
    print('Interrupted, now disconnecting.')
finally:
    print('All set! There will be a clear state now.')

