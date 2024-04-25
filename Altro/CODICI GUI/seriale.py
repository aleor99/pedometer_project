import serial.tools.list_ports

ports = serial.tools.list_ports.comports()
serialInst = serial.Serial()

portList = []

for onePort in ports:
    portList.append(str(onePort))
    print(str(onePort))

#val = input("select Port: COM ")

for x in range(0,len(portList)):
    if "KitProg USB-UART" in portList[x]:
        port_number=portList[x].split()
        portVar = port_number[0]
    #if portList[x].startswith("COM" + str(val)):
    #    portVar = "COM"+str(val)

serialInst.baudrate = 9600;
serialInst.port = portVar
serialInst.open()

while True:
    if serialInst.inWaiting():
        packet = serialInst.readline()
        print(packet.decode('utf'))
