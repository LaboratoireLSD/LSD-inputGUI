
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
        if int(wizardNode.attribute("automaticLaunchAtStartup")[0]):
            self.checkBoxWizard.setChecked(True)
        if int(checkNode.attribute("automaticCheckAtStartup")[0]):
            self.checkBoxCheck.setChecked(True)
        if int(scenarioNode.attribute("showEnv")[0]):
            self.checkBoxScenarioModel.setChecked(True)
        if int(lsdNode.attribute("automaticLoadAtStartup")[0]):
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
        
        lsdNode.setAttribute("automaticLoadAtStartup", self.checkBoxLsd.isChecked())
        checkNode.setAttribute("automaticCheckAtStartup", self.checkBoxCheck.isChecked())  
        wizardNode.setAttribute("automaticLaunchAtStartup", self.checkBoxWizard.isChecked())
        
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
