from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import *
import pandas as pd
from PyQt5 import uic
import icone_rc
from database_conn import Comunicazione
import sys, time, logging, serial, serial.tools.list_ports
from PyQt5.QtCore import *
import PyQt5.QtGui as qtg
import time, csv, os
import pyqtgraph as pg
from pyqtgraph import PlotWidget
from math import remainder
import datetime
import costanti as cs

lista_X = []
lista_Y = []
lista_Z = []
lista_utente=[]
tempo = []
x_filtered_list=[]
y_filtered_list=[]
z_filtered_list=[]
accelerazione_list=[0]*99

list_serial_worker=[]
totave=[]
lista_ultimi_50=[]
list_serial=[]

c = 0
t = 0
sample_x = 0
min_range = 0
max_range = 1
# Definizione di variabili per il conteggio dei passi
num_steps = 0
num_distance = 0
num_speed=0
num_calories=0
stride=0
t2=0
num_steps_2s=0
flag_aggiungi=0


flag_profilo_caricato=0

flag=0

precisione = 200 #precisione
massimo=0
minimo=0
conteggio=0
acc=0

accelerazione_precisione=[0]*99
accelerazione_threshold=[0]*99

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
        if not cs.CONN_STATUS:
            try:
                self.port_serial = serial.Serial(port=self.port_name, baudrate=self.baudrate,
                                        write_timeout=0, timeout=2)                
                if self.port_serial.is_open:
                    cs.CONN_STATUS = True
                    self.signals.status.emit(self.port_name, 1)
                    self.send(cs.CHAR_SEND_ID)
                    self.reaD()
                    time.sleep(0.01)     
            except serial.SerialException as e:
                    logging.info("Error with port {}.".format(self.port_name))
                    self.signals.status.emit(self.port_name, 0)
                    time.sleep(0.01)
    
    @pyqtSlot()
    def send(self, char):
        try:
            if char==cs.CHAR_SEND_DATA and self.port_name==cs.PORT:
                self.port_serial.write(char.encode('utf-8'))
                logging.info("Written {} on port {}.".format(char, self.port_name))
                w.label_data.setText("Acquiring Data . . .")
                w.label_data.setStyleSheet("color: Green; font: 20pt 'Rockwell';")
                w.data_btn.setDisabled(True)
                cs.FLAG_DRAW = True
            elif char==cs.CHAR_SEND_DATA and self.port_name!=cs.PORT:
                self.killed()
            else:
                self.port_serial.write(char.encode('utf-8'))
                logging.info("Written {} on port {}.".format(char, self.port_name))

        except Exception as e:
            logging.info("Could not write {} on port {}.".format(char, self.port_name))


    def reaD(self):
        global num_steps
        try:
            while True:
                if self.port_serial.in_waiting != 0 and cs.KILL == False:
                    self.packet = self.port_serial.readline()
                    self.packet = self.packet.decode('utf-8')
                    packet1=self.packet.split()
                    if packet1[0] == cs.CHAR_RISP:
                        self.signals.founded.emit(True, self.port_name)
                        logging.info("Answer {} on port {}.".format(self.packet, self.port_name))
                        self.packet=""
                    else:
                        #logging.info("Answer {} on port {}.".format(self.packet, self.port_name))
                        self.signals.packetto2.emit(self.packet)
                        self.packet=""
                elif cs.KILL == True:
                    self.packet=""
                    w.label_data.setText("No data here")
                    break
        except Exception as e:
            w.label_data.setText("No data here")
            w.label_port.setText("Connection Lost")
            time.sleep(0.5)
            self.killed()

    

    def aggiorna_grafico(self, packet):
        global c, t
        if cs.CONN_STATUS:
            packet = packet.split()
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


            conteggio = remainder(c,3)
            if conteggio==0:
                if cs.FLAG_DRAW == True:
                    t+=cs.TIME_PSOC
                    tempo.append(t)
                    self.plot()   
    
    def plot(self):
        global max_range, min_range
        if len(lista_X)>=100:
            x_offset,y_offset,z_offset=self.calibrazione()
            self.calcola_step(x_offset,y_offset,z_offset)
        else:
            x_filtered_list.append(0)
            y_filtered_list.append(0)
            z_filtered_list.append(0)
        w.graphWidgetX.clear()
        w.graphWidgetY.clear()
        w.graphWidgetZ.clear()
        if tempo[len(tempo)-1] >= 1:
            min_range+=cs.TIME_PSOC
            max_range+=cs.TIME_PSOC
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
    
    def calibrazione(self):
        global lista_X, lista_Y, lista_Z
        x_sum=0
        y_sum=0
        z_sum=0
        for i in range(0,100):
            x_sum += lista_X[i]
            y_sum += lista_Y[i]
            z_sum += lista_Z[i]
        
        x_offset=x_sum/100
        y_offset=y_sum/100
        z_offset=z_sum/100

        return x_offset, y_offset, z_offset

        
    def calcola_step(self, x_offset, y_offset, z_offset):
        global lista_X,lista_Y,lista_Z,x_filtered_list,y_filtered_list,z_filtered_list, tempo
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

        global num_steps, tempo, accelerazione_list, acc, totave, flag, lista_ultimi_50, conteggio, num_speed, num_distance, num_calories, stride, t2, num_steps_2s

        accelerazione = math.sqrt(x_filtered**2+y_filtered**2+z_filtered**2)
        accelerazione_list.append(accelerazione)
        accelerazione_precisione.append(precisione)
        accelerazione_threshold.append(acc)

        w.graphWidgetACC.clear()
        pen3 = pg.mkPen(color='c')
        pen4 = pg.mkPen(color='b', style=Qt.DotLine)
        pen5 = pg.mkPen(color='g', style=Qt.DashLine)
        w.graphWidgetACC.plot(tempo, accelerazione_list, name="Acceleration", pen=pen3)
        w.graphWidgetACC.plot(tempo, accelerazione_precisione, name="Precision", pen=pen4)

        '''
        ALGORITMO: UTILIZZA ACCELERAZIONE TOTALE (QUINDI PRENDE SEMPRE L'ASSE CON LA MAGGIORE ESCURSIONE)
        FUNZIONAMENTO: Una volta ottenuto il vettore accelerazione calibrato, 
                        viene calcolato l'avarage value degli ultimi 50 campioni (Max+Min)/2 (dynamic threshold level)
                        e questa threshold viene utilizzata per discriminare il passo per i successivi 50 campioni. 
                        Mentre si corre l'accelerometro potrebbe assumere qualsiasi orientamento,quindi questo approccio utilizza 
                        l'asse la cui accelerazione varia maggiormente (utilizzo il modulo). 
        Step eseguiti:
        1. Calibrazione e ottenimento dati filtrati
        2. Calcolo Media degli ultimi 50 campioni del vettore 
                totale di accelerazione e definizione della dynamic threshold
        3. Se il valore di accelerazione supera la dynamic threshold viene 
                contato il passo solo se quest'ultima ha superato un definita precisione 
                (è un filtraggio che elimina le oscillazioni quando si è fermi)
        4. Dal passo si definiscono gli altri dati
        '''
        
        lista_ultimi_50.append(accelerazione_list[len(accelerazione_list)-1])
        conteggio+=1
        if conteggio==50:
            massimo=max(lista_ultimi_50)
            minimo=min(lista_ultimi_50)
            acc=(massimo+minimo)/2
            totave.append(acc)
            conteggio=0
            lista_ultimi_50=[]
        
        if totave!=[]:
            t2+=0.02
            if accelerazione>totave[len(totave)-1] and flag==0 and totave[len(totave)-1]>=precisione:
                    num_steps+=1
                    num_steps_2s +=1
                    w.label_passi.setText("Steps: {}".format(num_steps))
                    self.send(cs.CHAR_SEND_PASSO)
                    flag=1
            elif accelerazione>totave[len(totave)-1] and flag==1 and totave[len(totave)-1]>=precisione:
                    pass
            if accelerazione<totave[len(totave)-1] and flag==1:
                    flag=0
            if num_steps<0:
                    num_steps=0
            
            w.graphWidgetACC.plot(tempo, accelerazione_threshold, name="Threshold", pen=pen5)

            '''
            CALCOLO ALTRI DATI DAL PASSO:

            Sono necessari i dati dell'utente come peso e altezza e il numero di passi effettuati in 2 secondi;
            Fonte: "Full-Featured Pedometer Design Realized with 3-Axis  Digital Accelerometer By Neil Zhao";
            Per la velocità, si preferisce questo approccio alla derivazione dell'accelerazione dato il calcolo della distanza compiuta su 2s;

            '''
            
            if round(t2, 0)==2:
                dati_utente = Comunicazione().cerca_utente(lista_utente[0], lista_utente[1])
                dati_utente=dati_utente[0]
                altezza = int(dati_utente[4])
                altezza=altezza/100
                peso = int(dati_utente[5])
                if num_steps in range(0,2):
                    stride = altezza/5
                elif num_steps == 3:
                    stride = altezza/4
                elif num_steps == 4:
                    stride = altezza/3
                elif num_steps == 5:
                    stride = altezza/2
                elif num_steps == 6:
                    stride = altezza/1.2
                elif num_steps in range(7,8):
                    stride = altezza
                elif num_steps >=9:
                    stride = 1.2*altezza
                
                num_distance += (num_steps_2s*stride) #in m
                num_distance_2s = (num_steps_2s*stride) #in m
                num_speed = num_distance_2s/2 #in m/s

                if num_steps_2s == 0:
                    num_calories += 1*(peso/1800)
                else:
                    num_calories += num_speed*(peso/400)


                w.label_distanza.setText("Distance: {} m".format(str(round(num_distance,0))))
                w.label_velocita.setText("Speed: {} m/s ".format(round(num_speed,1)))
                w.label_calorie.setText("Calories: {} cal ".format(str(round(num_calories,0))))
                self.send("d{}\n".format(str(round(num_distance,0))))
                self.send("v{}\n".format(str(round(num_speed,1))))
                self.send("k{}\n".format(str(round(num_calories,0))))
                t2=0
                num_steps_2s=0
                    

        
    @pyqtSlot()
    def killed(self):
        global tempo, t, c, lista_X, lista_Y, lista_Z, min_range, max_range
        global num_steps, tempo, accelerazione_list, tempo_acc, tempo_acc_list, x_filtered_list
        global y_filtered_list,z_filtered_list, acc, flag_profilo_caricato, num_distance
        global num_speed, num_calories, stride, t2, num_steps_2s
        if cs.KILL and cs.CONN_STATUS:
            self.send(cs.CHAR_PAUSA)
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
            acc=0
            num_steps = 0
            num_distance = 0
            num_speed=0
            num_calories=0
            stride=0
            t2=0
            num_steps_2s=0
            tempo_acc=0
            flag_profilo_caricato=0
            tempo_acc_list=[]
            w.graphWidgetX.clear()
            w.graphWidgetY.clear()
            w.graphWidgetZ.clear()
            w.graphWidgetACC.clear()
            w.label_port.setStyleSheet("color: Red")
            w.label_data.setStyleSheet("color: Red")
            w.label_passi.setText("Steps: 0")
            w.label_distanza.setText("Distance: 0 m")
            w.label_velocita.setText("Speed: 0 m/s ")
            w.label_calorie.setText("Calories: 0 cal ")
            time.sleep(0.01)
            cs.CONN_STATUS = False
            self.signals.device_port.emit(self.port_name)
            
        cs.KILL = False
        logging.info("Process killed")

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.serial_worker = SerialWorker(None)

        #Load UI
        uic.loadUi("nuova.ui", self)

        self.serial_worker = SerialWorker(None)
        # create thread handler
        self.threadpool = QThreadPool()
        self.connected = cs.CONN_STATUS
        self.database = Comunicazione()
        self.initUI()

    def initUI(self):
        self.button_riduci.hide()
        #DATA E ORA
        self.update_time()
        self.Timer = QTimer()
        self.Timer.timeout.connect(self.update_time)
        self.Timer.start(cs.TIME)

        #ELIMINO BARRA SUPERIORE
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowOpacity(1)

        #SIZE GRIP
        self.gripSize = 10
        self.grip = QtWidgets.QSizeGrip(self)
        self.grip.resize(self.gripSize, self.gripSize)

        #MUOVERE LA FINESTRA
        self.frame_superiore.mouseMoveEvent = self.muovi_finestra

        #BOTTONI BARRA SUPERIORE
        self.button_close.clicked.connect(lambda: self.close())
        self.button_allarga.clicked.connect(self.allarga_pagina)
        self.button_riduci.clicked.connect(self.riduci_pagina)
        self.button_icona.clicked.connect(self.icona_pagina)
        self.button_menu.clicked.connect(self.menu)

        #BOTTONI BARRA LATERALE
        self.button_personaldata.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_user))
        self.button_dati.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_data))
        self.button_database.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_database))
        self.button_info.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_info))
        self.button_help.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_help))

        #ADATTAMENTO DIMENSIONE TABELLA
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        #USER PAGE
        #Disattivo entries iniziali
        self.lineEdit_nome.setEnabled(False)
        self.lineEdit_cognome.setEnabled(False)
        self.spinBox.setEnabled(False)
        self.lineEdit_sesso.setEnabled(False)
        self.lineEdit_altezza.setEnabled(False)
        self.lineEdit_peso.setEnabled(False)
        #Disattivo bottoni
        self.cambiafoto_button.setEnabled(False)
        self.btn_salva.setEnabled(False)
        #ComboBox
        self.utenti = Comunicazione().ottieni_utenti()
        self.lista_nomi_cognomi = []
        for tupla in self.utenti:
            nome_cognome=str(tupla[0]+" "+tupla[1])
            self.lista_nomi_cognomi.append(nome_cognome)
        self.comboBox_utenti.clear()
        self.comboBox_utenti.addItems(self.lista_nomi_cognomi)

        #Load Button
        self.caricadati_button.clicked.connect(self.inserisci_dati)

        #Change Foto Button
        self.cambiafoto_button.clicked.connect(self.cambia_foto)

        #Button Save
        self.btn_salva.clicked.connect(self.salva_dati)

        #Butto Register
        self.register_btn.clicked.connect(self.registrazione)

        #DATA ANALYSIS PAGE
        self.search_btn.setCheckable(True)
        self.search_btn.clicked.connect(self.search)
        self.data_btn.clicked.connect(self.data)
        self.data_btn.setDisabled(True)

        self.graphWidgetX.setYRange(-cs.RISOLUZIONE, +cs.RISOLUZIONE, padding=0)
        self.graphWidgetY.setYRange(-cs.RISOLUZIONE, +cs.RISOLUZIONE, padding=0)
        self.graphWidgetZ.setYRange(-cs.RISOLUZIONE, +cs.RISOLUZIONE, padding=0)
        self.graphWidgetACC.setYRange(0, +cs.RISOLUZIONE, padding=0)

        self.graphWidgetX.showGrid(x=True, y=True)
            # Set background color
        self.graphWidgetX.setBackground('w')
            # Add title
        self.graphWidgetX.setTitle("Acceleration X over time")
            # Add axis labels
        styles = {'color':'k', 'font-size':'15px'}
        self.graphWidgetX.setLabel('left', 'Acc X [mg]', **styles)
        self.graphWidgetX.setLabel('bottom', 'Time [s]', **styles)
            # Add legend
        self.graphWidgetX.addLegend()

        #Y
        self.graphWidgetY.showGrid(x=True, y=True)
            # Set background color
        self.graphWidgetY.setBackground('w')
            # Add title
        self.graphWidgetY.setTitle("Acceleration Y over time")
            # Add axis labels
        styles = {'color':'k', 'font-size':'15px'}
        self.graphWidgetY.setLabel('left', 'Acc Y [mg]', **styles)
        self.graphWidgetY.setLabel('bottom', 'Time [s]', **styles)
            # Add legend
        self.graphWidgetY.addLegend()

        #Z
        self.graphWidgetZ.showGrid(x=True, y=True)
            # Set background color
        self.graphWidgetZ.setBackground('w')
            # Add title
        self.graphWidgetZ.setTitle("Acceleration Z over time")
            # Add axis labels
        styles = {'color':'k', 'font-size':'15px'}
        self.graphWidgetZ.setLabel('left', 'Acc Z [mg]', **styles)
        self.graphWidgetZ.setLabel('bottom', 'Time [s]', **styles)
            # Add legend
        self.graphWidgetZ.addLegend()

        #ACC
        self.graphWidgetACC.showGrid(x=True, y=True)
            # Set background color
        self.graphWidgetACC.setBackground('w')
            # Add title
        self.graphWidgetACC.setTitle("Total Acceleration over time")
            # Add axis labels
        styles = {'color':'k', 'font-size':'15px'}
        self.graphWidgetACC.setLabel('left', 'Total Acceleration [mg]', **styles)
        self.graphWidgetACC.setLabel('bottom', 'Time [s]', **styles)
            # Add legend
        self.graphWidgetACC.addLegend()


        #DATABASE PAGE
        #aggiungo dati
        self.dati=Comunicazione().mostra_dati()
        table_row=0
        self.tableWidget.setRowCount(len(self.dati))
        for riga_dati in self.dati:
            self.tableWidget.setItem(table_row,0,QtWidgets.QTableWidgetItem(riga_dati[0]))
            self.tableWidget.setItem(table_row,1,QtWidgets.QTableWidgetItem(riga_dati[1]))
            self.tableWidget.setItem(table_row,2,QtWidgets.QTableWidgetItem(riga_dati[2]))
            self.tableWidget.setItem(table_row,3,QtWidgets.QTableWidgetItem(riga_dati[3]))
            self.tableWidget.setItem(table_row,4,QtWidgets.QTableWidgetItem(riga_dati[4]))
            self.tableWidget.setItem(table_row,5,QtWidgets.QTableWidgetItem(riga_dati[5]))
            self.tableWidget.setItem(table_row,6,QtWidgets.QTableWidgetItem(riga_dati[6]))
            table_row+=1
        
        self.caricadati_button_database.clicked.connect(self.mostra_tabella)
        self.reset_btn.clicked.connect(self.reset_tabella)
        self.export_btn.clicked.connect(self.export_data)
        self.tableWidget.doubleClicked.connect(self.row_clicked)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.BarPlot_steps.setBackground('w')
        self.BarPlot_steps.setTitle("Steps over time")
        self.BarPlot_distance.setBackground('w')
        self.BarPlot_distance.setTitle("Distance over time")
        self.BarPlot_calories.setBackground('w')
        self.BarPlot_calories.setTitle("Calories over time")


        #HELP PAGE
        self.radioButton_Conn.setChecked(True)
        self.pushButton_sendRequest.clicked.connect(self.manda_richiesta)
    
    def manda_richiesta(self):
        msg = QMessageBox()
        if self.radioButton_Conn.isChecked()==True:
            self.Type = self.radioButton_Conn.text()
        elif self.radioButton_Visual.isChecked()==True:
            self.Type = self.radioButton_Visual.text()
        elif self.radioButton_dataS.isChecked()==True:
            self.Type = self.radioButton_dataS.text()
        elif self.radioButton_other.isChecked()==True:
            self.Type = self.radioButton_other.text()
        
        self.Name = self.lineEdit_nome_2.text()
        self.Surname = self.lineEdit_surname_2.text()
        self.Mail = self.lineEdit_mail.text()
        self.Issue = self.textEdit.toPlainText()

        if self.Mail.strip().count("@") != 1:
            self.lineEdit_mail.setStyleSheet(cs.style_notcorrect)
        elif self.Name =='' or self.Name.find(" ") > 0 or self.Name.isdigit()==True:
            self.lineEdit_nome_2.setStyleSheet(cs.style_notcorrect)
        elif self.Surname =='' or self.Surname.find(" ")> 0 or self.Surname.isdigit()==True:
            self.lineEdit_surname_2.setStyleSheet(cs.style_notcorrect)
        elif self.Issue == "":
            self.textEdit.setStyleSheet(cs.style_notcorrect)
        else:
            Comunicazione().invia_problema(self.Name, self.Surname, self.Mail, self.Issue, self.Type)
            self.lineEdit_nome_2.setStyleSheet(cs.style_correct)
            self.lineEdit_surname_2.setStyleSheet(cs.style_correct)
            self.lineEdit_mail.setStyleSheet(cs.style_correct)
            self.textEdit.setStyleSheet(cs.style_correct)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setWindowTitle("Success")
            msg.setText("Help Request Reported")
            msg.exec()
            self.lineEdit_nome_2.clear()
            self.lineEdit_surname_2.clear()
            self.lineEdit_mail.clear()
            self.textEdit.clear()
            self.lineEdit_nome_2.setStyleSheet(cs.style_normal)
            self.lineEdit_surname_2.setStyleSheet(cs.style_normal)
            self.lineEdit_mail.setStyleSheet(cs.style_normal)
            self.textEdit.setStyleSheet(cs.style_normal_text_edit)


    def row_clicked(self):
        for idx in self.tableWidget.selectionModel().selectedIndexes():
            row_number = idx.row()
        riga = []
        for i in range(0,7):
            riga.append(self.tableWidget.item(row_number, i).text())
        
        Name = riga[0]
        Surname = riga[1]
        dati= Comunicazione().mostra_dati_nome_cognome(Name,Surname)
        
        self.df = pd.DataFrame(dati, columns=('Name', 'Surname', 'Steps', 'Distance', 'Speed', 'Calories', 'Date'))
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.df['Steps'] = self.df['Steps'].astype(int)
        self.df['Distance'] = self.df['Distance'].astype(float)
        self.df['Speed'] = self.df['Speed'].astype(float)
        self.df['Calories'] = self.df['Calories'].astype(float)
        #dati.value_counts()
        grouped_df = self.df.groupby(['Name', 'Surname', 'Date']).agg({
                                        'Steps': 'sum',
                                        'Distance': 'sum',
                                        'Calories': 'sum',
                                        'Speed': 'mean'
                                    }).reset_index()
        grouped_df = grouped_df.sort_values('Date')
        grouped_df['Date'] = grouped_df['Date'].dt.strftime('%d-%m-%Y')

        #STEPS
        lista_righe=[]
        for i in range(0, len(grouped_df)):
            lista_righe.append(i)
        x_step = lista_righe
        y_step = grouped_df['Steps'].tolist() 
        self.BarPlot_steps.clear()
        self.Bar_steps = pg.BarGraphItem(x=x_step, height=y_step, width=0.5, brush='b')
        self.BarPlot_steps.addItem(self.Bar_steps)
        #(grouped_df)
        #cambio label su asse x
        axis_s = self.BarPlot_steps.getAxis('bottom')  # Ottieni l'oggetto AxisItem per l'asse x
        valori_x = grouped_df['Date'].tolist()  # I nuovi nomi da assegnare
        axis_s.setTicks([list(zip(x_step, valori_x))])

        #DISTANCE
        x_distance = lista_righe
        y_distance = grouped_df['Distance'].tolist()
        self.BarPlot_distance.clear()
        self.Bar_distance = pg.BarGraphItem(x=x_distance, height=y_distance, width=0.5, brush='g')
        self.BarPlot_distance.addItem(self.Bar_distance)
        #cambio label su asse x
        axis_d = self.BarPlot_distance.getAxis('bottom')  # Ottieni l'oggetto AxisItem per l'asse x
        axis_d.setTicks([list(zip(x_distance, valori_x))])

        #CALORIES
        x_calories = lista_righe
        y_calories = grouped_df['Calories'].tolist() 
        self.BarPlot_calories.clear()
        self.Bar_calories = pg.BarGraphItem(x=x_calories, height=y_calories, width=0.5, brush='r')
        self.BarPlot_calories.addItem(self.Bar_calories)
        #cambio label su asse x
        axis_c = self.BarPlot_calories.getAxis('bottom')  # Ottieni l'oggetto AxisItem per l'asse x
        axis_c.setTicks([list(zip(x_calories, valori_x))])

    def export_data(self):
        path, ok = QtWidgets.QFileDialog.getSaveFileName(
            self, 'Save CSV', os.getenv('HOME'), 'CSV(*.csv)')
        if ok:
            columns = range(self.tableWidget.columnCount())
            header = [self.tableWidget.horizontalHeaderItem(column).text()
                      for column in columns]
            with open(path, 'w') as csvfile:
                writer = csv.writer(
                    csvfile, dialect='excel', lineterminator='\n')
                writer.writerow(header)
                for row in range(self.tableWidget.rowCount()):
                    writer.writerow(
                        self.tableWidget.item(row, column).text()
                        for column in columns)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setWindowTitle("Success")
            msg.setText("Data Exported")
            msg.exec()
    
    def reset_tabella(self):
        for i in reversed(range(self.tableWidget.rowCount())):
                    self.tableWidget.removeRow(i)
        self.dati=Comunicazione().mostra_dati()
        table_row=0
        self.tableWidget.setRowCount(len(self.dati))
        for riga_dati in self.dati:
            self.tableWidget.setItem(table_row,0,QtWidgets.QTableWidgetItem(riga_dati[0]))
            self.tableWidget.setItem(table_row,1,QtWidgets.QTableWidgetItem(riga_dati[1]))
            self.tableWidget.setItem(table_row,2,QtWidgets.QTableWidgetItem(riga_dati[2]))
            self.tableWidget.setItem(table_row,3,QtWidgets.QTableWidgetItem(riga_dati[3]))
            self.tableWidget.setItem(table_row,4,QtWidgets.QTableWidgetItem(riga_dati[4]))
            self.tableWidget.setItem(table_row,5,QtWidgets.QTableWidgetItem(riga_dati[5]))
            self.tableWidget.setItem(table_row,6,QtWidgets.QTableWidgetItem(riga_dati[6]))
            table_row+=1

    def mostra_tabella(self):
        msg=QMessageBox()
        self.Nome_dati=self.lineEdit_searchpername.text()
        if self.Nome_dati =='' or self.Nome_dati.find(" ") > 0 or self.Nome_dati.isdigit()==True:
            self.lineEdit_searchpername.setStyleSheet(cs.style_notcorrect)
        else:
            self.lineEdit_searchpername.setStyleSheet(cs.style_normal)
            self.dati_nome=Comunicazione().mostra_dati_nome(self.Nome_dati)
            if self.dati_nome==[]:
                msg.setIcon(QMessageBox.Critical)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setWindowTitle("Results")
                msg.setText("No Data Founded")
                msg.exec()
                for i in reversed(range(self.tableWidget.rowCount())):
                    self.tableWidget.removeRow(i)
            else:
                msg.setIcon(QMessageBox.Information)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setWindowTitle("Results")
                msg.setText("Data Founded")
                msg.exec()
                for i in reversed(range(self.tableWidget.rowCount())):
                    self.tableWidget.removeRow(i)
                table_row=0
                self.tableWidget.setRowCount(len(self.dati_nome))
                for riga_dati in self.dati_nome:
                    self.tableWidget.setItem(table_row,0,QtWidgets.QTableWidgetItem(riga_dati[0]))
                    self.tableWidget.setItem(table_row,1,QtWidgets.QTableWidgetItem(riga_dati[1]))
                    self.tableWidget.setItem(table_row,2,QtWidgets.QTableWidgetItem(riga_dati[2]))
                    self.tableWidget.setItem(table_row,3,QtWidgets.QTableWidgetItem(riga_dati[3]))
                    self.tableWidget.setItem(table_row,4,QtWidgets.QTableWidgetItem(riga_dati[4]))
                    self.tableWidget.setItem(table_row,5,QtWidgets.QTableWidgetItem(riga_dati[5]))
                    self.tableWidget.setItem(table_row,6,QtWidgets.QTableWidgetItem(riga_dati[6]))
                    table_row+=1


    def port_scan(self):
        self.port_text = ""
        self.serial_ports = [
                p.name
                for p in serial.tools.list_ports.comports()
            ]
    
    def search(self, checked):
        global list_serial_worker, lista_utente, flag_profilo_caricato, flag_aggiungi
        self.port_scan()
        if flag_profilo_caricato==1:
            for port in self.serial_ports:
                self.port_text = port
                if checked:
                    flag_aggiungi==0
                    self.serial_worker = SerialWorker(self.port_text) # needs to be re defined
                    list_serial_worker.append(self.serial_worker)
                    self.serial_worker.signals.status.connect(self.check_serialport_status)
                    self.serial_worker.signals.device_port.connect(self.connected_device)
                    self.serial_worker.signals.founded.connect(self.change_label)
                    self.threadpool.start(self.serial_worker)
                else:
                    # kill thread
                    global num_steps, num_speed, num_distance, num_calories
                    cs.KILL = True
                    self.data_btn.setChecked(False)
                    self.data_btn.setDisabled(True)
                    self.search_btn.setText("Search Psoc")
                    self.label_data.setText("No data here")
                    self.label_port.setText("No port here")
                    num_distance=round(num_distance,0)
                    num_speed=round(num_speed,1)
                    num_calories=round(num_calories,0)
                    #aggiungo la riga al database
                    if flag_aggiungi==0:
                        flag_aggiungi=1
                        Comunicazione().inserisci_dati(lista_utente[0],lista_utente[1], num_steps, num_distance, num_speed, num_calories, lista_utente[2])
                        for i in reversed(range(self.tableWidget.rowCount())):
                            self.tableWidget.removeRow(i)
                        self.dati=Comunicazione().mostra_dati()
                        table_row=0
                        self.tableWidget.setRowCount(len(self.dati))
                        for riga_dati in self.dati:
                            self.tableWidget.setItem(table_row,0,QtWidgets.QTableWidgetItem(riga_dati[0]))
                            self.tableWidget.setItem(table_row,1,QtWidgets.QTableWidgetItem(riga_dati[1]))
                            self.tableWidget.setItem(table_row,2,QtWidgets.QTableWidgetItem(riga_dati[2]))
                            self.tableWidget.setItem(table_row,3,QtWidgets.QTableWidgetItem(riga_dati[3]))
                            self.tableWidget.setItem(table_row,4,QtWidgets.QTableWidgetItem(riga_dati[4]))
                            self.tableWidget.setItem(table_row,5,QtWidgets.QTableWidgetItem(riga_dati[5]))
                            self.tableWidget.setItem(table_row,6,QtWidgets.QTableWidgetItem(riga_dati[6]))
                            table_row+=1
                    
                    self.serial_worker.killed()
        else:
            msg=QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setWindowTitle("Error")
            msg.setText("Load/Register a profile before starting")
            msg.exec()

    
    def change_label(self, found, porta):
        if found == True:
            cs.PORT = porta
            self.search_btn.setText(
                "Disconnect"
            )
            self.label_port.setText("Connected")
            logging.info("Psoc found on port {}".format(cs.PORT))
            self.label_port.setStyleSheet("color: Green; font: 20pt 'Rockwell';")
            self.data_btn.setDisabled(False)
        else:
            self.search_btn.setText("Search device")
            self.label_port.setText("Device not found")
            self.label_data.setText("No data here")
            self.data_btn.setDisabled(True)
            self.search_btn.setChecked(False)
            cs.KILL=True
            self.serial_worker.killed()


    def data(self):
        self.indice=self.serial_ports.index(cs.PORT)
        global list_serial_worker
        self.serial_worker=list_serial_worker[self.indice]
        
        for index in range(0,len(list_serial_worker)):
            if index != self.indice:
                worker=list_serial_worker[index]
                worker.killed()
            
        self.serial_worker.send(cs.CHAR_SEND_DATA)
        self.serial_worker.signals.packetto2.connect(self.grafico)
    
    def grafico(self, packet):
        self.serial_worker.aggiorna_grafico(packet)
    
    
    def check_serialport_status(self, port_name, status):
        if status == 0:
            self.search_btn.setChecked(False)
        elif status == 1:
            logging.info("Connected to port {}".format(port_name))
    
    def connected_device(self, port_name):
        logging.info("Port {} closed.".format(port_name))

    def ExitHandler(self):
        if(cs.CONN_STATUS):
            self.serial_worker.send(cs.CHAR_PAUSA)
        cs.KILL = True
        self.serial_worker.killed()

    def registrazione(self):
        self.lineEdit_nome.setEnabled(True)
        self.lineEdit_cognome.setEnabled(True)
        self.spinBox.setEnabled(True)
        self.lineEdit_sesso.setEnabled(True)
        self.lineEdit_altezza.setEnabled(True)
        self.lineEdit_peso.setEnabled(True)
        self.cambiafoto_button.setEnabled(True)
        self.btn_salva.setEnabled(True)
        self.register_btn.setEnabled(False)
        self.lineEdit_nome.clear()
        self.lineEdit_cognome.clear()
        self.spinBox.clear()
        self.lineEdit_sesso.clear()
        self.lineEdit_altezza.clear()
        self.lineEdit_peso.clear()
    
    def inserisci_dati(self):
        if self.utenti!=[]:
            msg=QMessageBox()
            persona=self.comboBox_utenti.currentText()
            persona=persona.split()
            self.Name = persona[0]
            self.Surname = persona[1]
            self.utente = Comunicazione().ottieni_utente(self.Name, self.Surname)
            self.utente = self.utente[0]

            self.lineEdit_nome.setEnabled(True)
            self.lineEdit_cognome.setEnabled(True)
            self.spinBox.setEnabled(True)
            self.lineEdit_sesso.setEnabled(True)
            self.lineEdit_altezza.setEnabled(True)
            self.lineEdit_peso.setEnabled(True)
            self.cambiafoto_button.setEnabled(True)
            self.btn_salva.setEnabled(True)
            self.register_btn.setEnabled(False)

            self.lineEdit_nome.setText(self.utente[0])
            self.lineEdit_cognome.setText(self.utente[1])
            self.spinBox.setValue(int(self.utente[2]))
            self.lineEdit_sesso.setText(self.utente[3])
            self.lineEdit_altezza.setText(self.utente[4])
            self.lineEdit_peso.setText(self.utente[5])
            self.Foto = self.utente[6]
            self.pixmap = qtg.QPixmap()
            try:
                if self.pixmap.loadFromData(self.Foto):
                    self.label_foto.setPixmap(self.pixmap)
            except:
                self.label_foto.setText("No Foto")
            
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setWindowTitle("Success")
            msg.setText("Data Loaded")
            msg.exec()
            
        else:
            self.label_error_load.setText("No Users, Please register")
            self.lineEdit_nome.setEnabled(True)
            self.lineEdit_cognome.setEnabled(True)
            self.spinBox.setEnabled(True)
            self.lineEdit_sesso.setEnabled(True)
            self.lineEdit_altezza.setEnabled(True)
            self.lineEdit_peso.setEnabled(True)
            self.cambiafoto_button.setEnabled(True)
            self.btn_salva.setEnabled(True)
            self.register_btn.setEnabled(False)
            self.lineEdit_nome.clear()
            self.lineEdit_cognome.clear()
            self.spinBox.clear()
            self.lineEdit_sesso.clear()
            self.lineEdit_altezza.clear()
            self.lineEdit_peso.clear()
    
    def cambia_foto(self):
        self.Foto = QFileDialog.getOpenFileName(self, 'Open Photo', os.getenv('HOME'),'PNG(*.png);; JPG(*.jpg)')
        self.pixmap = qtg.QPixmap(self.Foto[0])
        self.label_foto.setPixmap(self.pixmap)
        self.label_foto.setText("")
        self.Foto=self.convert_in_binary(self.Foto[0])
    
    def convert_in_binary(self, filename):
        try:
            with open(filename, 'rb') as file:
                blobData = file.read()
            return blobData
        except:
            return 0

    def salva_dati(self):
        global lista_utente, flag_profilo_caricato
        lista_utente=[]
        flag=0
        msg = QMessageBox()
        self.Name = self.lineEdit_nome.text()
        self.Surname = self.lineEdit_cognome.text()
        self.Age = self.spinBox.value()
        self.Gender = self.lineEdit_sesso.text()
        self.Height = self.lineEdit_altezza.text()
        self.Weight = self.lineEdit_peso.text()
        
        try:
            if self.Foto !=0:
                self.Photo = self.Foto
                flag=1
            else:
                msg.setIcon(QMessageBox.Critical)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setWindowTitle("Error")
                msg.setText("Please enter Photo")
                msg.exec() 
        except:
            msg.setIcon(QMessageBox.Critical)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setWindowTitle("Error")
            msg.setText("Please enter Photo")
            msg.exec()
        

        if self.Name =='' or self.Name.find(" ") > 0 or self.Name.isdigit()==True:
            self.lineEdit_nome.setStyleSheet(cs.style_notcorrect)
        
        elif self.Surname =='' or self.Surname.find(" ")> 0 or self.Surname.isdigit()==True:
            self.lineEdit_cognome.setStyleSheet(cs.style_notcorrect)
        
        elif self.Age <= 10 or self.Age >= 90:
            self.spinBox.setStyleSheet(cs.style_notcorrect)

        elif self.Gender =='' or self.Gender.find(" ")> 0 or self.Gender.isdigit()==True:
            self.lineEdit_sesso.setStyleSheet(cs.style_notcorrect)

        elif self.Height =='' or self.Height.find(" ")> 0 or self.Height.isdigit()==False or self.Height.find(".")> 0 or self.Height.find(",")> 0:
            self.lineEdit_altezza.setStyleSheet(cs.style_notcorrect)

        elif self.Weight =='' or self.Weight.find(" ")> 0 or self.Weight.isdigit()==False or self.Weight.find(".")> 0 or self.Weight.find(",")> 0:
            self.lineEdit_nome.setStyleSheet(cs.style_notcorrect)

        
        elif flag==1:
            self.lineEdit_nome.setStyleSheet(cs.style_correct)
            self.lineEdit_cognome.setStyleSheet(cs.style_correct)
            self.spinBox.setStyleSheet(cs.style_correct)
            self.lineEdit_sesso.setStyleSheet(cs.style_correct)
            self.lineEdit_altezza.setStyleSheet(cs.style_correct)
            self.lineEdit_peso.setStyleSheet(cs.style_correct)
            lista_utente.append(self.Name)
            lista_utente.append(self.Surname)
            self.current_data = datetime.datetime.strftime(datetime.datetime.now(), "%d.%m.%y")
            lista_utente.append(str(self.current_data))
            us = Comunicazione().cerca_utente(self.Name, self.Surname)
            if us==[]:
                #inserisco utente
                Comunicazione().inserisci_utente(self.Name, self.Surname, self.Age, self.Gender, self.Height, self.Weight, self.Photo)
                #aggiorno combobox
                self.utenti = Comunicazione().ottieni_utenti()
                self.lista_nomi_cognomi = []
                for tupla in self.utenti:
                    nome_cognome=str(tupla[0]+" "+tupla[1])
                    self.lista_nomi_cognomi.append(nome_cognome)
                #ripulisco tutto e mostro messaggio
                self.comboBox_utenti.clear()
                self.comboBox_utenti.addItems(self.lista_nomi_cognomi)
                msg.setIcon(QMessageBox.Information)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setWindowTitle("Success")
                msg.setText("Successful registration")
                msg.exec()
                self.lineEdit_nome.setEnabled(False)
                self.lineEdit_cognome.setEnabled(False)
                self.spinBox.setEnabled(False)
                self.lineEdit_sesso.setEnabled(False)
                self.lineEdit_altezza.setEnabled(False)
                self.lineEdit_peso.setEnabled(False)
                self.lineEdit_nome.clear()
                self.lineEdit_cognome.clear()
                self.spinBox.clear()
                self.lineEdit_sesso.clear()
                self.lineEdit_altezza.clear()
                self.lineEdit_peso.clear()
                self.label_foto.clear()
                self.cambiafoto_button.setEnabled(False)
                self.btn_salva.setEnabled(False)
                self.register_btn.setEnabled(True)
                flag_profilo_caricato=1
                self.lineEdit_nome.setStyleSheet(cs.style_normal)
                self.lineEdit_cognome.setStyleSheet(cs.style_normal)
                self.spinBox.setStyleSheet(cs.style_normal)
                self.lineEdit_sesso.setStyleSheet(cs.style_normal)
                self.lineEdit_altezza.setStyleSheet(cs.style_normal)
                self.lineEdit_peso.setStyleSheet(cs.style_normal)
            else:
                Comunicazione().aggiorna_utente(self.Name, self.Surname, self.Age, self.Gender, self.Height, self.Weight, self.Photo)
                msg.setIcon(QMessageBox.Information)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setWindowTitle("Success")
                msg.setText("Successful data update")
                msg.exec()
                self.lineEdit_nome.setEnabled(False)
                self.lineEdit_cognome.setEnabled(False)
                self.spinBox.setEnabled(False)
                self.lineEdit_sesso.setEnabled(False)
                self.lineEdit_altezza.setEnabled(False)
                self.lineEdit_peso.setEnabled(False)
                self.lineEdit_nome.clear()
                self.lineEdit_cognome.clear()
                self.spinBox.clear()
                self.lineEdit_sesso.clear()
                self.lineEdit_altezza.clear()
                self.lineEdit_peso.clear()
                self.label_foto.clear()
                self.cambiafoto_button.setEnabled(False)
                self.btn_salva.setEnabled(False)
                self.register_btn.setEnabled(True)
                flag_profilo_caricato=1
                self.lineEdit_nome.setStyleSheet(cs.style_normal)
                self.lineEdit_cognome.setStyleSheet(cs.style_normal)
                self.spinBox.setStyleSheet(cs.style_normal)
                self.lineEdit_sesso.setStyleSheet(cs.style_normal)
                self.lineEdit_altezza.setStyleSheet(cs.style_normal)
                self.lineEdit_peso.setStyleSheet(cs.style_normal)


    def update_time(self):
        self.cur_time = datetime.datetime.strftime(datetime.datetime.now(), "%d.%m.%y %H:%M:%S")
        self.label_dataora.setText(self.cur_time)
    
    def icona_pagina(self):
        self.showMinimized()
    
    def riduci_pagina(self):
        self.showNormal()
        self.button_riduci.hide()
        self.button_allarga.show()

    def allarga_pagina(self):
        self.showMaximized()
        self.button_riduci.show()
        self.button_allarga.hide()

    #SIZEGRIP
    def resizeEvent(self, event):
        rect = self.rect()
        self.grip.move(rect.right() - self.gripSize, rect.bottom() - self.gripSize)

    #MUOVERE FINESTRA
    def mousePressEvent(self,event):
        self.click_position = event.globalPos()

    def muovi_finestra(self, event):
        if self.isMaximized() == False:
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.click_position)
                self.click_position = event.globalPos()
                event.accept()
        
        if event.globalPos().y() <=10:
            self.showMaximized()
            self.button_allarga.hide()
            self.button_riduci.show()
        else:
            self.showNormal()
            self.button_allarga.show()
            self.button_riduci.hide()
    
    #MENU
    def menu(self):
        if True:
            width = self.frame_control.width()
            normal=0
            if width == 0:
                extender = 200
            else:
                extender = normal
            self.animazione = QPropertyAnimation(self.frame_control, b'minimumWidth')
            self.animazione.setDuration(300)
            self.animazione.setStartValue(width)
            self.animazione.setEndValue(extender)
            self.animazione.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
            self.animazione.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    app.aboutToQuit.connect(w.ExitHandler)
    w.show()
    sys.exit(app.exec_())
