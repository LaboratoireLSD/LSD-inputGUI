'''
Created on 2010-10-06

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
from model.baseTreatmentsModel import BaseTreatmentsModel
from model.baseVarModel import GeneratorBaseModel, SimpleBaseVarModel, fakeSingletonSimpleModel

class Ui_OpenDialog(QtGui.QDialog):
    '''
    This dialog allows the user to open a variable/scenario/process tree
    The choices shown to the user have to be part of the current model
    '''

    def __init__(self,parent=None):
        '''
        @summary Constructor
        @param parent : application's main window
        '''
        QtGui.QDialog.__init__(self,parent)
        self.chosenNode = None
        self.setupUi()
        
    def setupUi(self):
        self.dialogButtonBox = QtGui.QDialogButtonBox()
        self.dialogButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Open )
        self.mainLayout = QtGui.QVBoxLayout()
        self.choiceLabel = QtGui.QLabel("Choose a tree to open : ")
        self.comboBox = QtGui.QComboBox()
        baseVarModel = GeneratorBaseModel()
        baseProcModel = BaseTreatmentsModel()    
        try:
            for profiles in baseVarModel.getProfilesList():
                for variables in sorted(baseVarModel.getSimVarsList(profiles)):
                    self.comboBox.addItem(variables+" ("+profiles+")", profiles)
            for processes in sorted(baseProcModel.getTreatmentsDict()):
                self.comboBox.addItem(processes, "process")
        
        #if except, then its a simpleVaseVarModel
        except AttributeError:
            for variables in baseVarModel.getVarsList():
                self.comboBox.addItem(variables)
                
        self.mainLayout.addWidget(self.choiceLabel)
        self.mainLayout.addWidget(self.comboBox )
        self.mainLayout.addWidget(self.dialogButtonBox)
        self.mainLayout.setAlignment(self.dialogButtonBox, QtCore.Qt.AlignRight)
        
        self.setLayout(self.mainLayout)
        
        QtCore.QObject.connect(self.dialogButtonBox,QtCore.SIGNAL("accepted()"),self.open)
        QtCore.QObject.connect(self.dialogButtonBox,QtCore.SIGNAL("rejected()"),self.reject)
        
    def open(self):
        '''
        @summary Sets chosen Node and close
        '''
        baseVarModel = GeneratorBaseModel()
        baseProcModel = BaseTreatmentsModel()
        if not self.comboBox.itemData(self.comboBox.currentIndex()):
            #Was called from the demography editor, hence baseVarModel is a SimpleBaseVarModel
            self.chosenNode = baseVarModel.getVarNode(self.comboBox.currentText())
        else:
            if self.comboBox.itemData(self.comboBox.currentIndex()) == "process":
                self.chosenNode = baseProcModel.getTreatmentTree(self.comboBox.currentText())
            else:
                #Chose Tree is a process
                self.chosenNode = baseVarModel.getVarNode(self.comboBox.itemData(self.comboBox.currentIndex()).toString(), self.comboBox.currentText().remove(" ("+self.comboBox.itemData(self.comboBox.currentIndex())+")"))
        
        self.accept()
