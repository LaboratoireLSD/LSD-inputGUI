
from PyQt4.QtXmlPatterns import QXmlQuery
from PyQt4.QtXml import QDomNode
from util.opener import Opener
from PyQt4.QtCore import QIODevice, QBuffer, QTextStream, QByteArray
from model.LocalVariableModel import BaseLocalVariablesModel

def fakeSingleton(GeneratorBaseModel):
    '''
    Python Decorator, emulates a singleton behavior
    It emulates the behavior because if the user passes arguments to the constructor, we implicitly consider he wants a new instance of GeneratorBaseModel
    Else, its acts as a singleton
    '''
    instance_container = []
    def wrapper(*args):
        '''
        @summary Wrapper function
        '''
        try:
            return SimpleBaseVarModel()
        except:
            if not instance_container:
                #Create GeneratorBaseModel if it doesn't exist
                instance_container.append(GeneratorBaseModel(*args))
            elif len(args):
                #If it exists and arguments are passed through the constructor, create new instance
                instance_container[0] = GeneratorBaseModel(*args)
            #return singleton or new instance
            return instance_container[0]
    return wrapper

@fakeSingleton
class GeneratorBaseModel:
    '''
    This is a huge class containing all the data of the xml tag <PopulationManager> of a configuration file (often named parameters.xml)
    All the data is mapped to two dictionaries, the modelMapper and the validity list:
    
    GeneratorBaseModel.domNodeDict
    GeneratorBaseModel.profileDict
    GeneratorBaseModel.modelMapper
    GeneratorBaseModel.validityList
    
    GeneratorBaseModel.domNodeDict:
                                  [ProfileName]["ProfileNode"] = [] -  the node(s) <Generate profile="ProfileName" time="" size=""> from <Source> node
                                  [ProfileName]["GeneratorNode"] = the node <GenProfile label="ProfileName"> from <Profiles> node
                                  [ProfileName][varName] = all <Variable> nodes contain in the <SimulationVariables> node of a profile, where varName is mapped to <Variable label="varName">
                                  [ProfileName]["demoFile"] = name of the demography file this profile refers to
    GeneratorBaseModel.profileDict: this one is intense
                                    [ProfileName]["demoVars"] = demography variables dictionary
                                                 ["demoVars"]["varName"] = variable's properties dictionary
                                                             ["varName"]["keepVar"] = Bool if varName is  or is not a child of tag <IndividualModel>
                                                             ["varName"]["Range"] = [], list of possible Values for varName
                                                             ["varName"]["Dependencies"] = [],list of variables which vaRName depends on
                                                             ["varName"]["type"] = type of this variable(Int, Bool, String, etc...)
                                    [ProfileName]["simVars"] = simulation variables dictionary
                                                 ["simVars"]["varName"] = variable's properties dictionary
                                                            ["varName"]["Dependencies"] = [],list of variables which vaRName depends on
                                                            ["varName"]["type"] = type of this variable(Int, Bool, String, etc...)
    GeneratorBaseModel.modelMapper:                                                
                                   [ProfileName] = [], list of the different simulation variables of ProfileName in order the user want them to appear in the tableView.
                                                       Since demography variables are immutable, we only have a modelMapper for the simulation Variables
    GeneretarBaseModel.validityList:
                                   [ProfileName]["varName"] = Event, list of the different validity "states" of a variable xml Tree.<
                                                              Currently, possible values are : "Unknown", "Valid", "Warning", "Errors"
                                    
    '''
    def __init__(self, windowObject, generatorDom=QDomNode(), sourceDom=QDomNode()):
        '''
        @summary Constructor
        @param windowObject : application's main window
        @param generatorDom :  Generator's xml node
        @param sourceDom : Population creation's xml node
        Note : Source dom contains information about how many individuals are generated, from which profile and when they are generated
        '''
        self.generatorDom = generatorDom
        self.sourceDom = sourceDom

        self.topObject = windowObject
        self.profileDict = {}
        self.domNodeDict = {}
        self.modelMapper = {}
        self.validityDict = {}
        
        if not self.generatorDom.isNull():
            self._updateMainStructure()
        
    def howManyDemoVars(self, profileName):
        ''' 
        @summary Return number of demography variables in profile
        @param profileName : profile's name
        '''
        if profileName in self.profileDict.keys():
            return len(self.profileDict[profileName]["demoVars"]) 
        return 0
    
    def howManySimVars(self, profileName):
        ''' 
        @summary Return number of simulation variables in profile
        @param profileName : profile's name
        '''
        if profileName in self.profileDict.keys():
            return len(self.profileDict[profileName]["simVars"]) 
        return 0
        
    def howManyProfiles(self):
        ''' 
        @summary Return number of profile of this simulation
        '''
        return len(self.profileDict.keys())
    
    def howManyGeneration(self):
        ''' 
        @summary Return number of subpopulation that will compose the population
        '''
        return self.sourceDom.childNodes().count()
        
    def variableExists(self, profileName, varName):
        ''' 
        @summary Return if a variable exists in a profile
        @param profileName : profile's name
        @param varName : variable's name
        '''
        return varName in self.profileDict[profileName]["simVars"].keys()
    
    def getDemographyFileName(self, profile):
        '''
        @summary Return name of the demography file used in profile
        @param profile : profile's name
        '''
        return self.domNodeDict[profile]["demoFile"]
    
    def getAllPossibleVars(self):
        '''
        @summary Return a list of all differently named variables in all available profiles
        '''
        varList = []
        for profile in self.profileDict.keys():
            for category in self.profileDict[profile].keys():
                for variable in self.profileDict[profile][category].keys():
                    if not variable in varList:
                        if category == "demoVars":
                            if self.isSelected(profile,variable):
                                varList.append(variable)
                        else:
                            varList.append(variable)
        return varList
                    
    def getAcceptFunctionNode(self, profileName):
        '''
        @summary Return XML Node of a profile's accept function
        @profileName : profile's name
        '''
        return self.domNodeDict[profileName]["GeneratorNode"].firstChildElement("AcceptFunction")

    def getDemoVarsList(self, profileName):
        '''
        @summary Return a list of demography variables name of profile
        @param profileName : profile's name
        '''
        return self.profileDict[profileName]["demoVars"].keys()
    
    def getSimVarsList(self, profileName):
        '''
        @summary Return a list of simulation variables name of profile
        @param profileName : profile's name
        '''
        return self.profileDict[profileName]["simVars"].keys()
    
    def getSimViewVarsList(self, profileName):
        '''
        @summary Return simulation variable list as shown in view, which is the modelMapper list
        @param profileName : profile's name
        '''
        return self.modelMapper[profileName]
    
    def getDemoViewVarsList(self, profileName):
        '''
        @summary Return demography variable list as shown in view, which is the modelMapper list
        @param profileName : profile's name
        '''
        return self.getDemoVarsList(profileName)
    
    def isSelected(self, profileName, varName):
        '''
        @summary Return if a demography variable is kept after population has been generated
        @param profileName : profile's name
        @param varName : variable's name
        '''
        return self.profileDict[profileName]["demoVars"][varName]["KeepVar"]
    
    def changeSelection(self, profileName, varName):
        '''
        @summary Modify the selection status of a demography variable
        @param profileName : profile's name
        @param varName : variable's name
        '''
        individualModelNode = self.domNodeDict[profileName]["GeneratorNode"].firstChildElement("IndividualModel")
        
        if self.profileDict[profileName]["demoVars"][varName]["KeepVar"]:
            varNodes = individualModelNode.elementsByTagName("Variable")
            for i in range(varNodes.count()):
                currVar = varNodes.item(i)
                if currVar.toElement().attribute("label", "") == varName:
                    individualModelNode.removeChild(currVar)
                    self.profileDict[profileName]["demoVars"][varName]["KeepVar"] = False
                    self.topObject.dirty = True
                    return
        else :
            newVarNode = individualModelNode.ownerDocument().createElement("Variable")
            newVarNode.setAttribute("label", varName)
            individualModelNode.appendChild(newVarNode)
            self.profileDict[profileName]["demoVars"][varName]["KeepVar"] = True
            self.topObject.dirty = True
            return
        
        print("Warning : in GeneratorBaseModel::changeSelection, variable named", varName, "wasn't found in <IndividualModel> when it should has been)")
    
    def getVarTypeIgnoringSubPop(self, varName):
        '''
        @summary Convenience function used by PrimitiveModel to fetch type without knowing what profile a variable belongs to
        @param varName : variable's name
        '''
        for profile in self.profileDict.keys():
            for category in self.profileDict[profile].keys():
                if varName in self.profileDict[profile][category].keys():
                    return self.profileDict[profile][category][varName]["type"]
                
        print("Variable not in any of the profile!")
        return "Unknown"
    
    def variableExistsIgnoringSupPop(self, varName):
        '''
        @summary Convenience function used by PrimitiveModel to ask the model if a variable exists, regardless of the profiles
        @param varName : variable's name
        '''
        for profile in self.profileDict.keys():
            for category in self.profileDict[profile].keys():
                if varName in self.profileDict[profile][category].keys():
                    if category == "demoVars":
                            if self.isSelected(profile,varName):
                                return True
                    else:
                        return True
        return False
    
    def getVarType(self, profileName, varName):
        '''
        @summary Return variable's type
        @param profileName : profile's name
        @param varName : variable's name
        '''
        if varName in self.profileDict[profileName]["simVars"]:
            if "type" in self.profileDict[profileName]["simVars"][varName]:
                return self.profileDict[profileName]["simVars"][varName]["type"]
        elif varName in self.profileDict[profileName]["demoVars"]:
            if "type" in self.profileDict[profileName]["demoVars"][varName]:
                return self.profileDict[profileName]["demoVars"][varName]["type"]
        return "Unknown"
    
    def getVarDepends(self, profileName, varName):
        '''
        @summary Return variable's dependencies
        @param profileName : profile's name
        @param varName : variable's name
        '''
        if varName in self.profileDict[profileName]["simVars"]:
            return self.profileDict[profileName]["simVars"][varName]["Dependencies"]
        elif varName in self.profileDict[profileName]["demoVars"]:
            return self.profileDict[profileName]["demoVars"][varName]["Dependencies"]
        else:
            return []
        
    def getVarNameFromIndex(self, profileName,  QtIndex, fromDict="simVars"):
        '''
        @summary Return variable's name
        @param profileName : profile's name
        @param QtIndex : index of variable in view, model and therefore in modelMapper
        @param fromDict : simVars or demoVars
        '''
        return self.profileDict[profileName][fromDict]["modelMapper"][QtIndex.row()]
    
    def getVarRange(self, profileName, varName):
        '''
        @summary Return range of a demography variable
        @param profileName : profile's name
        @param varName : variable's name
        '''
        return self.profileDict[profileName]["demoVars"][varName]["Range"]
    
    def renameVariable(self, profileName, oldName, newName):
        '''
        @summary Rename a variable
        @param profileName : profile's name
        @param oldName, newName : variable's old name and new name
        Note : variable's name won't be changed in the trees, so be aware of what you are doing!
        '''
        varNode = self.domNodeDict[profileName][oldName]
        varNode.toElement().setAttribute("label", newName)
        profileModelMapper = self.modelMapper[profileName]
        profileModelMapper[profileModelMapper.index(oldName)] = newName
        self.profileDict[profileName]["simVars"][newName] = self.profileDict[profileName]["simVars"][oldName]
        del self.profileDict[profileName]["simVars"][oldName] 
        self.domNodeDict[profileName][newName] = self.domNodeDict[profileName][oldName]
        del self.domNodeDict[profileName][oldName]
        self.topObject.dirty = True
        
    def setDemoFileName(self, profile, fileName):
        '''
        @summary Sets a profile's demography file name
        @param profile : profile's name
        @param fileName : file's name
        '''
        self.domNodeDict[profile]["GeneratorNode"].firstChildElement("Demography").setAttribute("file", fileName)
        f = Opener(fileName)
        tmpNodeImport = self.generatorDom.ownerDocument().importNode(f.getRootNode(), True)
        self.domNodeDict[profile]["GeneratorNode"].firstChildElement("Demography").appendChild(tmpNodeImport)
        self._updateMainStructure()
        self.topObject.dirty = True
        
    def updateValidationState(self, varName, pmtRoot, profile=None):
        '''
        @summary Tries to update the validation state of a variable
        @param varName : variable's name
        @param pmtRoot : Primitive instance from class Primitive in model.Primitive.model. It is the first Primitive
        of the xml tree, where the validation state of a tree is kept
        @param profile : profile's name 
        @return True if success, else False
        '''
        if self.variableExistsIgnoringSupPop(varName):
            if profile:
                self.validityDict[profile][varName] = pmtRoot.worstEvent
                return True
       
        return False
    
    def getVariableValidity(self, varName, profileName):
        '''
        @summary Return variable's validity state
        @param varName : variable's name
        @param profileName : profile's name
        Actual validity values are : Valid, Error, Warning, Unknown
        '''
        if varName in self.validityDict[profileName].keys():
            return self.validityDict[profileName][varName]
        return "Unknown"
    
    def addVar(self, profileName, varName, varType, rowToInsert=0):
        '''
        @summary Adds a variable to the model
        @param profileName : profile's name
        @param varName : variable's name
        @param varType : variable's type
        @param rowToInsert : position to insert in the model mapper
        '''
        #Rename Variable if it already exists
        if varName in self.profileDict[profileName]["simVars"].keys():
            print("Warning in BaseVarModel::addVar() :", varName, "already present. Renaming variable.")
            count = 1
            while varName in self.profileDict[profileName]["simVars"].keys():
                varName = varName.rstrip("0123456789 ")
                varName += str(count)
                count += 1

        newVarElement = self.generatorDom.ownerDocument().createElement("Variable")
        newVarElement.setAttribute("label", varName)
        newVarElement.setAttribute("type", varType)
        pmtTree = self.generatorDom.ownerDocument().createElement("PrimitiveTree")
        notTree = self.generatorDom.ownerDocument().createElement("Control_Nothing")
        locVarTree = self.generatorDom.ownerDocument().createElement("LocalVariables")
        simVarsNode = self.domNodeDict[profileName]["GeneratorNode"].firstChildElement("SimulationVariables").firstChildElement("SimulationVariables")
        if simVarsNode.isNull():
            #New profile, doesn't have a SimulationVariables Node yet
            simVarsNode = self.generatorDom.ownerDocument().createElement("SimulationVariables")
            self.domNodeDict[profileName]["GeneratorNode"].firstChildElement("SimulationVariables").appendChild(simVarsNode)
            
        simVarsNode.appendChild(newVarElement)
        newVarElement.appendChild(locVarTree)
        newVarElement.appendChild(pmtTree)
        pmtTree.appendChild(notTree)
        
        self.modelMapper[profileName].insert(rowToInsert, varName)
        self._updateVarList(profileName)
        self.topObject.dirty = True
        
    def removeVar(self, profileName, varName):
        '''
        @summary Remove a variable from profile
        @param profileName : profile's name
        @param varName : variable's name
        '''
        if varName not in self.domNodeDict[profileName]:
            print("Warning in BaseVarModel::removeVar() : tentative to remove an inexistant variable", varName)
        else:
            self.domNodeDict[profileName][varName].parentNode().removeChild(self.domNodeDict[profileName][varName])
            self._updateVarList(profileName)
            self.topObject.dirty = True
            
    def setVarType(self,profileName, varName, newVarType):
        '''
        @summary Modify variable's type
        @param profileName : profile's name
        @param varName : variable's name
        @param newVarType : new variable's type
        '''
        self.domNodeDict[profileName][varName].toElement().setAttribute("type", newVarType)
        self.profileDict[profileName]["simVars"][varName]["type"] = newVarType
        self.topObject.dirty = True
        
    def swapSimVars(self, rowDragged, rowDropped, profileName):
        '''
        @summary Insert variable before an other one in model mapper
        @param rowDragged index of swapped item in model mapper
        @param rowDropped index of pushed item in model mapper
        @param profileName Current profile
        '''
        self.modelMapper[profileName].insert(rowDropped, self.modelMapper[profileName].pop(rowDragged))
        
    def cloneProfile(self, newProfileName, clonedProfileName):
        '''
        @summary Create a new profile by copying another profile
        @param newProfileName : new profile's name
        @param clonedProfileName : cloned profile's name
        '''
        newProfileNode = self.domNodeDict[clonedProfileName]["GeneratorNode"].cloneNode(True)
        newProfileNode.toElement().setAttribute("label",newProfileName)
        self.generatorDom.toElement().elementsByTagName("Profiles").item(0).appendChild(newProfileNode)
        #Make sure that <PrimitiveTree> dont' keep their id tags, if any
        pmtTreeNodeList = newProfileNode.toElement().elementsByTagName("PrimitiveTree")
        for i in range(pmtTreeNodeList.count()):
            currPmtTree = pmtTreeNodeList.item(i)
            currPmtTree.toElement().removeAttribute("gui.id")
        self._updateMainStructure()
        self.topObject.dirty = True
        
    def removeProfile(self, profileName):
        '''
        @summary Remove a profile from generator
        @param profileName : profile's name
        '''
        removedProfileGenNode = self.domNodeDict[profileName]["GeneratorNode"]
        if "ProfileNode"in self.domNodeDict[profileName].keys():
            removedProfileSourceNode = self.domNodeDict[profileName]["ProfileNode"]
            for sourceNodes in removedProfileSourceNode:
                self.sourceDom.removeChild(sourceNodes)
        
        self.generatorDom.elementsByTagName("Profiles").item(0).removeChild(removedProfileGenNode)
        del self.domNodeDict[profileName]
        del self.profileDict[profileName]
        del self.modelMapper[profileName]
        del self.validityDict[profileName]
        self.topObject.dirty = True
        
    def addProfile(self, profileName, demoFile, simVarProfileFrom, acceptFuncProfileFrom):
        '''
        @summary Create new profile, possibly using parts of other profiles
        @param profileName : new profile's name
        @param demoFile : name of the demography file
        @param simVarProfileFrom : clone simulation variable from this profile
        @param acceptFuncProfileFrom :  clone accept function from this profile
        '''
        #Creating Profile Node and demography node
        newProfileNode = self.generatorDom.ownerDocument().createElement("GenProfile")
        newProfileNode.setAttribute("label", profileName)
        newDemoNode = self.generatorDom.ownerDocument().createElement("Demography")
        if demoFile:
            newDemoNode.setAttribute("file", demoFile)
            #Opening demography file
            f = Opener(demoFile)
            tmpNodeImport = self.generatorDom.ownerDocument().importNode(f.getRootNode(), True)
            newDemoNode.appendChild(tmpNodeImport)
            
        #Creating SimulationVariables Node
        baseSimVarNode = self.generatorDom.ownerDocument().createElement("SimulationVariables")

        if simVarProfileFrom:
            #simVarProfileName refers to an existing Profile
            #Clone Node and append to new SimulationVariables Node
            profileFrom = self.domNodeDict[simVarProfileFrom]["GeneratorNode"]
            simVarProfileFromNode = profileFrom.firstChildElement("SimulationVariables").firstChild()
            newSimVarNode = simVarProfileFromNode.cloneNode(True)
        else:
            #Simulation VariableNode is empty, create node and append it
            #Don't forget that simulationVariable node is <SimulationVariables>
            #                                                <SimulationVariables>
            newSimVarNode = self.generatorDom.ownerDocument().createElement("SimulationVariables")
        baseSimVarNode.appendChild(newSimVarNode)
        #Create accept Function Node
        acceptFuncNode = self.generatorDom.ownerDocument().createElement("AcceptFunction")

        if acceptFuncProfileFrom:
            #acceptFuncProfileFrom refers to an existing Profile
            #Clone PrimitiveTree Node
            profileFrom = self.domNodeDict[acceptFuncProfileFrom]["GeneratorNode"]
            acceptFuncProfileFromNode = profileFrom.firstChildElement("AcceptFunction").firstChild()
            newAcceptFuncPmtTreeNode = acceptFuncProfileFromNode.cloneNode(True)
        else:
            #acceptFuncProfileFrom is empty
            #Create PrimitiveTree Node and it's first child, a boolean set to True
            newAcceptFuncPmtTreeNode = self.generatorDom.ownerDocument().createElement("PrimitiveTree")
            newTokenNode = self.generatorDom.ownerDocument().createElement("Data_Value")
            newTokenNode.setAttribute("inValue_Type", "Bool")
            newTokenNode.setAttribute("inValue", "true")
            newAcceptFuncPmtTreeNode.appendChild(newTokenNode)
        acceptFuncNode.appendChild(newAcceptFuncPmtTreeNode)
      
        newModelNode = self.generatorDom.ownerDocument().createElement("IndividualModel")
        #Append <GenProfile> node to <Profiles>
        self.generatorDom.toElement().elementsByTagName("Profiles").item(0).appendChild(newProfileNode)
        
        #Append all Node to new Profile
        newProfileNode.appendChild(newDemoNode)
        newProfileNode.appendChild(acceptFuncNode)
        newProfileNode.appendChild(newModelNode)
        newProfileNode.appendChild(baseSimVarNode)
        #update model
        self._updateMainStructure()
        self.topObject.dirty = True
        
    def replaceSimulationVariables(self, profileReplaced, profileFrom):
        '''
        @summary Use another profile's simulation variables and assign it to profile
        @profileReplaced : clone profile's name
        @profileFrom : original profile's name
        '''
        profileFromNode = self.domNodeDict[profileFrom]["GeneratorNode"]
        profileReplaced = self.domNodeDict[profileReplaced]["GeneratorNode"]
        
        simVarFrom = profileFromNode.firstChildElement("SimulationVariables")
        simVarReplaced = profileReplaced.firstChildElement("SimulationVariables")
        
        profileReplaced.replaceChild(simVarFrom.cloneNode(True), simVarReplaced)
        #Make sure that <PrimitiveTree> dont' keep their id tags, if any
        pmtTreeNodeList = self.domNodeDict[profileReplaced]["GeneratorNode"].toElement().elementsByTagName("PrimitiveTree")
        for i in range(pmtTreeNodeList.count()):
            currPmtTree = pmtTreeNodeList.item(i)
            currPmtTree.toElement().removeAttribute("gui.id")
        
        self.topObject.dirty = True
        
    def replaceAcceptFunction(self, profileReplaced, profileFrom):
        '''
        @summary Use another profile's accept Function and assign it to profile
        @profileReplaced : clone profile's name
        @profileFrom : original profile's name
        '''
        profileFromNode = self.domNodeDict[profileFrom]["GeneratorNode"]
        profileReplaced = self.domNodeDict[profileReplaced]["GeneratorNode"]
        
        acceptFuncFrom = profileFromNode.firstChildElement("AcceptFunction")
        acceptFuncReplaced = profileReplaced.firstChildElement("AcceptFunction")
        
        profileReplaced.replaceChild(acceptFuncFrom.cloneNode(True), acceptFuncReplaced)
        self.topObject.dirty = True
        
    def replaceAcceptFunctionDomNode(self, profileName, newDomNode):
        '''
        @summary Assign a new accept function
        @param profileName : profile's name
        @param newDomNode : XML node of the new accept function
        '''
        profileReplacedNode = self.domNodeDict[profileName]["GeneratorNode"]
        acceptFuncReplaced = profileReplacedNode.firstChildElement("AcceptFunction")
        
        profileReplacedNode.replaceChild(newDomNode, acceptFuncReplaced)
        self.topObject.dirty = True
        
    def _mapToModel(self):
        '''
        @ Summary Since you cannot control where the data will be inserted in a dictionary(it is dependent of the key and the hash function), we need a table to store
        the keys in order the user wants them to appear
        This function is created to keep the model and the data in sync, while keeping the current data layout in the view 
        '''
        for profile in self.profileDict.keys():
            for variable in self.getSimVarsList(profile):
                if variable not in self.modelMapper[profile]:
                    self.modelMapper[profile].append(variable)
                    
            for variable in self.modelMapper[profile]:
                if variable not in self.getSimVarsList(profile):
                    self.modelMapper[profile].remove(variable)
        
        for profile in self.profileDict.keys():
            mmCopy = list(self.modelMapper[profile])
            for variable in mmCopy:
                #Security for older files without positioning+ Security for older files with positioning attribute without "gui." identifier  + remove position and act as old file after first positioning
                if self.domNodeDict[profile][variable].toElement().hasAttribute("position"):
                    self.modelMapper[profile][int(self.domNodeDict[profile][variable].toElement().attribute("position"))] = variable
                    self.domNodeDict[profile][variable].toElement().removeAttribute("position")
                elif self.domNodeDict[profile][variable].toElement().hasAttribute("gui.position"):
                    self.modelMapper[profile][int(self.domNodeDict[profile][variable].toElement().attribute("gui.position"))] = variable
                    self.domNodeDict[profile][variable].toElement().removeAttribute("gui.position")
                else:
                    break
    
    def _findDependencies(self, profileName, varName, domNode=None):
        '''
        Parse dom of variable varName and find dependencies
        @param profileName : variable's profile
        @param varType : demoVars or simVars
        @param varName : variable's name
        @param domNode : variable's dom, if it is a demo variable(we have no way of finding it quickly if we don't pass it as an argument)
        Note : parsing is done using XQuery and Qt's XMLPatterns toolkit
        '''
        if domNode is None:
            varType = "simVars"
            self.profileDict[profileName][varType][varName]["Dependencies"] = []
            lCurrentNode = self.domNodeDict[profileName][varName]
        else:
            varType = "demoVars"
            self.profileDict[profileName][varType][varName]["Dependencies"] = []
            lCurrentNode = domNode
        
        dependencyQuery = QXmlQuery()
        queryBuffer = QBuffer()
        parsedXML = QByteArray()
        newTextStream = QTextStream(parsedXML)
        lCurrentNode.save(newTextStream, 2)
        queryBuffer.setData(newTextStream.readAll())
        queryBuffer.open(QIODevice.ReadOnly)
        dependencyQuery.bindVariable("varSerializedXML", queryBuffer)
        #Here is a big limit, we consider dependencies can be all found in attributes ending with the word label or Label
        dependencyQuery.setQuery("for $x in doc($varSerializedXML)//@inValue[starts-with(data(.),'@')] return substring-after(data($x),'@')")
        dependencies = dependencyQuery.evaluateToStringList()
        if dependencies is not None:
            for item in dependencies:
                if item not in self.profileDict[profileName][varType][varName]["Dependencies"] and item != varName:
                    self.profileDict[profileName][varType][varName]["Dependencies"].append(item)
                
    def _updateMainStructure(self):
        '''
        @Parse GeneratorDom and Source Dom and create fisrt layer of the dictionnaries
        '''
        self.profileDict = {}
        self.domNodeDict = {}
        
        lCurrentIndex = 0
        profileNode = self.generatorDom.firstChildElement("Profiles")
        assert not profileNode.isNull(), "In GeneratorBaseModel::_updateMainStructure, <Profiles> tag needed but not found!"
        while not profileNode.elementsByTagName("GenProfile").item(lCurrentIndex).isNull():
            lCurrentNode = profileNode.elementsByTagName("GenProfile").item(lCurrentIndex)
            
            profileName = lCurrentNode.toElement().attribute("label", "")
            
            if not profileName:
                print("Warning : in baseVarModel::_updateMainStructure, profile doesn't have a name")
            
            self.profileDict[profileName] = {}
            self.domNodeDict[profileName] = {}
            self.domNodeDict[profileName]["GeneratorNode"] = lCurrentNode
            if profileName not in self.modelMapper:
                self.modelMapper[profileName] = []
            if profileName not in self.validityDict:
                self.validityDict[profileName] = {}
                
            self._updateVarList(profileName)
            self.domNodeDict[profileName]["demoFile"] = lCurrentNode.firstChildElement("Demography").attribute("file", "")
            lCurrentIndex += 1
        lCurrentIndex = 0
        
        while not self.sourceDom.elementsByTagName("SubPopulation").item(lCurrentIndex).isNull():
            lCurrentNode = self.sourceDom.elementsByTagName("SubPopulation").item(lCurrentIndex)
            
            profileName = lCurrentNode.toElement().attribute("profile", "")
            if profileName == "":
                print("Warning : in baseVarModel::_updateMainStructure, <Generate> tag misses 'profile' attribute")
            if "ProfileNode" not in self.domNodeDict[profileName]:
                self.domNodeDict[profileName]["ProfileNode"] = []
            self.domNodeDict[profileName]["ProfileNode"].append(lCurrentNode)
            lCurrentIndex += 1
            
    def _updateVarList(self, profileName):
        '''
        @Parse xml node <Profile> and create bottom layer of dictionnaries
        @param profileName : profile's name
        '''
        self.profileDict[profileName] = {"demoVars":{}, "simVars":{}}
        
        #We're Making twice the call to firstChildElement() with SimulationVariables and Demography because
        #<SimulationVariables file="SimulationVariables.xml">
        #    <SimulationVariables>
        #       <Variable label = Age>
        #Same for demography
        
        demoVarsNode = self.domNodeDict[profileName]["GeneratorNode"].firstChildElement("Demography").firstChildElement("Demography")
        simVarsNode = self.domNodeDict[profileName]["GeneratorNode"].firstChildElement("SimulationVariables").firstChildElement("SimulationVariables")
        
        # Demography parsing

        lCurrentIndex = 0
        while not demoVarsNode.childNodes().item(lCurrentIndex).isNull():
            lCurrentNode = demoVarsNode.childNodes().item(lCurrentIndex)
            
            if lCurrentNode.isComment():
                lCurrentIndex += 1
                continue

            assert lCurrentNode.nodeName() == "Variable", "In BaseVarModel::_updateVarList : invalid child for <Demography>, received "+str(lCurrentNode.nodeName())+" when Variable was expected"
            lVarName = lCurrentNode.attributes().namedItem("label").toAttr().value()
            
            self.profileDict[profileName]["demoVars"][lVarName] = {}
            
            self.profileDict[profileName]["demoVars"][lVarName]["KeepVar"] = False
            
            #Type determination
             
            if not lCurrentNode.attributes().namedItem("type").isNull():
                self.profileDict[profileName]["demoVars"][lVarName]["type"] = lCurrentNode.attributes().namedItem("type").toAttr().value()
            else:
                self.profileDict[profileName]["demoVars"][lVarName]["type"] = "Unknown"
                
            # Dependencies determination(Using XQuery)
            self._findDependencies(profileName, lVarName,lCurrentNode)
            
            #Find variable range
            self.profileDict[profileName]["demoVars"][lVarName]["Range"] = set()
            
            parsedXML = QByteArray()
            newTextStream = QTextStream(parsedXML)
            lCurrentNode.save(newTextStream, 2)
            queryBuffer = QBuffer()
            queryBuffer.setData(newTextStream.readAll())
            queryBuffer.open(QIODevice.ReadOnly)
            dependencyQuery = QXmlQuery()
            dependencyQuery.bindVariable("varSerializedXML", queryBuffer)
            #This is a quite complex xquery 
            #Find possible values for this attribute
            dependencyQuery.setQuery("for $x in doc($varSerializedXML)//*[matches(name(.),'Data_Value')][matches(name(parent::*),'Control_Branch') or matches(name(parent::*),'Control_BranchMulti') or matches(name(parent::*),'Control_Switch')][not(matches(data(@inValue),'[@$%#]'))] return string(data($x/@inValue))")
            varRange = dependencyQuery.evaluateToStringList()
            if self.profileDict[profileName]["demoVars"][lVarName]["type"] == "Bool":
                self.profileDict[profileName]["demoVars"][lVarName]["Range"].add("True")
                self.profileDict[profileName]["demoVars"][lVarName]["Range"].add("False")
            else:
                for item in varRange:
                    self.profileDict[profileName]["demoVars"][lVarName]["Range"].add(item)

            self.profileDict[profileName]["demoVars"][lVarName]["Range"] = list(self.profileDict[profileName]["demoVars"][lVarName]["Range"])
            
            #Check individual Model (does the simulation keep this variable)
            individualModelNode = self.domNodeDict[profileName]["GeneratorNode"].firstChildElement("IndividualModel")
            varNodes = individualModelNode.elementsByTagName("Variable")
            for i in range(varNodes.count()):
                currVar = varNodes.item(i)
                if currVar.toElement().attribute("label", "") == lVarName:
                    self.profileDict[profileName]["demoVars"][lVarName]["KeepVar"] = True
                    break
            
            lCurrentIndex+=1
            
            
        # Simulation Variables parsing 
            
        lCurrentIndex = 0
        
        while not simVarsNode.childNodes().item(lCurrentIndex).isNull():
            lCurrentNode = simVarsNode.childNodes().item(lCurrentIndex)
            
            if lCurrentNode.isComment():
                lCurrentIndex += 1
                continue

            assert lCurrentNode.nodeName() == "Variable", "In BaseVarModel::_updateVarList : invalid child for <SimulationVariables>, received " + lCurrentNode.nodeName() + " when Variable was expected"
            lVarName = lCurrentNode.attributes().namedItem("label").toAttr().value()
            self.profileDict[profileName]["simVars"][lVarName] = {}
            self.domNodeDict[profileName][lVarName]=lCurrentNode
            
            if not lCurrentNode.attributes().namedItem("type").isNull():
                self.profileDict[profileName]["simVars"][lVarName]["type"] = lCurrentNode.attributes().namedItem("type").toAttr().value()
            else:
                self.profileDict[profileName]["simVars"][lVarName]["type"] = "Unknown"
        
            # Dependencies determination(Using XQuery)           
            self._findDependencies(profileName, lVarName)
            
            #Preload in local variable model so Primitive Model Validator can find local variables even if tree hasn't yet been loaded in tree editor
            baseLocVarModel = BaseLocalVariablesModel()
            baseLocVarModel.parseLocVars(lCurrentNode.firstChildElement("PrimitiveTree"))
            
            lCurrentIndex += 1
            
        self._mapToModel()

