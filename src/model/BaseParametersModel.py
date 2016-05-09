
from PyQt4 import QtXml
from PyQt4 import QtXmlPatterns
from PyQt4 import QtCore

def fakeSingleton(BaseParametersModel):
    '''
    Python Decorator, emulates a singleton behavior
    It emulates the behavior because if the user passes arguments to the constructor, we implicitly consider he wants a new instance of BaseParametersModel
    Else, its acts as a singleton
    '''
    instance_container = []
    def wrapper(*args):
        '''
        @summary Wrapper function
        '''
        if not len(instance_container):
            #Create BaseParametersModel if it doesn't exist
            instance_container.append(BaseParametersModel(*args))
        elif len(args):
            #If it exists and arguments are passed through the constructor, create new instance
            instance_container[0] = BaseParametersModel(*args)
        #return singleton or new instance
        return instance_container[0]
    return wrapper

@fakeSingleton
class BaseParametersModel:
    '''
    This is a class containing data from the xml tag <Parameters> of a configuration file (often named parameters.xml)
    Only parameters which names begin by ref. are considered in the model(other are application specific and can only be modified by an advanced user)
    These parameters are called references
    References are mapped to a dictionnary and the modelMapper.
    '''
    def __init__(self, windowObject, dom=QtXml.QDomNode()):
        '''
        @summary Constructor
        @param windowObject : application's main window
        @param dom : Parameters's xml node  
        '''
        self.dom = dom
        self.needUpdate = True
        self.refVars = {}
        self.varNodes  = {}
        self.topObject = windowObject
        self.modelMapper = []
        if not dom.isNull():
            self._updateVarList()

    def howManyRefVars(self):
        '''
        @summary Return number of reference in dictionnary
        '''
        return len(self.refVars.keys())
        
    def getRefList(self):
        '''
        @summary Return reference's name list
        '''
        return self.refVars.keys() 
    
    def getTruncatedRefList(self):
        '''
        @summary Return reference's name list without the first 4 characters(".ref")
        '''
        return [keys[4:] for keys in self.refVars.keys()]
    
    def getTruncatedRefNameFromIndex(self,row):
        '''
        @summary Return reference's name without the first 4 characters(".ref")
        @param row : row of the reference in the model
        '''
        return self.modelMapper[row][4:]
    
    def getValue(self,refName):
        '''
        @summary Return reference's value
        @param refName : name of the reference
        '''
        return self.refVars[refName]["value"]
    
    def getRefNumValues(self,refName):
        '''
        @summary Return reference's number of value (reference can be a vector)
        @param refName : name of the reference
        '''
        return len(self.getValue(refName))
    
    def getContainerType(self,refName):
        '''
        @summary Return reference's container
        @param refName : name of the reference
        '''
        if len(self.refVars[refName]["value"]) > 1:
            return "Vector"
        else:
            return "Scalar"
    
    def getRefType(self,refName):
        '''
        @summary Return reference's type(type is double, int, etc...)
        @param refName : name of the reference
        '''
        return self.refVars[refName]["type"]
    
    def getRefNode(self,refName):
        '''
        @summary Return reference's node
        @param refName : reference's complete name
        '''
        return self.varNodes[refName]
    
    def addRef(self, refName, refType,refValue=[0], rowToInsert=0):
        '''
        @summary Adds a reference in model
        @param refName :reference's name
        @param refType : reference's type
        @param refValue : reference's value
        @param rowToInsert : position to insert in the model mapper 
        '''
        #Scalar
        if len( refValue) == 1:
            newRefElement = self.dom.ownerDocument().createElement("Entry")
            newRefElement.setAttribute("label",refName)
            newValElement = self.dom.ownerDocument().createElement(refType)
            newValElement.setAttribute("value",refValue[0])
            newRefElement.appendChild(newValElement)
        #Vector
        else:
            newRefElement = self.dom.ownerDocument().createElement("Entry")
            newRefElement.setAttribute("label",refName)
            newVectorElement = self.dom.ownerDocument().createElement("Vector")
            newRefElement.appendChild(newVectorElement)
            for values in refValue:
                newValElement = self.dom.ownerDocument().createElement(refType)
                newValElement.setAttribute("value",values)
                newVectorElement.appendChild(newValElement)
            
        self.dom.appendChild(newRefElement)
        self.modelMapper.insert(rowToInsert, refName)
        
        
        self.needUpdate = True
        self._updateVarList()

    def removeRef(self, refName):
        '''
        @summary Remove a reference from model
        @param refName : name of the reference to remove
        '''
        assert refName in self.refVars.keys(), " Error : in BaseParametersModel::removeRef, trying to delete a non-existant parameter!"
        self.dom.removeChild(self.varNodes[refName])
        self.needUpdate = True
        self._updateVarList()
        
    def referenceExists(self,refName):
        '''
        @summary Tell if a reference already exists in model
        @param refName : name of the reference to check for
        '''
        return "ref." + refName in self.refVars.keys()
    
    def lookForRefUsed(self):
        '''
        @summary Check all References and see if they are currently used in model
        '''
        dependencyQuery = QtXmlPatterns.QXmlQuery()
        parsedXML = QtCore.QByteArray()
        newTextStream = QtCore.QTextStream(parsedXML)
        self.dom.ownerDocument().save(newTextStream, 2)
        queryBuffer = QtCore.QBuffer()
        queryBuffer.setData(newTextStream.readAll())
        queryBuffer.open(QtCore.QIODevice.ReadOnly)
        dependencyQuery.bindVariable("varSerializedXML", queryBuffer)
        #Here is a big limit, we consider dependencies can be all found in attributes ending with the word label or Label
        dependencyQuery.setQuery("for $x in doc($varSerializedXML)//@*[starts-with(data(.),'$')] return (substring-after(string(data($x)),'$'))")
        dependencies = QtXmlPatterns.QXmlResultItems()
        dependencyQuery.evaluateTo(dependencies)
        
        item = QtXmlPatterns.QXmlItem(dependencies.next())
        for ref in self.refVars.keys():
            while not item.isNull():
                if ref == item:
                    self.refVars[ref]["used"] = True
                    break
                else:
                    item = dependencies.next()
            
            if item.isNull():
                self.refVars[ref]["used"] = False
                
    def isRefUsed(self,refName):
        '''
        @summary Tells if a reference has been set as currently used
        @param refNewName : reference's name
        '''
        try:
            return self.refVars[refName]["used"]
        except KeyError:
            #if app loses focus while model is refreshing, it causes a keyerror
            #So this some kind of a bad workaround to try catch the error
            return False
        
    def modifyName(self,refRow,refNewName):
        '''
        @summary Rename a reference
        @param refRow : position of the reference in model
        @param refNewName : new reference's name
        Watchout : If ever a this reference is used in one or more processes/scenarios, this will invalidate the associated tree
        However, the model checker is usually going to tell the user a reference doesn't exist anymore
        '''
        refOldName = self.modelMapper[refRow]
        self.varNodes[str(refOldName)].toElement().setAttribute("label", "ref."+refNewName)
        self.modelMapper[self.modelMapper.index(refOldName)] = "ref." + refNewName
        self.needUpdate = True
        self._updateVarList()
    
    def modifyValue(self,refName, newValue):
        '''
        @summary Change refrence's value(s)
        @param refName : name of the reference to modify
        @param newValue : newValue to assign
        '''
        if self.getContainerType(refName) == "Scalar":
            self.varNodes[refName].firstChildElement().setAttribute("value",newValue)
        else:
            commentCompteur = 0
            for i in range(self.varNodes[refName].firstChildElement().childNodes().length()):
                if self.varNodes[refName].firstChildElement().childNodes().item(i).isComment():
                    commentCompteur += 1
                    continue
                self.varNodes[refName].firstChildElement().childNodes().item(i).toElement().setAttribute("value", newValue[i-commentCompteur])
        
        self.needUpdate = True
        self._updateVarList()
    
    def setRefType(self,refRow,newType):
        '''
        @summary Change reference's data type
        @param refRow : reference's row
        @param newType : reference's new type
        '''
        if self.getContainerType(self.modelMapper[refRow]) == "Scalar":
            self.varNodes[self.modelMapper[refRow]].firstChildElement().setTagName(newType)
        else:
            for i in range(self.varNodes[self.modelMapper[refRow]].firstChildElement().childNodes().count()):
                if self.varNodes[self.modelMapper[refRow]].firstChildElement().childNodes().item(i).isComment():
                    continue
                self.varNodes[self.modelMapper[refRow]].firstChildElement().childNodes().item(i).toElement().setTagName(newType)
                
        self.needUpdate = True
        self._updateVarList()
            
    def _mapToModel(self):
        '''
        @summary Since you cannot control where the data will be inserted in a dictionary(it is dependent of the key and the hash function), we need a table to store
        the keys in order the user wants them to appear
        This function is created to keep the model and the data in sync, while keeping the current data layout in the view 
        '''
        for variable in self.refVars.keys():
            if variable not in self.modelMapper:
                self.modelMapper.append(variable)
        
        for variable in self.modelMapper:
            if variable not in self.refVars.keys():
                self.modelMapper.remove(variable)
    
    def _updateVarList(self):
        '''
        @summary Parse the xml node and store the data in the dictionnaries
        '''
        if self.needUpdate:
            self.refVars = {}
            self.varNodes = {}
            
            childNodes = self.dom.childNodes()
            
            for i in range(childNodes.length()):
                assert childNodes.item(i).nodeName() == "Entry", "Error : in BasePropertymodel::_updateVarList, Parameters has a child node with an invalid tag!"
                lCurrentParameter= childNodes.item(i)
                refName = lCurrentParameter.toElement().attribute("label","")
                
                #Check if it is a reference
                if refName[0:4] != "ref.":
                    continue
                
                self.refVars[refName] = {}
                if refName not in self.varNodes.keys():
                    self.varNodes[refName] = lCurrentParameter
                
                refChild = lCurrentParameter.firstChild()
                if refChild.toElement().tagName() != "Vector":
                    self.refVars[refName]["type"] = refChild.toElement().tagName()
                    self.refVars[refName]["value"] = [refChild.toElement().attribute("value")]
                else:
                    self.refVars[refName]["type"] = refChild.firstChild().toElement().tagName()
                    tmpValList = []
                    for j in range(refChild.childNodes().length()):
                        if refChild.childNodes().item(j).isComment():
                            continue
                        tmpValList.append(refChild.childNodes().item(j).toElement().attribute("value"))
                    self.refVars[refName]["value"] = tmpValList
                if not refName in self.modelMapper:
                    self.modelMapper.append(refName)
            
            self.lookForRefUsed()    
            self._mapToModel()
            self.topObject.dirty = True
            self.needUpdate = False
            
