from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5 import QtWidgets, QtGui
from PyQt5 import uic

import hunter

import serial

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
                                self.textBrowserSteer,
                                self.textBrowserArm_0, self.textBrowserArm_2,
                                self.textBrowserServo]

        self.helper = SerialHelper(self.textBrowserList, self.startSerialBtn, self.stopSerialBtn)

        # self.startSerialBtn.setEnabled(True)
        # self.stopSerialBtn.setEnabled(False)
        #
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
            textBrowser.insertPlainText("bonjour bon soir")

        self.thread = None
        self.worker = None

    def report_sensor_data(self, sensors):
        """
        TODO: write contract -- this feels so cursed beyond belief help
        :param n:
        :return: none
        """
        sensor_index = 0
        direction_index = 0
        for textBrowser in self.textBrowserList:
            textBrowser.clear()
            match direction_index:
                case 0:
                    textBrowser.setText(f"{sensors[sensor_index].mag_x}")
                    direction_index += 1
                case 1:
                    textBrowser.setText(f"{sensors[sensor_index].mag_y}")
                    direction_index += 1
                case 2:
                    textBrowser.setText(f"{sensors[sensor_index].mag_z}")
                    direction_index = 0
                    sensor_index += 1
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

            self.worker.sensors_signal.connect(self.report_sensor_data)

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
    sensors_signal = pyqtSignal(list)
    # counter = pyqtSignal(int)

    def setup_serial(self):
        print("setup_serial")
        self.pico = serial.Serial("COM6", 115200)
        self.pico.write(b"join\n")

    def disconnect(self):
        self.pico.write(b"quit\n")

    # def receive_sensor_data(self):
    #     """
    #     TODO: write contract
    #     :return:
    #     """
    #     i = 0
    #     while self.alive is True:
    #         # self.counter.emit(i)
    #         # i += 1
    #         try:
    #             update_sensors_from_serial(self.serial_connection, self.sensors, log)
    #         except RuntimeError as e:
    #             log.warning(str(e))
    #         else:
    #             print_sensors(self.sensors, log)
    #             self.sensors_signal.emit(self.sensors)
    #         # sleep(0.1)
    #     self.finished.emit()

    def receive_sensor_data(self):
        while self.alive is True:
            # self.counter.emit(i)
            # i += 1
            try:
                test = self.pico.readline()
                print(f"from pico:{test}")
            except RuntimeError as e:
                print(str(e))
            # else:
                # print(f"from pico:{test}")
                # self.sensors_signal.emit(self.sensors)
            # sleep(0.1)
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