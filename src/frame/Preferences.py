'''
Created on 2010-10-01

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

from PyQt4 import QtGui,QtCore

class Ui_Preferences(QtGui.QDialog):
    '''
    This class was designed as it was a ui designer class, but in fact was all written by user
    This dialog allows the user to edit his preferences , like automatically loading wizard at startup, automatically checking model at startup, etc...
    '''

    def __init__(self,settingsDom,parent=None):
        '''
        @summary Constructor
        @param settingsDom : Settings DOM node
        @param parent : application's main window
        '''
        QtGui.QDialog.__init__(self,parent)
        self.settingsDom = settingsDom
        self.setupUi()
        
    def setupUi(self):
        self.dialogButtonBox = QtGui.QDialogButtonBox()
        self.dialogButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok )
        self.mainLayout = QtGui.QVBoxLayout()
        self.checkBoxLsd = QtGui.QCheckBox("Automatically load last .lsd file at startup")
        self.checkBoxWizard = QtGui.QCheckBox("Automatically load wizard at startup")
        self.checkBoxCheck = QtGui.QCheckBox("Automatically check model at startup")
        self.checkBoxScenarioModel = QtGui.QCheckBox("Show environment target in scenario model/view")
        
        lsdNode = self.settingsDom.firstChildElement("LSD")
        checkNode = self.settingsDom.firstChildElement("Check")
        wizardNode = self.settingsDom.firstChildElement("Wizard")
        scenarioNode = self.settingsDom.firstChildElement("Models").firstChildElement("Scenario")
        if wizardNode.attribute("automaticLaunchAtStartup").toInt()[0]:
            self.checkBoxWizard.setChecked(True)
        if checkNode.attribute("automaticCheckAtStartup").toInt()[0]:
            self.checkBoxCheck.setChecked(True)
        if scenarioNode.attribute("showEnv").toInt()[0]:
            self.checkBoxScenarioModel.setChecked(True)
        if lsdNode.attribute("automaticLoadAtStartup").toInt()[0]:
            self.checkBoxLsd.setChecked(True)
            
        self.mainLayout.addWidget(self.checkBoxLsd)
        self.mainLayout.addWidget(self.checkBoxWizard)
        self.mainLayout.addWidget(self.checkBoxCheck)
        self.mainLayout.addWidget(self.checkBoxScenarioModel)
        self.mainLayout.addWidget(self.dialogButtonBox)
        self.mainLayout.setAlignment(self.dialogButtonBox, QtCore.Qt.AlignRight)
        
        self.setLayout(self.mainLayout)
        self.setWindowTitle("Preferences")
        
        QtCore.QObject.connect(self.dialogButtonBox,QtCore.SIGNAL("accepted()"),self.modifySettings)
        QtCore.QObject.connect(self.dialogButtonBox,QtCore.SIGNAL("rejected()"),self.reject)
        
    def modifySettings(self):
        '''
        @summary Save settings before closing dialog
        '''
        lsdNode = self.settingsDom.firstChildElement("LSD")
        checkNode = self.settingsDom.firstChildElement("Check")
        wizardNode = self.settingsDom.firstChildElement("Wizard")
        scenarioNode = self.settingsDom.firstChildElement("Models").firstChildElement("Scenario")
        
        if self.checkBoxLsd.isChecked():
            lsdNode.setAttribute("automaticLoadAtStartup",1)
        else:
            lsdNode.setAttribute("automaticLoadAtStartup",0)
        if self.checkBoxCheck.isChecked():
            checkNode.setAttribute("automaticCheckAtStartup",1)
        else:
            checkNode.setAttribute("automaticCheckAtStartup",0)    
        if self.checkBoxWizard.isChecked():
            wizardNode.setAttribute("automaticLaunchAtStartup",1)
        else:
            wizardNode.setAttribute("automaticLaunchAtStartup",0)
        
        if self.checkBoxScenarioModel.isChecked():
            scenarioNode.setAttribute("showEnv",1)
            self.parent().simTab.tableView.model().beginInsertColumns(QtCore.QModelIndex(), 2, 2 )
            self.parent().simTab.tableView.model().showEnvTarget = True
            self.parent().simTab.tableView.model().endInsertColumns()
        else:
            scenarioNode.setAttribute("showEnv",0)
            self.parent().simTab.tableView.model().beginRemoveColumns(QtCore.QModelIndex(), 2, 2 )
            self.parent().simTab.tableView.model().showEnvTarget = False
            self.parent().simTab.tableView.model().endRemoveColumns()
            
        self.accept()
