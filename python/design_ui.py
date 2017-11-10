# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import os
import serial


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(652, 527)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidget.sizePolicy().hasHeightForWidth())
        self.listWidget.setSizePolicy(sizePolicy)
        self.listWidget.setObjectName("listWidget")
        self.horizontalLayout.addWidget(self.listWidget)
        self.verticalLayoutLight = QtWidgets.QVBoxLayout()
        self.verticalLayoutLight.setObjectName("verticalLayoutLight")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.verticalLayoutLight.addWidget(self.label)
        self.lcdNumberLicht = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcdNumberLicht.setObjectName("lcdNumberLicht")
        self.verticalLayoutLight.addWidget(self.lcdNumberLicht)
        self.horizontalLayout.addLayout(self.verticalLayoutLight)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_3.addWidget(self.label_2)
        self.lcdNumberTemp = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcdNumberTemp.setObjectName("lcdNumberTemp")
        self.verticalLayout_3.addWidget(self.lcdNumberTemp)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout_7.addLayout(self.horizontalLayout)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.graphicsViewLine = PlotWidget(self.centralwidget)
        self.graphicsViewLine.setObjectName("graphicsViewLine")
        self.verticalLayout_6.addWidget(self.graphicsViewLine)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.btnBrowse = QtWidgets.QPushButton(self.centralwidget)
        self.btnBrowse.setObjectName("btnBrowse")
        self.horizontalLayout_2.addWidget(self.btnBrowse)
        self.btnReset = QtWidgets.QPushButton(self.centralwidget)
        self.btnReset.setObjectName("btnReset")
        self.horizontalLayout_2.addWidget(self.btnReset)
        self.btnPause = QtWidgets.QPushButton(self.centralwidget)
        self.btnPause.setObjectName("btnPause")
        self.horizontalLayout_2.addWidget(self.btnPause)
        self.verticalLayout_6.addLayout(self.horizontalLayout_2)
        self.verticalLayout_7.addLayout(self.verticalLayout_6)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 652, 27))
        self.menuBar.setObjectName("menuBar")
        self.menuSettings = QtWidgets.QMenu(self.menuBar)
        self.menuSettings.setObjectName("menuSettings")
        MainWindow.setMenuBar(self.menuBar)
        self.actionLight_settings = QtWidgets.QAction(MainWindow)
        self.actionLight_settings.setObjectName("actionLight_settings")
        self.actionTemp_settings = QtWidgets.QAction(MainWindow)
        self.actionTemp_settings.setObjectName("actionTemp_settings")
        self.menuSettings.addSeparator()
        self.menuSettings.addAction(self.actionLight_settings)
        self.menuSettings.addAction(self.actionTemp_settings)
        self.menuBar.addAction(self.menuSettings.menuAction())

        self.retranslateUi(MainWindow)
        self.actionLight_settings.triggered.connect(MainWindow.showDialogLight)
        self.actionTemp_settings.triggered.connect(MainWindow.showDialogTemp)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        x = os.system("ls /dev/ttyACM1")
        y = os.system("ls /dev/ttyACM0")

        if x == 0:
            arduinoTemp = serial.Serial('/dev/ttyACM1', 9600, timeout=.1)
        else:
            arduinoTemp = ""
            self.lcdNumberTemp.hide()
            self.label_2.hide()

        if y == 0:
            arduinoTemp = serial.Serial('/dev/ttyACM0', 9600, timeout=.1)
        else:
            arduinoTemp = ""
            self.lcdNumberLicht.hide()
            self.label.hide()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Licht:"))
        self.label_2.setText(_translate("MainWindow", "Temperatuur:"))
        self.btnBrowse.setText(_translate("MainWindow", "Add value"))
        self.btnReset.setText(_translate("MainWindow", "Start"))
        self.btnPause.setText(_translate("MainWindow", "Pause"))
        self.menuSettings.setTitle(_translate("MainWindow", "Settings"))
        self.actionLight_settings.setText(_translate("MainWindow", "Light settings"))
        self.actionTemp_settings.setText(_translate("MainWindow", "Temp settings"))

from pyqtgraph import PlotWidget
