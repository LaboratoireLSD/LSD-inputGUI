'''
Created on 2010-01-18

@author:  Mathieu Gagnon
@contact: mathieu.gagnon.10@ulaval.ca
@organization: Universite Laval

@license
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 
'''
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'wizstart.ui'
#
# Created: Mon Jan 18 10:46:29 2010
#      by: PyQt4 UI code generator 4.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    '''
    This class was automatically generated using a qtdesigner .ui file and qt's pyuic4 program.
    It is the first shown page of the wizard
    '''
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(640, 480)
        self.parent = Dialog.parent()
        self.filePath = QtCore.QString("")
        self.pushButton_3 = QtGui.QPushButton(Dialog)
        self.pushButton_3.setEnabled(False)
        self.pushButton_3.setGeometry(QtCore.QRect(100, 192, 92, 28))
        self.pushButton_3.setObjectName("pushButton_3")
        self.lineEdit = QtGui.QLineEdit(Dialog)
        self.lineEdit.setEnabled(False)
        self.lineEdit.setGeometry(QtCore.QRect(200, 190, 113, 31))
        self.lineEdit.setObjectName("lineEdit")
        self.radioButton_2 = QtGui.QRadioButton(Dialog)
        self.radioButton_2.setGeometry(QtCore.QRect(50, 110, 291, 23))
        self.radioButton_2.setObjectName("radioButton_2")
        self.radioButton = QtGui.QRadioButton(Dialog)
        self.radioButton.setGeometry(QtCore.QRect(50, 150, 351, 23))
        self.radioButton.setObjectName("radioButton")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        self.connect(self.radioButton,QtCore.SIGNAL("toggled(bool)"),self.changeEnableState)
        self.radioButton_2.setChecked(True)
        self.connect(self.pushButton_3,QtCore.SIGNAL("clicked()"),self.openDialog)
        self.connect(self.lineEdit,QtCore.SIGNAL("textChanged(QString)"),self.updateFilePath)
        
    def openDialog(self):
        '''
        @summary Opens a File dialog so the user can choose an already existing simulation
        '''
        xmlPath = ""
        self.filePath = QtGui.QFileDialog.getOpenFileName(self, self.tr("Open XML parameters file"),
                                                                  xmlPath, self.tr("LSD Files (*.lsd);;XML files (*.xml);;All files (*);;"))
        self.lineEdit.setText(self.filePath)
        
    def retranslateUi(self, Dialog):
        Dialog.setSubTitle(QtGui.QApplication.translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Welcome to the LSD Simulation Dashboard wizard. The next steps will help you create a valid simulation. First, choose if you want to define a new simulation or start from an existing simulation.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_3.setText(QtGui.QApplication.translate("Dialog", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_2.setText(QtGui.QApplication.translate("Dialog", "Start a new simulation", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton.setText(QtGui.QApplication.translate("Dialog", "Start from an existing simulation", None, QtGui.QApplication.UnicodeUTF8))
        Dialog.setTitle("Simulation")
        
    def changeEnableState(self,state):
        '''
        @summary Disable/Enable pushButton/lineEdit
        '''
        self.lineEdit.setEnabled(state)
        self.pushButton_3.setEnabled(state)

    def updateFilePath(self,newText):
        '''
        @summary Update simulation configuration file's path
        '''
        self.filePath = newText
        
    def validatePage(self):
        '''
        @summary Reimplemented from QWizardPage.validatePage(self)
        Called automatically when the page is about to be changed
        '''
        if self.radioButton.isChecked():
            if self.filePath.isEmpty():
                errorDialog = QtGui.QErrorMessage(self)
                errorDialog.showMessage("File Path is empty!")
                return False
            try:
                self.parent.topWObject.openParametersFile(QtCore.QString(self.filePath))
            except AssertionError:
                errorDialog = QtGui.QErrorMessage(self)
                errorDialog.showMessage("Invalid parameters File")
                return False
            return True
        else:
            self.parent.topWObject.openParametersFile(QtCore.QString("util/parameters_file_template.xml"))
        return True
    