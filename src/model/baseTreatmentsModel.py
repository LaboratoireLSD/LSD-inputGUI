'''
Created on 2009-09-15

@author:  Marc-Andre Garnder
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

from PyQt4 import QtXml,QtCore
from util.opener import Opener
from model.LocalVariableModel import BaseLocalVariablesModel

def fakeSingleton(BaseTreatmentsModel):
    '''
    Python Decorator, emulates a singleton behavior
    It emulates the behavior because if the user passes arguments to the constructor, we implicitly consider he wants a new instance of BaseTreatmentsModel
    Else, its acts as a singleton
    '''
    instance_container = []
    def wrapper(*args):
        '''
        @summary Wrapper function
        '''
        if not len(instance_container):
            #Create BaseTreatmentsModel if it doesn't exist
            instance_container.append(BaseTreatmentsModel(*args))
        elif len(args):
            #If it exists and arguments are passed through the constructor, create new instance
            instance_container[0] = BaseTreatmentsModel(*args)
        #return singleton or new instance
        return instance_container[0]
    return wrapper

@fakeSingleton
class BaseTreatmentsModel:
    '''
    This is a class containing all the data of the xml tags <Processes> and <Scenarios> of a configuration file (often named parameters.xml)
    All the data is mapped to dictionaries and two modelMappers.
    Note : a scenario is a process that gets called at the beginning of the simulation
    '''

    def __init__(self, domTree, scenarioDomTree, windowObject):
        '''
        @summary Constructor
        @param domTree : Processes's xml node
        @param scenarioDomTree : Scenarios's xml node
        @param windowObject : application's main window
        '''
        self.dom = domTree
        self.topObject = windowObject
        self.scenarioDom = scenarioDomTree
        self.treatmentsDict = {}
        self.scenariosDict = {}
        
        self.need_update = True
        self.scenarioModelMapper = []
        self.processesModelMapper = []
        self.validityDict = {}
        
        if not self.dom.isNull():
            self._listTreatments()
    
    def getScenarioLabel(self,scenarioName):
        '''
        @summary Return scenario's label dict
        @param scenarioName : name of the scenario'S process
        '''
        return self.scenariosDict[scenarioName]
    
    def getTreatmentTree(self, tr_name):
        '''
        @summary Return xml dom tree of a process
        @param tr_name : process's name
        '''
        if str(tr_name) not in self.treatmentsDict.keys():
            print("ERROR in BaseTreatmentsModel::getTreatmentTree() : no such treatment like '" + str(tr_name) + "'")
            return
        else:
            return self.treatmentsDict[str(tr_name)]
        
    def updateValidationState(self,trName, pmtRoot):
        '''
        @summary Tries to update the validation state of a process
        @param trName : name of the process
        @param pmtRoot : Primitive instance from class Primitive in model.Primitive.model. It is the first Primitive
        of the xml tree, where the validation state of a tree is kept
        @return True if success, else False
        '''
        if trName in  self.getViewTreatmentsDict():
            self.validityDict[trName] = pmtRoot._findWorstEvent(True)
            return True
        return False
        
    def getProcessValidity(self,processName):
        '''
        @summary Return's process/scenario validity
        @param processName : process/scenario's name
        Actual validity values are : Valid, Error, Warning, Unknown
        '''
        if processName in self.validityDict:
            return self.validityDict[processName]
        return "Unknown"
    
    def _mapToModel(self):
        '''
        @summary Since you cannot control where the data will be inserted in a dictionary(it is dependent of the key and the hash function), we need a table to store
        the keys in order the user wants them to appear
        This function is created to keep the model and the data in sync, while keeping the current data layout in the view 
        '''
        for variable in self.scenariosDict.keys():
            if variable not in self.scenarioModelMapper:
                self.scenarioModelMapper.append(variable)
        
        for variable in self.scenarioModelMapper:
            if variable not in self.scenariosDict.keys():
                self.scenarioModelMapper.remove(variable)
                
        for variable in self.treatmentsDict.keys():
            if variable not in self.processesModelMapper:
                self.processesModelMapper.append(variable)
                        
        for variable in self.processesModelMapper:
            if variable not in self.treatmentsDict.keys():
                self.processesModelMapper.remove(variable)
    
    def getTreatmentsDict(self):
        ''' 
        @summary Return a list of all defined process that aren't scenarios
        '''
        if self.need_update:
            self._listTreatments()

        return self.treatmentsDict
    
    def getViewTreatmentsDict(self):
        ''' 
        @summary Return a list of all defined process that aren't scenarios in order they appear in the view
        '''
        return self.processesModelMapper
    
    def getViewScenariosDict(self):
        ''' 
        @summary Return a list of all defined scenarios in order they appear in the view
        '''
        return self.scenarioModelMapper

    def _isScenario(self, name):
        '''
        @summary Return true if label is a scenario
        @param name : processe's name
        '''
        return str(name) in self.scenariosDict.keys()
        
    def getHowManyTreatments(self):
        ''' 
        @summary Return number of processes that aren't scenarios
        '''
        return len(self.treatmentsDict)

    def getHowManyScenarios(self):
        ''' 
        @summary Return number of scenarios
        '''
        return len(self.scenariosDict.keys())
    
    def addTreatment(self, trName, trTree=QtXml.QDomNode(),isScenario=False,rowToInsert=0):
        '''
        @summary Adds a process to the model
        @param trName : process's name
        @param trTree : process's xml tree, if any
        @param isScenario : boolean, True if user adds a scenario
        @param rowToInsert : position to insert in the model mapper
        '''
        #Check if process is already in model
        compteur = 0
        while trName in self.treatmentsDict.keys() or trName in self.scenariosDict.keys():
            if compteur == 0:
                print("Warning in BaseTreatmentsModel::addTreatment() : cannot add existing treatment " + str(trName)+". Renaming treatment.")
            trName = trName.rstrip("0123456789")
            trName = trName + str(compteur)
            compteur+=1
        
        if isScenario:
            #Append a new scenario to the <scenario Node>
            newScenarioNode = self.scenarioDom.ownerDocument().createElement("Scenario")
            newScenarioNode.toElement().setAttribute("label",trName)
            newScenarioNode.toElement().setAttribute("processIndividual","")
            self.scenarioDom.appendChild(newScenarioNode)
            self.scenarioModelMapper.insert(rowToInsert,str(trName))
            
        else:
            #Create process
            newEntryNode = self.dom.ownerDocument().createElement("Process")
            newEntryNode.toElement().setAttribute("label", trName)
            
            newProcessNode = self.dom.ownerDocument().createElement("Process")
            newProcessNode.toElement().setAttribute("label", trName)
            
            newLocVarNode = self.dom.ownerDocument().createElement("LocalVariables")
            
            newPmtTreeNode = self.dom.ownerDocument().createElement("PrimitiveTree")
            newPmtTreeNode.toElement().setAttribute("size", 1)
    
            if trTree.isNull():
                newBaseContentNode = self.dom.ownerDocument().createElement("Control_Nothing")
            else:
                newBaseContentNode = trTree
            
            
            newPmtTreeNode.appendChild(newBaseContentNode)
            newProcessNode.appendChild(newLocVarNode)
            newProcessNode.appendChild(newPmtTreeNode)
            newEntryNode.appendChild(newProcessNode)
            self.dom.appendChild(newEntryNode)
            
            self.processesModelMapper.insert(rowToInsert,str(trName))
        
        self.topObject.dirty = True
        self.need_update = True
        self._listTreatments()
        
    def addProcessFromDom(self,processDom):
        '''
        @summary Adds a process coming from another DOM, usually an other simulation
        @param processDom : process's DOM
        '''
        newEntry = self.dom.ownerDocument().createElement("Process")
        fileRootNode = self.dom.ownerDocument().importNode(processDom, True)
        newEntry.toElement().setAttribute("label", fileRootNode.toElement().attribute("label"))
        newEntry.appendChild(fileRootNode)
        self.dom.appendChild(newEntry)
        
        self.topObject.dirty = True
        self.need_update = True
        self._listTreatments()
        
    def renameTreatment(self, trOldName, trNewName):
        '''
        @summary Rename process
        @param trOldName, trNewName : old process's name and new name
        '''
        #First, stringify trNewName(might be a QString)
        trNewName = str(trNewName)
        assert trNewName not in self.treatmentsDict.keys() or trNewName not in self.scenariosDict.keys(), "Error : can't rename treatment to an existing name"
        if trNewName == "":
            print("Cannot rename to an empty name!")
            return
        
        #Looking for Treatment name in <Scenario> Node if Treatment is a scenario
        if self._isScenario(trOldName):
            scenarios = self.scenarioDom.childNodes()
            for i in range(0,scenarios.count()):
                currentScenarioName = str(scenarios.item(i).toElement().attribute("label", ""))
                assert currentScenarioName != "", "In BaseTreatmentsModel::_isScenario() : scenario does not have label attribute!"
                if currentScenarioName == trOldName:
                    scenarios.item(i).toElement().setAttribute("label", QtCore.QString.fromUtf8(trNewName))
                    break
            self.scenarioModelMapper[self.scenarioModelMapper.index(str(trOldName))] = trNewName
        
        else:    
            #Looking for Treatment name in <Process> Node
            for indexTr in range(0, self.dom.childNodes().length()):
                currentTr = self.dom.childNodes().item(indexTr)
                if str(currentTr.toElement().attribute("label")) == trOldName:
                    currentTr.toElement().setAttribute("label", QtCore.QString.fromUtf8(trNewName))
                    currentTr.firstChildElement("Process").setAttribute("label",QtCore.QString.fromUtf8(trNewName))
                    break
    
            self.processesModelMapper[self.processesModelMapper.index(str(trOldName))] = trNewName
       
            
            #Check for treatment in Clock observer
            ClockObserverNode = self.topObject.domDocs["clockObservers"]
            assert not ClockObserverNode.isNull(), "Error : in baseTreatmentsModel::renameTreatment, no clock Node found"
            for i in range(0,ClockObserverNode.childNodes().size()):
                assert ClockObserverNode.childNodes().item(i).nodeName() == "Observer", "Error: in baseTreatmentsModel::renameTreatment, Invalid Tag "+ClockObserverNode.childNodes.item(i).nodeName()+" in ClockObservers Child List"
                #assert ClockObserverNode.childNodes().item(i).toElement().attribute("process") != "", "Error: in baseTreatmentsModel::renameTreatment, Observer Element has no process attribute"      
                if ClockObserverNode.childNodes().item(i).toElement().attribute("process") == trOldName:
                    #Rename Entry
                    ClockObserverNode.childNodes().item(i).toElement().setAttribute("process", QtCore.QString.fromUtf8(trNewName))
                    break
            
            #Check for tree in scenarios
            for i in range(0,self.scenarioDom.childNodes().size()):
                assert self.scenarioDom.childNodes().item(i).nodeName() == "Scenario", "Error: in baseTreatmentsModel::renameTreatment, Invalid Tag "+self.scenarioDom.childNodes().item(i).nodeName()+" in ClockObservers Child List"
                if self.scenarioDom.childNodes().item(i).toElement().attribute("processIndividual") == trOldName:
                    #Rename Entry
                    self.scenarioDom.childNodes().item(i).toElement().setAttribute("processIndividual", QtCore.QString.fromUtf8(trNewName))
                if self.scenarioDom.childNodes().item(i).toElement().attribute("processEnvironment") == trOldName:
                    #Rename Entry
                    self.scenarioDom.childNodes().item(i).toElement().setAttribute("processEnvironment", QtCore.QString.fromUtf8(trNewName))
                
        #Make document dirty, saving options will pop upon program termination
        self.topObject.dirty = True
        
        #If process in validtyDict, rename
        if trOldName in self.validityDict.keys():
            self.validityDict[trNewName] = self.validityDict[trOldName]
            self.validityDict.pop(trOldName)
        
        self.need_update = True
        self._listTreatments()      
                                                                   
    def removeTreatment(self, trName,isScenario=True):
        '''
        @summary Remove a process/scenario from the model
        @param trName : process or scenario's name
        '''
        #Delete entry in <Scenario> node if isScenario == True
        if isScenario:
            scenariosList = self.scenarioDom.childNodes()
            for i in range(0,scenariosList.count()):
                currentScenarioName = str(scenariosList.item(i).toElement().attribute("label", ""))
                assert currentScenarioName != "", "In BaseTreatmentsModel::_isScenario() : scenario does not have label attribute!"
                if currentScenarioName == trName:
                    self.scenarioDom.removeChild(scenariosList.item(i))
                    break

        else:
            for indexTr in range(0, self.dom.childNodes().length()):
                currentTr = self.dom.childNodes().item(indexTr)
                if str(currentTr.toElement().attribute("label")) == trName:
                    print("Info : deleting treatment named " + str(trName))
                    self.dom.removeChild(currentTr)
            #Check for treatment in Clock observer 
            ClockObserverNode = self.topObject.domDocs["clockObservers"]
            assert not ClockObserverNode.isNull(), "Error : in baseTreatmentsModel::removeVariable, no clock Node found"
            for i in range(0,ClockObserverNode.childNodes().size()):
                assert ClockObserverNode.childNodes().item(i).nodeName() == "Observer", "Error: in baseTreatmentsModel::renameTreatment, Invalid Tag "+ClockObserverNode.childNodes.item(i).nodeName()+" in ClockObservers Child List"      
                if ClockObserverNode.childNodes().item(i).toElement().attribute("process") == trName:
                    #Delete Entry
                    ClockObserverNode.removeChild(ClockObserverNode.childNodes().item(i))
                    break

        self.topObject.dirty = True
        
        #If process in validtyDict, rename
        if trName in self.validityDict.keys():
            self.validityDict.pop(trName)
            
        self.need_update = True
        self._listTreatments()

    def modifyInd(self,scenarioName,processName):
        '''
        @summary Sets the process of a scenario
        A scenario consists of a label, a process tree and/or and environment process tree(tree executed on the environment)
        This method allows a scenario individual's tree to point to a different tree
        @param scenarioName : name of the scenario
        @param processName: name of the tree this scenario refers to
        '''
        self.scenariosDict[scenarioName]["node"].toElement().setAttribute("processIndividual",processName)
        self.need_update = True
        self._listTreatments()
        
    def modifyEnv(self,scenarioName,processName):
        '''
        @summary Sets the process of a scenario
        A scenario consists of a label, a process tree and/or and environment process tree(tree executed on the environment)
        This method allows a scenario environment's tree to point to a different tree
        @param scenarioName : name of the scenario
        @param processName: name of the tree this scenario refers to
        '''
        self.scenariosDict[scenarioName]["node"].toElement().setAttribute("processEnvironment",processName)
        self.need_update = True
        self._listTreatments()
        
    def _listTreatments(self):
        '''
        @summary Parse dom and dispatch the information in the corresponding dictionaries/list
        '''
        self.treatmentsDict = {}
        self.scenariosDict = {}
        list_trt = self.dom.childNodes()
        
        for index_trt in range(0, list_trt.length()):
            treatmentNode = list_trt.item(index_trt)
            if treatmentNode.isComment():
                continue
            treatmentName = str(treatmentNode.toElement().attribute("label", ""))
            assert treatmentName != "", "In BaseTreatmentsModel::_listTreatments() : a <Process> tag does not have a 'label' attribute (required)"

            if not treatmentNode.hasChildNodes():
                include_file = treatmentNode.toElement().attribute("file", "")
                if str(include_file) != "":
                # Separated treatment file used for definition
                    f = Opener(self.topObject.saveDirectory+"/"+self.topObject.projectName+"/"+include_file)
                    fileRootNode = treatmentNode.ownerDocument().importNode(f.getRootNode(), True)
                    treatmentNode.appendChild(fileRootNode)
                    
            self.treatmentsDict[treatmentName] = treatmentNode.firstChild()
            if not treatmentName in self.processesModelMapper:
                self.processesModelMapper.append(treatmentName)
            #Preload in local variable model so Primitive Model Validator can find local variables even if tree hasn't yet been loaded in tree editor
            baseLocVarModel = BaseLocalVariablesModel()
            baseLocVarModel.parseLocVars(treatmentNode.toElement().elementsByTagName("PrimitiveTree").item(0))
                      
        list_scenarios = self.scenarioDom.childNodes()
        for index_scen in range(0,list_scenarios.length()):
            scenarioNode = list_scenarios.item(index_scen)
            if scenarioNode.isComment():
                continue
            scenarioName = str(scenarioNode.toElement().attribute("label", ""))
            assert scenarioName != "", "In BaseTreatmentsModel::_listTreatments() : a <Scenario> tag does not have a 'label' attribute (required)"
        
            self.scenariosDict[scenarioName] = {"indProcess":"","envProcess":"","node":""}
            self.scenariosDict[scenarioName]["indProcess"] = str(scenarioNode.toElement().attribute("processIndividual",""))
            self.scenariosDict[scenarioName]["envProcess"] = str(scenarioNode.toElement().attribute("processEnvironment",""))
            self.scenariosDict[scenarioName]["node"] = scenarioNode
            
            if not scenarioName in self.scenarioModelMapper:
                self.scenarioModelMapper.append(scenarioName)
                                                                                                        
        self._mapToModel()
        self.need_update = False
        