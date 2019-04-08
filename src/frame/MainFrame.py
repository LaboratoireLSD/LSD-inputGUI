'''
Created on 2009-07-08

@author:  Majid Malis
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

import os
import platform
import zipfile
import shutil

from PyQt4 import QtCore, QtGui, QtXml, QtSvg

from controller.ProcessListDelegate import ProcessListDelegate
from controller.ObserverDelegate import ObserverDelegate
from controller.VarDelegate import VarSimDelegate, VarGeneratorDelegate
from controller.EnvDelegate import EnvDelegate
from controller.SensAnalysisDelegate import SensAnalysisDelegate
from controller.ParamDelegate import ParamDelegate
from frame.environment import Ui_environment as UITab1
from frame.observers import Ui_observers as UITabObservers
from frame.simulation import Ui_simulation as UITab4
from frame.trees import Ui_trees as UITab3
from frame.population import Ui_population as UITabPopulation
from frame.OutCome import Ui_Outcome as UITabOutCome
from frame.sensanalysis import Ui_Analysis as UITabAnalysis
from frame.parameters import Ui_parameters as UITabParameters
from frame.demoFileEditor import demoFileEditor
from frame.FileGenerator import FileGenerator
from frame.Preferences import Ui_Preferences as PrefDialog
from frame.pluginViewer import PluginViewer
from frame.SearchTool import searchDialog
from model.PopModel import PopModel, PopModelSim
from model.envModel import EnvModel
from model.SensAnalysisModel import SaTableModel, SaComboBoxModel
from model.TreatmentsModel import ListTreatmentsModel
from model.baseEnvModel import BaseEnvModel
from model.baseTreatmentsModel import BaseTreatmentsModel
from model.BaseParametersModel import BaseParametersModel
from model.LocalVariableModel import BaseLocalVariablesModel
from model.ObserversModel import ListClockObserversModel
from model.OutcomeModel import OutcomeListProfileModel, OutcomeEnvModel
from model.ParametersModel import ParametersModel
from model.GeneratorManagerModel import GeneratorManagerModel
from model.baseVarModel import GeneratorBaseModel, fakeSingletonSimpleModel
from model.PrimitiveModel import Primitive
from model.PrefModel import PrefModel
from util.DocPrimitive import PrimitiveDict
from util.opener import Opener
from wizard.MainWizard import MainWizard

xmlVersion = 1.0

__version__ = "2.0.0"


class MainWindow(QtGui.QMainWindow):
    '''
    This class is the application's main window
    It inherits QtGui.QMainWindow, see QMainWindow's documentation for more details
    '''
    def __init__(self, parent=None):
        '''
        @summary Constructor
        @param parent : not used
        '''
        QtGui.QMainWindow.__init__(self, parent)
        self.xmlPath = ""
        self.filePath = ""
        self.saveDirectory = ""
        self.projectName = ""
        self.dirty = False
        self.domDocs = {"environment": QtXml.QDomNode(),
            "population": QtXml.QDomNode(),
            "treatments": QtXml.QDomNode(),
            "clock": QtXml.QDomNode(),
            "main": QtXml.QDomNode()}
        self.tabs = QtGui.QTabWidget()
        self.tmpTextStream = QtCore.QTextStream()
        self.document = QtXml.QDomDocument()
        self.SAdocument = QtXml.QDomDocument()
        self.prefDocument = QtXml.QDomDocument()
        self.pmtDictList = PrimitiveDict(self)
        self.Wizard = None
        
        self.envTab = MyWidgetTabEnvironment(self)
        self.tabs.addTab(self.envTab, "&Environment")
        
        self.popTab = MyWidgetTabPopulation(self)
        self.tabs.addTab(self.popTab, "&Population")
        
        self.treeTab = MyWidgetTabProcesses(self)
        self.tabs.addTab(self.treeTab, "P&rocesses trees")
        
        self.paramTab = MyWidgetTabParameters(self)
        self.tabs.addTab(self.paramTab, "Para&meters")
        
        self.obsTab = MyWidgetTabObservers(self)
        self.tabs.addTab(self.obsTab,"&Observers")
        
        self.simTab = MyWidgetTabSimulation(self)
        self.tabs.addTab(self.simTab, "&Simulation")
 
        self.outTab = MyWidgetTabOutCome(self)
        self.tabs.addTab(self.outTab,"Out&Come")
 
        self.saTab = MyWidgetTabAnalysis(self)
        self.tabs.addTab(self.saTab, "A&nalysis")
       
        self.createMenus()
        self.setCentralWidget(self.tabs)
        self.tabs.setMinimumSize(0, 0)
        self.setWindowTitle(self.tr("%s" % QtGui.QApplication.applicationName()))
        #self.setWindowIcon(QtGui.QIcon("../img/emblems/emblem-mushroom.png"))
        
    def startWizard(self):
        '''
        @summary : Create and show wizard
        '''
        self.Wizard = MainWizard(self)
        self.Wizard.resize(980,730)
        self.Wizard.setWindowTitle("LSD Simulator Dashboard -- version alpha")
        self.Wizard.exec_()
        
    def createMenus(self):
        '''
        @summary Creates Menus for the main window
        '''
        
        ''' File menu '''
        self.fileMenu = self.menuBar().addMenu(self.tr("&File"))
        fileOpenAction = self.createAction("&Open...", self.openParametersFile, "Ctrl+O", "document-open", "Open File")
        fileSaveAction = self.createAction("&Save", self.save, "Ctrl+S", "document-save", "Save File")
        fileSaveAsAction = self.createAction("Save &As...", self.saveAs, "Ctrl+Shift+S", "document-save-as", "Save File As")
        fileOpenPrimitiveDict = self.createAction("Open &Plugin", self.openXSDdictFile, "Ctrl+Shift+O", "plugin-add", "Open XSD Primitive Information File")
        fileExitAction = self.createAction("E&xit", self.exit, "Ctrl+Q", "system-log-out", "Exit")
        fileStartProject = self.createAction("Start &New Project",self.openNewProject,None,"document-new","Start New Project")
        self.fileMenu.addAction(fileOpenAction)
        self.fileMenu.addAction(fileStartProject)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(fileSaveAction)
        self.fileMenu.addAction(fileSaveAsAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(fileOpenPrimitiveDict)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(fileExitAction)
        
        '''View Menu '''
        self.viewMenu = self.menuBar().addMenu(self.tr("&View"))
        viewShowEnvironment = self.createAction("Show &Environment Tab",self.showEnv,None, None, None, True, "toggled(bool)")
        viewShowObservers = self.createAction("Show &Observers Tab", self.showObs, None, None, None, True,  "toggled(bool)")
        self.viewMenu.addAction(viewShowEnvironment)
        self.viewMenu.addAction(viewShowObservers)
        
        '''Tools Menu'''
        self.toolMenu  = self.menuBar().addMenu(self.tr("&Tools"))
        toolTakeScreenshotAction = self.createAction("&Take Screenshot", self.takeScreenshot, "Ctrl+T", "camera-photo", "Screenshot")
        toolCheckValidityVars = self.createAction("&Check Variables Validity", self.checkVars, None, "view-refresh", "Check variables for errors or warnings")
        toolCheckValidityProcessesAndScenarios = self.createAction("&Check Processes Validity", self.checkProcessesAndScenarios, None, "view-refresh", "Check processes for errors or warnings")
        toolCheckValidity = self.createAction("&Check All", self.checkModel, None, "view-refresh", "Check all simulation for possible errors or warnings")
        toolDemoFileEditor = self.createAction("&Demography Editor", self.demoEditor, None, "demography", "Edit Demography")
        toolGenerator = self.createAction("&File Generator", self.fileGenerator, None, "generator", "Generate Configuration files")
        toolSearchTool = self.createAction("&Search",self.search,None,"edit-find","Search for primitives in processes")
        self.toolMenu.addAction(toolTakeScreenshotAction)
        self.toolMenu.addSeparator()
        self.toolMenu.addAction(toolCheckValidityVars)
        self.toolMenu.addAction(toolCheckValidityProcessesAndScenarios)
        self.toolMenu.addAction(toolCheckValidity)
        self.toolMenu.addSeparator()
        self.toolMenu.addAction(toolDemoFileEditor)
        self.toolMenu.addSeparator()
        self.toolMenu.addAction(toolGenerator)
        self.toolMenu.addSeparator()
        self.toolMenu.addAction(toolSearchTool)
        ''' Help menu '''
        self.helpMenu = self.menuBar().addMenu(self.tr("&Help"))
        helpAboutAction = self.createAction("&About", self.helpAbout, None, None, "Help")
        #Icon in different folder
        helpAboutAction.setIcon(QtGui.QIcon("../img/apps/help-browser.png"))
        helpAboutAction.setIconVisibleInMenu(True)
        self.helpMenu.addAction(helpAboutAction)
        preferenceAction = self.createAction("&Preferences", self.showPref, None, "document-properties", "Preferences")
        self.helpMenu.addAction(preferenceAction)
        
    def createAction(self, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False, signal="triggered()"):
        '''
        @Summary Creates the choices that will be be shown in the different menus(ex : Save Or Save as in the file menu)
        @param text : Text shown in the menu bar
        @param slot : QtGui.QMainWindow function that will be called when the item is going to be clicked in the menu
        @param shortcut : keyboard shortcut that will trigger the action(ex : ctrl+v for action paste)
        @param icon : An icon or picture that will be seen left to the text in the menu
        @param tip : a tooltip shown when the user will hover the mouse over an action
        @param checkable : Sets if a checkbox is visible left to the text in the menu
        @signal : default signal that will trigger the action(triggered, checked, etc...)
        '''
        action = QtGui.QAction(text, self)
        if icon is not None:
            action.setIcon(QtGui.QIcon("../img/actions/%s.png" % icon))
            action.setIconVisibleInMenu(True)
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, QtCore.SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action
        
    def okToContinue(self):
        '''
        @summary Verifies if changes had been saved or not before continuing
        '''
        if self.dirty:
            reply = QtGui.QMessageBox.question(self, "%s" % QtGui.QApplication.applicationName() + " - Unsaved Changes", "Document looks like it has been modified. Save unsaved changes?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)
            if reply == QtGui.QMessageBox.Cancel:
                return False
            elif reply == QtGui.QMessageBox.Yes:
                self.dirty = False
                self.save()
                self.updateWindowTitle()
                return True
            elif reply == QtGui.QMessageBox.No:
                return True
        return True
    
    def reopenParametersFile(self, reason):
        '''
        @summary Re-opens the parameters file, because of reason 
        '''
        if self.Wizard:
            if self.Wizard.isActiveWindow():
                return
        if reason:
            errorDialog = QtGui.QErrorMessage(self)
            errorDialog.showMessage(reason)
            self.connect(errorDialog, QtCore.SIGNAL("accepted()"), self.openParametersFile)

    def openXSDdictFile(self, xsdFilePath=""):
        '''
        @summary Opens a .xsd dictionnary file
        '''
        if xsdFilePath == "":
            pv = PluginViewer()
            pv.exec_()
            return

        self.pmtDictList.addFromXSD(xsdFilePath)
        #Add to configuration file
        pluginsNode = self.domDocs["main"].firstChildElement("System").firstChildElement("Plugins")
        pluginsList = pluginsNode.elementsByTagName("Plugin")
        for i in range(0,pluginsList.count()):
            currentNode = pluginsList.item(i)
            if str(currentNode.toElement().attribute("xsdfile")).rpartition("/")[-1] == str(xsdFilePath).rpartition("/")[-1]:
                return
        newPlugin =  pluginsNode.ownerDocument().createElement("Plugin")
        dictName = str(xsdFilePath).rpartition("/")[-1]
        newPlugin.setAttribute("xsdfile","XSD/"+dictName)
        sourceName = "lib"+dictName.split(".")[0]+".so"
        newPlugin.setAttribute("source",sourceName)
        pluginsNode.appendChild(newPlugin)

    def openNewProject(self):
        '''
        @summary Opens New Project
        '''
        self.openParametersFile(QtCore.QString("util/parameters_file_template.xml"))
        self.saveDirectory = ""
        self.projectName = ""
        
    def openParametersFile(self, filePath=QtCore.QString("")):
        '''
        @summary Opens the parameters file, witch points to many configuration files, and dispatches info over the tabs
        @param filePath : configuration file to open
        '''
        
        global xmlVersion
        if self.okToContinue():
            if filePath.isEmpty():
                self.filePath = QtGui.QFileDialog.getOpenFileName(self, self.tr("Open XML parameters file"),
                                                                  self.xmlPath, self.tr("LSD files (*.lsd);;XML files (*.xml);;All files (*);;"))
            else: 
                self.filePath = filePath
                
            if not self.filePath.isEmpty():
                filePathPartition = str(self.filePath).rpartition(".")
                if filePathPartition[2] == "lsd":
                    self.openParametersFileLSD(self.filePath)
        
                f = Opener(self.filePath)
                
                self.document = f.getDomDocument()
                root_node = f.getRootNode()
                input_node = root_node.firstChildElement("Input")
                simulation_node = root_node.firstChildElement("Simulation")
                output_node = root_node.firstChildElement("Output")
                
                self.folderPath = str(self.filePath).rpartition("/")[0] + "/"
                self.saveDirectory = str(self.filePath).rpartition("/")[0].rpartition("/")[0]
                self.projectName = str(self.filePath).rpartition("/")[0].rpartition("/")[-1]
                
                system_elem = root_node.firstChildElement("System")
                environment_elem = input_node.firstChildElement("Environment")
                clock_observers_elem = simulation_node.firstChildElement("ClockObservers")
                treatments_elem = simulation_node.firstChildElement("Processes")
                clock_elem = simulation_node.firstChildElement("Clock")
                scenarios_elem = simulation_node.firstChildElement("Scenarios")
                profile_elem = input_node.firstChildElement("PopulationManager")
                parameters_elem = system_elem.firstChildElement("Parameters")
                
                assert not system_elem.isNull(), self.reopenParametersFile("In MainFrame : <System> tag is missing!")
                assert not environment_elem.isNull(), self.reopenParametersFile("In MainFrame : <Environment> tag is missing!")
                assert not treatments_elem.isNull(), self.reopenParametersFile("In MainFrame : <Treatments> tag is missing!")
                assert not scenarios_elem.isNull(), self.reopenParametersFile("In MainFrame : <Scenarios> tag is missing!")
                assert not clock_elem.isNull(), self.reopenParametersFile("In MainFrame : <Clock> tag is missing!")
                assert not profile_elem.isNull(), self.reopenParametersFile("In MainFrame : <Clock> tag is missing!")
                assert not clock_observers_elem.isNull(), self.reopenParametersFile("In MainFrame : <ClockObservers> tag is missing!") 
                assert not parameters_elem.isNull(), self.reopenParametersFile("In MainFrame : <Parameters> tag is missing!")  
                
                self.domDocs["clockObservers"] = clock_observers_elem
                self.domDocs["treatments"] = treatments_elem
                self.domDocs["clock"] = clock_elem
                self.domDocs["main"] = root_node
                self.domDocs["scenario"] = scenarios_elem
                self.domDocs["outputNode"] = output_node
                self.domDocs["population"] = profile_elem
                self.domDocs["parameters"] = parameters_elem
                self.domDocs["system"] = system_elem
                # Update XSD dictionnaries
                # Creating a new PmtDictList, so we don't add the same pmtDict twice
                self.pmtDictList = PrimitiveDict(self)
                pluginsDef = system_elem.firstChildElement("Plugins")
                pluginsList = pluginsDef.childNodes()
                for i in range(0, pluginsList.length()):
                    currentPlugin = pluginsList.item(i)
                    if currentPlugin.isElement():
                        if currentPlugin.toElement().attribute("xsdfile",QtCore.QString("")) != QtCore.QString(""):
                            # We have a XSD file
                            listXSDFiles = str(currentPlugin.toElement().attribute("xsdfile")).split(";")
                            for xsdFile in listXSDFiles:
                                if os.path.isfile(self.folderPath + xsdFile):
                                    self.openXSDdictFile(self.folderPath + xsdFile)
                                elif os.path.isfile(self.saveDirectory+"/"+xsdFile):
                                    self.openXSDdictFile(self.saveDirectory+"/"+xsdFile)
                                else:
                                    print("Warning : unable to find required xsd file '" + self.folderPath+self.projectName + xsdFile + "'")
            
                stateNode = environment_elem.elementsByTagName("State")
                if stateNode.count():
                    self.domDocs["environment"] = environment_elem
                else : 
                    if environment_elem.hasAttribute("file"):
                        envNodePtr =  Opener(self.saveDirectory +"/"+self.projectName+"/"+ str(environment_elem.attribute("file")))
                        stateNode = environment_elem.ownerDocument().importNode(envNodePtr.getRootNode(), True)
                        environment_elem.parentNode().replaceChild(stateNode,environment_elem)
                        self.domDocs["environment"] = stateNode
                    else:
                        assert False, "In MainFrame::openParametersFile, couldn't find <State> in <Environment> node children"
                        #self.domDocs["environment"] = environment_elem.firstChild()
                
                #Update Environment tableview
                newEnvModel = EnvModel(self.domDocs["environment"], self)
                self.envTab.tableView.setModel(newEnvModel)
                self.envTab.tableView.setItemDelegate(EnvDelegate(self.envTab.tableView,self))
                
                #Make sure local variable model is empty
                baseLocVarModel = BaseLocalVariablesModel()
                baseLocVarModel.cleanUp()
                
                #Update Processes tab's widgets
                newProcessesListModel = ListTreatmentsModel(self.domDocs["treatments"], self.domDocs["clock"], "processes", self, self, self.domDocs["scenario"])
                self.treeTab.processesList.setModel(newProcessesListModel)
                self.treeTab.processesList.setItemDelegate(ProcessListDelegate(self.treeTab.processesList , self))
                
                #Update parameters tableView
                newParametersModel = ParametersModel(self.domDocs["parameters"],self,self.paramTab.tableView)
                self.paramTab.tableView.setModel(newParametersModel)
                self.paramTab.tableView.setItemDelegate(ParamDelegate(self.paramTab.tableView,self))
                #Update Clock Observers Table/list View
                newClockObserverModel = ListClockObserversModel(self.domDocs["clockObservers"],self.obsTab.clockObservers,self)
                self.obsTab.clockObservers.setModel(newClockObserverModel)
                self.obsTab.clockObservers.setItemDelegate(ObserverDelegate(self.obsTab.clockObservers,self))
                self.obsTab.clockObserversData.setModel(None)
                
                #Update scenarios tree/list view
                newScenariosListModel = ListTreatmentsModel(self.domDocs["treatments"], self.domDocs["clock"], "scenarios", self, self, self.domDocs["scenario"])
                self.simTab.tableView.setModel(newScenariosListModel)
                self.simTab.tableView.setItemDelegate(ProcessListDelegate(self.simTab.tableView , self))
                #Look if clock Tree has a fixed Value:
                foundFixedValue = False
                
                if self.domDocs["clock"].firstChildElement("PrimitiveTree").firstChild().nodeName()==QtCore.QString("Operators_IsEqualComplex"):
                    if self.domDocs["clock"].firstChildElement("PrimitiveTree").firstChild().firstChild().nodeName()==QtCore.QString("Data_Clock"):
                        if self.domDocs["clock"].firstChildElement("PrimitiveTree").firstChild().firstChild().nextSiblingElement().nodeName()==QtCore.QString("Data_Value"):
                            if str(self.domDocs["clock"].firstChildElement("PrimitiveTree").firstChild().firstChild().nextSiblingElement().attribute("inValue_Type")) in ["ULong","UInt"]:
                                self.simTab.spinBox_2.setValue(int(self.domDocs["clock"].firstChildElement("PrimitiveTree").firstChild().firstChild().nextSiblingElement().attribute("inValue")))
                                self.simTab.radioButton_Fixed.setChecked(True)
                                foundFixedValue = True
                                
                if not foundFixedValue:
                    self.simTab.spinBox_2.setValue(0)
                    self.simTab.radioButton_Complex.setChecked(True)
                
                #Update clock units combobox
                self.simTab.unitsComboBox.setCurrentIndex(self.simTab.unitsComboBox.findText(self.domDocs["clock"].attribute("units","other")))
                        
                self.xmlPath = self.filePath
               
                #Loop through Profiles
                #If files are used to store data, open them and import root_node
               
                profileNode = profile_elem.firstChildElement("Generator").firstChildElement("Profiles")
                profileNodeList = profileNode.elementsByTagName("GenProfile")
                for i in range(0,profileNodeList.count()):
                    currProfile = profileNodeList.item(i)
                    currDemography = currProfile.firstChildElement("Demography")
                    currSimVar = currProfile.firstChildElement("SimulationVariables")
                    include_file = currDemography.attribute("file", "")
                    if include_file != QtCore.QString(""):
                        if not os.path.isfile(include_file):
                            f = Opener(self.saveDirectory +"/"+self.projectName+"/"+include_file)
                        else:
                            f = Opener(include_file)
                        tmpNodeImport = currDemography.ownerDocument().importNode(f.getRootNode(), True)
                        currDemography.appendChild(tmpNodeImport)
                    include_file = currSimVar.attribute("file", "")
                    if include_file != QtCore.QString(""):
                        if not os.path.isfile(include_file):
                            f = Opener(self.saveDirectory +"/"+self.projectName+"/"+include_file)
                        else:
                            f = Opener(include_file)
                        tmpNodeImport = currSimVar.ownerDocument().importNode(f.getRootNode(), True)
                        currSimVar.appendChild(tmpNodeImport)
                        
                #Finding Population Nodes in dom
                generatorDom = profile_elem.firstChildElement("Generator")
                sourceDom = profile_elem.firstChildElement("Population")
                #Creating models
                newBaseVarModelTemp = GeneratorBaseModel( self, generatorDom,sourceDom)
                profileMgrModel = GeneratorManagerModel(newBaseVarModelTemp, self.simTab.tableViewProMgr,self)
                self.simTab.tableViewProMgr.setModel(profileMgrModel)
                
                #Finding current index in comboBox and setting the appropriate model in the two tableviews
                #At first, empty comboBox
                self.popTab.comboBox.clear()
                for profiles in newBaseVarModelTemp.getProfilesList():
                    self.popTab.comboBox.addItem(QtCore.QString("Profile named : "+profiles), QtCore.QVariant(QtCore.QString(profiles)))
                currIndex = self.popTab.comboBox.currentIndex()
                baseModelDemo = PopModel(newBaseVarModelTemp,str(self.popTab.comboBox.itemData(currIndex).toString()))
                baseModelSim = PopModelSim(newBaseVarModelTemp,str(self.popTab.comboBox.itemData(currIndex).toString()))
                self.popTab.tableView_Supp.setModel(baseModelSim)
                self.popTab.tableView.setModel(baseModelDemo)
                self.outTab.listView.setModel(OutcomeListProfileModel(newBaseVarModelTemp,self.outTab.listView))
                self.outTab.listView_3.setModel(OutcomeEnvModel(newEnvModel,output_node,self.outTab.listView_3,self))
                #Setting delegates
                self.popTab.baseModel = newBaseVarModelTemp
                self.popTab.tableView_Supp.setItemDelegate(VarSimDelegate(self.popTab.tableView,self))
                self.simTab.tableViewProMgr.setItemDelegate(VarGeneratorDelegate(self.simTab.tableViewProMgr,self))
                #Specific file for sensibility analysis
                self.openSensAnalysis()
                #Clearing tree Tab Preview(reload Mushroom)
                self.treeTab.SVGViewScroll.setWidget(QtSvg.QSvgWidget("Tests/Mushroom.svg"))
                
        self.dirty = False
        self.updateWindowTitle()
    
    def openParametersFileLSD(self, filePath):
        '''
        @summary Opens the parameters file, witch points to many configuration files, and dispatches info over the tabs
        This version opens a file named with the extension .lsd, itself containing a whole project
        This extension is actually a .zip containing all the files used for a simulation
        @param filePath : .lsd file to open
        '''
        
        ZipFile = zipfile.PyZipFile(str(filePath),"r")
        #Extracting the files needs path manipulation
        #because extractall() would extract the files in .exe's folder
        #Get rid of the .lsd file's name in the relpath
        lsdRelPathPartition = str(filePath).rpartition("/")
        wantedPath = lsdRelPathPartition[0]
        #Extract Files and open parameters file
        filePathPartition = str(filePath).rpartition(".")
        self.projectName = filePathPartition[0].split("/")[-1]
        ZipFile.extractall(wantedPath)
        projectMainFolder = filePathPartition[0]+"/"
        
        # Send configuration file to the standard function
        self.filePath = QtCore.QString(projectMainFolder+"parameters.xml")
        

    def openSensAnalysis(self):
        '''
        @summary Opens or create the sensibility analysis file if it doesn't exist
        Dispatch the information in the sensibility analysis tab
        '''
        if not self.saveDirectory:
            f = Opener("util/" + "sensanalysis.xml")
        else:
            if not os.path.exists(self.saveDirectory +"/"+self.projectName+"/" + "sensanalysis.xml"):
                newFile = QtCore.QFile(self.saveDirectory +"/"+self.projectName+"/"+"sensanalysis.xml")
                newFile.open(QtCore.QIODevice.WriteOnly)
                newFile.writeData("<SA/>")
            f = Opener(self.saveDirectory +"/"+self.projectName+"/" + "sensanalysis.xml")
        self.SAdocument = f.getDomDocument()
        saNode = f.getRootNode()
        saListModel = SaTableModel(saNode,self.saTab.saList,self)
        self.saTab.saList.setModel(saListModel)
        saCBModel = SaComboBoxModel( self.paramTab.tableView.model(),saListModel,self.saTab.comboBoxVar,self)
        self.saTab.comboBoxVar.setModel(saCBModel)
        self.saTab.saList.setItemDelegate(SensAnalysisDelegate(self.saTab.saList,self))
           
    def save(self):
        '''
        @summary Save function
        '''
        def cleanup(directory):
            for fileInfo in directory.entryInfoList(QtCore.QDir.NoDotAndDotDot|QtCore.QDir.Dirs):
                if str(fileInfo.absoluteFilePath()).rsplit("/")[-1] =="XSD":
                    continue
                cleanup(QtCore.QDir(fileInfo.absoluteFilePath()))
                directory.rmdir(fileInfo.absoluteFilePath())
            for fileInfo in directory.entryInfoList(QtCore.QDir.NoDotAndDotDot|QtCore.QDir.Files):
                directory.remove(fileInfo.absoluteFilePath())
        
        if not self.saveDirectory and not self.projectName:
            self.saveAs()
        else:
            #Creating saving directory
            currentDir = QtCore.QDir(self.saveDirectory)
            currentDir.mkdir(self.projectName)
            saveDir = QtCore.QDir(self.saveDirectory + "/" + self.projectName)
            #Empty directory before creating new directories
            cleanup(saveDir)
            saveDir.mkdir("Processes")    
            saveDir.mkdir("Populations")
            saveDir.mkdir("Environment")
            if not os.path.exists(self.saveDirectory + "/" + self.projectName+"/XSD"):
                saveDir.mkdir("XSD")
                for dictionnaries in self.pmtDictList.getDictList().keys():
                    fileName = dictionnaries.rpartition("/")[-1]
                    shutil.copyfile(dictionnaries,self.saveDirectory + "/" + self.projectName+"/XSD/"+fileName)
                #Copy 2 base dictionary
                shutil.copyfile("util/XSD/GUI.xsd",self.saveDirectory + "/" + self.projectName+"/XSD/GUI.xsd")
                shutil.copyfile("util/XSD/PMT.xsd",self.saveDirectory + "/" + self.projectName+"/XSD/PMT.xsd")
            
            else:
                for dictionnaries in self.pmtDictList.getDictList().keys():
                    if not os.path.isfile(self.saveDirectory + "/" + self.projectName+"/XSD/"+dictionnaries.rpartition("/")[-1]):
                        #Dictionary added to the saved project
                        shutil.copyfile(dictionnaries,self.saveDirectory + "/" + self.projectName+"/XSD/"+dictionnaries.rpartition("/")[-1])
                        
            for i in range(0, self.domDocs["system"].firstChildElement("Plugins").elementsByTagName("Plugin").count()):
                currentPlugin = self.domDocs["system"].firstChildElement("Plugins").elementsByTagName("Plugin").item(i)
                currentPlugin.toElement().setAttribute("xsdfile","XSD/"+str(currentPlugin.toElement().attribute("xsdfile")).rpartition("/")[-1])
            
            
            saveDir.mkdir("Libraries")
            #First, clean dom for gui related attributes
            pmtTreeDomList = self.document.elementsByTagName("PrimitiveTree")
            for currIndex in range(0,pmtTreeDomList.count()):
                currPmtDom = pmtTreeDomList.item(currIndex)
                if currPmtDom.toElement().hasAttribute("gui.id"):
                    currPmtDom.toElement().removeAttribute("gui.id")
            
            popGenTag = self.domDocs["population"]
            
            baseTrModel = BaseTreatmentsModel()
            
            processesDict = baseTrModel.getTreatmentsDict()
            scenariosDict = baseTrModel.scenariosDict
            #get ModelMappers
            processesMM = baseTrModel.getViewTreatmentsDict()
            scenariosMM = baseTrModel.getViewScenariosDict()
            #Processes save in different file+Removal in current DOM
            lastItemMoved = QtXml.QDomNode()
            for currP in processesMM:
                currPDom = processesDict[currP]
                fileP = QtCore.QFile(self.saveDirectory + "/" + self.projectName + "/Processes/" + currP + ".xml")
                fileP.open(QtCore.QIODevice.ReadWrite|QtCore.QIODevice.Truncate)
                self.tmpTextStream.setDevice(fileP)
                #Set xml declaration
                domNodeProcessingInstruction = self.document.createProcessingInstruction("xml", "version=\"1.0\" encoding=\"UTF-8\"")
                domNodeProcessingInstruction.save(self.tmpTextStream, 2)
                currPDom.save(self.tmpTextStream, 2)
                fileP.close()
                currPDom.parentNode().toElement().setAttribute("file", "Processes/" + currP + ".xml")
                #So the user gets the file back in the order he left them at the last save
                
                if processesMM.index(currP) == 0:
                    if currPDom.parentNode().previousSibling().isComment():
                        currPDom.parentNode().parentNode().insertBefore(currPDom.parentNode().previousSibling(),currPDom.parentNode().parentNode().firstChild())
                        currPDom.parentNode().parentNode().insertAfter(currPDom.parentNode(),currPDom.parentNode().parentNode().firstChild())
                    else:
                        currPDom.parentNode().parentNode().insertBefore(currPDom.parentNode(),currPDom.parentNode().parentNode().firstChild())
                    lastItemMoved = currPDom.parentNode()
                else:
                    if currPDom.parentNode().previousSibling().isComment():
                        nodeComment = currPDom.parentNode().previousSibling()
                        currPDom.parentNode().parentNode().insertAfter(nodeComment,lastItemMoved)
                        currPDom.parentNode().parentNode().insertAfter(currPDom.parentNode(), nodeComment)
                    else:
                        currPDom.parentNode().parentNode().insertAfter(currPDom.parentNode(),lastItemMoved)
                    lastItemMoved = currPDom.parentNode()
                    
                currPDom.parentNode().removeChild(currPDom)

            #Scenario swap in dom, if necessary
            for currS in scenariosMM:
                currSDom = scenariosDict[currS]["node"]
                if scenariosMM.index(currS) == 0:
                    if currSDom.previousSibling().isComment():
                        currSDom.parentNode().insertBefore(currSDom.previousSibling(),currSDom.parentNode().firstChild())
                        currSDom.parentNode().insertAfter(currSDom,currSDom.parentNode().firstChild())
                    else:
                        currSDom.parentNode().insertBefore(currSDom,currSDom.parentNode().firstChild())
                else:
                    if currSDom.previousSibling().isComment():
                        nodeComment = currSDom.previousSibling()
                        currSDom.parentNode().insertAfter(nodeComment,lastItemMoved)
                        currSDom.parentNode().insertAfter(currSDom, nodeComment)
                    else:
                        currSDom.parentNode().insertAfter(currSDom,lastItemMoved)
                lastItemMoved = currSDom
                
             
            #Environment save in different file+ Removal in current DOM
            fileP = QtCore.QFile(self.saveDirectory+ "/"+ self.projectName+"/Environment/" + "Environment" +".xml")
            fileP.open(QtCore.QIODevice.ReadWrite|QtCore.QIODevice.Truncate)
            self.tmpTextStream.setDevice(fileP)
            #Set xml declaration
            domNodeProcessingInstruction = self.document.createProcessingInstruction("xml", "version=\"1.0\" encoding=\"UTF-8\"")
            domNodeProcessingInstruction.save(self.tmpTextStream, 2)
            #Save variables in order they appear in the view
            stateNode = self.domDocs["environment"].toElement().elementsByTagName("State").item(0)
            envModel = BaseEnvModel()
            if len(envModel.getVars()):
                currentEnvNode = stateNode.insertBefore(envModel.getVarNode(envModel.getVars()[0]),QtXml.QDomNode())
                for envVarName in envModel.getVars()[1:]:
                    currentEnvNode = stateNode.insertAfter(envModel.getVarNode(envVarName),currentEnvNode)
            
            self.domDocs["environment"].toElement().removeAttribute("file")
            self.domDocs["environment"].save(self.tmpTextStream,2)
            fileP.close()
            #Removal in Dom
            self.domDocs["environment"].toElement().setAttribute("file", "Environment/" + "Environment" + ".xml")
            self.domDocs["environment"].removeChild(self.domDocs["environment"].firstChild())
            #PopulationManager : Each Profiles will save it's simulation Variables in a different file
            #                    Demography will also be removed from Dom
            
            profileTagChildren = popGenTag.elementsByTagName("GenProfile")
            for i in range(0,profileTagChildren.count()):
                currentGenProfile = profileTagChildren.item(i)
                currentSimVar = currentGenProfile.firstChildElement("SimulationVariables")
                currentSimVarFileName = currentSimVar.attribute("file")
                if currentSimVarFileName.isEmpty() or os.path.exists(self.saveDirectory+ "/"+ self.projectName + "/"+str(currentSimVarFileName)):
                    currentSimVarFileName = "Populations/SimulationVariables.xml"
                    count = 0 
                    while True:
                        if os.path.exists(self.saveDirectory+ "/"+ self.projectName + "/"+str(currentSimVarFileName)):
                            currentSimVarFileName = currentSimVarFileName.rstrip("0123456789.xml")+str(count)+(".xml")
                            count+=1
                            continue
                        break
                
                fileP = QtCore.QFile(self.saveDirectory+ "/"+ self.projectName + "/"+str(currentSimVarFileName))
                fileP.open(QtCore.QIODevice.ReadWrite|QtCore.QIODevice.Truncate)
                self.tmpTextStream.setDevice(fileP)
                #Set xml declaration
                domNodeProcessingInstruction = self.document.createProcessingInstruction("xml", "version=\"1.0\" encoding=\"UTF-8\"")
                domNodeProcessingInstruction.save(self.tmpTextStream, 2)
                #Save variables in the order they appear in the view, check for dependencies(save non-dependent variable first)                
                simVarNode = currentSimVar.ownerDocument().createElement("SimulationVariables")
                baseVarModel = GeneratorBaseModel()
                simVarMM = list(baseVarModel.getSimViewVarsList(str(currentGenProfile.toElement().attribute("label"))))
                
                #Write checking dependencies
                while simVarMM:
                    wroteVariables = []
                    for variable in simVarMM:
                        if baseVarModel.getVarDepends(currentGenProfile.toElement().attribute("label"), variable):
                            dependencies = baseVarModel.getVarDepends(currentGenProfile.toElement().attribute("label"), variable)
                            if filter(lambda x:x in simVarMM,dependencies):
                                #dependency still in list continue
                                continue
                                
                        #dependencies have all been written
                        newChildReference = simVarNode.appendChild(baseVarModel.getVarNode(currentGenProfile.toElement().attribute("label"), variable))
                        newChildReference.toElement().setAttribute("gui.position",baseVarModel.getSimViewVarsList(str(currentGenProfile.toElement().attribute("label"))).index(variable))
                        wroteVariables.append(variable)
                    
                    simVarMM = filter(lambda x:x not in wroteVariables,simVarMM)
                
                
                simVarNode.save(self.tmpTextStream, 2)
                fileP.close()
                currentSimVar.removeChild(currentSimVar.firstChild())
                currentSimVar.setAttribute("file",str(currentSimVarFileName))
                currentDemography = currentGenProfile.firstChildElement("Demography")
                demographyName = str(currentDemography.attribute("file")).rpartition("/")[-1]
                if demographyName :
                    fileP = QtCore.QFile(self.saveDirectory+ "/"+ self.projectName + "/Populations/"+demographyName)
                    fileP.open(QtCore.QIODevice.ReadWrite|QtCore.QIODevice.Truncate)
                    self.tmpTextStream.setDevice(fileP)
                    #Set xml declaration
                    domNodeProcessingInstruction = self.document.createProcessingInstruction("xml", "version=\"1.0\" encoding=\"UTF-8\"")
                    domNodeProcessingInstruction.save(self.tmpTextStream, 2)
                    #Write file
                    currentDemography.firstChildElement("Demography").save(self.tmpTextStream,2)
                    currentDemography.setAttribute("file","Populations/"+demographyName)
                currentDemography.removeChild(currentDemography.firstChildElement("Demography"))
            
            #Save Parameters in order they appear in the view
            baseParamModel = BaseParametersModel()
            paramMM = baseParamModel.modelMapper
            if paramMM:
                refNode = self.domDocs["parameters"].insertBefore(baseParamModel.getRefNode(paramMM[0]),self.domDocs["parameters"].firstChild())
            for reference in paramMM[1:]:
                refNode = self.domDocs["parameters"].insertAfter(baseParamModel.getRefNode(reference),refNode)
            
            #Save parameters file
            #Before saving file, ensure outcome model doesn't contain profiles/variables that do not belong to the model anymore
            #Environment first
            envOutputNode = self.domDocs["outputNode"].firstChildElement("Environment")
            varList = envOutputNode.elementsByTagName("Variable")
            envModel = BaseEnvModel()
            for i in range(0,varList.count()):
                if str(varList.item(i).toElement().attribute("label","")) not in envModel.getVars():
                    envOutputNode.removeChild(varList.item(i))
            #Then Population
            #See if all profiles exist
            popOutputNode = self.domDocs["outputNode"].firstChildElement("Population")
            profileList = popOutputNode.elementsByTagName("SubPopulation")
            popModel = GeneratorBaseModel()
            for i in range(0,profileList.count()):
                if str(profileList.item(i).toElement().attribute("profile","")) not in popModel.getProfilesList():
                    popOutputNode.removeChild(profileList.item(i))
            
            #See if all variables exist
            profileList = popOutputNode.elementsByTagName("SubPopulation")
            popModel = GeneratorBaseModel()
            for i in range(0,profileList.count()):
                currentProfile = profileList.item(i)
                varList = currentProfile.toElement().elementsByTagName("Variable")
            #Protection to prevent demography variables from entering outcome
             #   for j in range(0,varList.count()):
                 #   if str(varList.item(j).toElement().attribute("label","")) not in popModel.getSimVarsList(currentProfile.toElement().attribute("profile","")):
                      #  currentProfile.removeChild(varList.item(j)) 
                        
            #File can now be saved
            fileParameters = QtCore.QFile(self.saveDirectory + "/" + self.projectName + "/parameters.xml")
            fileParameters.open(QtCore.QIODevice.ReadWrite|QtCore.QIODevice.Truncate)
            self.tmpTextStream.setDevice(fileParameters)
            #Set xml declaration
            domNodeProcessingInstruction = self.document.createProcessingInstruction("xml", "version=\"1.0\" encoding=\"UTF-8\"")
            domNodeProcessingInstruction.save(self.tmpTextStream, 2)
            #Save file
            self.domDocs["main"].save(self.tmpTextStream, 2)
            fileParameters.close()
            
            #Save sens analysis
            fileSensAnalysis = QtCore.QFile(self.saveDirectory + "/" + self.projectName + "/sensanalysis.xml")
            fileSensAnalysis.open(QtCore.QIODevice.ReadWrite|QtCore.QIODevice.Truncate)
            self.tmpTextStream.setDevice(fileSensAnalysis)
            #Set xml declaration
            domNodeProcessingInstruction = self.document.createProcessingInstruction("xml", "version=\"1.0\" encoding=\"UTF-8\"")
            domNodeProcessingInstruction.save(self.tmpTextStream, 2)
            #Save SA File
            self.saTab.saList.model().dom.save(self.tmpTextStream, 2)
            fileSensAnalysis.close()
            
            #Compressing to zip archive
            ZipFile = zipfile.PyZipFile(self.saveDirectory+"/"+self.projectName+".lsd","w")
            for dirPath, dirNames, fileNames in os.walk(self.saveDirectory+"/"+self.projectName):
                for file in fileNames:
                   
                    #Find the relative path from Main folder to Save Folder
                    relativeFileName = os.path.relpath(os.path.join(dirPath, file))
                    #Write the archive in Save Folder
                    #Archive is going to be SaveFolder/projectname.lsd
                    #the content of the archive is going to be : projectname/ - Environments/etc..
                    #                                                         - Populations/etc...
                    #                                                         - Processes/etc...
                    #                                                         - Libraries/etc...
                    #                                                         - XSD/etc...
                    #                                                         - parameters.xml

                    ZipFile.write(relativeFileName,os.path.relpath(relativeFileName, self.saveDirectory))
            ZipFile.close()
            
            self.dirty = False
            
            ##TODO Delete Folders, keep only .lsd
            self.openParametersFile(QtCore.QString(self.saveDirectory + "/" + self.projectName + ".lsd"))
            
    def loadSettings(self):
        '''
        @summary Loads settings located in settings.xml
        '''
        if os.path.exists("util/settings.xml"):
            f = Opener("util/settings.xml")
        else:
            #if file doesn't exist, create one with default settings so app doesn't crash
            file = open("util/settings.xml","w")
            file.write("""  <Settings>
                            <View>
                            <envTab show="0"/>
                            <obsTab show="0"/>
                            </View>
                            <Models>
                            <Scenario showEnv="0"/>
                            </Models>
                            <LSD automaticLoadAtStarup="0"/>
                            <Check automaticCheckAtStartup="0"/>
                            <Wizard automaticLaunchAtStartup="0"/>
                            <Loading lastLoadedProject=""/>
                            <SC>
                            <Project label=""/>
                            <Mail label=""/>
                            <Mailif label="n"/>
                            <Server address="" user=""/>
                            </SC>
                            </Settings>""")
            file.close()
            f = Opener("util/settings.xml")
        self.prefDocument = f.getDomDocument()
        self.domDocs["settings"] = f.getRootNode()
        viewNode = self.domDocs["settings"].firstChildElement("View")
        self.viewMenu.actions()[0].setChecked(viewNode.firstChildElement("envTab").attribute("show").toInt()[0])
        self.viewMenu.actions()[1].setChecked(viewNode.firstChildElement("obsTab").attribute("show").toInt()[0])
        self.showEnv(viewNode.firstChildElement("envTab").attribute("show").toInt()[0])
        self.showObs(viewNode.firstChildElement("obsTab").attribute("show").toInt()[0])
        lsdNode = self.domDocs["settings"].firstChildElement("LSD")
        checkNode = self.domDocs["settings"].firstChildElement("Check")
        wizardNode = self.domDocs["settings"].firstChildElement("Wizard")
        loadNode = self.domDocs["settings"].firstChildElement("Loading")
        if wizardNode.attribute("automaticLaunchAtStartup").toInt()[0]:
            self.startWizard()
        else:
            if loadNode.attribute("lastLoadedProject") == QtCore.QString("") or not lsdNode.attribute("automaticLoadAtStartup").toInt()[0]:
                self.openParametersFile(QtCore.QString("util/parameters_file_template.xml"))
            else:
                filePath = loadNode.attribute("lastLoadedProject")
                try :
                    self.openParametersFile(QtCore.QString(filePath))
                except IOError:
                    #IOError from pyzipfile, file cannot be loaded, open default project
                    self.openNewProject()
          
        self.showMaximized()
        
        self.settingsModel = PrefModel(self.domDocs["settings"],self)
        
        if checkNode.attribute("automaticCheckAtStartup").toInt()[0]:
            self.checkModel()
        
    def showPref(self):
        prefDialog = PrefDialog(self.domDocs["settings"],self)
        prefDialog.exec_()
    
    def saveAs(self):
        '''
        @summary Save as a new project
        '''
        newPath = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save simulation project"),
                                                        "Tests", self.tr("LSD Simulator files (*.lsd);;All files (*);;"))
        if newPath == QtCore.QString(""):
            #User pressed cancel, return
            return
        if newPath.contains("."):
            newPath = newPath.section(".",0,-2)
        self.projectName = str(newPath.section('/', -1))
        self.saveDirectory = str(newPath.section('/', 0, -2))

        self.save()
            
    def checkModel(self):
        '''
        @summary Check project for errors
        '''
        self.checkVars()
        self.checkProcessesAndScenarios()
      
    def checkVars(self):
        '''
        @summary Check simulation variables for errors
        '''
        self.statusBar().showMessage(self.tr("Checking Variables"))
        #get BaseVarModel instance :
        baseVarModel = GeneratorBaseModel()
        for profiles in baseVarModel.getProfilesList():
            for variables in baseVarModel.getSimVarsList(profiles):
                primitive = Primitive(None,None,self,baseVarModel.getVarNode(profiles,variables).toElement().elementsByTagName("PrimitiveTree").item(0).firstChild())
                baseVarModel.updateValidationState(variables,primitive,profiles)
            
    def checkProcessesAndScenarios(self):
        '''
        @summary Check processes and scenarios for errors
        '''
        self.statusBar().showMessage(self.tr("Checking Processes And Scenarios"))
        #Get BaseTreatmentsModel instance :
        baseTrModel = BaseTreatmentsModel()
        for processes in baseTrModel.getViewTreatmentsDict():
            primitive = Primitive(None,None,self,baseTrModel.getTreatmentTree(processes).toElement().elementsByTagName("PrimitiveTree").item(0).firstChild())
            baseTrModel.updateValidationState(processes,primitive)
            
    def demoEditor(self):
        '''
        @summary Launch demography editor
        '''
        reply = QtGui.QMessageBox.question(self,"Launching Demography File Editor" , "Do you want to start by loading an existing demography File?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            demoEditor = demoFileEditor(self)
        else:
            demoEditor = demoFileEditor(self,False)
            
        demoEditor.exec_()
        #Clear demography file editor's base model
        fakeSingletonSimpleModel.clearVar()
        
    def fileGenerator(self):
        '''
        @summary Open file generator, which allwos to create multiple files with different seed elements
        '''
        fileGenerator = FileGenerator(self.filePath,self)
        fileGenerator.exec_()
        
    def search(self):
        '''
        @summary Open search dialog
        '''
        searchTool = searchDialog(self)
        searchTool.exec_()
        
    def showObs(self,boolShow):
        '''
        @summary Hide or Show observers tab and update settings
        @param boolShow : Hide or show
        '''
        if boolShow:
            self.tabs.insertTab(self.tabs.indexOf(self.treeTab)+1,self.obsTab,"&Observers")
            self.domDocs["settings"].firstChildElement("View").firstChildElement("obsTab").setAttribute("show",1)
            return
        self.domDocs["settings"].firstChildElement("View").firstChildElement("obsTab").setAttribute("show",0)
        self.tabs.removeTab(self.tabs.indexOf(self.obsTab))
        
    def showEnv(self,boolShow):
        '''
        @summary Hide or Show Environment tab and update settings
        @param boolShow : Hide or show
        '''
        if boolShow:
            self.tabs.insertTab(0,self.envTab, "&Environment")
            self.domDocs["settings"].firstChildElement("View").firstChildElement("envTab").setAttribute("show",1)
            return
        self.domDocs["settings"].firstChildElement("View").firstChildElement("envTab").setAttribute("show",0)
        self.tabs.removeTab(0)

    def exit(self):
        '''
        @summary Leave program
        '''
        if self.okToContinue():
            self.close()
            
    def helpAbout(self):
        '''
        @summary Show help message
        '''
        QtGui.QMessageBox.about(self, "About LSD Simulator",
                                """<b>LSD Simulator</b> v %s
                          <p>This program is free software.
                          <p>This is the simulator input application.
                          <p>Python %s - Qt %s - PyQt %s on %s""" 
                                % (__version__, platform.python_version(), QtCore.QT_VERSION_STR, QtCore.PYQT_VERSION_STR, platform.system()))
                            
    def updateWindowTitle(self):
        '''
        @summary Update program's title bar
        '''
        if self.dirty:
            self.setWindowTitle(self.tr("%s" % QtGui.QApplication.applicationName() + " * [" + str(self.filePath) + "]"))
        else:
            if self.filePath.isEmpty():
                self.setWindowTitle("LSD Simulator Dashboard -- version alpha")
            else:
                self.setWindowTitle(self.tr("%s" % QtGui.QApplication.applicationName() + " [" + str(self.filePath) + "]"))
        
    def closeEvent(self, event):
        '''
        @summary Reimplemented from QtGui.QMainWindow.closeEvent(self,event). Save settings and quit.
        @param event : see QMainWindow's documentation for more information
        '''
        if self.okToContinue():
            #Save GUI settings
            if self.saveDirectory and self.projectName:
                self.domDocs["settings"].firstChildElement("Loading").setAttribute("lastLoadedProject",self.saveDirectory+"/"+self.projectName+".lsd")
            fileP = QtCore.QFile("util/settings.xml")
            fileP.open(QtCore.QIODevice.ReadWrite|QtCore.QIODevice.Truncate)
            self.tmpTextStream.setDevice(fileP)
            #Set xml declaration
            domNodeProcessingInstruction = self.document.createProcessingInstruction("xml", "version=\"1.0\" encoding=\"UTF-8\"")
            domNodeProcessingInstruction.save(self.tmpTextStream, 2)
            self.domDocs["settings"].save(self.tmpTextStream, 2)
            fileP.close()
            self.close()
        else:
            event.ignore()
    
    def showEvent(self,event):
        '''
        @summary Resize table headers 
        @param event : see Qt's documentation for more information
        '''
        QtGui.QWidget.showEvent(self,event)
        self.envTab.tableView.horizontalHeader().resizeSections(QtGui.QHeaderView.ResizeToContents)
        self.popTab.tableView.horizontalHeader().resizeSections(QtGui.QHeaderView.ResizeToContents)
        self.popTab.tableView_Supp.horizontalHeader().resizeSections(QtGui.QHeaderView.ResizeToContents)
        self.paramTab.tableView.horizontalHeader().resizeSections(QtGui.QHeaderView.ResizeToContents)
        self.simTab.tableView.horizontalHeader().resizeSections(QtGui.QHeaderView.ResizeToContents)
        self.simTab.tableViewProMgr.horizontalHeader().resizeSections(QtGui.QHeaderView.ResizeToContents)
        
    def getOutputNode(self):
        '''
        @summary Return OutputNode XML node
        '''
        return self.domDocs["outputNode"]
    
    def takeScreenshot(self):
        '''
        @summary Takes and save a picture of the currently visible window
        '''
        #-22 is to grab the window frame(the title bar)
        screenshot = QtGui.QPixmap.grabWindow(self.winId(),0,-22)
        fileName = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save screenshot"),
                                                        self.filePath, self.tr("PNG files (*.png);;All files (*);;"))
        if fileName:
            screenshot.save(fileName,QtCore.QString("png").toAscii())
        
class MyWidgetTabEnvironment(QtGui.QWidget, UITab1):
    '''
    Transforms the class in the generated python file in an executable Widget
    This is the environment tab
    '''
    def __init__(self, parent):
        QtGui.QWidget.__init__(self)
        UITab1.__init__(self, parent)
        self.setupUi(self)

class MyWidgetTabProcesses(QtGui.QWidget, UITab3):
    '''
    Transforms the class in the generated python file in an executable Widget
    This is the processes(tree) tab
    '''
    def __init__(self, parent):
        QtGui.QWidget.__init__(self)
        UITab3.__init__(self, parent)
        self.setupUi(self)

class MyWidgetTabSimulation(QtGui.QWidget, UITab4):
    '''
    Transforms the class in the generated python file in an executable Widget
    This is the simulation tab
    '''
    def __init__(self, parent):
        QtGui.QWidget.__init__(self)
        UITab4.__init__(self, parent)
        self.setupUi(self)

class MyWidgetTabObservers(QtGui.QWidget, UITabObservers):
    '''
    Transforms the class in the generated python file in an executable Widget
    This is the Observers tab
    '''
    def __init__(self, parent):
        QtGui.QWidget.__init__(self)
        UITabObservers.__init__(self, parent)
        self.setupUi(self)
        
class MyWidgetTabPopulation(QtGui.QWidget,UITabPopulation):
    '''
    Transforms the class in the generated python file in an executable Widget
    This is the population tab
    '''
    def __init__(self, parent):
        QtGui.QWidget.__init__(self)
        UITabPopulation.__init__(self, parent)
        self.setupUi(self)
        
class MyWidgetTabParameters(QtGui.QWidget,UITabParameters):
    '''
    Transforms the class in the generated python file in an executable Widget
    This is the parameters tab
    '''
    def __init__(self, parent):
        QtGui.QWidget.__init__(self)
        UITabParameters.__init__(self, parent)
        self.setupUi(self)

    def showEvent(self,event):
        '''
        @summary Resets the model before tab is shown
        Adding parameters via the tree editor causes the model to be out of sync, hence the necessity of this function
        '''
        if self.tableView.model():
            self.tableView.model().beginResetModel()
            self.tableView.model().getBaseModel().lookForRefUsed()
            self.tableView.model().endResetModel()
        QtGui.QWidget.showEvent(self,event)
            
        
class MyWidgetTabOutCome(QtGui.QWidget,UITabOutCome):
    '''
    Transforms the class in the generated python file in an executable Widget
    This is the Outcome tab
    '''
    def __init__(self, parent):
        QtGui.QWidget.__init__(self)
        UITabOutCome.__init__(self, parent)
        self.setupUi(self)
    
    def showEvent(self,event):
        '''
        @summary Reset models before tab is shown
        Adding variable to the environments or an already selected profile will cause model(s) to be out of sync, hence the necessity of this function
        '''
        self.listView.model().beginResetModel()
        self.listView.model().endResetModel()
        if self.listView_2.model():
            self.listView_2.model().beginResetModel()
            self.listView_2.model().endResetModel()
        self.listView_3.model().beginResetModel()
        self.listView_3.model().endResetModel()
        QtGui.QWidget.show(self)  

class MyWidgetTabAnalysis(QtGui.QWidget,UITabAnalysis):
    '''
    Transforms the class in the generated python file in an executable Widget
    This is the SensAnalysis tab
    '''
    def __init__(self, parent):
        QtGui.QWidget.__init__(self)
        UITabAnalysis.__init__(self, parent)
        self.setupUi(self)   
