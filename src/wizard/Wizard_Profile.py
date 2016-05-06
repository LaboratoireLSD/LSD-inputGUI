
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Wizard_Profile.ui'
#
# Created: Wed May 26 10:13:16 2010
#      by: PyQt4 UI code generator 4.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from model.baseVarModel import GeneratorBaseModel

class Ui_WizardPage(object):
    '''
    This class was automatically generated using a qtdesigner .ui file and qt's pyuic4 program.
    It is a dialog allowing a user to manage profiles of a simulation
    '''
    def setupUi(self, WizardPage):
        self.wizardPage = WizardPage
        self.parent = WizardPage.parent()
        WizardPage.setObjectName("WizardPage")
        WizardPage.resize(640, 480)
        self.listView = QtGui.QListWidget(WizardPage)
        self.listView.setGeometry(QtCore.QRect(30, 120, 241, 251))
        self.listView.setObjectName("listView")
        self.verticalLayoutWidget = QtGui.QWidget(WizardPage)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(300, 250, 171, 121))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.pushButton_2 = QtGui.QPushButton(self.verticalLayoutWidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.verticalLayout.addWidget(self.pushButton_2)
        self.pushButton_3 = QtGui.QPushButton(self.verticalLayoutWidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.verticalLayout.addWidget(self.pushButton_3)
        self.pushButton = QtGui.QPushButton(self.verticalLayoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)
        self.label = QtGui.QLabel(WizardPage)
        self.label.setGeometry(QtCore.QRect(310, 130, 121, 17))
        self.label.setObjectName("label")
        self.label_2 = QtGui.QLabel(WizardPage)
        self.label_2.setGeometry(QtCore.QRect(440, 130, 400, 17))
        self.label_2.setObjectName("label_2")
        self.addProfile = False
        self.retranslateUi(WizardPage)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)
        QtCore.QObject.connect(self.pushButton_2,QtCore.SIGNAL("clicked()"),self.changeId)
        QtCore.QObject.connect(self.listView,QtCore.SIGNAL("itemClicked(QListWidgetItem*)"),self.displayDemoFile)
        QtCore.QObject.connect(self.pushButton,QtCore.SIGNAL("clicked()"),self.deleteProfile)
        QtCore.QObject.connect(self.pushButton_3,QtCore.SIGNAL("clicked()"),self.modifyProfile)
        WizardPage.registerField("currProfile",self.listView)

    def changeId(self):
        '''
        @summary Little hook to change the page that would have been shown otherwise
        If profile is inserted, go to Demography Dialog
        '''
        if self.insertProfile():
            self.addProfile = True
            self.wizardPage.wizard().next()
        
    def insertProfile(self):
        '''
        @summary Create new profile
        '''
        bVarModel = GeneratorBaseModel()
        newProfileName, result = QtGui.QInputDialog.getText(self,"New Profile", "Enter new profile's name")
        if result:
            bVarModel.addProfile(newProfileName, "", "", "")
            self.parent.topWObject.popTab.comboBox.addItem("Profile named : "+newProfileName, newProfileName)
            self.listView.addItem(QtGui.QListWidgetItem(newProfileName))
            self.setField("currProfile", self.listView.count()-1)
        return result
            
    def validatePage(self):
        '''
        @summary Reimplemented from QWizardPage.validatePage(self)
        Called automatically when the page is about to be changed
        '''
        if self.modifyProfile:
            if not self.listView.selectedItems():
                QtGui.QMessageBox.information(self,"No Profile selected","Choose a profile first!")
                self.modifyProfile = False
                return False
        
        return True
    
    def deleteProfile(self):
        '''
        @summary Remove a profile from profile list
        '''
        bVarModel = GeneratorBaseModel()
        for items in self.listView.selectedItems():
            self.listView.takeItem(self.listView.row(items))
            bVarModel.removeProfile(items.text())
            self.parent.topWObject.popTab.comboBox.removeItem(self.listView.row(items))
            
    def modifyProfile(self):
        '''
        @summary Little hook that allows a profile modification
        If profile is marked for modifying, go to Demography Dialog
        '''
        self.modifyProfile = True
        self.wizardPage.wizard().next()
        
    def displayDemoFile(self,item):
        '''
        @summary Update label_2 to show demography file name of the currently selected profile
        @param item QListWiodgetItem containing the string of the currently selected profile
        '''
        bVarModel = GeneratorBaseModel()
        self.label_2.setText(bVarModel.getDemographyFileName(item.text()))
        
    def initializePage(self):
        '''
        @summary Reimplemented from QWizardPage.initializePage(self)
        Called automatically when the page is shown
        '''
        bVarModel = GeneratorBaseModel()
        self.listView.clear()
        self.listView.addItems([k for k in bVarModel.profileDict.keys()])
        
    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setTitle(QtGui.QApplication.translate("WizardPage", "Population", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("WizardPage", "Add Profile", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_3.setText(QtGui.QApplication.translate("WizardPage", "Modify Profile", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("WizardPage", "Remove Profile", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("WizardPage", "Demography File :", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("WizardPage", "No profile selected", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setSubTitle(QtGui.QApplication.translate("WizardPage", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Here are the current available profiles for this simulation. A profile describes the variables of the individuals in a population. A profile contains : <ul><li>A demography file</li><li>A function which describes the individuals you want to keep for your simulation</li><li>Variables related to the simulation</li></ul></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
