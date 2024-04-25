import sys, time, logging, serial, serial.tools.list_ports
from PyQt5.QtWidgets import *

from PyQt5.QtCore import *
import PyQt5.QtGui as qtg
import time
import pyqtgraph as pg
from pyqtgraph import PlotWidget
from math import remainder

CONN_STATUS = False
KILL        = False
PORT        = ""

CHAR_SEND_ID    = "c"
CHAR_SEND_DATA  = "s"
CHAR_RISP       = "h"
CHAR_PAUSA      = "p"
FLAG_DRAW       = False

PORT = ""

lista_X = []
lista_Y = []
lista_Z = []
tempo = []
c = 0
t = 0
sample_x = 0
min_range = 0
max_range = 1
TIME_PSOC=0.02
RISOLUZIONE = 2000

# Definizione di variabili per il conteggio dei passi
num_steps = 0
x_filtered_list=[]
y_filtered_list=[]
z_filtered_list=[]
accelerazione_list=list()
max_x=0
min_x=0
max_y=0
min_y=0
max_y=0
min_z=0
max_z=0

list_serial_worker=[]

THRESHOLD=800
STEP_THRESHOLD=200


flag=0
first_cross=0
last_cross=0
last_x=0
list_serial=[]

###opz 2
threshold = 1000
massimo=0
minimo=0
totave=[]
acc=0
#commento



logging.basicConfig(format="%(message)s", level=logging.INFO)

#Andiamo a definire quali segnali emetterà il mio thread quando finisce di svolgere un'operazione
#   1. device_port: una volta che la connessione è stata effettuata ed è stata definita 
#                   la porta in maniera automatica, il thread mi manda il nome della porta
#   2. satus: utile per verificaro lo stato della connessione
class SerialWorkerSignals(QObject):
    device_port = pyqtSignal(str)
    founded = pyqtSignal(bool, str)
    answer = pyqtSignal(str)
    packetto2 = pyqtSignal(str)
    status = pyqtSignal(str, int)

