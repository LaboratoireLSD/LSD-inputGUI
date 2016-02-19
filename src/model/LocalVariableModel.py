'''
Created on 2011-04-02

@author:  Mathieu Gagnon
@contact: mathieu.gagnon@fmed.ulaval.ca
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

from PyQt4 import QtCore
from PyQt4.QtGui import QColor
from uuid import uuid4

def singleton(BaseLocalVariablesModel):
    '''
    Python Decorator, allows singleton behavior
    '''
    instance_container = []
    def wrapper(*args):
        '''
        @summary Wrapper function
        '''
        if not len(instance_container):
            #Create GeneratorBaseModel if it doesn't exist
            instance_container.append(BaseLocalVariablesModel(*args))
            
        return instance_container[0]
    
    return wrapper

@singleton
class BaseLocalVariablesModel:
    '''
    This is a class containing all local variables for every <Variable> or <Process> tag found in the project
    First, here is a look at the xml of the aforementioned tags/nodes:
    
                <Variable/Process>
                    <LocalVariables>
                        <LocalVariable ... />
                            .
                            .
                            .
                    </LocalVariables>
                    <PrimitiveTree>
                            .
                            .
                            .
                    </PrimitiveTree>
                </Variable/Process>
    
    Local Variables will mainly be used in the AdvancedTreeEditor, mainEditorFrame and PrimitiveModel related classes
    Since these classes only have access to the PrimitiveTree node, it will be used as the index to get local variables data 
    '''
    
    def __init__(self):
        '''
        @summary Constructor
        '''
        #Initialize dictionary
        self.locVarDict = {}
        
    def cleanUp(self):
        '''
        @summary Make this class brand new
        '''
        self.locVarDict = {}
    
    def reload(self):
        '''
        @summary Reload class by calling a parseLocVars on indexed nodes
        '''
        for tree in self.locVarDict.keys():
            for locVar in self.locVarDict[tree].keys():
                self.parseLocVars(self.locVarDict[tree][locVar]["node"])
        
    def parseLocVars(self,indexNode):
        '''
        @summary Add local variables to the dictionary
        @param indexNode: QDomNode, <PrimitiveTree> node related to the local variables(sibling of <LocalVariables>)
        '''
        #First look if id has been generated for the primitveTree node
        if not indexNode.toElement().hasAttribute("gui.id"):
            indexNode.toElement().setAttribute("gui.id",uuid4().hex)
        index = str(indexNode.toElement().attribute("gui.id"))
        #Get Local variable dom node (always previous sibling of index node)
        locVarNode = indexNode.previousSiblingElement() 
        self.locVarDict[index] = {}
        locVarNodeList = locVarNode.childNodes()
        for locVarNodeIndex in range(0,locVarNodeList.count()):
            currentLocVar = locVarNodeList.item(locVarNodeIndex)
            currentLocVarName = str(currentLocVar.toElement().attribute("label"))
            self.locVarDict[index][currentLocVarName] = {}
            if str(currentLocVar.firstChild().nodeName()) == "Vector":
                currentLocVarName = str(currentLocVar.toElement().attribute("label"))
                self.locVarDict[index][currentLocVarName]["type"] = str(currentLocVar.firstChild().firstChild().nodeName())
                self.locVarDict[index][currentLocVarName]["node"] = currentLocVar
                self.locVarDict[index][currentLocVarName]["value"] = []
                valueNodeList = currentLocVar.firstChild().childNodes()
                for j in range(0,valueNodeList.count()):
                    currValueNode = valueNodeList.item(j)
                    self.locVarDict[index][currentLocVarName]["value"].append(str(currValueNode.toElement().attribute("value")))
            else:
                self.locVarDict[index][currentLocVarName]["type"] = str(currentLocVar.firstChild().nodeName())
                self.locVarDict[index][currentLocVarName]["value"] = str(currentLocVar.firstChild().toElement().attribute("value"))
                self.locVarDict[index][currentLocVarName]["node"] = currentLocVar
    
    def checkForSimilarLocals(self,indexNode):
        '''
        @summary Look if local variables for indexNode have been modified since it has been loaded in dict
        @param indexNode: <PrimitiveTree> node, index in locVarsDict
        '''
        tmpDict = {}
        index = str(indexNode.toElement().attribute("gui.id"))
        #Get Local variable dom node (always previous sibling of index node)
        locVarNode = indexNode.previousSiblingElement() 
        locVarNodeList = locVarNode.childNodes()
        for locVarNodeIndex in range(0,locVarNodeList.count()):
            currentLocVar = locVarNodeList.item(locVarNodeIndex)
            currentLocVarName = str(currentLocVar.toElement().attribute("label"))
            tmpDict[currentLocVarName] = {}
            if str(currentLocVar.firstChild().nodeName()) == "Vector":
                currentLocVarName = str(currentLocVar.toElement().attribute("label"))
                tmpDict[currentLocVarName]["type"] = str(currentLocVar.firstChild().firstChild().nodeName())
                tmpDict[currentLocVarName]["node"] = currentLocVar
                tmpDict[currentLocVarName]["value"] = []
                valueNodeList = currentLocVar.firstChild().childNodes()
                for j in range(0,valueNodeList.count()):
                    currValueNode = valueNodeList.item(j)
                    tmpDict[currentLocVarName]["value"].append(str(currValueNode.toElement().attribute("value")))
            else:
                tmpDict[currentLocVarName]["type"] = str(currentLocVar.firstChild().nodeName())
                tmpDict[currentLocVarName]["value"] = str(currentLocVar.firstChild().toElement().attribute("value"))
                tmpDict[currentLocVarName]["node"] = currentLocVar
        
        if not tmpDict.keys() == self.locVarDict[index].keys():
            return False
        for locVar in tmpDict.keys():
            if not tmpDict[locVar]["type"] == self.locVarDict[index][locVar]["type"]:
                return False
            if not tmpDict[locVar]["value"] == self.locVarDict[index][locVar]["value"]:
                return False
            
        return True
        
    def getLocVarsList(self,indexNode):
        '''
        @summary Return list of local variables 
        @param indexNode: <PrimitiveTree> node, index in locVarsDict
        '''
        try:
            index = str(indexNode.toElement().attribute("gui.id"))
            return self.locVarDict[index].keys()
        except KeyError:
            print("Couldn't find local variables associated with this node")
            return []
    
    def howManyLocVar(self,indexNode):
        '''
        @summary Return number of local variables 
        @param indexNode: <PrimitiveTree> node, index in locVarsDict
        '''
        index = str(indexNode.toElement().attribute("gui.id"))
        return len(self.locVarDict[index].keys())

    def locVarExists(self, indexNode,varName):
        '''
        @summary Look if variable exists
        @param indexNode : Node associated with this local variable
        @param varName : name of the local variable
        '''
        return str(varName) in self.getLocVarsList(indexNode)
    
    def getLocalVarType(self,indexNode, varName):
        '''
        @summary Return local variable's type
        @param indexNode : <PrimitiveTree> node, index in locVarsDict
        @param varName : local variable's name
        '''
        index = str(indexNode.toElement().attribute("gui.id"))
        return self.locVarDict[index][varName]["type"]
    
    def getLocalVarValue(self,indexNode, varName):
        '''
        @summary Return local variable's default value
        @param indexNode : <PrimitiveTree> node, index in locVarsDict
        @param varName : local variable's name
        '''
        index = str(indexNode.toElement().attribute("gui.id"))
        return self.locVarDict[index][varName]["value"]
    
    '''
    !!!!!MODIFIERS SECTION!!!!!!
    Unlike other models, changes are not directly commited in dom
    Since data is used in tree editor, user might decide to cancel changes
    Hence, changes are only forwarded to the dom once user explicitly saves the modified tree
    '''
    
    def removeLocalVar(self,indexNode,varName):
        '''
        @summary Remove local variable
        @param indexNode : <PrimitiveTree> node, index in locVarsDict
        @param varName : local variable's name
        '''
        index = str(indexNode.toElement().attribute("gui.id"))
        self.locVarDict[index].pop(varName)
        
    def addLocalVar(self,indexNode,varName, varType = "Double", varDefaultValue = "0"):
        '''
        @summary Add local variable
        @param indexNode : <PrimitiveTree> node, index in locVarsDict
        @param varName : new local variable's name
        @param varType : new local variable's type
        @param varDefaultValue : new local variable's default value
        '''
        #Check if local variable is already in model
        compteur = 0
        while varName in self.getLocVarsList(indexNode):
            if compteur == 0:
                print("Warning in BaseLocalVariablesModel::addLocalVar() : cannot add existing local variable " + str(varName)+". Renaming local variable.")
            varName = varName.rstrip("0123456789")
            varName = varName + str(compteur)
            compteur+=1
            
        index = str(indexNode.toElement().attribute("gui.id"))
        #Add in dict
        self.locVarDict[index][str(varName)] = {}
        self.locVarDict[index][str(varName)]["type"] = str(varType)
        if isinstance(varDefaultValue, list):
            self.locVarDict[index][str(varName)]["value"] = varDefaultValue
        else:
            self.locVarDict[index][str(varName)]["value"] = str(varDefaultValue)
        #self.locVarDict[index][str(varName)]["node"] = newLocVarNode
        self.locVarDict[index][str(varName)]["node"] = None
        
    def renameLocalVar(self,indexNode, oldName, newName):
        '''
        @summary Rename local variable
        @param indexNode : <PrimitiveTree> node, index in locVarsDict
        @param oldName : local variable's old name
        @param newName : new local variable's name
        '''
        index = str(indexNode.toElement().attribute("gui.id"))
        self.locVarDict[index][str(newName)] = self.locVarDict[index][str(oldName)]
        self.locVarDict[index].pop(str(oldName))
        #self.locVarDict[index][str(newName)]["node"].toElement().setAttribute("label",str(newName))
    
    def setLocalVarType(self,indexNode, varName, newType):
        '''
        @summary Modify local variable's type
        @param indexNode : <PrimitiveTree> node, index in locVarsDict
        @param varName : local variable's name
        @param newType : new local variable's type
        '''
        index = str(indexNode.toElement().attribute("gui.id"))
        self.locVarDict[index][str(varName)]["type"] = str(newType)
        #self.locVarDict[index][str(varName)]["node"].toElement().setAttribute("type",str(newType))
        
    def setLocalVarValue(self,indexNode, varName, newValue):
        '''
        @summary Modify local variable's default value
        @param indexNode : <PrimitiveTree> node, index in locVarsDict
        @param varName : local variable's name
        @param newValue : new local variable's default value
        '''
        index = str(indexNode.toElement().attribute("gui.id"))
        self.locVarDict[index][str(varName)]["value"] = newValue
        #self.locVarDict[index][str(varName)]["value"].toElement().setAttribute("value",str(newValue))
        
    def save(self,indexNode):
        '''
        @summary Tells model to forward changes in the dom tree
        @param indexNode : <PrimitiveTree> node, index in locVarsDict
        '''
        index = str(indexNode.toElement().attribute("gui.id"))
        if index not in self.locVarDict.keys():
            #Tree without local variables, do as if nothing happened and leave
            return
        newLocVarNode = indexNode.ownerDocument().createElement("LocalVariables")
        #Clear Node
        for localVariable in self.locVarDict[index].keys():
            newLocVar = newLocVarNode.ownerDocument().createElement("LocalVariable")
            newLocVar.setAttribute("label",localVariable)
            if isinstance(self.locVarDict[index][localVariable]["value"],list):
                newVectorNode = newLocVarNode.ownerDocument().createElement("Vector")
                for values in self.locVarDict[index][localVariable]["value"]:
                    newValueNode = newLocVarNode.ownerDocument().createElement(self.locVarDict[index][localVariable]["type"])
                    newValueNode.setAttribute("value",values)
                    newVectorNode.appendChild(newValueNode)
                newLocVar.appendChild(newVectorNode)
            else:
                newValueNode = newLocVarNode.ownerDocument().createElement(self.locVarDict[index][localVariable]["type"])
                newValueNode.setAttribute("value",self.locVarDict[index][localVariable]["value"])
                newLocVar.appendChild(newValueNode)
                
            newLocVarNode.appendChild(newLocVar)
        #Node created, just Replace it
        indexNode.parentNode().replaceChild(newLocVarNode, indexNode.previousSiblingElement())
        self.parseLocVars(indexNode)
        
class LocVarsModel(QtCore.QAbstractTableModel):
    '''
    Model handling local variables representation
    '''

    def __init__(self, pTreeNode, parent=None):
        '''
        @summary Constructor
        @param pTreeNode :  associated <PrimitiveTree> dom node, used to get information from baseModel
        @param parent : model's view
        '''
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.baseModel = BaseLocalVariablesModel()
        self.node = pTreeNode
        self.baseModel.parseLocVars(self.node)
        
    def getBaseModel(self):
        '''
        @summary Return base model
        '''
        return self.baseModel
                                         
    def getVarNameFromIndex(self, index):
        '''' 
        @summary : Return local variable's name
        @param index : variable's position in model/index
        '''
        return self.baseModel.getLocVarsList(self.node)[index.row()]
    
    def getVarTypeFromIndex(self, index):
        '''' 
        @summary : Return local variable's name
        @param index : variable's position in model/index
        '''
        return self.baseModel.getLocalVarType(self.node, self.baseModel.getLocVarsList(self.node)[index.row()])
    
    def getVarValueFromIndex(self, index):
        '''' 
        @summary : Return local variable's default Value
        @param index : variable's position in model/index
        '''
        return self.baseModel.getLocalVarValue(self.node, self.baseModel.getLocVarsList(self.node)[index.row()])
    
    def columnCount(self, parent=QtCore.QModelIndex()):
        '''' 
        @summary : Reimplemented from QAbstractTableModel.columnCount(self,parent)
        Column count is fixed to 3(name,type, default value)
        @param parent : not used
        '''
        return 3
    
    def rowCount(self, parent=QtCore.QModelIndex()):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.rowCount(self,parent)
        How many local variables do we have
        @param parent : not used
        '''
        return self.baseModel.howManyLocVar(self.node)
    
    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.data(self, index, role=QtCore.Qt.DisplayRole)
        Return data for role at position index in model. Controls what is going to be displayed in the table view.
        @param index : cell's index in model/table
        @param role : Qt item role
        '''     
        if not index.isValid() or index.row() >= self.rowCount():
            return QtCore.QVariant()
        
        column = index.column()
        varName = self.getVarNameFromIndex(index)
                
        if role == QtCore.Qt.CheckStateRole:
            return QtCore.QVariant()                #Discard Unwanted checkboxes
        
        if role == QtCore.Qt.ToolTipRole:
            return QtCore.QVariant()
        
        if role == QtCore.Qt.ForegroundRole:
            return QtCore.QVariant(QColor(QtCore.Qt.black))
                
        if role == QtCore.Qt.DisplayRole:
            if column == 0:
                #Variable's name
                return QtCore.QVariant(QtCore.QString(varName))
            elif column == 1:
                # Type
                type = self.baseModel.getLocalVarType(self.node, varName)
                return QtCore.QVariant(QtCore.QString(type))
            
            elif column == 2:
                # Value
                value = self.baseModel.getLocalVarValue(self.node, varName)
                return QtCore.QVariant(QtCore.QString(str(value)))
            
            return QtCore.QVariant(QtCore.QString(""))

    def headerData(self, section, orientation, role):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.headerData(self, section, orientation, role)
        See QAbstractTableModel's documentation for mode details
        @param section : model's column or row
        @param orientation : horizontal or vertical
        @param role : Qt item role
        '''
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        
        if orientation == QtCore.Qt.Horizontal:
            if section == 0:
                return QtCore.QVariant("Name")
            elif section == 1:
                return QtCore.QVariant("Type")
            elif section == 2:
                return QtCore.QVariant("Default Value")
            else:
                return QtCore.QVariant()
        else:
            return QtCore.QVariant(section + 1)  
        
        return QtCore.QVariant()
    
    def flags(self, index):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.flags(self,index)
        See QAbstractTableModel's documentation for mode details
        @param index : cell's index in model/table
        '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index) | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled |QtCore.Qt.ItemIsDropEnabled)

    def insertRow(self, rowafter, parent=QtCore.QModelIndex(),varName = "New_variable", varType ="Unknown",varValue="0"):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.insertRow(self, row, parent=QtCore.QModelIndex())
        See QAbstractTableModel's documentation for mode details
        Inserts a variable in the model/table
        @param rowafter : insertion row in model/table
        @pram parent : parent's index(not really relevant for list views)
        @param name : name of the variable
        '''
        self.beginInsertRows(parent, rowafter, rowafter)
        self.baseModel.addLocalVar(self.node,varName,varType,varValue)
        self.endInsertRows()
        return
      
    def removeRow(self, row, parent = QtCore.QModelIndex()):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.removeRow(self, row , parent=QtCore.QModelIndex())
        See QAbstractTableModel's documentation for mode details
        Removes a row from the model/table
        @param row : row of the deleted index
        @param parent : parent's index (not relevant for QtableView)
        '''
        self.beginRemoveRows(parent, row, row)
        self.baseModel.removeLocalVar(self.node, self.baseModel.getLocVarsList(self.node)[row])
        self.endRemoveRows()
        
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.setData(self, index, value, role=QtCore.Qt.EditRole)
        Sets data for role at position index in model. Modify model and its underlying data structure
        @param index : cell's position in model/table
        @param value : new Value
        @param role : Qt item role
        '''
        if index.isValid() and role == QtCore.Qt.EditRole:
            if index.column() == 0:
                if str(value.toString()) in self.baseModel.getLocVarsList(self.node):
                    print("Cannot set variable's name, " + str(value.toString()) + " already exists.")
                    return False
                else:
                    self.baseModel.renameLocalVar(self.node, self.getVarNameFromIndex(index), value.toString())
                    return True
            elif index.column() == 1:
                self.baseModel.setLocalVarType(self.node, self.getVarNameFromIndex(index), value.toString())
                return True
            elif index.column() == 2:
                if str(value.typeName()) == "QStringList":
                    self.baseModel.setLocalVarValue(self.node, self.getVarNameFromIndex(index), [str(item) for item in list(value.toStringList())])
                else:
                    self.baseModel.setLocalVarValue(self.node, self.getVarNameFromIndex(index), str(value.toString()))
                return True
            else:
                return False
        