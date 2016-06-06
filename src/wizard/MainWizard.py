"""
.. module:: MainWizard

.. codeauthor:: Mathieu Gagnon <mathieu.gagnon.10@ulaval.ca>

:Created on: 2010-01-18

"""

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
        Constructor.
        
        :param parent: Optional - Application's main window.
        :type parent: :class:`.MainFrame`.
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
         
    def updateTitle(self, idC):
        '''
        Update window title.
        
        :param idC: Current wizard page.
        :type idC: Int
        '''
        strTitle = "LSD - Wizard -- VOUS ETES A LA PAGE #" + str(idC)
        self.setWindowTitle(strTitle)
            
class Start_dialog(QtGui.QWizardPage, Wizard_Start):
    '''
    Transforms the class in the generated python file in a QWizardPage.
    '''
    def __init__(self, parent=None):
        """
        Constructor.
        
        :param parent: Optional - Application's main window.
        :type parent: :class:`.MainFrame`
        """
        QtGui.QWizardPage.__init__(self,parent)
        Wizard_Start.__init__(self)
        self.setupUi(self)

class Library_dialog(QtGui.QWizardPage, Wizard_Library):
    '''
    Transforms the class in the generated python file in a QWizardPage.
    '''
    def __init__(self, parent=None):
        """
        Constructor.
        
        :param parent: Optional - Application's main window.
        :type parent: :class:`.MainFrame`
        """
        QtGui.QWizardPage.__init__(self,parent)
        Wizard_Library.__init__(self)
        self.setupUi(self)

class Process_dialog(QtGui.QWizardPage, Wizard_Process):
    '''
    Transforms the class in the generated python file in a QWizardPage.
    '''
    def __init__(self, parent=None):
        """
        Constructor.
        
        :param parent: Optional - Application's main window.
        :type parent: :class:`.MainFrame`
        """
        QtGui.QWizardPage.__init__(self,parent)
        Wizard_Process.__init__(self)
        self.setupUi(self)

class Scenario_dialog(QtGui.QWizardPage, Wizard_Scenario):
    '''
    Transforms the class in the generated python file in a QWizardPage.
    '''
    def __init__(self, parent=None):
        """
        Constructor.
        
        :param parent: Optional - Application's main window.
        :type parent: :class:`.MainFrame`
        """
        QtGui.QWizardPage.__init__(self,parent)
        Wizard_Scenario.__init__(self)
        self.setupUi(self)
        
class Start_Sim_dialog(QtGui.QWizardPage,Wizard_Start_Sim):
    '''
    Transforms the class in the generated python file in a QWizardPage.
    '''
    def __init__(self, parent=None):
        """
        Constructor.
        
        :param parent: Optional - Application's main window.
        :type parent: :class:`.MainFrame`
        """
        QtGui.QWizardPage.__init__(self,parent)
        Wizard_Start_Sim.__init__(self)
        self.setupUi(self)
        
class Profile_dialog(QtGui.QWizardPage,Wizard_Profile):
    '''
    Transforms the class in the generated python file in a QWizardPage.
    '''
    def __init__(self, parent=None):
        """
        Constructor.
        
        :param parent: Optional - Application's main window.
        :type parent: :class:`.MainFrame`
        """
        QtGui.QWizardPage.__init__(self,parent)
        Wizard_Profile.__init__(self)
        self.setupUi(self)

    def nextId(self):
        """
        Returns the id of the next window.
        
        :return: Int. 3 if adding od editing a profile. 6 otherwise.
        """
        if self.addProfile or self.modifyProfile:
            self.addProfile = self.modifyProfile = False
            return 3
        return 6
    
class Demography_dialog(QtGui.QWizardPage,Wizard_Demography):
    '''
    Transforms the class in the generated python file in a QWizardPage.
    '''
    def __init__(self, parent=None):
        """
        Constructor.
        
        :param parent: Optional - Application's main window.
        :type parent: :class:`.MainFrame`
        """
        QtGui.QWizardPage.__init__(self,parent)
        Wizard_Demography.__init__(self)
        self.setupUi(self)
    
    def nextId(self):
        """
        Returns the id of the next window.
        
        :return: Int. Always 4.
        """
        return 4
    
class SimVar_dialog(QtGui.QWizardPage,Wizard_SimVar):
    '''
    Transforms the class in the generated python file in a QWizardPage
    '''
    def __init__(self, parent=None):
        """
        Constructor.
        
        :param parent: Optional - Application's main window.
        :type parent: :class:`.MainFrame`
        """
        QtGui.QWizardPage.__init__(self,parent)
        Wizard_SimVar.__init__(self)
        self.setupUi(self)
        
    def nextId(self):
        """
        Returns the id of the next window.
        
        :return: Int. Always 2.
        """
        return 2
    
class AcceptFunction_dialog(QtGui.QWizardPage,Wizard_AcceptFunction):
    '''
    Transforms the class in the generated python file in a QWizardPage
    '''
    def __init__(self, parent=None):
        """
        Constructor.
        
        :param parent: Optional - Application's main window.
        :type parent: :class:`.MainFrame`
        """
        QtGui.QWizardPage.__init__(self,parent)
        Wizard_AcceptFunction.__init__(self)
        self.setupUi(self)

    def nextId(self):
        """
        Returns the id of the next window.
        
        :return: Int. Always 5.
        """
        return 5
