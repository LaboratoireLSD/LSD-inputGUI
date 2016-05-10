'''
Created on 2009-05-26

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

# Form implementation generated from reading ui file 'Wizard_Demography.ui'
#
# Created: Wed May 26 12:37:32 2010
#      by: PyQt4 UI code generator 4.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from model.PopModel import PopModel
from model.baseVarModel import GeneratorBaseModel

class Ui_WizardPage(object):
    '''
    This class was automatically generated using a qtdesigner .ui file and qt's pyuic4 program.
    It is a dialog allowing a user manage the demography of a simulation
    '''
    def setupUi(self, WizardPage):
        WizardPage.setObjectName("WizardPage")
        WizardPage.resize(640, 480)
        self.parent = WizardPage.parent()
        self.tableView = QtGui.QTableView(WizardPage)
        self.tableView.setGeometry(QtCore.QRect(40, 120, 256, 231))
        self.tableView.setObjectName("tableView")
        self.label = QtGui.QLabel(WizardPage)
        self.label.setGeometry(QtCore.QRect(40, 80, 131, 17))
        self.label.setObjectName("label")
        self.pushButton = QtGui.QPushButton(WizardPage)
        self.pushButton.setGeometry(QtCore.QRect(320, 130, 171, 27))
        self.pushButton.setObjectName("pushButton")
        self.textNote = QtGui.QTextBrowser(WizardPage)
        self.textNote.setObjectName("textNote")
        self.textNote.move(320,180)
        self.textNote.setFrameShape(QtGui.QFrame.NoFrame)
        self.textNote.viewport().setAutoFillBackground(False)
        self.retranslateUi(WizardPage)
        QtCore.QObject.connect(self.pushButton,QtCore.SIGNAL("clicked()"),self.changeDemoFile)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)
        
    def initializePage(self):
        '''
        @summary Reimplemented from QWizardPage.initializePage(self)
        Called automatically when the page is shown
        '''
        self.initialize()
        
    def initialize(self):
        '''
        @summary Since initializePage can only be called at the beginning of this page, this function acts as a bridge
        '''
        rowProfile = self.field("currProfile")
        currProfileName = self.parent.topWObject.popTab.comboBox.itemData(rowProfile)
        baseModel = GeneratorBaseModel()
        demoFileName = baseModel.domNodeDict[currProfileName]["demoFile"]
        self.pushButton.setEnabled(not demoFileName)
        self.tableView.setModel(PopModel(baseModel,currProfileName))
        
    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setTitle(QtGui.QApplication.translate("WizardPage", "Profile - Step 1", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setSubTitle(QtGui.QApplication.translate("WizardPage", "First, choose the demography file you want to use for your population.", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("WizardPage", "Available Variables :", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("WizardPage", "Choose Demography File", None, QtGui.QApplication.UnicodeUTF8))
        self.textNote.setText(QtGui.QApplication.translate("WizardPage", """<p>Demography can only be set if the profile doesn't yet have one
                                                                            <p>Try deleting the profile and creating a new one if you wish to change the demography"""
                                                                            , None, QtGui.QApplication.UnicodeUTF8))
    def changeDemoFile(self):
        '''
        @summary Modify file used for demography
        '''
        filePath = QtGui.QFileDialog.getOpenFileName(self, self.tr("Open Demography file"),
                                                                  "./database", self.tr("XML files (*.xml);;All files (*);;"))
        
        
        if filePath:
            bVarModel = GeneratorBaseModel()
            bVarModel.setDemoFileName(self.parent.topWObject.popTab.comboBox.itemData(self.field("currProfile")), filePath)
            
        self.initialize()
            
