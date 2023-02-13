from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer

import enum

# serial port
# import serial

# parallel port
from psychopy import parallel


class PortType(enum.Enum):
    SERIAL = 0
    PARALLEL = 1


class CLASGUI(QtWidgets.QMainWindow):

    triggertest_timer = None
    triggertest_state = 0

    def __init__(self):
        super().__init__()

        # load the UI
        uic.loadUi('triggertest.ui', self)

        # bind buttons
        self.btn_sequence.clicked.connect(self.triggertest_start)
        self.btn_stop.clicked.connect(self.triggertest_stop)
        self.btn_max.clicked.connect(self.triggertest_max)

        # serial port
        # self.port = serial.Serial('COM7', baudrate=9600)
        # self.port_type = PortType.SERIAL

        # parallel port
        self.port = parallel.ParallelPort(address=0x3ff8)
        self.port_type = PortType.PARALLEL

        ### Show figure ###
        self.show()

    def triggertest_stop(self):
        # reset timer
        if self.triggertest_timer is not None:
            self.triggertest_timer.stop()
            self.triggertest_timer = None

        # reset trigger test state variable
        self.triggertest_reset()

    def triggertest_sendsingle(self):
        # get value from textbox
        value = int(self.txt_code.text())

        # send trigger
        self.send_trigger(value)
        QTimer.singleShot(100, self.triggertest_reset)

    def triggertest_start(self):
        # reset timer
        if self.triggertest_timer is not None:
            self.triggertest_timer.stop()

        # reset trigger test state variable
        self.triggertest_state = 0

        # start callback timer
        self.triggertest_timer = QTimer(self)
        self.triggertest_timer.timeout.connect(self.triggertest_callback)
        self.triggertest_timer.start(250)
        self.lbl_status.setText('Starting...')

    def triggertest_callback(self):
        if self.triggertest_state > 15:
            self.triggertest_timer.stop()  # type:ignore
            self.triggertest_timer = None
            self.send_trigger(255)
            QTimer.singleShot(100, self.triggertest_reset)

        else:
            pw = self.triggertest_state if (self.triggertest_state < 8) else (
                15 - self.triggertest_state)
            self.triggertest_state += 1
            self.send_trigger(2**pw)

    def triggertest_max(self):
        self.send_trigger(255)
        self.triggertest_state = -2
        QTimer.singleShot(100, self.triggertest_reset)

    def triggertest_reset(self):
        self.triggertest_state = -1
        self.lbl_status.setText('Ready...')

    def send_trigger(self, value: int):
        ''' Send a trigger using specified port interface. '''
        if self.port_type == PortType.SERIAL:
            self.port.write((value).to_bytes(1,
                                             byteorder='little',
                                             signed=False))
        elif self.port_type == PortType.PARALLEL:
            self.port.setData(value)
            QTimer.singleShot(10, lambda: self.port.setData(0))
        else:
            raise(ValueError('Invalid port type'))

        self.lbl_status.setText('Sent {:d}'.format(value))
