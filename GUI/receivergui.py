# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 06:09:38 2021

@author: A
"""

from PyQt5.QtCore    import QCoreApplication, QObject, QThread, pyqtSignal, pyqtSlot ,Qt
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtWidgets import QPushButton, QLineEdit, QFileDialog, QCheckBox, QComboBox
import os
import serial
from serial.tools import list_ports
import matplotlib.pyplot as plt

class Processor(QObject):
    sigCount1 = pyqtSignal(int)
    sigCount2 = pyqtSignal(int)
    sigCount3 = pyqtSignal(int)
    sigCount4 = pyqtSignal(int)
    sigCount5 = pyqtSignal(int)

    def __init__(self):
        QObject.__init__(self)
        self.Receiving = False
        self.Saving = False
        self.data_list = []
        self.ser = 0
        self.filenamep = ' '
        self.ac_factor = []
        self.gy_factor = []
        self.conf = True
        self.code = ''
        self.unitNum = []

    def ProcessRunner(self):
        print('...Initiating')
        
        import time
        from numpy import int16

        
        counter1 = 0;counter1_old = 0
        counter2 = 0;counter2_old = 0
        counter3 = 0;counter3_old = 0
        counter4 = 0;counter4_old = 0
        counter5 = 0;counter5_old = 0
        t = time.perf_counter()
        print_delay = time.time()
        
        while self.Receiving:
            
            while self.conf:
                self.ser.flush()
                config = self.code
                self.ser.write(config.encode())
                time.sleep(1)
                ack = self.ser.read(self.ser.inWaiting())
                print(ack)
                if len(ack) > 3 and ack[0] == 114 and ack[1] == 114 and ack[2] == 114:
                   self.conf = False 
                
            data = (self.ser.read_until(b'\x65\x66\x67'))
            t = time.perf_counter()
            if len(data)>13:
                data_split = []
                data_split.append(data[0])
                data_split.append(data[1])
                data_split.append(int16(data[2]<<8)|data[3])
                data_split.append(int16(data[4]<<8)|data[5])
                data_split.append(int16(data[6]<<8)|data[7])
                data_split.append(int16(data[8]<<8)|data[9])
                data_split.append(int16(data[10]<<8)|data[11])
                data_split.append(int16(data[12]<<8)|data[13])
                data_split.append(t)
                self.data_list.append(data_split)
               
                if data[0] == 1:
                   counter1 += 1
                if data[0] == 2:
                   counter2 += 1          
                if data[0] == 3:
                   counter3 += 1
                if data[0] == 4:
                   counter4 += 1         
                if data[0] == 5:
                   counter5 += 1   
               #print(line)
                
            if time.time() > print_delay + 1:
               self.sigCount1.emit(counter1-counter1_old)
               counter1_old = counter1
               self.sigCount2.emit(counter2-counter2_old)
               counter2_old = counter2
               self.sigCount3.emit(counter3-counter3_old)
               counter3_old = counter3
               self.sigCount4.emit(counter4-counter4_old)
               counter4_old = counter4
               self.sigCount5.emit(counter5-counter5_old)
               counter5_old = counter5
               print_delay = time.time()
               
            QCoreApplication.processEvents()
        
        
        if self.Saving:
            print("\ndata recieved...")
            data_list_len = len(self.data_list)
            samp_num_ini = int(data_list_len/int(self.code[1]))
            print("initial number of samples (for each sensor) is ",samp_num_ini)
               
            samp_num = 0
            sens = []
            sens.append([])
            sens.append([])
            sens.append([])
            sens.append([])
            sens.append([])
            
            self.unitNum = []
            for i in range(int(self.code[1])):
                self.unitNum.append(int(self.code[i+2]))
    
            for i in range(data_list_len-len(self.unitNum)+1): 
                cek = 0                      
                for n in range(len(self.unitNum)):
                    if self.data_list[i+n][0] == self.unitNum[n]:
                        cek += 1
                if cek == len(self.unitNum):
                    for n in range(len(self.unitNum)):
                        sens[n].append(self.data_list[i+n])
                    samp_num += 1  
            
            print("the number of usable samples is ",samp_num)
            print("the number of lost samples is ",samp_num_ini-samp_num)
            

            if  len(self.filenamep) >4 :
                with open(self.filenamep, 'w') as file:
                    file.write("number\ttime\t")
                    for n in range(len(self.unitNum)): 
                            file.write("s"+self.code[n+2]+"acx\ts"+self.code[n+2]+"acy\ts"
+self.code[n+2]+"acz\ts"+self.code[n+2]+"gyx\ts"+self.code[n+2]+"gyy\ts"+self.code[n+2]+"gyz\t")                    
                    inittime = float(sens[0][0][8])
                    for i in range(len(sens[0])):
                        file.write('\n'+str(i)+'\t')
                        time = float(sens[0][i][8])-inittime
                        time = round(time,3)
                        file.write(str(time)+'\t')
                        for j in range(len(self.unitNum)):
                            for k in range(2,5):
                                file.write(str(round(sens[j][i][k]/self.ac_factor[j],4))+'\t')
                            for k in range(5,8):
                                file.write(str(round(sens[j][i][k]/self.gy_factor[j],4))+'\t')
                    
                    file.close()
                year = [2014, 2015, 2016, 2017, 2018, 2019]  
                tutorial_count = [39, 117, 111, 110, 67, 29]

                plt.plot(year, tutorial_count, color="#6c3376", linewidth=3)  
                plt.xlabel('Year')  
                plt.ylabel('Number of futurestud.io Tutorials')  
                plt.savefig('line_plot.jpg', dpi=300)  
            



    @pyqtSlot(str,list,list,str)
    def Start(self,com,acr,gyr,cod):
        print('..... Starting')
        self.ac_factor.clear()
        for i in range(int(cod[1])):
            if acr[int(cod[i+2])-1] == '±2g':
                self.ac_factor.append(16384)
            if acr[int(cod[i+2])-1] == '±4g':
                self.ac_factor.append(8192)
            if acr[int(cod[i+2])-1] == '±8g':
                self.ac_factor.append(4096) 
            if acr[int(cod[i+2])-1] == '±16g':
                self.ac_factor.append(2048) 
        
        self.gy_factor.clear()
        for i in range(int(cod[1])):
            if gyr[int(cod[i+2])-1] == '±250°/s':
                self.gy_factor.append(131)
            if gyr[int(cod[i+2])-1] == '±500°/s':
                self.gy_factor.append(65.5)
            if gyr[int(cod[i+2])-1] == '±1000°/s':
                self.gy_factor.append(32.8) 
            if gyr[int(cod[i+2])-1] == '±2000°/s':
                self.gy_factor.append(16.4) 
        self.code = cod
        self.conf = True          
        self.Receiving = True
        self.Saving = False
        self.ser = serial.Serial(com,1000000)
        self.data_list = []
        self.ProcessRunner()

    @pyqtSlot()
    def Stop(self):
        print('..... Stopping')
        self.Receiving = False
        self.Saving = False
        self.ser.close()


    @pyqtSlot(str)
    def Save(self,filenamein):
        print('..... Saving')
        self.Receiving = False
        self.Saving = True
        self.filenamep = filenamein.__str__()
        print(self.filenamep)
        self.ProcessRunner()

    @pyqtSlot()
    def RestartCount(self):
        print('..... Restarted Counting')
        if not self.Connected:
            self.Connected = True
            self.ProcessRunner()
        self.Delay = 0
        self.Count = 0
        
class MainWindow(QWidget):
    sigStart  = pyqtSignal(str,list,list,str)
    sigStop  = pyqtSignal()
    sigSave = pyqtSignal(str)
    filename =  pyqtSignal(str)
    

    def __init__(self):
        QWidget.__init__(self)

        self.setWindowTitle('Main Window')    
        self.setGeometry(150, 150, 200, 250)

        self.btnSave = QPushButton('ذخیره')
        self.btnSave.clicked.connect(self.sve)
        self.btnSave.setEnabled(False)

        self.btnStop = QPushButton('توقف')
        self.btnStop.clicked.connect(self.stp)
        self.btnStop.setEnabled(False)
        
        self.btnStart = QPushButton('شروع')
        self.btnStart.clicked.connect(self.strt)
        
        
        self.lneOutput1 = QLineEdit()
        self.lneOutput1.setFixedWidth(50)
        self.lneOutput2 = QLineEdit()
        self.lneOutput2.setFixedWidth(50)
        self.lneOutput3 = QLineEdit()
        self.lneOutput3.setFixedWidth(50)
        self.lneOutput4 = QLineEdit()
        self.lneOutput4.setFixedWidth(50)
        self.lneOutput5 = QLineEdit()
        self.lneOutput5.setFixedWidth(50)
        
        self.s0 = "QCheckBox::indicator""{""background-color : red;""border : 2px solid red;"\
        "width : 14px;""height : 14px;""border-radius : 9px;""}"
        
        self.s1 = "QCheckBox::indicator""{""background-color : green;""border : 2px solid green;"\
        "width : 14px;""height : 14px;""border-radius : 9px;""}"
        
        self.s2 = "QCheckBox::indicator""{""background-color : black;""border : 2px solid black;"\
        "width : 14px;""height : 14px;""border-radius : 9px;""}"
        
        self.led1 = QCheckBox()
        self.led1.setFixedWidth(18)
        self.led1.setStyleSheet(self.s0) 
        self.led2 = QCheckBox()
        self.led2.setFixedWidth(18)
        self.led2.setStyleSheet(self.s0)
        self.led3 = QCheckBox()
        self.led3.setFixedWidth(18)
        self.led3.setStyleSheet(self.s0)
        self.led4 = QCheckBox()
        self.led4.setFixedWidth(18)
        self.led4.setStyleSheet(self.s0)
        self.led5 = QCheckBox()
        self.led5.setFixedWidth(18)
        self.led5.setStyleSheet(self.s0)

        self.state1 = QCheckBox("سنسور 1",self)
        self.state1.setLayoutDirection(Qt.RightToLeft)
        self.state1.toggle()
        self.state1.stateChanged.connect(self.clickBox1)
        self.units = []
        self.units.append(True)
        self.state2 = QCheckBox('سنسور 2',self)
        self.state2.setLayoutDirection(Qt.RightToLeft)
        self.state2.toggle()
        self.state2.stateChanged.connect(self.clickBox2)
        self.units.append(True)
        self.state3 = QCheckBox('سنسور 3',self)
        self.state3.setLayoutDirection(Qt.RightToLeft)
        self.state3.toggle()
        self.state3.stateChanged.connect(self.clickBox3)
        self.units.append(True)
        self.state4 = QCheckBox('سنسور 4',self)
        self.state4.setLayoutDirection(Qt.RightToLeft)
        self.state4.toggle()
        self.state4.stateChanged.connect(self.clickBox4)
        self.units.append(True)
        self.state5 = QCheckBox('سنسور 5',self)
        self.state5.setLayoutDirection(Qt.RightToLeft)
        self.state5.toggle()
        self.state5.stateChanged.connect(self.clickBox5)
        self.units.append(True)
        self.txtp = QLabel('شماره‌ی پورت')
        self.txtg = QLabel('دامنه‌ ژیروسکوپ')
        self.txta = QLabel('دامنه شتاب‌سنج')
        self.txtr = QLabel('نرخ')
        self.txts = QLabel('شماره سنسور             ')



        self.space = QLabel(' ')
        
        self.portname = QComboBox()
        self.portname.setFixedWidth(90)
        comports = list_ports.comports()
        for index, comport in enumerate(comports):
            self.portname.addItem(comport.device)
        
        acc_scales = ['±2g','±4g','±8g','±16g']
        self.acc1 = QComboBox()
        self.acc1.setFixedWidth(56)
        for i in range(4):
            self.acc1.addItem(acc_scales[i])
        self.acc2 = QComboBox()
        self.acc2.setFixedWidth(56)
        for i in range(4):
            self.acc2.addItem(acc_scales[i])
        self.acc3 = QComboBox()
        self.acc3.setFixedWidth(56)
        for i in range(4):
            self.acc3.addItem(acc_scales[i])
        self.acc4 = QComboBox()
        self.acc4.setFixedWidth(56)
        for i in range(4):
            self.acc4.addItem(acc_scales[i])
        self.acc5 = QComboBox()
        self.acc5.setFixedWidth(56)
        for i in range(4):
            self.acc5.addItem(acc_scales[i])
            
        gyr_scales = ['±250°/s','±500°/s','±1000°/s','±2000°/s']
        self.gyr1 = QComboBox()
        self.gyr1.setFixedWidth(82)
        for i in range(4):
            self.gyr1.addItem(gyr_scales[i])
        self.gyr2 = QComboBox()
        self.gyr2.setFixedWidth(82)
        for i in range(4):
            self.gyr2.addItem(gyr_scales[i])
        self.gyr3 = QComboBox()
        self.gyr3.setFixedWidth(82)
        for i in range(4):
            self.gyr3.addItem(gyr_scales[i])
        self.gyr4 = QComboBox()
        self.gyr4.setFixedWidth(82)
        for i in range(4):
            self.gyr4.addItem(gyr_scales[i])
        self.gyr5 = QComboBox()
        self.gyr5.setFixedWidth(82)
        for i in range(4):
            self.gyr5.addItem(gyr_scales[i])
       
     
        
        boxv1 = QHBoxLayout()
        boxv1.setSpacing(34)
        boxv1.addWidget(self.gyr1)
        boxv1.addWidget(self.acc1)
        boxv1.addWidget(self.lneOutput1)
        boxv1.addWidget(self.led1)
        boxs1 = QHBoxLayout()
        boxs1.addLayout(boxv1) 
        boxs1.addWidget(self.state1, alignment=Qt.AlignLeft)
        
        boxv2 = QHBoxLayout()
        boxv2.setSpacing(34)
        boxv2.addWidget(self.gyr2)
        boxv2.addWidget(self.acc2)
        boxv2.addWidget(self.lneOutput2)
        boxv2.addWidget(self.led2)
        boxs2 = QHBoxLayout()
        boxs2.addLayout(boxv2) 
        boxs2.addWidget(self.state2, alignment=Qt.AlignLeft)
        
        boxv3 = QHBoxLayout()
        boxv3.setSpacing(34)
        boxv3.addWidget(self.gyr3)
        boxv3.addWidget(self.acc3)
        boxv3.addWidget(self.lneOutput3)
        boxv3.addWidget(self.led3)
        boxs3 = QHBoxLayout()
        boxs3.addLayout(boxv3) 
        boxs3.addWidget(self.state3, alignment=Qt.AlignLeft)
        
        boxv4 = QHBoxLayout()
        boxv4.setSpacing(34)
        boxv4.addWidget(self.gyr4)
        boxv4.addWidget(self.acc4)
        boxv4.addWidget(self.lneOutput4)
        boxv4.addWidget(self.led4)
        boxs4 = QHBoxLayout()
        boxs4.addLayout(boxv4) 
        boxs4.addWidget(self.state4, alignment=Qt.AlignLeft)
        
        boxv5 = QHBoxLayout()
        boxv5.setSpacing(34)
        boxv5.addWidget(self.gyr5)
        boxv5.addWidget(self.acc5)
        boxv5.addWidget(self.lneOutput5)
        boxv5.addWidget(self.led5)
        boxs5 = QHBoxLayout()
        boxs5.addLayout(boxv5) 
        boxs5.addWidget(self.state5, alignment=Qt.AlignLeft)
        
        boxtxt = QHBoxLayout()
        boxtxt.setSpacing(18)
        boxtxt.addWidget(self.txtg, alignment=Qt.AlignLeft)
        boxtxt.addWidget(self.txta, alignment=Qt.AlignLeft)
        boxtxt.addWidget(self.txtr, alignment=Qt.AlignLeft)
        boxtxt.addWidget(self.txts, alignment=Qt.AlignLeft)
        boxtxt.addStretch(1)
        
        boxbut = QVBoxLayout()
        boxbut.setSpacing(25)
        boxbut.addWidget(self.txtp)
        boxbut.addWidget(self.portname)
        boxbut.addWidget(self.btnStart)
        boxbut.addWidget(self.btnStop)
        boxbut.addWidget(self.btnSave)
        boxbut.addStretch(1)
        
        
        boxsens = QVBoxLayout()
        boxsens.setSpacing(20)
        boxsens.addLayout(boxtxt)
        boxsens.addLayout(boxs1)
        boxsens.addLayout(boxs2)
        boxsens.addLayout(boxs3)
        boxsens.addLayout(boxs4)
        boxsens.addLayout(boxs5)
        boxsens.addStretch(1)
        
        BOX = QHBoxLayout()
        BOX.setSpacing(40)
        BOX.addLayout(boxsens)
        BOX.addLayout(boxbut)
        BOX.addStretch(1)
        
        self.setLayout(BOX)
        self.EstablishThread()

    def EstablishThread(self):
      # Create the Object from Class
        self.Prcssr = Processor()
      # Assign the Database Signals to Slots
        self.Prcssr.sigCount1.connect(self.CountRecieve1)
        self.Prcssr.sigCount2.connect(self.CountRecieve2)
        self.Prcssr.sigCount3.connect(self.CountRecieve3)
        self.Prcssr.sigCount4.connect(self.CountRecieve4)
        self.Prcssr.sigCount5.connect(self.CountRecieve5)
      # Assign Signals to the Database Slots
        self.sigStart.connect(self.Prcssr.Start)
        self.sigStop.connect(self.Prcssr.Stop)
        self.sigSave.connect(self.Prcssr.Save)

      # Create the Thread
        self.ThredHolder = QThread()
      # Move the Listener to the Thread
        self.Prcssr.moveToThread(self.ThredHolder)
      # Assign the Listener Starting Function to the Thread Call
        self.ThredHolder.started.connect(self.Prcssr.ProcessRunner)
      # Start the Thread which launches Listener.Connect( )
        self.ThredHolder.start()

    
    def clickBox1(self, state):

        if state == Qt.Checked:
            self.led1.setStyleSheet(self.s0)
            self.units[0] = True
        else:
            self.led1.setStyleSheet(self.s2)
            self.units[0] = False
            
    def clickBox2(self, state):

        if state == Qt.Checked:
            self.led2.setStyleSheet(self.s0)
            self.units[1] = True
        else:
            self.led2.setStyleSheet(self.s2)
            self.units[1] = False
    
    def clickBox3(self, state):

        if state == Qt.Checked:
            self.led3.setStyleSheet(self.s0)
            self.units[2] = True
        else:
            self.led3.setStyleSheet(self.s2)
            self.units[2] = False
    
    def clickBox4(self, state):

        if state == Qt.Checked:
            self.led4.setStyleSheet(self.s0)
            self.units[3] = True
        else:
            self.led4.setStyleSheet(self.s2)
            self.units[3] = False
            
    def clickBox5(self, state):

        if state == Qt.Checked:
            self.led5.setStyleSheet(self.s0)
            self.units[4] = True
        else:
            self.led5.setStyleSheet(self.s2)
            self.units[4] = False

    
    @pyqtSlot(int)
    def CountRecieve1(self, Count):
        if self.units[0]:    
            self.lneOutput1.setText(str(Count))
            if Count == 0:
                self.led1.setStyleSheet(self.s0)
            else:
                self.led1.setStyleSheet(self.s1)
        else:
            self.lneOutput1.setText("")
    
    @pyqtSlot(int)
    def CountRecieve2(self, Count):
        if self.units[1]:
            self.lneOutput2.setText(str(Count))
            if Count == 0:
                self.led2.setStyleSheet(self.s0)
            else:
                self.led2.setStyleSheet(self.s1)
        else:
            self.lneOutput2.setText("")

    @pyqtSlot(int)
    def CountRecieve3(self, Count):
        if self.units[2]:
            self.lneOutput3.setText(str(Count))
            if Count == 0:
                self.led3.setStyleSheet(self.s0)
            else:
                self.led3.setStyleSheet(self.s1)
        else:
            self.lneOutput3.setText("")

    @pyqtSlot(int)
    def CountRecieve4(self, Count):
        if self.units[3]:
            self.lneOutput4.setText(str(Count))
            if Count == 0:
                self.led4.setStyleSheet(self.s0)
            else:
                self.led4.setStyleSheet(self.s1)
        else:
            self.lneOutput4.setText("")
        
    @pyqtSlot(int)
    def CountRecieve5(self, Count):
        if self.units[4]:
            self.lneOutput5.setText(str(Count))
            if Count == 0:
                self.led5.setStyleSheet(self.s0)
            else:
                self.led5.setStyleSheet(self.s1)
        else:
            self.lneOutput5.setText("")

    def strt(self):
        accrang = []
        accrang.append(self.acc1.currentText())
        accrang.append(self.acc2.currentText())
        accrang.append(self.acc3.currentText())
        accrang.append(self.acc4.currentText())
        accrang.append(self.acc5.currentText())
        gyrrang = []
        gyrrang.append(self.gyr1.currentText())
        gyrrang.append(self.gyr2.currentText())
        gyrrang.append(self.gyr3.currentText())
        gyrrang.append(self.gyr4.currentText())
        gyrrang.append(self.gyr5.currentText())
        configcode = ""
        count = 0
        for i in range(5):
            if self.units[i]:
                configcode += str(i+1)
                count += 1
        configcode = 'n'+str(count)+configcode
        print(configcode)
        if count > 0:
            self.sigStart.emit(self.portname.currentText(),accrang,gyrrang,configcode)
        self.btnStart.setEnabled(False)
        self.btnStop.setEnabled(True)
        self.btnSave.setEnabled(False)
        self.state1.setEnabled(False)
        self.state2.setEnabled(False)
        self.state3.setEnabled(False)
        self.state4.setEnabled(False)
        self.state5.setEnabled(False)


    def stp(self):
        self.sigStop.emit()
        self.btnStart.setEnabled(True)
        self.btnSave.setEnabled(True)
        self.btnStop.setEnabled(False)
        self.state1.setEnabled(True)
        self.state2.setEnabled(True)
        self.state3.setEnabled(True)
        self.state4.setEnabled(True)
        self.state5.setEnabled(True)
        self.lneOutput1.setText(" ")
        self.lneOutput2.setText(" ")
        self.lneOutput3.setText(" ")
        self.lneOutput4.setText(" ")
        self.lneOutput5.setText(" ")
        if self.units[0]:
            self.led1.setStyleSheet(self.s0)
        else:
            self.led1.setStyleSheet(self.s2)
        if self.units[1]:
            self.led2.setStyleSheet(self.s0)
        else:
            self.led2.setStyleSheet(self.s2)
        if self.units[2]:
            self.led3.setStyleSheet(self.s0)
        else:
            self.led3.setStyleSheet(self.s2)
        if self.units[3]:
            self.led4.setStyleSheet(self.s0)
        else:
            self.led4.setStyleSheet(self.s2)
        if self.units[4]:
            self.led5.setStyleSheet(self.s0)
        else:
            self.led5.setStyleSheet(self.s2)

    def sve(self):
        qfilename = QFileDialog.getSaveFileName(self, 'Save File', os.getenv('HOME'),
                                                'Text files (*.txt)')
        self.filename = qfilename[0]
        print(self.filename)
        self.sigSave.emit(self.filename)



if __name__ == '__main__':
    MainThred = QApplication([])

    MainApplication = MainWindow()
    MainApplication.show()

    MainThred.exec()
