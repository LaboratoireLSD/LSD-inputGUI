"""
.. module:: Wiz_Library

.. codeauthor:: Mathieu Gagnon <mathieu.gagnon.10@ulaval.ca>

:Created on: 2010-01-18

"""

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'wizstart2.ui'
#
# Created: Mon Jan 18 10:46:39 2010
#      by: PyQt4 UI code generator 4.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from util.DocPrimitive import PrimitiveDict
import os

class Ui_Dialog(object):
    '''
    This class was automatically generated using a qtdesigner .ui file and qt's pyuic4 program.
    It is a dialog allowing a user to see available libraries(.xsd files) and select them for the current project
    '''
    def setupUi(self, Dialog):
        """
        Creates the widgets that will be displayed on the frame.
        """
        Dialog.setObjectName("Dialog")
        Dialog.resize(640, 480)
        self.parent = Dialog.parent()
        
        self.listWidget = QtGui.QListWidget(Dialog)
        self.listWidget.setGeometry(QtCore.QRect(50, 120, 561, 91))
        self.listWidget.setObjectName("listWidget")
        self.listWidget_2 = QtGui.QListWidget(Dialog)
        self.listWidget_2.setGeometry(QtCore.QRect(50, 250, 561, 91))
        self.listWidget_2.setObjectName("listWidget_2")
        self.listWidget.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.listWidget_2.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(50, 90, 141, 18))
        self.label.setObjectName("label")
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(50, 230, 141, 18))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(50, 360, 191, 18))
        self.label_3.setObjectName("label_3")
        self.pushButton_3 = QtGui.QPushButton(Dialog)
        self.pushButton_3.setGeometry(QtCore.QRect(250, 355, 92, 28))
        self.pushButton_3.setObjectName("pushButton_3")
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(50, 10, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setWeight(75)
        font.setBold(True)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.lineEdit = QtGui.QLineEdit(Dialog)
        self.lineEdit.setEnabled(True)
        self.lineEdit.setGeometry(QtCore.QRect(350, 355, 113, 31))
        self.lineEdit.setObjectName("lineEdit")
        self.listWidget.setDragEnabled(True)
        self.listWidget_2.setDragEnabled(True)
        self.pushButton_up = QtGui.QPushButton(Dialog)
        self.pushButton_up.setGeometry(QtCore.QRect(290,220,20,20))
        self.pushButton_down = QtGui.QPushButton(Dialog)
        self.pushButton_down.setGeometry(QtCore.QRect(250,220,20,20))
        self.pushButton_up.setIcon(QtGui.QIcon("../img/actions/go-up.png"))
        self.pushButton_down.setIcon(QtGui.QIcon("../img/actions/go-down.png"))
        
        self.listWidget_2.setAcceptDrops(True)
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
#       
        self.connect(self.pushButton_3,QtCore.SIGNAL("clicked()"),self.openDialog)
        self.connect(self.pushButton_down,QtCore.SIGNAL("clicked()"),self.addNewItem)
        self.connect(self.pushButton_up,QtCore.SIGNAL("clicked()"),self.removeItem)

    def retranslateUi(self, Dialog):
        '''
        Function allowing naming of the different labels regardless of app's language.
        
        :param Dialog: Visual frame to translate
        :type Dialog: :class:`.MainWizard.Library_dialog`
        '''
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "LSD - Wizard", None, QtGui.QApplication.UnicodeUTF8))
        Dialog.setSubTitle(QtGui.QApplication.translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">First, choose the libraries you want to use for your simulation using drag and drop.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        __sortingEnabled = self.listWidget.isSortingEnabled()
        self.listWidget.setSortingEnabled(False)
        self.listWidget.setSortingEnabled(__sortingEnabled)
        __sortingEnabled = self.listWidget_2.isSortingEnabled()
        self.listWidget_2.setSortingEnabled(False)
        self.listWidget_2.setSortingEnabled(__sortingEnabled)
        self.label.setText(QtGui.QApplication.translate("Dialog", "Available libraries :", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Used libraries :", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Add library from file system :", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_3.setText(QtGui.QApplication.translate("Dialog", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.setTitle("Libraries")

    def initializePage(self):
        '''
        Reimplemented from QWizardPage.initializePage(self).
        
        Called automatically when the page is shown.
        '''
        self.listWidget.clear()
        self.listWidget_2.clear()
        self.projectDir = self.parent.topWObject.folderPath
        pmtDict = PrimitiveDict()
        for files in os.listdir("util/XSD"):
            if os.path.splitext(files)[1] == ".xsd":
                newListWidgetItem = QtGui.QListWidgetItem()
                newListWidgetItem.setData(QtCore.Qt.DisplayRole, os.path.splitext(files)[0])
                #If it's a definition library, do not show
                if os.path.splitext(files)[0] in ["PMT","GUI","BaseTypes"]:
                    continue
                if self.projectDir + "XSD/" + files in pmtDict.dictPrimitives.keys():
                    self.listWidget_2.addItem(newListWidgetItem)
                    newListWidgetItem.setToolTip(os.path.abspath(self.projectDir+"XSD/"+files))
                else:
                    self.listWidget.addItem(newListWidgetItem)
                    newListWidgetItem.setToolTip(os.path.abspath("util/"+"XSD/"+files))
                    
    def openDialog(self):
        '''
        Opens a dialog so the user can add libraries that weren't found by the initializePage function.
        '''
        xmlPath = ""
        self.filePath = QtGui.QFileDialog.getOpenFileName(self, self.tr("Open XML parameters file"),
                                                                  xmlPath, self.tr("XSD files (*.xsd);;All files (*);;"))
        if self.filePath and self.filePath.rsplit(".")[0] == "xsd":
            self.lineEdit.setText(self.filePath)
            newListWidgetItem = QtGui.QListWidgetItem()
            newListWidgetItem.setData(QtCore.Qt.DisplayRole, os.path.split(os.path.splitext(self.filePath)[0])[1])
            newListWidgetItem.setToolTip(os.path.abspath(self.filePath))
            self.listWidget_2.addItem(newListWidgetItem)
        
    def validatePage(self):
        '''
        Reimplemented from QWizardPage.validatePage(self).
        Called automatically when the page is about to be changed.
        
        :return: Boolean. Always True if no error occurred.
        '''
        pmtDict = PrimitiveDict()
        for i in range(self.listWidget_2.count()):
            if self.projectDir + "XSD/" + self.listWidget_2.item(i).data(QtCore.Qt.DisplayRole) + ".xsd" not in pmtDict.dictPrimitives.keys():
                dictLocation = os.path.relpath(self.listWidget_2.item(i).data(QtCore.Qt.ToolTipRole))
                self.parent.topWObject.openXSDdictFile(dictLocation)
        for i in range(self.listWidget.count()):
            if self.projectDir + "XSD/" + self.listWidget.item(i).data(QtCore.Qt.DisplayRole) + ".xsd" in pmtDict.dictPrimitives.keys():
                pmtDict.removeDictFromFilePath(self.projectDir+"XSD/"+self.listWidget.item(i).data(QtCore.Qt.DisplayRole)+".xsd")
        return True
    
    def addNewItem(self):
        '''
        Adds a library to the selected libraries list.
        '''
        if self.listWidget.selectedItems():            
            for i in self.listWidget.selectedItems():
                self.listWidget_2.addItem(self.listWidget.takeItem(self.listWidget.row(i)))

    def removeItem(self):
        '''
        Removes a library from the selected libraries list.
        '''
        if self.listWidget_2.selectedItems():
            for i in self.listWidget_2.selectedItems():
                self.listWidget.addItem(self.listWidget_2.takeItem(self.listWidget_2.row(i)))
                
