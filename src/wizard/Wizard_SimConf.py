'''
Created on 2010-05-27

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

# Form implementation generated from reading ui file 'Wizard_SimConf.ui'
#
# Created: Thu May 27 16:03:19 2010
#      by: PyQt4 UI code generator 4.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from editor.mainEditorFrame import MainEditorWindow

class Ui_WizardPage(object):
    '''
    This class was automatically generated using a qtdesigner .ui file and qt's pyuic4 program.
    It is a dialog allowing a user to edit the remaining important items before a simulation is considered as valid
    '''
    def setupUi(self, WizardPage):
        WizardPage.setObjectName("WizardPage")
        WizardPage.resize(640, 480)
        self.parent= WizardPage.parent()
        self.gridLayoutWidget = QtGui.QWidget(WizardPage)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(20, 80, 601, 311))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setMargin(10)
        self.gridLayout.setHorizontalSpacing(10)
        self.gridLayout.setVerticalSpacing(30)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtGui.QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.label = QtGui.QLabel(self.gridLayoutWidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)
        self.tableView = QtGui.QTableView(self.gridLayoutWidget)
        self.tableView.setObjectName("tableWidget")
        self.gridLayout.addWidget(self.tableView, 1, 1, 1, 1)
        self.widget = QtGui.QWidget(self.gridLayoutWidget)
        self.widget.setObjectName("widget")
        self.pushButton = QtGui.QPushButton(self.widget)
        self.pushButton.setGeometry(QtCore.QRect(30, 120, 121, 27))
        self.pushButton.setObjectName("pushButton")
        self.radioButton_2 = QtGui.QRadioButton(self.widget)
        self.radioButton_2.setGeometry(QtCore.QRect(10, 90, 171, 22))
        self.radioButton_2.setObjectName("radioButton_2")
        self.radioButton_2.setAutoExclusive(True)
        self.spinBox = QtGui.QSpinBox(self.widget)
        self.spinBox.setGeometry(QtCore.QRect(30, 40, 55, 27))
        self.spinBox.setObjectName("spinBox")
        self.radioButton = QtGui.QRadioButton(self.widget)
        self.radioButton.setGeometry(QtCore.QRect(10, 10, 131, 22))
        self.radioButton.setObjectName("radioButton")
        self.radioButton.setAutoExclusive(True)
        self.label_3 = QtGui.QLabel(self.widget)
        self.label_3.setGeometry(QtCore.QRect(100, 40, 62, 31))
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.widget, 1, 0, 1, 1)
        
        self.horizontalWidget = QtGui.QHBoxLayout()
        self.pushButton_Add = QtGui.QPushButton("Add Generation",)
        self.pushButton_Delete = QtGui.QPushButton("Delete Generation")
        self.horizontalWidget.addWidget(self.pushButton_Add)
        self.horizontalWidget.addWidget(self.pushButton_Delete)
        self.gridLayout.addLayout( self.horizontalWidget, 2, 1)
        
        self.connect(self.spinBox,QtCore.SIGNAL("valueChanged(int)"),self.updateClock)
        self.connect(self.pushButton_Add,QtCore.SIGNAL("clicked()"),self.addProfile)
        self.connect(self.pushButton_Delete,QtCore.SIGNAL("clicked()"),self.removeProfile)
        self.connect(self.radioButton_2,QtCore.SIGNAL("toggled(bool)"),self.changeEnableState)
        self.connect(self.pushButton,QtCore.SIGNAL("clicked()"),self.openClockEditor)
        self.retranslateUi(WizardPage)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)
        
    def initializePage(self):
        '''
        @summary Reimplemented from QWizardPage.initializePage(self)
        Called automatically when the page is shown
        '''
        self.tableView.setModel(self.parent.topWObject.simTab.tableViewProMgr.model())
        self.tableView.setItemDelegate(self.parent.topWObject.simTab.tableViewProMgr.itemDelegate())
        model = self.parent.topWObject.simTab.tableView.model()
        clockNode = model.getClockNode()
        fixed,value = self.lookForFixedValue(clockNode)
        if fixed:
            self.radioButton.setChecked(True)
            self.spinBox.setValue(int(str(value)))
            return
        self.radioButton_2.setChecked(True)
        
    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setTitle(QtGui.QApplication.translate("WizardPage", "Simulation Configuration", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setSubTitle(QtGui.QApplication.translate("WizardPage", "The simulation requires this information before it is launched ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("WizardPage", "1. Tell the simulator how long\n"
                                                          "    the simulation is going to last", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("WizardPage", "2. Choose a profile, then tell the wizard how many\n"
                                                        "    individuals must be created at a desired timestep.", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("WizardPage", "Open Tree Editor", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_2.setText(QtGui.QApplication.translate("WizardPage", "Conditional duration", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton.setText(QtGui.QApplication.translate("WizardPage", "Fixed Duration", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("WizardPage", "Steps", None, QtGui.QApplication.UnicodeUTF8))
    
    def lookForFixedValue(self,clockDom):
        '''
        @summary Check if DOM looks like a fixed clock value
        @param clockDom : clock's XML node
        '''
        if clockDom.tagName() == "Basic_IsEqual":
            if clockDom.countChilds()== 2:
                if clockDom.childList().item(0).tagName() == "Basic_Clock":
                    if clockDom.childList().item(1).tagName() == "Basic_Token":
                        return True,clockDom.childList().item(1).attribute("value")
        return False,0
    
    def addProfile(self):
        '''
        @summary Insert a profile in the generator list
        '''
        self.tableView.model().insertRow(self.tableView.model().rowCount())
        
    def removeProfile(self):
        '''
        @summary Removes a profile from the generator list
        '''
        index = self.tableView.currentIndex()
        if index.isValid():
            self.tableView.model().removeRow(index.row())
    
    def updateClock(self):
        '''
        @summary Sync model with widget's clock value
        '''
        model = self.parent.topWObject.simTab.tableView.model()
        model.setFixedClockValue(self.spinBox.value())
            
    def changeEnableState(self,state):
        '''
        @summary Enable/Disable widgets depending of clock configuration(Fixed or Conditional)
        @param state Enable/Disable state
        '''
        if not state:
            answer = QtGui.QMessageBox.question(self, "Clock modifying", "Are you sure you want to set a fixed clock value? If the clock was a conditional value, it will be erased!",QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel)
            if answer==QtGui.QMessageBox.Cancel:
                self.radioButton_2.setChecked(True)
                return
        self.spinBox.setEnabled(not state)
        self.pushButton.setEnabled(state)
        if not state:
            model = self.parent.topWObject.simTab.tableView.model()
            model.setFixedClockValue(self.spinBox.value())
            
    def openClockEditor(self):
        '''
        @summary Open clock's tree for edition
        '''
        model = self.parent.topWObject.simTab.tableView.model()
        clockNode = model.getClockNode()
        editor = MainEditorWindow(clockNode.elementsByTagName("PrimitiveTree").item(0).firstChild(),self.parent.topWObject,"Clock")
        editor.setWindowModality(QtCore.Qt.WindowModal)
        editor.exec_()