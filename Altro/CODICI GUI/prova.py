from PyQt5.QtWidgets import *

from PyQt5.QtCore import *
import PyQt5.QtGui as qtg
import random

import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()

        self.setWindowTitle("GUI")
        width = 300
        height = 250
        self.setMinimumSize(width, height)

        self.initGUI()
        self.show()

    def initGUI(self):
        #self.setLayout(QVBoxLayout()) così si setta quello totale

        #LABEL
        self.label_number=int(random.random()*100)
        self.my_label = QLabel("The number is: "+str(self.label_number))
        self.my_label.setFont(qtg.QFont("Helvetica",20))
        self.my_label.setAlignment(Qt.AlignCenter)

        self.my_label2 = QLabel("Write something here")
        self.my_label2.setFont(qtg.QFont("Helvetica",20))
        self.my_label2.setAlignment(Qt.AlignCenter)

        #ENTRY
        self.my_entry = QLineEdit()
        self.my_entry.setObjectName("name_field")
        self.my_entry.setText("")

        #COMBOBOX
        self.my_combo = QComboBox(self,
                                  editable=True,
                                  insertPolicy=QComboBox.InsertAtBottom)

        #SPINBOX
        self.my_spin = QDoubleSpinBox(self,
                                value=10.5,
                                maximum=100,
                                minimum=0,
                                singleStep=0.1,
                                prefix='Replace number #',
                                suffix=' in the entry')
        self.my_spin.setFont(qtg.QFont('Helvetica',10))
        

        #BUTTON
        self.my_button = QPushButton("+1",
                                         clicked = lambda: self.add_it())
        
        self.my_button2 = QPushButton("-1",
                                         clicked = lambda: self.remove_it())
        
        self.my_button3 = QPushButton("Sum number in entry box",
                                         clicked = lambda: self.sum_it())
        self.my_button4 = QPushButton("Subtract number in entry box",
                                         clicked = lambda: self.sub_it())
        self.my_button5 = QPushButton("Replace number of combo in entry box",
                                         clicked = lambda: self.rep_it())
        self.my_button6 = QPushButton("Replace number of spin in entry box",
                                         clicked = lambda: self.replace_it())
        self.my_button7 = QPushButton("Replace",
                                         clicked = lambda: self.write_it())
        
        #TEXTBOX
        self.my_text=QTextEdit(self,
                               acceptRichText=True,
                               lineWrapMode=QTextEdit.FixedColumnWidth,
                               lineWrapColumnOrWidth=50,
                               placeholderText="Hello World!",
                               readOnly=False
                               )
        
        #SHOW ALL
        vlay = QVBoxLayout()
        hlay = QHBoxLayout()
        vlay.addWidget(self.my_label)
        vlay.addWidget(self.my_entry)
        vlay.addWidget(self.my_combo)
        vlay.addWidget(self.my_spin)
        vlay.addWidget(self.my_button3)
        vlay.addWidget(self.my_button4)
        vlay.addWidget(self.my_button5)
        vlay.addWidget(self.my_button6)
        vlay.addLayout(hlay)
        hlay.addWidget(self.my_button)
        hlay.addWidget(self.my_button2)
        vlay.addWidget(self.my_label2)
        vlay.addWidget(self.my_text)
        vlay.addWidget(self.my_button7)
        widget = QWidget()
        widget.setLayout(vlay)
        self.setCentralWidget(widget)

    def add_it(self):
        self.label_number+=1
        self.my_label.setText("The number is: "+str(self.label_number))
        self.my_entry.setText("")

    def remove_it(self):
        self.label_number-=1
        self.my_label.setText("The number is: "+str(self.label_number))
        self.my_entry.setText("")

    def sum_it(self):
        try:
            if(self.my_entry.text()!=""):
                self.label_number+=float(self.my_entry.text())
                self.my_label.setText("The number is: "+str(self.label_number))
                self.my_combo.addItem(str(self.my_entry.text()))
                self.my_entry.setText("")
            else:
                self.my_entry.setText("Enter a number, please")
        except Exception as e:
            self.my_entry.setText("This is not a number")
            print(e)

    def sub_it(self):
        try:
            if(self.my_entry.text()!=""):
                self.label_number-=float(self.my_entry.text())
                self.my_label.setText("The number is: "+str(self.label_number))
                self.my_combo.addItem(str(self.my_entry.text()))
                self.my_entry.setText("")
            else:
                self.my_entry.setText("Enter a number, please")
        except Exception as e:
            self.my_entry.setText("This is not a number")
            print(e)

    def rep_it(self):
        self.my_entry.setText(self.my_combo.currentText())

    def replace_it(self):
        self.my_entry.setText(str(self.my_spin.value()))

    def write_it(self):
        self.my_label2.setText(self.my_text.toPlainText())
        


app =QApplication(sys.argv)
mw = MainWindow()

sys.exit(app.exec_())