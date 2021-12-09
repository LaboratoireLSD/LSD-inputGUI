"""
.. module:: Wizard_Demography

.. codeauthor:: Mathieu Gagnon <mathieu.gagnon.10@ulaval.ca>

:Created on: 2010-05-26

"""

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
    It is a dialog allowing a user manage the demography of a simulation.
    '''
    def setupUi(self, WizardPage):
        """
        Creates the widgets that will be displayed on the frame.
        
        :param WizardPage: Visual frame of the accept function.
        :type WizardPage: :class:`.MainWizard.Demography_dialog`
        """
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
        Reimplemented from QWizardPage.initializePage(self).
        Called automatically when the page is shown.
        '''
        self.initialize()
        
    def initialize(self):
        '''
        Since initializePage can only be called at the beginning of this page, this function acts as a bridge.
        '''
        rowProfile = self.field("currProfile")
        currProfileName = self.parent.topWObject.popTab.comboBox.itemData(rowProfile)
        baseModel = GeneratorBaseModel()
        demoFileName = baseModel.domNodeDict[currProfileName]["demoFile"]
        self.pushButton.setEnabled(not demoFileName)
        self.tableView.setModel(PopModel(baseModel,currProfileName))
        
    def retranslateUi(self, WizardPage):
        '''
        Function allowing naming of the different labels regardless of app's language.
        
        :param WizardPage: Visual frame to translate.
        :type WizardPage: :class:`.MainWizard.Demography_dialog`
        '''
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
        Modifies file used for demography.
        '''
        filePath = QtGui.QFileDialog.getOpenFileName(self, self.tr("Open Demography file"),
                                                                  "./database", self.tr("XML files (*.xml);;All files (*);;"))
        
        
        if filePath:
            bVarModel = GeneratorBaseModel()
            bVarModel.setDemoFileName(self.parent.topWObject.popTab.comboBox.itemData(self.field("currProfile")), filePath)
            
        self.initialize()
            
