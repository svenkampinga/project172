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
maxTemp = 25

state = "running"



class MyThread(QtCore.QThread):
    trigger = QtCore.pyqtSignal(tuple)

    def __init__(self, parent=None):
        super(MyThread, self).__init__(parent)

    def setup(self, thread_no):
        self.thread_no = thread_no

    def run(self):
        z = 0
        while True:
            if state == "running":
                if z < 30:
                    z += 5
                elif z > 30:
                    z -= 5






                arduinoDataLicht = (arduinoLicht.readline()[:-2]).decode('utf-8')
                if (arduinoTemp != ""):
                    arduinoDataTemp = (arduinoTemp.readline()[:-2]).decode('utf-8')
                    print(arduinoDataTemp)
                else:
                    arduinoDataTemp = ""

                print(arduinoDataLicht)


                #print(data)
                if arduinoDataLicht != "":
                    time.sleep(0.5)  # random sleep to imitate working

                    randTotaal = (1, arduinoDataLicht)
                    self.trigger.emit(randTotaal)
                elif arduinoDataTemp != "":
                    time.sleep(0.5)  # random sleep to imitate working

                    randTotaal = (2, arduinoDataTemp)
                    self.trigger.emit(randTotaal)
                else:
                    h = 0

class ExampleApp(QtWidgets.QMainWindow, design_ui.Ui_MainWindow):
    def __init__(self):
        # Explaining super is out of the scope of this article
        # So please google it if you're not familar with it
        # Simple reason why we use it here is that it allows us to
        # access variables, methods etc in the design.py file
        super(self.__class__, self).__init__()
        self.setupUi(self)  # This is defined in design.py file automatically
        # It sets up layout and widgets that are defined
        self.btnReset.clicked.connect(self.start_threads)  # When the button is pressed
        self.btnBrowse.clicked.connect(self.button)  # When the button is pressed
        self.btnPause.clicked.connect(self.button)  # When the button is pressed
        self.menuSettings.addAction(self.actionLight_settings)

        self.graphicsViewLine.setTitle('My Graph')
        self.graphicsViewLine.setLabel('bottom', '')
        self.graphicsViewLine.setLabel('left', '')

        self.lcdNumberLicht.display(0)
        self.lcdNumberTemp.display(0)

    def start_threads(self):
        self.threads = []  # this will keep a reference to threads
        thread = MyThread(self)  # create a thread
        thread.trigger.connect(self.update_text)  # connect to it's signal
        thread.setup([0, 1])  # just setting up a parameter
        thread.start()  # start the thread
        self.threads.append(thread)  # keep a reference

    def update_text(self, rand):
        global seriesLicht, seriesTemp, line, randLicht, randTemp

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

            if (int(randLicht) > maxLight):
                arduinoLicht.write("2".encode())
            elif (int(randLicht) > 20):
                arduinoLicht.write("1".encode())
            else:
                arduinoLicht.write("0".encode())

        if int(randTemp) != 0:
            seriesTemp.append(int(randTemp))
            self.lcdNumberTemp.display(randTemp)
            self.graphicsViewLine.plot(seriesTemp)
            self.listWidget.addItem("Temp : " + str(randTemp))  # add file to the listWidget

            if (int(randTemp) > 400):
                arduinoTemp.write("2".encode())
            elif (int(randTemp) > 200):
                arduinoTemp.write("1".encode())
            else:
                arduinoTemp.write("0".encode())
        else:
            h = 0

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
            self.le.setText(str(text))



    def buttonPause(self):
        global state
        if state == "running":
            state = "pause"
        else:
            state = "running"

    def button(self):
        global seriesLicht, seriesTemp, line

        randLicht = randint(0, 9)
        randTemp = randint(0, 9)

        seriesLicht.append(randLicht)
        seriesTemp.append(randTemp)

        line = self.graphicsViewLine

        self.graphicsViewLine.plot(seriesLicht)
        self.graphicsViewLine.plot(seriesTemp)
        self.lcdNumberLicht.display(randLicht)
        self.lcdNumberTemp.display(randTemp)
        self.listWidget.addItem("Licht : " + str(randLicht))  # add file to the listWidget
        self.listWidget.addItem("Temp : " + str(randTemp))  # add file to the listWidget

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