#WORKER
class SerialWorker(QRunnable):
    #Inizializza la comunicazione seriale definendo il serial, il nome della porta, baudrate e quali segnali deve trasmettere (definiti prima)
    def __init__(self, serial_port_name):
        super().__init__()
        self.port_serial = serial.Serial()
        self.port_name = serial_port_name
        self.baudrate = 9600
        self.signals = SerialWorkerSignals()

    @pyqtSlot()
    def run(self): #port_name, baudrate sono definiti in init come arg e kwarg
        global CONN_STATUS
        if not CONN_STATUS:
            try:
                self.port_serial = serial.Serial(port=self.port_name, baudrate=self.baudrate,
                                        write_timeout=0, timeout=2)                
                if self.port_serial.is_open:
                    CONN_STATUS = True
                    self.signals.status.emit(self.port_name, 1)
                    self.send(CHAR_SEND_ID)
                    self.reaD()
                    time.sleep(0.01)     
            except serial.SerialException as e:
                    print(e)
                    logging.info("Error with port {}.".format(self.port_name))
                    self.signals.status.emit(self.port_name, 0)
                    time.sleep(0.01)
    
    @pyqtSlot()
    def send(self, char):
        global FLAG_DRAW, PORT, KILL
        try:
            if char==CHAR_SEND_DATA and self.port_name==PORT:
                self.port_serial.write(char.encode('utf-8'))
                logging.info("Written {} on port {}.".format(char, self.port_name))
                w.label_data.setText("Acquiring Data . . .")
                w.label_data.setStyleSheet("color: Green")
                w.data_btn.setDisabled(True)
                FLAG_DRAW = True
            elif char==CHAR_SEND_DATA and self.port_name!=PORT:
                self.killed()
            else:
                self.port_serial.write(char.encode('utf-8'))
                logging.info("Written {} on port {}.".format(char, self.port_name))

        except Exception as e:
            logging.info("Could not write {} on port {}.".format(char, self.port_name))
            print(e)


    def reaD(self):
        #print(self.port_serial.in_waiting)
        global KILL, num_steps
        try:
            while True:
                if self.port_serial.in_waiting != 0 and KILL == False:
                    self.packet = self.port_serial.readline()
                    self.packet = self.packet.decode('utf-8')
                    packet1=self.packet.split()
                    #print(self.packet)
                    if packet1[0] == CHAR_RISP:
                        self.signals.founded.emit(True, self.port_name)
                        logging.info("Answer {} on port {}.".format(self.packet, self.port_name))
                        self.packet=""
                    else:
                        #logging.info("Answer {} on port {}.".format(self.packet, self.port_name))
                        self.signals.packetto2.emit(self.packet)
                        self.packet=""
                elif KILL == True:
                    self.packet=""
                    w.label_data.setText("No data here")
                    break
        except Exception as e:
            w.label_data.setText("No data here")
            w.label_port.setText("Connection Lost")
            time.sleep(0.5)
            print(e)
            self.killed()

    

    def aggiorna_grafico(self, packet):
        global c, t, TIME_PSOC, FLAG_DRAW
        #print(packet)
        if CONN_STATUS:
            packet = packet.split()
            #print(packet)
            if packet[0] == 'Accx':
                lista_X.append(int(packet[2]))
                c+=1
            elif packet[0] == 'Accy':
                lista_Y.append(int(packet[2]))
                c+=1
            elif packet[0] == 'Accz':
                lista_Z.append(int(packet[2]))
                c+=1
            else:
                lista_X.append(0)
                #self.killed()
                pass

            #print(c)
            conteggio = remainder(c,3)
            #print(isinstance(conteggio,int))
            if conteggio==0:
                if FLAG_DRAW == True:
                    t+=TIME_PSOC
                    tempo.append(t)
                    #print(lista_X)
                    self.plot()   
    
    def plot(self):
        global max_range, min_range, TIME_PSOC, sample_x
        self.calcola_step()
        w.graphWidgetX.clear()
        w.graphWidgetY.clear()
        w.graphWidgetZ.clear()
        #print(tempo[len(tempo)-1])
        if tempo[len(tempo)-1] >= 1:
            min_range+=TIME_PSOC
            max_range+=TIME_PSOC
        w.graphWidgetX.setXRange(min_range, max_range, padding=0)
        w.graphWidgetY.setXRange(min_range, max_range, padding=0)
        w.graphWidgetZ.setXRange(min_range, max_range, padding=0)
        w.graphWidgetACC.setXRange(min_range, max_range, padding=0)
        pen = pg.mkPen(color='r', style=Qt.DotLine)
        pen_f = pg.mkPen(color='k')
        pen1 = pg.mkPen(color='g', style=Qt.DotLine)
        pen2 = pg.mkPen(color='b', style=Qt.DotLine)
        w.graphWidgetX.plot(tempo, lista_X, name="Acc X [mg]", pen=pen)
        w.graphWidgetX.plot(tempo, x_filtered_list, name="X filtered", pen=pen_f)
        w.graphWidgetY.plot(tempo, lista_Y, name="Acc Y [mg]", pen=pen1)
        w.graphWidgetY.plot(tempo, y_filtered_list, name="Y filtered", pen=pen_f)
        w.graphWidgetZ.plot(tempo, lista_Z, name="Acc Z [mg]", pen=pen2)
        w.graphWidgetZ.plot(tempo, z_filtered_list, name="Z filtered", pen=pen_f)
    
    def calcola_step(self):
        global lista_X,lista_Y,lista_Z, max_x,min_x,max_y,min_y,max_z,min_z,x_filtered_list,y_filtered_list,z_filtered_list, tempo
        # Calibrazione iniziale dell'accelerometro
        '''
        if lista_X[len(lista_X)-1] < min_x:
            min_x = lista_X[len(lista_X)-1]
        if lista_X[len(lista_X)-1] > max_x:
            max_x = lista_X[len(lista_X)-1]

        if lista_Y[len(lista_Y)-1] < min_y:
            min_y = lista_Y[len(lista_Y)-1]
        if lista_Y[len(lista_Y)-1] > max_y:
            max_y = lista_Y[len(lista_Y)-1]

        if lista_Z[len(lista_Z)-1] < min_z:
            min_z = lista_Z[len(lista_Z)-1]
        if lista_Z[len(lista_Z)-1] > max_z:
            max_z = lista_Z[len(lista_Z)-1]
        
        x_offset = (max_x + min_x) / 2
        y_offset = (max_y + min_y) / 2
        z_offset = (max_z + min_z) / 2
        '''
        
        x_offset = sum(lista_X) / len(lista_X)
        y_offset = sum(lista_Y) / len(lista_Y)
        z_offset = sum(lista_Z) / len(lista_Z)
        
        # Lettura dell'accelerazione dal sensore
        x=lista_X[len(lista_X)-1]
        y=lista_Y[len(lista_Y)-1]
        z=lista_Z[len(lista_Z)-1]
        x_filtered = (x - x_offset)
        y_filtered = (y - y_offset)
        z_filtered = (z - z_offset)

        x_filtered_list.append(x_filtered)
        y_filtered_list.append(y_filtered)
        z_filtered_list.append(z_filtered)  

        import math

        global THRESHOLD,STEP_THRESHOLD, num_steps, tempo, accelerazione_list, acc, totave, flag, massimo, minimo

        accelerazione = math.sqrt(x_filtered**2+y_filtered**2+z_filtered**2)
        accelerazione_list.append(accelerazione)

        w.graphWidgetACC.clear()
        pen3 = pg.mkPen(color='c')
        w.graphWidgetACC.plot(tempo, accelerazione_list, name="Accelerazione", pen=pen3)
        
        
        '''
        ###ALGORITMO 1: NON USA ACCELERAZIONE TOTALE###
        Funzionamento: Questo algoritmo permette una rilevazione del primo campione di salita e ultimo campione di discesa
        In particolare viene applicato il metodo della derivata, cioè l'algoritmo compara di volta in volta due campioni successivi
        dal momento in cui il segnale supera la threshold. Vengono salvati il primo campione di salita, con il tempo in cui è avvenuto
        il superamento, e l'ultimo campione di discesa nel momento in cui si ha una pendenza negativa e si supera la threshold. Successivamente
        si calcola il tempo che si è impiegato a svolgere il potenziale passo e se questo tempo sura dai 0,15 s a 2 s allora il passo viene contato
        '''

        '''
        global last_x, first_cross, last_cross, flag
        if x_filtered > STEP_THRESHOLD or x_filtered < -STEP_THRESHOLD:
                last_x=x_filtered
                if flag == 0:
                    first_cross=tempo[len(tempo)-1]
                    flag=1
            
        if x_filtered < last_x and x_filtered < STEP_THRESHOLD and flag==1:
                last_cross=tempo[len(tempo)-1]
                flag=0
                if (last_cross-first_cross) >= 0.15 and (last_cross-first_cross) <= 2:
                        num_steps+=1
                        last_x=0
                        print(num_steps)
                else:
                    last_x=0
        '''

        '''
        ALGORITMO 2, UTILIZZA ACCELERAZIONE TOTALE (QUINDI PRENDE SEMPRE L'ASSE CON LA MAGGIORE ESCURSIONE)
        FUNZIONAMENTO: Una volta ottenuti i tre dati filtrati, viene calcolato l'avarage value dei 3 assi (Max+Min)/2 (dynamic threshold level)
        e questa threshold viene utilizzata per discriminare il passo. mentre si corre l'accelerometro potrebbe assumere qualsiasi orientamento,
        quindi questo approccio utilizza l'asse la cui accelerazione varia maggiormente. Step eseguiti:
        1. Calibrazione e ottenimento dati filtrati
        2. Calcolo del vettore totale di accelerazione
        3. comparazione tra l'average value e la threshold
        4. se il vettore di accelerazione supera la threshold, il passo viene contato
        '''
        
        if len(accelerazione_list)>=10:
            for i in range(1,10):
                acc+=accelerazione_list[len(accelerazione_list)-i]
            totave.append(acc/10)
            #massimo = max(accelerazione_list)
            #minimo = min(accelerazione_list)
            #totave.append((massimo+minimo)/2)
            #print(totave[len(totave)-1])
            if totave[len(totave)-1] > threshold and flag==0:
                    num_steps+=1
                    w.label_passi.setText("Numero passi acquisiti: {}".format(num_steps))
                    self.send("z")
                    flag=1
            elif totave[len(totave)-1] > threshold and flag==1:
                    pass
            if totave[len(totave)-1]<threshold and flag==1:
                    flag=0
            if num_steps<0:
                    num_steps=0
        

        
    @pyqtSlot()
    def killed(self):
        global CONN_STATUS, KILL, tempo, t, c, lista_X, lista_Y, lista_Z, min_range, max_range, num_steps, last_peak,last_valley,last_peak_val,last_valley_val, tempo, accelerazione_list, tempo_acc, tempo_acc_list, max_x,min_x,max_y,min_y,max_z,min_z,x_filtered_list,y_filtered_list,z_filtered_list, acc
        if KILL and CONN_STATUS:
            self.send(CHAR_PAUSA)
            #self.port_serial.close()
            tempo = []
            t=0
            c=0
            lista_X = []
            lista_Y = []
            lista_Z = []
            min_range = 0
            max_range = 1
            num_steps = 0
            x_filtered_list=[]
            y_filtered_list=[]
            z_filtered_list=[]
            accelerazione_list=[]
            max_x=0
            min_x=0
            max_y=0
            min_y=0
            max_y=0
            min_z=0
            max_z=0
            acc=0
            last_peak = 0
            last_valley = 0
            last_peak_val = 0
            last_valley_val = 0
            tempo_acc=0
            tempo_acc_list=[]
            w.graphWidgetX.clear()
            w.graphWidgetY.clear()
            w.graphWidgetZ.clear()
            w.graphWidgetACC.clear()
            w.label_port.setStyleSheet("color: Red")
            w.label_data.setStyleSheet("color: Red")
            w.label_passi.setText(" ")
            time.sleep(0.01)
            CONN_STATUS = False
            self.signals.device_port.emit(self.port_name)
            
        KILL = False
        logging.info("Process killed")