class fakeSingletonSimpleModel(object):
    def __init__(self, decoratedClass):
        fakeSingletonSimpleModel.instance_container = []
        self.simpleBaseVarModelClass = decoratedClass
    def __call__(self, *args):
        """
        The __call__ method is not called until the
        decorated function is called.
        """
        if not len(self.instance_container):
            fakeSingletonSimpleModel.instance_container.append(self.simpleBaseVarModelClass(*args))
        elif len(args):
            fakeSingletonSimpleModel.instance_container[0] = self.simpleBaseVarModelClass(*args)
        return fakeSingletonSimpleModel.instance_container[0]
    
    @staticmethod
    def clearVar():
        fakeSingletonSimpleModel.instance_container = []
     
@fakeSingletonSimpleModel      
class SimpleBaseVarModel:
    '''
    This is a simplified GeneratorBaseModel class, that accepts any well defined variable XML file
    At first, this class is used to allow the edition of demography XML files
    '''
    
    def __init__(self, windowObject, demographyDom=QDomNode()):
        '''
        @summary Constructor
        @param windowObject : application's main window
        @param demographyDom : Demography's XML node
        '''
        self.demoDom = demographyDom
        self.topObject = windowObject
        self.varDict = {}
        self.domNodeDict = {}
        self.modelMapper = []
        
        if not self.demoDom.isNull() is None:
            self._updateVarList()
    
    def getDemoNode(self):
        '''
        @summary Return <Demography> XML's node
        '''
        return self.demoDom
    
    def getVarsList(self):
        '''
        @summary Return a list of model's variables name
        '''
        return self.modelMapper
    
    def getAllPossibleVars(self):
        '''
        @summary Return a list of model's variables name(Hook to work with PrimitiveModel)
        '''
        return self.getVarsList()
    
    def setVarType(self, varName, newVarType):
        '''
        @summary Modify variable's type
        @param varName : variable's name
        @param newVarType : new variable's type
        '''
        self.domNodeDict[varName].toElement().setAttribute("type", newVarType)
        self._updateVarList()
    
    def howManyVars(self):
        '''
        @summary Return Number of variables in dictionnary
        '''
        return len(self.modelMapper)    
        
    def variableExists(self, varName):
        '''
        @summary Return if variable is in dictionary
        @param varName : name of the variable 
        '''
        return varName in self.varDict.keys()
    
    def variableExistsIgnoringSupPop(self, varName):
        '''
        @summary Return if variable is in dictionary (Hook to work with PrimitiveModel)
        @param varName : name of the variable 
        '''
        return self.variableExists(varName)
    
    def getVarType(self, varName):
        '''
        @summary Return variable's type
        @param varName : variable's name
        '''
        return self.varDict[varName]["type"]
    
    def getVarTypeIgnoringSubPop(self, varName):
        '''
        @summary Return variable's type (Hook to work with PrimitiveModel)
        @param varName : name of the variable 
        '''
        return self.getVarType(varName)
    
    def getVarDepends(self, varName):
        '''
        @summary Return variable's dependencies
        @param varName : variable's name
        '''
        return self.varDict[varName]["Dependencies"]
    
    def getVarRange(self, varName):
        '''
        @summary Return variable's range
        @param varName : variable's name
        '''
        return self.varDict[varName]["Range"]
    
    def renameVariable(self, oldName, newName):
        '''
        @summary Rename a variable
        @param oldName, newName : variable's old name and new name
        '''
        varNode = self.domNodeDict[oldName]
        varNode.toElement().setAttribute("label", newName)
        
        self.modelMapper[self.modelMapper.index(oldName)] = newName
        self._updateVarList()
    
    def addVar(self, varName, varType, rowToInsert=0):
        '''
        @summary Adds a variable to the model
        @param varName : variable's name
        @param varType : variable's type
        @param rowToInsert : position to insert in the model mapper
        '''
        if varName in self.varDict.keys():
            print("Warning in SimpleBaseVarModel::addVar() :", varName, "already present. Renaming variable.")
            count = 1
            while varName in self.varDict.keys():
                varName = varName.rstrip("0123456789 ")
                varName += str(count)
                count += 1
        
        newVarElement = self.demoDom.ownerDocument().createElement("Variable")
        newVarElement.setAttribute("label", varName)
        newVarElement.setAttribute("type", varType)
        locVarTree = self.demoDom.ownerDocument().createElement("LocalVariables")
        pmtTree = self.demoDom.ownerDocument().createElement("PrimitiveTree")
        notTree = self.demoDom.ownerDocument().createElement("Control_Nothing")
            
        self.demoDom.appendChild(newVarElement)
        newVarElement.appendChild(locVarTree)
        newVarElement.appendChild(pmtTree)
        pmtTree.appendChild(notTree)
        self.modelMapper.insert(rowToInsert, varName)
        self._updateVarList()
    
    def removeVar(self, varName):
        '''
        @summary Remove a variable from demography
        @param varName : variable's name
        '''
        if varName not in self.domNodeDict.keys():
            print("Warning in SimpleBaseVarModel::removeVar() : tentative to remove an inexistant variable", varName)
        else:
            self.domNodeDict[varName].parentNode().removeChild(self.domNodeDict[varName])
            self.modelMapper.remove(varName)
            self._updateVarList()
        
    def _findDependencies(self, varName):
        '''
        @summary: Parse dom of variable varName and find dependencies
        @param varName : variable's name
        Note : parsing is done using XQuery and Qt's XMLPatterns toolkit
        '''
        self.varDict[varName]["Dependencies"] = []
        dependencyQuery = QXmlQuery()
        parsedXML = QByteArray()
        newTextStream = QTextStream(parsedXML)
        self.domNodeDict[varName].save(newTextStream, 2)
        queryBuffer = QBuffer()
        queryBuffer.setData(newTextStream.readAll())
        queryBuffer.open(QIODevice.ReadOnly)
        dependencyQuery.bindVariable("varSerializedXML", queryBuffer)
        #Here is a big limit, we consider dependencies can be all found in attributes ending with the word label or Label
        dependencyQuery.setQuery("for $x in doc($varSerializedXML)//@inValue[starts-with(data(.),'@')] return substring-after(data($x),'@')")
        dependencies = dependencyQuery.evaluateToStringList()
        for item in dependencies:
            if item not in self.varDict[varName]["Dependencies"] and item != varName:
                self.varDict[varName]["Dependencies"].append(item)
    
    def _findRange(self, varName):
        '''
        Parse dom of variable varName and find range
        @param varName : variable's name
        Note : parsing is done using XQuery and Qt's XMLPatterns toolkit
        '''
        self.varDict[varName]["Range"] = set()
        dependencyQuery = QXmlQuery()
        parsedXML = QByteArray()
        newTextStream = QTextStream(parsedXML)
        self.domNodeDict[varName].save(newTextStream, 2)
        queryBuffer = QBuffer()
        queryBuffer.setData(newTextStream.readAll())
        queryBuffer.open(QIODevice.ReadOnly)
        dependencyQuery.bindVariable("varSerializedXML", queryBuffer)
        #This is a quite complex xquery 
        #For all item named Basic_Token with a parent not named Basic_RouletteDynamic return the value of attribute named value as a string
        dependencyQuery.setQuery("for $x in doc($varSerializedXML)//*[matches(name(.),'Data_Value')][matches(name(parent::*),'Control_Branch') or matches(name(parent::*),'Control_BranchMulti') or matches(name(parent::*),'Control_Switch')][not(matches(data(@inValue),'[@$%#]'))] return string(data($x/@inValue))")
        varRange = []
        dependencyQuery.evaluateTo(varRange)
        if self.varDict[varName]["type"] == "Bool":
            self.varDict[varName]["Range"].add("True")
            self.varDict[varName]["Range"].add("False")
        else:
            for item in list(varRange):
                self.varDict[varName]["Range"].add(str(item))

        self.varDict[varName]["Range"] = list(self.varDict[varName]["Range"])
                
    def _updateVarList(self):
        '''
        @Parse xml node <Demography> and populate dictionnaries
        '''
        self.varDict = {}
        self.domNodeDict = {}
        
        # Demography parsing
        lCurrentIndex = 0
         
        while not self.demoDom.childNodes().item(lCurrentIndex).isNull():
            lCurrentNode = self.demoDom.childNodes().item(lCurrentIndex)
            
            if lCurrentNode.isComment():
                lCurrentIndex += 1
                continue

            assert lCurrentNode.nodeName() == "Variable", "In SimpleBaseVarModel::_updateVarList : invalid child for <Demography>, received " + lCurrentNode.nodeName() + " when Variable was expected"
            lVarName = lCurrentNode.attributes().namedItem("label").toAttr().value()
            if lVarName not in self.modelMapper:
                self.modelMapper.append(lVarName)
            self.domNodeDict[lVarName] = lCurrentNode
            self.varDict[lVarName] = {}
            
            #Type determination
            
            if not lCurrentNode.attributes().namedItem("type").isNull():
                self.varDict[lVarName]["type"] = lCurrentNode.attributes().namedItem("type").toAttr().value()
            else:
                self.varDict[lVarName]["type"] = "Unknown"
            
            # Dependencies determination(Using XQuery)
              
            self._findDependencies(lVarName)
                        
            #Fin variable range
            self._findRange(lVarName)
            
            #Preload in local variable model so Primitive Model Validator can find local variables even if tree hasn't yet been loaded in tree editor
            baseLocVarModel = BaseLocalVariablesModel()
            baseLocVarModel.parseLocVars(lCurrentNode.firstChildElement("PrimitiveTree"))
            
            lCurrentIndex += 1
        
        
