# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Form.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def __init__(self):
        self.horizontalLayoutWidget = QtWidgets.QWidget()
        self.horizontalLayoutWidget.setMinimumWidth(650)
        self.horizontalLayoutWidget.setMaximumWidth(650)
        self.FormInfoLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.FormInfoLayout.setContentsMargins(0, 0, 0, 0)
        # self.FormInfoLayout.setObjectName("FormInfoLayout")

        self.lineEdit_LowerLimit = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.lineEdit_LowerLimit.setText("")
        self.lineEdit_LowerLimit.setMinimumWidth(185)
        self.lineEdit_LowerLimit.setMaximumWidth(185)
        self.lineEdit_LowerLimit.setPlaceholderText("Lower Limit")
        self.lineEdit_LowerLimit.setObjectName("lineEdit_LowerLimit")
        self.FormInfoLayout.addWidget(self.lineEdit_LowerLimit)

        self.lineEdit_UpperLimit = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.lineEdit_UpperLimit.setText("")
        self.lineEdit_UpperLimit.setMinimumWidth(185)
        self.lineEdit_UpperLimit.setMaximumWidth(185)
        self.lineEdit_UpperLimit.setPlaceholderText("Upper Limit")
        self.lineEdit_UpperLimit.setObjectName("lineEdit_UpperLimit")
        self.FormInfoLayout.addWidget(self.lineEdit_UpperLimit)

        self.checkBox_Fixed = QtWidgets.QCheckBox(self.horizontalLayoutWidget)
        self.checkBox_Fixed.setMinimumSize(QtCore.QSize(0, 0))
        self.checkBox_Fixed.setMaximumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.checkBox_Fixed.setFont(font)
        self.checkBox_Fixed.setText("Fixed")
        self.checkBox_Fixed.setObjectName("checkBox_Fixed")
        self.FormInfoLayout.addWidget(self.checkBox_Fixed)

        self.checkBox_None = QtWidgets.QCheckBox(self.horizontalLayoutWidget)
        self.checkBox_None.setMinimumSize(QtCore.QSize(100, 0))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.checkBox_None.setFont(font)
        self.checkBox_None.setText("Calibrate")
        self.checkBox_None.setObjectName("checkBox_None")
        self.FormInfoLayout.addWidget(self.checkBox_None)







