import sys, time, logging, serial, serial.tools.list_ports
from PyQt5.QtWidgets import *

from PyQt5.QtCore import *
import PyQt5.QtGui as qtg

CONN_STATUS = False
KILL        = False

CHAR_SEND = "c"
CHAR_RISP = "h"

PORT = ""
SENDED=0

logging.basicConfig(format="%(message)s", level=logging.INFO)

class SerialWorkerSignals(QObject):
    device_port = pyqtSignal(str)
    finished = pyqtSignal()
    status = pyqtSignal(str, int)

class SerialWorker(QRunnable):
    def __init__(self, serial_port_name):
        super().__init__()
        self.port = serial.Serial()
        self.port_name = serial_port_name
        self.baudrate = 9600
        self.signals = SerialWorkerSignals()

    @pyqtSlot()
    def run(self): #port_name, baudrate sono definiti in init come arg e kwarg
        global CONN_STATUS
        global SENDED

        if not CONN_STATUS:
            try:
                self.port = serial.Serial(port=self.port_name, baudrate=self.baudrate,
                                        write_timeout=0, timeout=2)                
                if self.port.is_open:
                    CONN_STATUS = True
                    self.signals.status.emit(self.port_name, 1) #Return dello stato di connessione
                    if(SENDED==0):
                        try:
                            SENDED=1
                            self.port.write(CHAR_SEND.encode('utf-8'))
                            logging.info("Written {} on port {}.".format(CHAR_SEND, self.port_name))
                            self.readData()
                        except Exception as e:
                            logging.info("Could not write {} on port {}.".format(CHAR_SEND, self.port_name))
                            print(e)
                    
                    time.sleep(0.01)     
            except serial.SerialException:
                logging.info("Error with port {}.".format(self.port_name))
                self.signals.status.emit(self.port_name, 0) #Return dello stato di errore
                time.sleep(0.01)

    @pyqtSlot()
    def readData(self):
        while True:
            if self.port.inWaiting():
                packet = self.port.readline()
                packet = packet.decode('utf')
                packet1= packet
                packet1 = packet1.split()
                #print(packet[0])
                if(packet1[0]==CHAR_RISP):
                    global PORT
                    PORT=self.port_name
                    self.signals.finished.emit()
                    w.my_label_data.setText(packet)
                else:
                    break

    @pyqtSlot()
    def killed(self):
        global CONN_STATUS
        global KILL

        if KILL and CONN_STATUS:
            self.port.close()
            time.sleep(0.01)
            CONN_STATUS = False
            self.signals.device_port.emit(self.port_name)
            
        KILL = False
        logging.info("Process killed")


class MainWindow(QMainWindow):
    def __init__(self):
        # define worker
        self.serial_worker = SerialWorker(None) #in realtà il worker posso usarlo quando attivo una funzione di lunga durata, oppure in questo caso lo definisco così poi uso serial_worker

        super(MainWindow, self).__init__()

        # title and geometry
        self.setWindowTitle("GUI")
        width = 400
        height = 320
        self.setMinimumSize(width, height)

        # create thread handler
        self.threadpool = QThreadPool()

        self.connected = CONN_STATUS
        self.initUI()
    
    def initUI(self):
        self.connect_btn = QPushButton(text="Connect to Psoc", 
                                       checkable=True,
                                       clicked=self.connected1)

        self.my_label_port = QLabel("No ports here")
        #self.my_label_port(qtg.QFont("Helvetica",20))
        self.my_label_port.setAlignment(Qt.AlignCenter)

        self.my_label_data = QLabel("No data here")
        #self.my_label_port(qtg.QFont("Helvetica",20))
        self.my_label_data.setAlignment(Qt.AlignCenter)

        vlay = QVBoxLayout()
        vlay.addWidget(self.connect_btn)
        vlay.addWidget(self.my_label_port)
        vlay.addWidget(self.my_label_data)
        widget = QWidget()
        widget.setLayout(vlay)
        self.setCentralWidget(widget)
    
    @pyqtSlot(bool)
    def connected1(self, checked):
        if checked:
            self.ports = serial.tools.list_ports.comports()
            self.serialInst = serial.Serial()
            self.portList = []
            for onePort in self.ports:
                self.portList.append(str(onePort))
            
            for port in self.portList:
                port = port.split()
                port = port[0]
                self.serial_worker = SerialWorker(port)
                self.serial_worker.signals.status.connect(self.check_serialport_status)
                self.serial_worker.signals.finished.connect(self.porta)
                self.serial_worker.signals.device_port.connect(self.connected_device)
                self.threadpool.start(self.serial_worker)

        else:
            # kill thread
            global KILL
            KILL = True
            self.serial_worker.killed()
            self.connect_btn.setDisabled(False) # enable the possibility to change port
            self.connect_btn.setText("Connect to Psoc")
            self.my_label_port.setText("No ports here")

    def check_serialport_status(self, port_name, status):
        if status == 0:
            self.connect_btn.setChecked(False)
        elif status == 1:
            #self.my_label_port.setText("The port is {}".format(port_name))
            self.connect_btn.setText("Disconnect from Psoc")
            logging.info("Connected to port {}".format(port_name))

    def porta(self):
        self.my_label_port.setText("The Psoc is connected at port {} ".format(PORT))
        self.serial_worker.readData
        
    
    def connected_device(self, port_name):
        global SENDED
        SENDED=0
        logging.info("Port {} closed.".format(port_name))
        

    def ExitHandler(self):
        global KILL
        KILL = True
        self.serial_worker.killed()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    app.aboutToQuit.connect(w.ExitHandler)
    w.show()
    sys.exit(app.exec_())



