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

from PyQt4 import QtCore,QtGui
from wizard.Wiz_Start import Ui_Dialog as Wizard_Start
from wizard.Wiz_Library import Ui_Dialog as Wizard_Library
from wizard.Wiz_Process import Ui_Dialog as Wizard_Process
from wizard.Wiz_Scenario import Ui_Dialog as Wizard_Scenario
from wizard.Wizard_Profile import Ui_WizardPage as Wizard_Profile
from wizard.Wizard_SimVar import Ui_WizardPage as Wizard_SimVar
from wizard.Wizard_AcceptFunction import Ui_WizardPage as Wizard_AcceptFunction
from wizard.Wizard_Demography import Ui_WizardPage as Wizard_Demography
from wizard.Wizard_SimConf import Ui_WizardPage as Wizard_Start_Sim

class MainWizard(QtGui.QWizard):
    
    def __init__(self, parent=None):
        '''
        summary Constructor
        @param parent : application's main window
        '''
        QtGui.QWizard.__init__(self, parent)
        self.topWObject = parent
        self.setPage(0,Start_dialog(self))
        self.setPage(1,Library_dialog(self))
        self.setPage(2,Profile_dialog(self))
        self.setPage(3,Demography_dialog(self))
        self.setPage(4,AcceptFunction_dialog(self))
        self.setPage(5,SimVar_dialog(self))
        self.setPage(6,Process_dialog(self))
        self.setPage(7,Scenario_dialog(self))
        self.setPage(8,Start_Sim_dialog(self))

        self.setPixmap(QtGui.QWizard.LogoPixmap, QtGui.QPixmap("../img/lsdChampignon.png"))
        self.connect(self, QtCore.SIGNAL("currentIdChanged(int)"), self.updateTitle)
                        
    def drawFrameInFile(self, idC):
        '''
        @summary Save current wizard page to a file
        @param idC : current wizard page
        '''
        FileName = "LSD wizard - page " + str(idC) + ".png"   
        picture = QtGui.QPixmap(self.currentPage().frameSize())
        picture.fill(QtCore.Qt.white)
        painter = QtGui.QPainter()
        painter.begin(picture)
        self.currentPage().render(painter)
        painter.end()
        picture.save(FileName)
         
    def updateTitle(self, idC):
        '''
        @summary Update window title
        @param idC : current wizard page
        '''
        strTitle = "LSD - Wizard -- VOUS ETES A LA PAGE #" + str(idC)
        self.setWindowTitle(strTitle)
            
class Start_dialog(QtGui.QWizardPage,Wizard_Start):
    '''
    Transforms the class in the generated python file in a QWizardPage
    '''
    def __init__(self, parent=None):
        QtGui.QWizardPage.__init__(self,parent)
        Wizard_Start.__init__(self)
        self.setupUi(self)

class Library_dialog(QtGui.QWizardPage, Wizard_Library):
    '''
    Transforms the class in the generated python file in a QWizardPage
    '''
    def __init__(self, parent=None):
        QtGui.QWizardPage.__init__(self,parent)
        Wizard_Library.__init__(self)
        self.setupUi(self)

class Process_dialog(QtGui.QWizardPage, Wizard_Process):
    '''
    Transforms the class in the generated python file in a QWizardPage
    '''
    def __init__(self, parent=None):
        QtGui.QWizardPage.__init__(self,parent)
        Wizard_Process.__init__(self)
        self.setupUi(self)

class Scenario_dialog(QtGui.QWizardPage, Wizard_Scenario):
    '''
    Transforms the class in the generated python file in a QWizardPage
    '''
    def __init__(self, parent=None):
        QtGui.QWizardPage.__init__(self,parent)
        Wizard_Scenario.__init__(self)
        self.setupUi(self)
        
class Start_Sim_dialog(QtGui.QWizardPage,Wizard_Start_Sim):
    '''
    Transforms the class in the generated python file in a QWizardPage
    '''
    def __init__(self, parent=None):
        QtGui.QWizardPage.__init__(self,parent)
        Wizard_Start_Sim.__init__(self)
        self.setupUi(self)
        
class Profile_dialog(QtGui.QWizardPage,Wizard_Profile):
    '''
    Transforms the class in the generated python file in a QWizardPage
    '''
    def __init__(self, parent=None):
        QtGui.QWizardPage.__init__(self,parent)
        Wizard_Profile.__init__(self)
        self.setupUi(self)

    def nextId(self):
        if self.addProfile or self.modifyProfile:
            self.addProfile = self.modifyProfile = False
            return 3
        return 6
    
class Demography_dialog(QtGui.QWizardPage,Wizard_Demography):
    '''
    Transforms the class in the generated python file in a QWizardPage
    '''
    def __init__(self, parent=None):
        QtGui.QWizardPage.__init__(self,parent)
        Wizard_Demography.__init__(self)
        self.setupUi(self)
    
    def nextId(self):
        return 4
    
class SimVar_dialog(QtGui.QWizardPage,Wizard_SimVar):
    '''
    Transforms the class in the generated python file in a QWizardPage
    '''
    def __init__(self, parent=None):
        QtGui.QWizardPage.__init__(self,parent)
        Wizard_SimVar.__init__(self)
        self.setupUi(self)
        
    def nextId(self):
        return 2
    
class AcceptFunction_dialog(QtGui.QWizardPage,Wizard_AcceptFunction):
    '''
    Transforms the class in the generated python file in a QWizardPage
    '''
    def __init__(self, parent=None):
        QtGui.QWizardPage.__init__(self,parent)
        Wizard_AcceptFunction.__init__(self)
        self.setupUi(self)

    def nextId(self):
        return 5
