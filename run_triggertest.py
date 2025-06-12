
import sys
import enum

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import yaml

class PortType(enum.Enum):
    SERIAL = 0
    PARALLEL = 1


class CLASGUI(QMainWindow):

    triggertest_timer = None
    triggertest_state = 0

    def __init__(self):
        super().__init__()

        # load the UI
        self.setupUi(self)


        # bind buttons
        self.btn_sequence.clicked.connect(self.triggertest_start)
        self.btn_stop.clicked.connect(self.triggertest_stop)
        self.btn_max.clicked.connect(self.triggertest_max)
        self.btn_specific.clicked.connect(self.triggertest_sendsingle)
        self.btn_10triggers.clicked.connect(self.start_10_triggers_every_2min)

        # load port config
        with open('config.yaml', 'r') as f:
            portconfig = yaml.safe_load(f)

        # initialize the port
        self.port = None
        portstatus = 'Not Connected !!'
        if portconfig and ('output_port' in portconfig) and ('parallel' in portconfig['output_port']):
            try:
                # if parallel port is requested in portconfig, use that
                from psychopy import parallel
                self.port = parallel.ParallelPort(address=portconfig['output_port']['parallel']['address'])

                portstatus = f'OK. Parallel @ 0x{portconfig["output_port"]["parallel"]["address"]:x}'
                self.port_type = PortType.PARALLEL

            except Exception as e:
                print('Cannot initialize parallel port')
                print(portconfig['output_port'])

        if self.port is None:
            try:
                # else look for usb trigger interface
                import serial
                import serial.tools.list_ports

                # find ports that match
                comports = serial.tools.list_ports.comports()
                comports = [p for p in comports if p.vid in [9025, 10755, 0x1a86]]

                if len(comports) == 0:
                    raise Exception('No matching ports found')

                if len(comports) > 1:
                    # use pick
                    print('Multiple matching ports found. Please select one:')
                    for i, p in enumerate(comports):
                        print(f'{i}: {p.device} ({p.manufacturer})')
                    port_idx = int(input('Enter port number: '))
                    comports = [comports[port_idx]]

                comstr = comports[0].device

                print(f'Using port {comstr}. ' + comports[0].hwid)
                self.port = serial.Serial(comstr, 9600)

                portstatus = 'OK. Serial @ ' + comports[0].hwid
                self.port_type = PortType.SERIAL

            except Exception as e:
                print('Cannot initialize serial port')
                raise ValueError('No Port found')

        ### Show figure ###
        self.show()

    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(422, 116)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.btn_sequence = QPushButton(self.centralwidget)
        self.btn_sequence.setObjectName(u"btn_sequence")
        self.btn_sequence.setGeometry(QRect(20, 10, 121, 91))
        self.btn_max = QPushButton(self.centralwidget)
        self.btn_max.setObjectName(u"btn_max")
        self.btn_max.setGeometry(QRect(150, 10, 121, 31))
        self.btn_stop = QPushButton(self.centralwidget)
        self.btn_stop.setObjectName(u"btn_stop")
        self.btn_stop.setGeometry(QRect(300, 80, 111, 23))
        self.btn_specific = QPushButton(self.centralwidget)
        self.btn_specific.setObjectName(u"btn_specific")
        self.btn_specific.setGeometry(QRect(150, 80, 121, 23))
        self.txt_code = QLineEdit(self.centralwidget)
        self.txt_code.setObjectName(u"txt_code")
        self.txt_code.setGeometry(QRect(150, 60, 121, 20))
        self.lbl_status = QLabel(self.centralwidget)
        self.lbl_status.setObjectName(u"lbl_status")
        self.lbl_status.setGeometry(QRect(306, 10, 101, 61))
        self.lbl_status.setStyleSheet(u"border: 1px #000 solid; padding: 2px;")
        MainWindow.setCentralWidget(self.centralwidget)

        self.btn_10triggers = QPushButton(self.centralwidget)
        self.btn_10triggers.setObjectName(u"btn_10triggers")
        self.btn_10triggers.setGeometry(QRect(20, 80, 121, 23))
        self.btn_10triggers.setText("10 triggers/2min")

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Trigger Test", None))
        self.btn_sequence.setText(QCoreApplication.translate("MainWindow", u"Send sequence", None))
        self.btn_max.setText(QCoreApplication.translate("MainWindow", u"Send 255", None))
        self.btn_stop.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
        self.btn_specific.setText(QCoreApplication.translate("MainWindow", u"Send number", None))
        self.lbl_status.setText(QCoreApplication.translate("MainWindow", u"Ready...", None))
    # retranslateUi


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

    def start_10_triggers_every_2min(self):
        """Start sending 10 triggers every 2 minutes."""
        self.triggers_sent = 0
        self.max_triggers = 10
        self.trigger_2min_timer = QTimer(self)
        self.trigger_2min_timer.timeout.connect(self.send_periodic_trigger)
        self.trigger_2min_timer.start(2 * 60 * 1000)  # 2 minutes in ms
        self.send_periodic_trigger()  # Send the first trigger immediately

    def send_periodic_trigger(self):
        """Send a trigger and update the count; stop after 10."""
        if self.triggers_sent < self.max_triggers:
            self.send_trigger(255)  # or any value you want
            self.triggers_sent += 1
            self.lbl_status.setText(f'Sent {self.triggers_sent}/{self.max_triggers}')
        else:
            self.trigger_2min_timer.stop()
            self.lbl_status.setText('Done sending 10 triggers.')
        

if __name__ == "__main__":
    App = QApplication(sys.argv)
    window = CLASGUI()
    sys.exit(App.exec_())
