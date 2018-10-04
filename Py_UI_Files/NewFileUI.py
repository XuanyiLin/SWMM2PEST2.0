# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'NewFileUI.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(960, 700)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Images/EPA1.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setGeometry(QtCore.QRect(410, 550, 150, 47))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(10)
        self.startButton.setFont(font)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("Images/Go.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.startButton.setIcon(icon1)
        self.startButton.setDefault(True)
        self.startButton.setObjectName("startButton")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(350, 20, 259, 256))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap("Images/EPA1.png"))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(60, 400, 400, 33))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.lineEdit_inputFile = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_inputFile.setGeometry(QtCore.QRect(60, 450, 650, 41))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(10)
        self.lineEdit_inputFile.setFont(font)
        self.lineEdit_inputFile.setReadOnly(True)
        self.lineEdit_inputFile.setObjectName("lineEdit_inputFile")
        self.btnBrowse = QtWidgets.QPushButton(self.centralwidget)
        self.btnBrowse.setGeometry(QtCore.QRect(750, 450, 150, 41))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(10)
        self.btnBrowse.setFont(font)
        self.btnBrowse.setDefault(False)
        self.btnBrowse.setObjectName("btnBrowse")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(400, 320, 200, 36))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 960, 38))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "SWMM2PEST"))
        self.startButton.setText(_translate("MainWindow", "Start"))
        self.label_3.setText(_translate("MainWindow", "Choose SWMM Input File (.inp):"))
        self.btnBrowse.setText(_translate("MainWindow", "Browse..."))
        self.label_4.setText(_translate("MainWindow", "SWMM2PEST"))

