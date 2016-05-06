
from PyQt4 import QtXml


def fakeSingleton(BaseEnvModel):
    '''
    Python Decorator, emulates a singleton behavior
    It emulates the behavior because if the user passes arguments to the constructor, we implicitly consider he wants a new instance of BaseEnvModel
    Else, its acts as a singleton
    '''
    instance_container = []
    def wrapper(*args):
        '''
        @summary Wrapper function
        '''
        if not len(instance_container):
            #Create BaseEnvModel if it doesn't exist
            instance_container.append(BaseEnvModel(*args))
        elif len(args):
            #If it exists and arguments are passed through the constructor, create new instance
            instance_container[0] = BaseEnvModel(*args)
        #return singleton or new instance
        return instance_container[0]
    return wrapper

@fakeSingleton
class BaseEnvModel:
    '''
    This is a class containing all the data of the xml tag <Environment> of a configuration file (often named parameters.xml)
    All the data is mapped to a dictionnary and the modelMapper.
    
    This class could have been avoided if we consider the relative simplicity of the xml node describing the environment
    The reason we created it is to keep our general class structure throughout our program
    '''
    
    def __init__(self, windowObject, envDom=QtXml.QDomNode()):
        '''
        @summary Constructor
        @param windowObject : application's main window
        @param envDom : Environment's xml node  
        '''
        self.envDom = envDom

        self.topObject = windowObject
        self.varNodeDict = {}
        self.varDict = {}
        self.modelMapper = []
        
        if not self.envDom == None:
            self._updateVarList()
        
    def howManyVars(self):
        '''
        @summary Return Number of variables in dictionnary
        '''
        return len(self.varDict.keys()) 
        
    def variableExists(self, varName):
        '''
        @summary Return if variable is in dictionnary
        @param varName : name of the variable 
        '''
        return varName in self.varDict.keys()
    
    def getSourceNode(self):
        '''
        @summary Return main xml node
        '''
        return self.envDom
    
    def getVarNode(self, varName):
        '''
        @summary Return xml node of a variable
        @param varName : name of the variable 
        '''
        return self.varNodeDict[varName]
    
    def getVars(self):
        '''
        @summary Return a list of model's variables name
        '''
        return self.modelMapper
    
    def getVarType(self, varName):
        '''
        @summary Return variable's type
        @param varName : name of the variable 
        '''
        return self.varDict[varName]["type"]

    def getVarValue(self, varName):
        '''
        @summary Return variable's value
        @param varName : name of the variable 
        '''
        return self.varDict[varName]["value"]

    def getVarNameFromIndex(self, QtIndex):
        '''
        @summary Return variable's name
        @param QtIndex : index of the variable in top model
        '''
        return self.modelMapper[QtIndex.row()]
    
    def renameVariable(self, oldName, newName):
        '''
        @summary Rename a variable
        @param oldName, newName : variable's old name and new name
        Note : variable's name won't be changed in the trees, so be aware of what you are doing!
        '''
        varNode = self.varNodeDict[oldName]
        varNode.toElement().setAttribute("label", newName)
        self.modelMapper[self.modelMapper.index(oldName)] = newName
        self._updateVarList()
        self.topObject.dirty = True
      
    def addVar(self, varName, varType="Unknown", rowToInsert=0):
        '''
        @summary Adds a variable in model
        @param varName :variable's name
        @param varType : variable's type
        @param rowToInsert : position to insert in the model mapper 
        '''
        
        #At first, rename if variable already exists
        if varName in self.modelMapper:
            print("Warning in BaseVarModel::addVar() :", varName, "already present. Renaming variable.")
            count = 1
            while varName in self.modelMapper:
                varName = varName.rstrip('0123456789 ')
                varName = varName + str(count)
                count+=1

        newVarElement = self.envDom.ownerDocument().createElement("Variable")
        newVarElement.setAttribute("label", varName)
        newVarElement.setAttribute("type", varType)
        newVarElement.setAttribute("value", 0)
        self.envDom.appendChild(newVarElement)
        
        self.modelMapper.insert(rowToInsert, varName)
        self._updateVarList()
        self.topObject.dirty = True
    
    def removeVar(self, varName):
        '''
        @summary Remove a variable from model
        @param varName : name of the variable to remove
        '''
        if varName not in self.modelMapper:
            print("Warning in BaseVarModel::removeVar() : tentative to remove an inexistant variable", varName)
        else:
            self.varNodeDict[varName].parentNode().removeChild(self.varNodeDict[varName])
            self._updateVarList()
            self.topObject.dirty = True
    
    def setVarType(self, varName, newVarType):
        '''
        @summary Change a variable's type
        @param varName : name of the variable
        @param newVarType : new type to be assigned
        '''
        self.varNodeDict[varName].toElement().setAttribute("type", newVarType)
        self._updateVarList()
        self.topObject.dirty = True
        
    def setVarValue(self, varName, newVarValue):
        '''
        @summary Change a variable's value
        @param varName : name of the variable
        @param newVarValue : new value to be assigned
        '''
        self.varNodeDict[varName].toElement().setAttribute("value", newVarValue)
        self._updateVarList()
        self.topObject.dirty = True
    
    def _mapToModel(self):
        '''
        @summary Since you cannot control where the data will be inserted in a dictionnary(it is dependent of the key and the hash function), we need a table to store
        the keys in order the user wants them to appear
        This function is created to keep the model and the data in sync, while keeping the current data layout in the view 
        '''
        for variable in self.varDict.keys():
            if variable not in self.modelMapper:
                self.modelMapper.append(variable)
        for variable in self.modelMapper:
            if variable not in self.varDict.keys():
                self.modelMapper.remove(variable)
            
    def _updateVarList(self):
        '''
        @summary Parse the xml node and store the data in the dictionnaries
        '''
        self.varDict = {}
        self.varNodeDict = {}
        
        #Variable parsing

        lCurrentIndex = 0
        while not self.envDom.childNodes().item(lCurrentIndex).isNull():
            lCurrentNode = self.envDom.childNodes().item(lCurrentIndex)
            
            if lCurrentNode.isComment():
                lCurrentIndex+=1
                continue

            assert lCurrentNode.nodeName() == "Variable", "In BaseEnvModel::_updateVarList : invalid child for <State>, received " + lCurrentNode.nodeName() +" when Variable was expected"
            lVarName = lCurrentNode.attributes().namedItem("label").toAttr().value()
            
            self.varNodeDict[lVarName] = lCurrentNode
            self.varDict[lVarName] = {}
             
            #Type determination
             
            if not lCurrentNode.attributes().namedItem("type").isNull():
                self.varDict[lVarName]["type"] = lCurrentNode.attributes().namedItem("type").toAttr().value()
            else:
                self.varDict[lVarName]["type"] = "Unknown"
            
            #Value determination
             
            if not lCurrentNode.attributes().namedItem("value").isNull():
                self.varDict[lVarName]["value"] = lCurrentNode.attributes().namedItem("value").toAttr().value()
            else:
                self.varDict[lVarName]["value"] = 0
                
            if not lVarName in self.modelMapper:
                self.modelMapper.append(lVarName)
                    
            lCurrentIndex+=1

        self._mapToModel()
        
