
import sys
import enum

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer

import yaml

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
        self.btn_specific.clicked.connect(self.triggertest_sendsingle)

        # load port config
        with open('config.yaml', 'r') as f:
            portconfig = yaml.safe_load(f)

        # initialize the port
        self.port = None
        portstatus = 'Not Connected !!'
        if ('output_port' in portconfig) and ('parallel' in portconfig['output_port']):
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

if __name__ == "__main__":
    App = QtWidgets.QApplication(sys.argv)
    window = CLASGUI()
    sys.exit(App.exec())