#MAIN WINDOW
class MainWindow(QMainWindow):
    def __init__(self):
        # define worker
        self.serial_worker = SerialWorker(None)

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
        self.graphWidgetX = PlotWidget()
        self.graphWidgetY = PlotWidget()
        self.graphWidgetZ = PlotWidget()
        self.graphWidgetACC = PlotWidget()
        self.search_btn = QPushButton(text="Search Psoc",
                                      checkable = True,
                                      toggled = self.search
                                      )
        self.data_btn = QPushButton(text="Obtain data from Psoc",
                                    clicked = self.data
                                    )
        self.data_btn.setDisabled(True)
        
        self.label_port = QLabel (text="No port here")
        self.label_port.setFont(qtg.QFont("Helvetica",15, qtg.QFont.Bold))
        self.label_port.setStyleSheet("color: Red")
        self.label_port.setAlignment(Qt.AlignCenter)
        
        self.label_data = QLabel (text="No data here")
        self.label_data.setFont(qtg.QFont("Helvetica",15))
        self.label_data.setStyleSheet("color: Red")
        self.label_data.setAlignment(Qt.AlignCenter)

        self.label_passi = QLabel (text=" ")
        self.label_passi.setFont(qtg.QFont("Helvetica",15, qtg.QFont.Bold))
        self.label_passi.setStyleSheet("color: Blue")
        self.label_passi.setAlignment(Qt.AlignCenter)

        self.graphWidgetX.setYRange(-RISOLUZIONE, +RISOLUZIONE, padding=0)
        self.graphWidgetY.setYRange(-RISOLUZIONE, +RISOLUZIONE, padding=0)
        self.graphWidgetZ.setYRange(-RISOLUZIONE, +RISOLUZIONE, padding=0)
        self.graphWidgetACC.setYRange(-RISOLUZIONE, +RISOLUZIONE, padding=0)

        layoutV = QVBoxLayout()
        layoutV.addWidget(self.search_btn)
        layoutV.addWidget(self.label_port)
        layoutV.addWidget(self.data_btn)
        layoutV.addWidget(self.label_data)
        layoutH = QHBoxLayout()
        layoutV.addLayout(layoutH)
        layoutH.addWidget(self.graphWidgetX)
        layoutH.addWidget(self.graphWidgetY)
        layoutH.addWidget(self.graphWidgetZ)
        layoutV.addWidget(self.graphWidgetACC)
        layoutV.addWidget(self.label_passi)
        widget = QWidget()
        widget.setLayout(layoutV)
        self.setCentralWidget(widget)

        #X
        self.graphWidgetX.showGrid(x=True, y=True)
            # Set background color
        self.graphWidgetX.setBackground('w')
            # Add title
        self.graphWidgetX.setTitle("Accelerazione X nel tempo")
            # Add axis labels
        styles = {'color':'k', 'font-size':'15px'}
        self.graphWidgetX.setLabel('left', 'Acc X', **styles)
        self.graphWidgetX.setLabel('bottom', 'Tempo', **styles)
            # Add legend
        self.graphWidgetX.addLegend()

        #Y
        self.graphWidgetY.showGrid(x=True, y=True)
            # Set background color
        self.graphWidgetY.setBackground('w')
            # Add title
        self.graphWidgetY.setTitle("Accelerazione Y nel tempo")
            # Add axis labels
        styles = {'color':'k', 'font-size':'15px'}
        self.graphWidgetY.setLabel('left', 'Acc Y', **styles)
        self.graphWidgetY.setLabel('bottom', 'Tempo', **styles)
            # Add legend
        self.graphWidgetY.addLegend()

        #Z
        self.graphWidgetZ.showGrid(x=True, y=True)
            # Set background color
        self.graphWidgetZ.setBackground('w')
            # Add title
        self.graphWidgetZ.setTitle("Accelerazione Z nel tempo")
            # Add axis labels
        styles = {'color':'k', 'font-size':'15px'}
        self.graphWidgetZ.setLabel('left', 'Acc Z', **styles)
        self.graphWidgetZ.setLabel('bottom', 'Tempo', **styles)
            # Add legend
        self.graphWidgetZ.addLegend()

        #ACC
        self.graphWidgetACC.showGrid(x=True, y=True)
            # Set background color
        self.graphWidgetACC.setBackground('w')
            # Add title
        self.graphWidgetACC.setTitle("Accelerazione totale nel tempo")
            # Add axis labels
        styles = {'color':'k', 'font-size':'15px'}
        self.graphWidgetACC.setLabel('left', 'Accelerazione totale', **styles)
        self.graphWidgetACC.setLabel('bottom', 'Tempo', **styles)
            # Add legend
        self.graphWidgetACC.addLegend()
    
    def port_scan(self):
        self.port_text = ""
        self.serial_ports = [
                p.name
                for p in serial.tools.list_ports.comports()
            ]
    

    def search(self, checked):
        global list_serial_worker
        self.port_scan()
        for port in self.serial_ports:
            #print(port)
            #port = port.split()
            #port = port[0]
            self.port_text = port
            #print(port)
            if checked:
                self.serial_worker = SerialWorker(self.port_text) # needs to be re defined
                list_serial_worker.append(self.serial_worker)
                self.serial_worker.signals.status.connect(self.check_serialport_status)
                self.serial_worker.signals.device_port.connect(self.connected_device)
                self.serial_worker.signals.founded.connect(self.change_label)
                self.threadpool.start(self.serial_worker)
            else:
                # kill thread
                global KILL
                KILL = True
                self.data_btn.setChecked(False)
                self.data_btn.setDisabled(True)
                self.search_btn.setText("Search Psoc")
                self.label_data.setText("No data here")
                self.label_port.setText("No port here")
                self.serial_worker.killed()
    
    def change_label(self, found, porta):
        global KILL
        global PORT
        #print(found)
        if found == True:
            PORT = porta
            self.search_btn.setText(
                "Disconnect from port {}".format(PORT)
            )
            self.label_port.setText("Psoc founded on port {}".format(porta))
            self.label_port.setStyleSheet("color: Green")
            self.data_btn.setDisabled(False)
        else:
            self.search_btn.setText("Search Psoc")
            self.label_port.setText("Psoc not founded")
            self.label_data.setText("No data here")
            self.data_btn.setDisabled(True)
            self.search_btn.setChecked(False)
            KILL=True
            self.serial_worker.killed()



    def data(self):
        global PORT
        self.indice=self.serial_ports.index(PORT)
        global list_serial_worker
        self.serial_worker=list_serial_worker[self.indice]
        self.serial_worker.send(CHAR_SEND_DATA)
        self.serial_worker.signals.packetto2.connect(self.grafico)
    
    def grafico(self, packet):
        self.serial_worker.aggiorna_grafico(packet)
    
    
    
    def check_serialport_status(self, port_name, status):
        global PORT
        if status == 0:
            self.search_btn.setChecked(False)
        elif status == 1:
            logging.info("Connected to port {}".format(port_name))
    
    def connected_device(self, port_name):
        logging.info("Port {} closed.".format(port_name))

    def ExitHandler(self):
        global KILL
        global CONN_STATUS
        if(CONN_STATUS):
            self.serial_worker.send(CHAR_PAUSA)
        KILL = True
        self.serial_worker.killed()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    app.aboutToQuit.connect(w.ExitHandler)
    w.show()
    sys.exit(app.exec_())
