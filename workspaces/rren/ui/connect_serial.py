"""
    @authors    : alea and casci
    @created    : Sep 5, 2022, 12:04

    @description: Finds and returns the serial port to which a uC is connected.
                  Use find_and_get_serial to open a serial connection with an
                  F232R Serial UART IC. find_mc_serial_port can be used to find
                  alternate ports by Vendor ID (VID) and Product ID (PID).

    @IMPORTANT  : To access correct serial ports on linux, the user may need to
                  add themselves to the dialout group in order to access the
                  correct port. This can be done using the command:
                      sudo usermod -a -G dialout $USER
                  in the terminal. May require reboot to take effect.
"""

import sys
import glob
import serial
import serial.tools.list_ports

from logger import Logger
log = Logger()
log.init_log(level='INFO')

SUPPORTED_BAUD_RATES = [50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400,
                        4800, 9600, 19200, 38400, 57600, 115200]
DEFAULT_BAUD_RATE = 115200

# VID and PID values provided are for F232R Serial UART IC
VID = 0x0403
PID = 0x6001


class UnsupportedBaudRate(Exception):
    """
    Exception raised when an unsupported baud rate has been entered.
    """

    def __init__(self, baud_rate):
        self.baud_rate = baud_rate
        self.error_msg = 'Baud rate {} is not supported'.format(baud_rate)
        super().__init__(self.error_msg)


def find_and_get_serial(baud_rate: int = DEFAULT_BAUD_RATE, timeout: int = 1):
    """
    Wrapper function to be called by user. Takes a baud rate and timeout,
    default timeout set to 1s.
    :param baud_rate: int - Desired baud rate for serial connection or default.
    :param timeout: int - Desired timeout period, default 1s.
    """
    if baud_rate not in SUPPORTED_BAUD_RATES:
        raise UnsupportedBaudRate(baud_rate)

    port_str = find_mc_serial_port_new()

    return serial.Serial(port_str, 115200, timeout=timeout)


def find_mc_serial_port_new(vid: int = VID, pid: int = PID) -> str:
    """
    Finds serial port for device on machine given the device's Vendor ID and
    Product ID. These IDs are intrinsic to each USB product, and can be found
    using lsusb on linux or Get-PnpDevice in PowerShell. Uses PySerial's
    list_ports tool to generate list of serial ports. Raises error if more or
    less than 1 device is found. User may catch exception and loop function
    until only 1 device is connected.
    :param vid: int - Desired device's vendor ID.
    :param pid: int - Desired device's product ID.
    :return: str - Serial port to which the uC is connected.
    """
    ports = serial.tools.list_ports.comports()
    matches = [port for port in ports if port.vid == vid and port.pid == pid]
    if len(matches) > 1:
        raise RuntimeError("Multiple devices found, please remove other devices")
    elif len(matches) < 1:
        raise RuntimeError("Device not found, please ensure device is connected")
    else:
        return matches[0].device


def get_serial_ports():
    """
    Returns the serial ports as a list. For unsupported or unknown platforms,
    it throws EnvironmentError.
    :param: None
    :return: The list of serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = [f'COM{(i + 1)}' for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        # ports = glob.glob('/dev/tty[A-Za-z]*')
        ports = glob.glob('/dev/tty*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    serial_ports = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            serial_ports.append(port)
        except (OSError, serial.SerialException):
            pass
    return serial_ports


def find_mcu_serial_port(serial_ports: list) -> str:
    """
    Finds the serial port string that the microcontroller is connected to. Not
    implemented for platforms other than macOS. Must implement. Issue related
    to this function could be that what happens if two or more devices with a
    string 'tty.usbmodem' are connected. Then which one to choose?
    :param serial_ports: list - List of serial ports available.
    :return: str - Serial port to which the uC is connected.
    """
    ser_port = None
    if sys.platform.startswith('darwin'):
        text_to_search = r'tty.usbmodem'
    elif sys.platform.startswith('linux'):
        text_to_search = r'ttyUSB'
    else:
        text_to_search = r'COM'

    for port in serial_ports:
        if text_to_search in port:
            ser_port = port
    return ser_port


if __name__ == '__main__':
    current_serial_ports = get_serial_ports()
    for num, port in enumerate(current_serial_ports):
        log.info('Serial port #{0}: {1}'.format(num, port))

    port_str = find_mcu_serial_port(current_serial_ports)
    print(port_str)
    log.info('Serial port to be used is {}'.format(port_str))

    exit(0)
