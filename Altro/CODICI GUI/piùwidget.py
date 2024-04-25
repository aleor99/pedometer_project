import sys

import time

import logging

#disconnettere quando si torna indietro


from PyQt5.QtSerialPort import QSerialPort


from PyQt5.QtCore import (
    QObject,
    QThreadPool, 
    QRunnable, 
    pyqtSignal, 
    pyqtSlot
)

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTextEdit,
    QPushButton,
    QComboBox,
    QHBoxLayout,
    QWidget,
)

import serial
import serial.tools.list_ports

#variabili globali:
CONN_STATUS = False
KILL        = False 

# questo non so bene cosa sia 
logging.basicConfig(format="%(message)s", level=logging.INFO)

# definisce il segnale 
class SerialWorkerSignals(QObject):
    device_port = pyqtSignal(str)#port name to which a device is connected
    status = pyqtSignal(str, int)#port name and macro representing the state (0 - error during opening, 1 - success)
    
class SerialWorker(QRunnable): #our parallel thread is a class 
    def __init__(self, serial_port_name): #init method in which we init parent class 
        self.message_received = pyqtSignal(str)
        super().__init__()
        self.port = serial.Serial() 
        self.port_name = serial_port_name
        self.baudrate = 9600 
        self.signals = SerialWorkerSignals()#con questa ho la instance che mi da il nome della porta e lo stato

    @pyqtSlot()
    #decorate a method as a slot 
    def run(self): #are active once we have a Qrunnable object 
        global CONN_STATUS

        if not CONN_STATUS:
            try:
                self.port = serial.Serial(port=self.port_name, baudrate=self.baudrate,
                                        write_timeout=0, timeout=2)#questa apre la porta seriale, seria.Serial sta per: da serial usa Serial         
                if self.port.is_open:
                    CONN_STATUS = True
                    self.signals.status.emit(self.port_name, 1) # status is one of the signal defined inn the self signal 
                    time.sleep(0.01)     # in seconds
            except serial.SerialException:
                logging.info("Error with port {}.".format(self.port_name))#we print error with port 
                self.signals.status.emit(self.port_name, 0)
                time.sleep(0.01)

    @pyqtSlot()
    def send(self, char):#function to send a signle char on the serial port 
        """!
        @brief Basic function to send a single char on serial port.
        """
        try:
            self.port.write(char.encode('utf-8'))
            logging.info("Written {} on port {}.".format(char, self.port_name))
        except:#if it failes 
            logging.info("Could not write {} on port {}.".format(char, self.port_name))
    
   
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
        
    def read_uart(self):
        if self.port.inWaiting():
                packet = self.port.readline()
                packet = packet.decode('utf')
                packet1= packet
                packet1 = packet1.split()
            


################################################################################################################################

class MainWindow(QMainWindow):
    
    def __init__(self):
        self.serial_worker = SerialWorker(None) 

        super(MainWindow, self).__init__()

        self.setWindowTitle("GUI")
        width = 400
        height = 320
        self.setMinimumSize(width, height)

        self.threadpool = QThreadPool()

        self.connected = CONN_STATUS
        self.serialscan()
        self.initUI()


    #####################
    # GRAPHIC INTERFACE #
    #####################
    def initUI(self): 
        button_hlay = QHBoxLayout()
        button_hlay.addWidget(self.com_list_widget)
        button_hlay.addWidget(self.conn_btn)
        button_hlay.addWidget(self.gotochart)
        widget = QWidget()
        widget.setLayout(button_hlay)
        self.setCentralWidget(widget)
        
    ####################
    # SERIAL INTERFACE #
    ####################
    def serialscan(self):
        self.port_text = "" # inizialmente non so come si chiama 
        self.com_list_widget = QComboBox()
        self.com_list_widget.currentTextChanged.connect(self.port_changed)
        
        self.gotochart= QPushButton("Plot",
                                    clicked = self.switch_window)
        self.gotochart.setDisabled(True)

        # Set the location of the button to (50, 50)
        self.gotochart.move(50, 50)
        
        # create the connection button
        self.conn_btn = QPushButton(
            text=("Connect to port {}".format(self.port_text)), 
            checkable=True,
            toggled=self.on_toggle
        )

        # acquire list of serial ports and add it to the combo box
        serial_ports = [
                p.name
                for p in serial.tools.list_ports.comports()
            ]
        self.com_list_widget.addItems(serial_ports)


    ##################
    # SERIAL SIGNALS #
    ##################
    def port_changed(self):
        self.port_text = self.com_list_widget.currentText()
        self.conn_btn.setText("Connect to port {}".format(self.port_text))

    @pyqtSlot(bool)
     
    def on_toggle(self, checked): 
        if checked:
            self.serial_worker = SerialWorker(self.port_text) 
            self.serial_worker.signals.status.connect(self.check_serialport_status)
            self.serial_worker.signals.device_port.connect(self.connected_device)
            self.threadpool.start(self.serial_worker)
        else:
            global KILL
            KILL = True
            self.serial_worker.killed()
            self.com_list_widget.setDisabled(False)
            self.conn_btn.setText(
                "Connect to port {}".format(self.port_text)
            )

    def check_serialport_status(self, port_name, status):
        if status == 0: 
            self.conn_btn.setChecked(False)
        elif status == 1:
            # enable all the widgets on the interface
            self.com_list_widget.setDisabled(True) # disable the possibility to change COM port when already connected
            self.conn_btn.setText(
                "Disconnect from port {}".format(port_name)
            )
            self.send_h()
            self.gotochart.setDisabled(False)
            

    def connected_device(self, port_name):
        logging.info("Port {} closed.".format(port_name))


    def ExitHandler(self): #method called when we press the x, running the kill method 
        global KILL
        KILL = True
        self.serial_worker.killed()

    def switch_window(self):
        self.window2 = Window2()
        self.window2.show()
        self.hide()
        #self.serial_worker.send("h")
        self.send_s("s")
        
        
    def send_h(self):
        self.serial_worker.send('h')
        
    def send_s(self):
        self.serial_worker.send('s')
        
class Window2(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Window 2")
        self.serial_worker = SerialWorker(None) 
        self.MainWindow = MainWindow()

        # Create a main widget to hold the button
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Create a vertical layout for the main widget
        layout = QHBoxLayout()
        main_widget.setLayout(layout)

        # Create a button to switch to the first window
        #btn_stop=QPushButton("Stop plotting", clicked= self.send_s)
        button = QPushButton("Switch to window 1")
        button.clicked.connect(self.switch_window)
        self.value =self.serial_worker.read_uart()
        #self.serial_port.message_received.connect(self.handle_message)
        my_text=QTextEdit(self,
                               acceptRichText=True,
                               lineWrapMode=QTextEdit.FixedColumnWidth,
                               lineWrapColumnOrWidth=50,
                               placeholderText=("The number is: "+str(self.value)),
                               readOnly=True
                               )
        layout.addWidget(my_text)
        layout.addWidget(button)
        layout.addWidget(btn_stop)
    


    def switch_window(self):
        self.window1 = MainWindow()
        self.window1.show()
        self.hide()
        self.MainWindow.conn_btn.setDisabled(True)
    


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window1 = MainWindow()
    window1.show()
    sys.exit(app.exec_())