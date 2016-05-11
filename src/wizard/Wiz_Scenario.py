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

# Form implementation generated from reading ui file 'Wiz10.ui'
#
# Created: Mon Jan 18 10:50:47 2010
#      by: PyQt4 UI code generator 4.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from editor.mainEditorFrame import MainEditorWindow
from model.baseTreatmentsModel import BaseTreatmentsModel
class Ui_Dialog(object):
    '''
    This class was automatically generated using a qtdesigner .ui file and qt's pyuic4 program.
    It is a dialog allowing a user to manage scenarios of a simulation
    '''
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(640, 480)
        self.parent = Dialog.parent()
        self.horizontalLayoutWidget_2 = QtGui.QWidget(Dialog)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(100, 300, 469, 61))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_2.setSpacing(40)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButton_5 = QtGui.QPushButton(self.horizontalLayoutWidget_2)
        self.pushButton_5.setObjectName("pushButton_5")
        self.horizontalLayout_2.addWidget(self.pushButton_5)
        self.pushButton_3 = QtGui.QPushButton(self.horizontalLayoutWidget_2)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout_2.addWidget(self.pushButton_3)
        self.textBrowser = QtGui.QTextBrowser(Dialog)
        self.textBrowser.setEnabled(True)
        self.textBrowser.setGeometry(QtCore.QRect(50, 40, 551, 50))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(237, 236, 235))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(237, 236, 235))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        self.textBrowser.setPalette(palette)
        self.textBrowser.setAutoFillBackground(True)
        self.textBrowser.setFrameShape(QtGui.QFrame.NoFrame)
        self.textBrowser.setLineWidth(0)
        self.textBrowser.setObjectName("textBrowser")
        self.pushButton = QtGui.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(100, 400, 151, 28))
        self.pushButton.setObjectName("pushButton")
        self.listWidget = QtGui.QTableView(Dialog)
        self.listWidget.setGeometry(QtCore.QRect(50, 90, 551, 192))
        self.listWidget.setObjectName("listWidget")
        self.horizontalLayoutWidget = QtGui.QWidget(Dialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(410, 390, 192, 80))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(50, 10, 251, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setWeight(75)
        font.setBold(True)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        self.connect(self.pushButton,QtCore.SIGNAL("clicked()"),self.openTreeEditor)
        self.connect(self.pushButton_5,QtCore.SIGNAL("clicked()"),self.addScenario)
        self.connect(self.pushButton_3,QtCore.SIGNAL("clicked()"),self.deleteScenario)
    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "LSD - Wizard", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_5.setText(QtGui.QApplication.translate("Dialog", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_3.setText(QtGui.QApplication.translate("Dialog", "Delete", None, QtGui.QApplication.UnicodeUTF8))
        self.textBrowser.setHtml(QtGui.QApplication.translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Add, delete or edit scenarios.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Dialog", "Open tree editor", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Dialog", "Scenarios", None, QtGui.QApplication.UnicodeUTF8))

    def initializePage(self):
        '''
        @summary Reimplemented from QWizardPage.initializePage(self)
        Called automatically when the page is shown
        '''
        self.listWidget.setModel(self.parent.topWObject.simTab.tableView.model())
        self.listWidget.setItemDelegate(self.parent.topWObject.simTab.tableView.itemDelegate())

    def openTreeEditor(self):
        '''
        @summary Opens the tree editor
        '''
        if self.listWidget.currentIndex().isValid():
            baseTrModel = BaseTreatmentsModel()
            treeName = baseTrModel.getScenarioLabel(baseTrModel.scenarioModelMapper[self.listWidget.currentIndex().row()])["indProcess"]
            tree = baseTrModel.getTreatmentTree(treeName)
            if tree:
                editor = MainEditorWindow(tree.toElement().elementsByTagName("PrimitiveTree").item(0).firstChild(),self.parent.topWObject,self.listWidget.model().getTreatmentNameFromIndex(self.listWidget.currentIndex()))
                editor.setWindowModality(QtCore.Qt.WindowModal)
                editor.show()
            
    def addScenario(self):
        '''
        @summary Add a scenario to the scenario list
        '''
        if self.listWidget.selectedIndexes() and len(self.listWidget.selectedIndexes()) == 1:
            self.listWidget.model().insertRow(self.listWidget.selectedIndexes()[0].row(), self.listWidget.rootIndex(), True)
            return
        self.listWidget.model().insertRow(self.listWidget.model().rowCount(), self.listWidget.rootIndex(),True)   
         
    def deleteScenario(self):
        '''
        @summary REmove a scenario from the scenario list
        '''
        if self.listWidget.currentIndex().isValid():
            self.listWidget.model().removeRow(self.listWidget.currentIndex().row(),True)    
            