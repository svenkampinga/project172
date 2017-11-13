from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtCore import QCoreApplication, QObject, QRunnable, QThread, QThreadPool, pyqtSignal
import sys  # We need sys so that we can pass argv to QApplication

import pyqtgraph as pg
from random import randint
import numpy as np
import time
import serial

import math

import design_ui  # This file holds our MainWindow and all design related things

# it also keeps events etc that we defined in Qt Designer
import os  # For listing directory methods

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

seriesLicht = []
seriesTemp = []

maxLight = 40
maxTemp = 152

state = 0

firstDown = True
firstUp = False

firstDownTemp = True
firstUpTemp = False

triggerDownLicht = False
triggerUpLicht = False
triggerDownTemp = False
triggerUpTemp = False



class MyThread(QtCore.QThread):
    trigger = QtCore.pyqtSignal(tuple)

    def __init__(self, parent=None):
        super(MyThread, self).__init__(parent)

    def setup(self, thread_no, temp, light):
        self.thread_no = thread_no
        self.serialY = temp
        self.serialX = light

    def run(self):
        z = 0
        while True:

            if(self.serialY == 0):
                arduinoLicht = serial.Serial('/dev/ttyACM0', 9600, timeout=.1)
                arduinoDataLicht = (arduinoLicht.readline()[:-2]).decode('utf-8')
                print(arduinoDataLicht)


            if (self.serialX == 0):
                arduinoTemp = serial.Serial('/dev/ttyACM1', 9600, timeout=.1)
                arduinoDataTemp = (arduinoTemp.readline()[:-2]).decode('utf-8')
                arduinoTemp.write("0".encode())
                print(arduinoDataTemp)
            else:
                arduinoDataTemp = ""




            #print(data)
            if self.serialY == 0:
                if arduinoDataLicht != "":
                    time.sleep(1.0)  # random sleep to imitate working

                    randTotaal = (1, arduinoDataLicht)
                    self.trigger.emit(randTotaal)
            if self.serialX == 0:
                if arduinoDataTemp != "":
                    time.sleep(1.0)  # random sleep to imitate working

                    randTotaal = (2, arduinoDataTemp)
                    self.trigger.emit(randTotaal)

class ExampleApp(QtWidgets.QMainWindow, design_ui.Ui_MainWindow):
    def __init__(self):
        # Explaining super is out of the scope of this article
        # So please google it if you're not familar with it
        # Simple reason why we use it here is that it allows us to
        # access variables, methods etc in the design.py file
        super(self.__class__, self).__init__()
        self.setupUi(self)  # This is defined in design.py file automatically
        # It sets up layout and widgets that are defined
        self.btnRolUit.clicked.connect(self.buttonRolUit)  # When the button is pressed
        self.btnRolIn.clicked.connect(self.buttonRolIn)  # When the button is pressed
        self.menuSettings.addAction(self.actionLight_settings)

        self.graphicsViewLine.setTitle('My Graph')
        self.graphicsViewLine.setLabel('bottom', '')
        self.graphicsViewLine.setLabel('left', '')

        self.lcdNumberLicht.display(0)
        self.lcdNumberTemp.display(0)
        self.start_threads()

        if(self.serialX != 0 and self.serialY != 0):
            self.showDialogError()

    def start_threads(self):
        temp = self.serialY
        light = self.serialX
        self.threads = []  # this will keep a reference to threads
        thread = MyThread(self)  # create a thread
        thread.trigger.connect(self.update_text)  # connect to it's signal
        thread.setup([0, 1], temp, light)  # just setting up a parameter
        thread.start()  # start the thread
        self.threads.append(thread)  # keep a reference

    def update_text(self, rand):
        global seriesLicht, seriesTemp, line, randLicht, randTemp, state, arduinoTemp, firstUp, firstDown, firstUpTemp, firstDownTemp

        global triggerDownLicht, triggerUpLicht, triggerDownTemp, triggerUpTemp
        [id, data] = rand

        randLicht = 0
        randTemp = 0

        line = self.graphicsViewLine

        if id == 1:
            randLicht = math.ceil(float(data) / 10)
        elif id == 2:
            randTemp = math.ceil(float(data))

        if int(randLicht) != 0:
            seriesLicht.append(int(randLicht))
            self.lcdNumberLicht.display(randLicht)
            self.graphicsViewLine.plot(seriesLicht)
            self.listWidget.addItem("Licht : " + str(randLicht))  # add file to the listWidget

            if (int(randLicht) > maxLight and  self.serialY == 0):

                triggerDownLicht = True

            elif (int(randLicht) < maxLight and  self.serialY == 0):

                triggerDownLicht = False




        if int(randTemp) != 0:
            seriesTemp.append(int(randTemp))
            self.lcdNumberTemp.display(randTemp)
            self.graphicsViewLine.plot(seriesTemp)
            self.listWidget.addItem("Temp : " + str(randTemp))  # add file to the listWidget


            if (int(randTemp) > maxTemp and  self.serialX == 0):

                triggerDownTemp = True


            elif (int(randTemp) < maxTemp and  self.serialX == 0):

                triggerDownTemp = False


        if(triggerDownLicht or triggerDownTemp):
            arduinoLicht = serial.Serial('/dev/ttyACM0', 9600, timeout=.1)
            if(firstDownTemp or firstDown):
                firstDown = False
                firstUp = True
                firstDownTemp = False
                firstUpTemp = True
                arduinoLicht.write("2".encode())
                arduinoLicht.write("2".encode())
            else:
                arduinoLicht.write("1".encode())

        else:
            arduinoLicht = serial.Serial('/dev/ttyACM0', 9600, timeout=.1)
            if (firstUpTemp or firstUp):
                firstUp = False
                firstDown = True
                firstDownTemp = True
                firstUpTemp = False
                arduinoLicht.write("2".encode())
                arduinoLicht.write("2".encode())
            else:
                arduinoLicht.write("0".encode())



    def showDialogLight(self):

        text, ok = QtGui.QInputDialog.getText(self, 'Light settings',
                                              'Enter value:')

        if ok:
            global maxLight
            maxLight = int(text)

    def showDialogTemp(self):

        text, ok = QtGui.QInputDialog.getText(self, 'Temperature settings',
                                              'Enter value:')

        if ok:
            global maxTemp
            maxTemp = int(text)

    def showDialogError(self):

        choice = QtGui.QMessageBox.warning(self, 'Error!',
                                            "Check if you have at least 1 arduino connected",
                                            QtGui.QMessageBox.Ok)
        if choice == QtGui.QMessageBox.Ok:
            sys.exit()
        else:
            pass

    def buttonRolUit(self):
        global triggerDownTemp, triggerDownLicht

        triggerDownTemp = True
        triggerDownLicht = True

    def buttonRolIn(self):
        global triggerDownTemp, triggerDownLicht

        triggerDownTemp = False
        triggerDownLicht = False

    def reset(self):
        global x
        global a
        a = [0, 1]
        x = 0
        self.graphicsView.plot(a)
        self.graphicsView.clear()
        self.listWidget.clear()

def main():
    app = QtWidgets.QApplication(sys.argv)  # A new instance of QApplication
    form = ExampleApp()  # We set the form to be our ExampleApp (design)
    form.show()  # Show the form
    app.exec_()

if __name__ == '__main__':  # if we're running file directly and not importing it
    main()  # run the main function
