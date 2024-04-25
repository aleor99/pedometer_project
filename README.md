# **FINAL ASSIGNMENT**

## **Electronic Technologies and Sensors Laboratory (Prof. Cerveri Pietro)**

**Students**:

Simone Lambiase

Miriam Morelli

Alessandro Ortu

**Tutor**:
Luca Marsilio

### **Description**

In this project, we designed and developed a wearable system that measures physical activity parameters from the 3-axis accelerometer LIS3DH.

The main objectives of this system are:

- Acquire data from the accelerometer using built-in FIFO to reduce the load of the CPU.
- Process and calibrate the raw data in order to obtain steps, calories, distance and speed.
- Provide a GUI (Graphical User Interface) where data can be displayed in real-time.
- Add some features to GUI and Hardware in order to make it more interactive and customizable.

![Semplice schematico del funzionamento](https://github.com/ltebs-polimi/AY2223_II_Project-5/blob/main/Altro/foto_project.png)

### **Requirements**

**Version**: *PSoC Creator 4.4*

**Board**: *PSoC 5LP CY8C5888LTI-LP097 in QFN68 format* [PSoC Creator](https://www.infineon.com/cms/en/design-support/tools/sdk/psoc-software/psoc-creator/)

**Additional Hardware**:

1. LIS3DH breakout board [LIS3DH Datasheet](https://www.st.com/resource/en/datasheet/lis3dh.pdf)
1. Bluetooth HC-06 [HC-06 Datasheet](https://www.st.com/resource/en/datasheet/lis3dh.pdf)
1. SSD1306 OLED by Adafruit [Adafruit Oled](https://www.adafruit.com/product/326)
1. Two external LEDs (Red and Green)
1. Button (Reset)
1. One LM7805 and two Capacitors in order to reduce the voltage from a 9 V battery to 5 V
1. One 9V battery
1. Three Resistors (two for the leds and one for the button)
2. Switch (ON/OFF)

(as an alternative to steps 6,7 and 9 , a powerbank can be used)

Additional softwares tools: Cool Term, Bridge Control Panel

## **Hardware**
![Foto Hardware](https://github.com/ltebs-polimi/AY2223_II_Project-5/blob/main/Altro/foto_H.jpg)
## **System Configuration**
Switch on the device via the switch (or alternatively connect the powerbank to the PSoC), check that the OLED turns on and that the Bluetooth starts flashing rapidly indicating that the device is ready to be connected. Connect the device to the PC via Bluetooth by selecting the HC-06 device and entering the password 1234. Once connected open the interface and follow the following steps:
1. Select your profile by going to "User Page", in the upper bar where you find "Search User" select your first and last name, click Load and then Save. Alternatively, register via the "Click here to register" button and then click "Save".
2. Select "Data Analysis", on this page you can view the data from the PSoC. Click "Search" and wait for the green text saying "Device found" to appear, then click "Run" to start the monitoring activity. At the bottom you will be able to see information about your physical activity, which are also shown on the OLED mounted on the device (you can switch from a parameter to the other by pressing the button on the device). At the end of monitoring, click the "Disconnect" button to disconnect.
3. In order to view and manage your data, go to "Database", on this page you can search for a user by name and by double-clicking on a row in the table, you will be able to see graphs of activity trends over time. You can also export your data to a .csv file by clicking on "Export Data".

***Additional Features***

There are two additional buttons:
- *Question mark button*: this page allows you to request help in using the interface or report possible errors. All required information must be entered and then click Send Request. 
- *Info Button*: this page shows information about the project and is the homepage of the GUI.

All operations performed on the GUI will be accompanied by warnings confirming the operation performed or helping to perform the desired operation. It is also possible to reduce the sidebar by clicking on the three lines on the left-hand side of the top bar.

### **Repository Organisation**
In the GUI FINALE folder you can find all the files necessary for the GUI, in particular:
- "Interfaccia_finale": contains the core code relating to the operation of the interface.
- "database_conn": contains the functions for connecting to the database via sqlite3.
- "dati_utenti.db": is the database (you can use DB Browser(SQLite) to open it).
- "icone_rc": contains the icons used in the interface.
- "nuova.ui": file containing the interface graphics.
- "costanti": a separate file with all the constants used.

In the PSOC folder there are all files pertaining to the PSoC firmware (divided in 2 versions, one where only the steps are shown on the OLED, the other with all the parameters, both working) and in the PC finale folder all files pertaining to the PCB.
Also, the case folder is divided in 2 folders: one for the case with the battery and one for the case with the powerbank.
Finally, in the "Altro" folder there are some old codes if you find them useful.

### **References**
- [PubMed link 1](https://pubmed.ncbi.nlm.nih.gov/25749552/)
- [PubMed link 2](https://pubmed.ncbi.nlm.nih.gov/24656871/)
- [Paper by Neil Zhao](https://www.analog.com/media/en/technical-documentation/technical-articles/pedometer.pdf)
- Course Notes by Pietro Cerveri

### **Final Presentation**
Link to the powerpoint final presentation and the videos of the demo: https://polimi365-my.sharepoint.com/:f:/g/personal/10675266_polimi_it/Ek28DVU131dCtsj3aeqviJQB96iRDbKKIaKprMv0jeDfnw?e=240ltB 


