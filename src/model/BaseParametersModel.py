'''
Created on 2010-08-11

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

from PyQt4 import QtXml
from PyQt4 import QtXmlPatterns
from PyQt4 import QtCore
import re
import os

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
    
    def getRefNameFromIndex(self,row):
        '''
        @summary Return reference's name
        @param row : row of the reference in the model
        '''
        return self.modelMapper[row]
    
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
        return self.refVars[str(refName)]["value"]
    
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
        if len(self.refVars[str(refName)]["value"]) > 1:
            return "Vector"
        else:
            return "Scalar"
    
    def getRefType(self,refName):
        '''
        @summary Return reference's type(type is double, int, etc...)
        @param refName : name of the reference
        '''
        return self.refVars[str(refName)]["type"]
    
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
        self.modelMapper.insert(rowToInsert,str(refName))
        
        
        self.needUpdate = True
        self._updateVarList()

    def removeRef(self, refName):
        '''
        @summary Remove a reference from model
        @param refName : name of the reference to remove
        '''
        assert str(refName) in self.refVars.keys(), " Error : in BaseParametersModel::removeRef, trying to delete a non-existant parameter!"
        self.dom.removeChild(self.varNodes[str(refName)])
        self.needUpdate = True
        self._updateVarList()
        
    def referenceExists(self,refName):
        '''
        @summary Tell if a reference already exists in model
        @param refName : name of the reference to check for
        '''
        return "ref."+str(refName) in self.getRefList()
    
    def lookForRefUsed(self):
        '''
        @summary Check all References and see if they are currently used in model
        '''
        dependencyQuery = QtXmlPatterns.QXmlQuery()
        parsedXML = QtCore.QString()
        newTextStream = QtCore.QTextStream(parsedXML)
        self.dom.ownerDocument().save(newTextStream,2)
        queryBuffer = QtCore.QBuffer()
        queryBuffer.setData(parsedXML.toUtf8())
        queryBuffer.open(QtCore.QIODevice.ReadOnly)
        dependencyQuery.bindVariable("varSerializedXML", queryBuffer)
        #Here is a big limit, we consider dependencies can be all found in attributes ending with the word label or Label
        dependencyQuery.setQuery("for $x in doc($varSerializedXML)//@*[starts-with(data(.),'$')] return (substring-after(string(data($x)),'$'))")
        dependencies = QtCore.QStringList()
        dependencyQuery.evaluateTo(dependencies)
        for ref in self.refVars.keys():
            if QtCore.QString(ref) in list(dependencies):
                self.refVars[ref]["used"] = True
            else:
                self.refVars[ref]["used"] = False
            #regular expression cannot find directly name of process, so we find directly in folder.
            #diep 24-3-2020
            for subdir, dirs, files in os.walk(self.topObject.folderPath + "/Processes"):
                for file in files:
                    filepath = subdir + os.sep + file
                    if filepath.endswith(".xml"):
                        if ref in open(filepath).read():
                            self.refVars[ref]["file"] = file.replace(".xml","")
    def isRefLoc(self,refName):
        try:
            return self.refVars[refName]["file"]
        except KeyError:
            return ""
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
        self.varNodes[str(refOldName)].toElement().setAttribute("label","ref."+str(refNewName))
        self.modelMapper[self.modelMapper.index(str(refOldName))] = "ref."+str(refNewName)
        self.needUpdate = True
        self._updateVarList()
    
    def modifyValue(self,refName, newValue):
        '''
        @summary Change refrence's value(s)
        @param refName : name of the reference to modify
        @param newValue : newValue to assign
        '''
        if self.getContainerType(refName) == "Scalar":
            self.varNodes[str(refName)].firstChildElement().setAttribute("value",newValue)
        else:
            commentCompteur = 0
            for i in range(0,self.varNodes[str(refName)].firstChildElement().childNodes().length()):
                if self.varNodes[str(refName)].firstChildElement().childNodes().item(i).isComment():
                    commentCompteur += 1
                    continue
                self.varNodes[str(refName)].firstChildElement().childNodes().item(i).toElement().setAttribute("value", newValue[i-commentCompteur])
        
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
            for i in range(0,self.varNodes[self.modelMapper[refRow]].firstChildElement().childNodes().count()):
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
            
            for i in range(0,childNodes.length()):
                assert childNodes.item(i).nodeName() == "Entry", "Error : in BasePropertymodel::_updateVarList, Parameters has a child node with an invalid tag!"
                lCurrentParameter= childNodes.item(i)
                refName = lCurrentParameter.toElement().attribute("label","")
                
                #Check if it is a reference
                if refName[0:4] != "ref.":
                    continue
                
                self.refVars[str(refName)] = {}
                if str(refName) not in self.varNodes.keys():
                    self.varNodes[str(refName)] = lCurrentParameter
                
                refChild = lCurrentParameter.firstChild()
                if str(refChild.toElement().tagName()) != "Vector":
                    self.refVars[str(refName)]["type"] = str(refChild.toElement().tagName())
                    self.refVars[str(refName)]["value"] = [str(refChild.toElement().attribute("value"))]
                else:
                    self.refVars[str(refName)]["type"] = str(refChild.firstChild().toElement().tagName())
                    tmpValList = []
                    for j in range(0,refChild.childNodes().length()):
                        if refChild.childNodes().item(j).isComment():
                            continue
                        tmpValList.append(str(refChild.childNodes().item(j).toElement().attribute("value")))
                    self.refVars[str(refName)]["value"] = tmpValList
                if not str(refName) in self.modelMapper:
                    self.modelMapper.append(str(refName))
                
            
            self.lookForRefUsed()    
            self._mapToModel()
            self.topObject.dirty = True
            self.needUpdate = False
            