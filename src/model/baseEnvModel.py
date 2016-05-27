"""
.. module:: baseEnvModel

.. codeauthor:: Mathieu Gagnon <mathieu.gagnon.10@ulaval.ca>

:Created on: 2010-09-10

"""
from PyQt4 import QtXml
from functools import wraps


def fakeSingleton(BaseEnvModel):
    '''
    Python Decorator, emulates a singleton behavior.
    It emulates the behavior because if the user passes arguments to the constructor, we implicitly consider he wants a new instance of BaseEnvModel.
    Else, its acts as a singleton.
    '''
    instance_container = []
    @wraps(BaseEnvModel)
    def wrapper(*args):
        '''
        Wrapper function.
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
    This is a class containing all the data of the xml tag <Environment> of a configuration file (often named parameters.xml).
    All the data is mapped to a dictionary and the modelMapper.
    
    This class could have been avoided if we consider the relative simplicity of the xml node describing the environment.
    The reason we created it is to keep our general class structure throughout our program.
    '''
    
    def __init__(self, windowObject, envDom=QtXml.QDomNode()):
        '''
        Constructor.
        
        :param windowObject: Application's main window
        :param envDom: Environment's xml node  
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
        Returns the number of variables in dictionary.
        
        :return: Int
        '''
        return len(self.varDict.keys()) 
        
    def variableExists(self, varName):
        '''
        Returns if a variable is in dictionary
        
        :param varName: Name of the variable.
        :type varName: String
        :return: Boolean. True if it exists, False if not. 
        '''
        return varName in self.varDict.keys()
    
    def getVarType(self, varName):
        '''
        Returns the variable's type.
        
        :param varName: Name of the variable.
        :type varName: String
        :return: String 
        '''
        return self.varDict[varName]["type"]

    def getVarValue(self, varName):
        '''
        Returns the variable's value as string.
        
        :param varName: Name of the variable.
        :type varName: String
        :return: String 
        '''
        return self.varDict[varName]["value"]

    def getVarNameFromIndex(self, QtIndex):
        '''
        Returns the variable's name.
        
        :param QtIndex: Index of the variable in top model.
        :type QtIndex: QModelIndex
        :return: String
        '''
        return self.modelMapper[QtIndex.row()]
    
    def renameVariable(self, oldName, newName):
        '''
        Rename a variable. 
        Note : variable's name won't be changed in the trees, so be aware of what you are doing!
        
        :param oldName: Name of the variable before renaming.
        :param newName: New name of the variable.
        :type oldName: String
        :type newName: String
        '''
        varNode = self.varNodeDict[oldName]
        varNode.toElement().setAttribute("label", newName)
        self.modelMapper[self.modelMapper.index(oldName)] = newName
        self._updateVarList()
        self.topObject.dirty = True
      
    def addVar(self, varName, varType="Unknown", rowToInsert=0):
        '''
        Adds a variable in model.
        
        :param varName: Variable's name.
        :param varType: Optional - Variable's type.
        :param rowToInsert: Optional - Position to insert in the model mapper.
        :type varName: String
        :type varType: String
        :type rowToInsert: Int
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
        Removes a variable from model.
        
        :param varName: Name of the variable to remove.
        :type varName: String
        '''
        if varName not in self.modelMapper:
            print("Warning in BaseVarModel::removeVar() : tentative to remove an inexistant variable", varName)
        else:
            self.varNodeDict[varName].parentNode().removeChild(self.varNodeDict[varName])
            self._updateVarList()
            self.topObject.dirty = True
    
    def setVarType(self, varName, newVarType):
        '''
        Changes a variable's type.
        
        :param varName: Name of the variable.
        :param newVarType: New type to be assigned.
        '''
        self.varNodeDict[varName].toElement().setAttribute("type", newVarType)
        self._updateVarList()
        self.topObject.dirty = True
        
    def setVarValue(self, varName, newVarValue):
        '''
        Changes a variable's value.
        
        :param varName: Name of the variable.
        :param newVarValue: New value to be assigned as string.
        :type varName: String
        :type newVarValue: String
        '''
        self.varNodeDict[varName].toElement().setAttribute("value", newVarValue)
        self._updateVarList()
        self.topObject.dirty = True
    
    def _mapToModel(self):
        '''
        Since you cannot control where the data will be inserted in a dictionary (it is dependent of the key and the hash function), we need a table to store
        the keys in order the user wants them to appear.
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
        Parse the xml node and store the data in the dictionaries.
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
        
