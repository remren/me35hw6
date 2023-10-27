from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5 import QtWidgets, QtGui
from PyQt5 import uic

import hunter

import serial
from time import sleep


class UiMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        """
        Initializes a QMainWindow from the .ui file and sets up the GUI.
        """
        QtWidgets.QMainWindow.__init__(self)
        self.ui = uic.loadUi('roboarmui_v0.1.ui', self)
        self.setWindowTitle("roboarmui_v0.1")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("WindowIcon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)

        self.textBrowserList = [self.textBrowserFWD_0, self.textBrowserREV_0,
                                self.textBrowserFWD_2, self.textBrowserREV_2,
                                self.textBrowserArm_0, self.textBrowserArm_2,
                                self.textBrowserServo,
                                self.textBrowserLogging]

        self.helper = SerialHelper(self.textBrowserList, self.startSerialBtn, self.stopSerialBtn)

        # self.startSerialBtn.setEnabled(True)
        # self.stopSerialBtn.setEnabled(False)

        self.startSerialBtn.clicked.connect(self.helper.start_worker)
        self.stopSerialBtn.clicked.connect(self.helper.stop_worker)

class SerialHelper:
    """
    TODO: write contract
    """
    def __init__(self, text_browser_list, start_btn, stop_btn):

        self.textBrowserList = text_browser_list

        self.start_btn = start_btn
        self.stop_btn = stop_btn

        for textBrowser in self.textBrowserList:
            textBrowser.insertPlainText("n/a")

        self.thread = None
        self.worker = None

    def report_pico_data(self, data):
        """
        TODO: write contract -- this feels so cursed beyond belief help

        Crazy thing, so the parameter, when the function is called, at least in PyQt5, it seems that
        you don't call the funcition like report_pico_data(data). The parameter is passed in through
        the signal the function is connected to. That's why in start_worker, it's:
            self.worker.picodata.connect(self.report_picodata)
                        ^ THIS IS THE SIGNAL WHICH IS PASSED INTO THE FUNCTION AS PARAMETER

        :param n:
        :return: none
        """
        sensor_index = 0
        direction_index = 0
        for textBrowser in self.textBrowserList:
            textBrowser.clear()
            textBrowser.insertPlainText(f"baller:{data}")

    def start_worker(self):
        """
        TODO: write contract
        :return:
        """
        print("calling start_worker")
        if self.worker is None:
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            print("starting thread!")
            self.thread = QThread()
            self.worker = Worker()

            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.receive_sensor_data)

            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)

            self.worker.picodata.connect(self.report_pico_data)

            self.thread.start()

            try:
                self.worker.setup_serial()
            except RuntimeError as e:
                print(str(e))

    def stop_worker(self):
        """
        TODO: write contract
        :return:
        """
        print("calling stop_worker")
        if self.worker is not None:
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            print("exiting thread!")
            self.worker.exit_worker()
            self.worker = None

class Worker(QObject):
    """
    TODO: write contract
    """
    alive = True
    finished = pyqtSignal()
    # sensors_signal = pyqtSignal(list)
    picodata = pyqtSignal(int)
    i = 0

    def setup_serial(self):
        print("setup_serial")
        try:
            self.pico = serial.Serial("COM6", 115200)
            self.pico.write(b"join\n")
        except Exception as e:
            print(e)

    def disconnect(self):
        try:
            self.pico.write(b"quit\n")
        except Exception as e:
            print(e)

    def receive_sensor_data(self):
        while self.alive is True:
            try:
                # incoming_data = self.pico.readline()
                # print(f"from pico:{incoming_data}")
                print(f"i:{self.i}")
                self.picodata.emit(self.i)
                self.i += 1
                sleep(0.1)
            except RuntimeError as e:
                print(str(e))
            # else:
            #     print(f"from pico:{incoming_data}")
                # self.sensors_signal.emit(self.sensors)
        self.finished.emit()

    def exit_worker(self):
        """
        TODO: write contract
        :return:
        """
        print("exiting worker and disconnecting attached pico's BLE!")
        self.disconnect() # Sends signal to Pico to disconnect BLE
        self.alive = False
        self.finished.emit()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = UiMainWindow()
    mainWindow.show()
    sys.exit(app.exec_())