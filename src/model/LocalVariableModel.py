"""
.. module:: LocalVariableModel

.. codeauthor:: Mathieu Gagnon <mathieu.gagnon.10@ulaval.ca>

:Created on: 2011-04-02

"""
from PyQt4 import QtCore
from PyQt4.QtGui import QColor
from uuid import uuid4
from functools import wraps

def singleton(BaseLocalVariablesModel):
    '''
    Python Decorator, allows singleton behavior
    '''
    instance_container = []
    @wraps(BaseLocalVariablesModel)
    def wrapper(*args):
        '''
        Wrapper function
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
        Constructor.
        '''
        #Initialize dictionary
        self.locVarDict = {}
        
    def cleanUp(self):
        '''
        Makes this class brand new.
        '''
        self.locVarDict = {}
    
    def reload(self):
        '''
        Reloads class by calling :meth:`.parseLocVars` on indexed nodes.
        '''
        for tree in self.locVarDict.keys():
            for locVar in self.locVarDict[tree].keys():
                self.parseLocVars(self.locVarDict[tree][locVar]["node"])
        
    def parseLocVars(self, indexNode):
        '''
        Adds local variables to the dictionary.
        
        :param indexNode: <PrimitiveTree> node related to the local variables(sibling of <LocalVariables>).
        :type indexNode: QDomNode
        '''
        #First, look if id has been generated for the primitveTree node
        if not indexNode.toElement().hasAttribute("gui.id"):
            indexNode.toElement().setAttribute("gui.id",uuid4().hex)
        index = indexNode.toElement().attribute("gui.id")
        #Get Local variable dom node (always previous sibling of index node)
        locVarNode = indexNode.previousSiblingElement() 
        self.locVarDict[index] = {}
        locVarNodeList = locVarNode.childNodes()
        for locVarNodeIndex in range(locVarNodeList.count()):
            currentLocVar = locVarNodeList.item(locVarNodeIndex)
            currentLocVarName = currentLocVar.toElement().attribute("label")
            self.locVarDict[index][currentLocVarName] = {}
            if currentLocVar.firstChild().nodeName() == "Vector":
                currentLocVarName = currentLocVar.toElement().attribute("label")
                self.locVarDict[index][currentLocVarName]["type"] = currentLocVar.firstChild().firstChild().nodeName()
                self.locVarDict[index][currentLocVarName]["node"] = currentLocVar
                self.locVarDict[index][currentLocVarName]["value"] = []
                valueNodeList = currentLocVar.firstChild().childNodes()
                for j in range(valueNodeList.count()):
                    currValueNode = valueNodeList.item(j)
                    self.locVarDict[index][currentLocVarName]["value"].append(currValueNode.toElement().attribute("value"))
            else:
                self.locVarDict[index][currentLocVarName]["type"] = currentLocVar.firstChild().nodeName()
                self.locVarDict[index][currentLocVarName]["value"] = currentLocVar.firstChild().toElement().attribute("value")
                self.locVarDict[index][currentLocVarName]["node"] = currentLocVar
    
    def checkForSimilarLocals(self, indexNode):
        '''
        Looks if local variables for indexNode have been modified since it has been loaded in dictionary.
        
        :param indexNode: <PrimitiveTree> node, index in locVarsDict.
        :type indexNode: QDomNode
        :return: Boolean.
        '''
        tmpDict = {}
        index = indexNode.toElement().attribute("gui.id")
        #Get Local variable dom node (always previous sibling of index node)
        locVarNode = indexNode.previousSiblingElement() 
        locVarNodeList = locVarNode.childNodes()
        for locVarNodeIndex in range(locVarNodeList.count()):
            currentLocVar = locVarNodeList.item(locVarNodeIndex)
            currentLocVarName = currentLocVar.toElement().attribute("label")
            tmpDict[currentLocVarName] = {}
            if currentLocVar.firstChild().nodeName() == "Vector":
                currentLocVarName = currentLocVar.toElement().attribute("label")
                tmpDict[currentLocVarName]["type"] = currentLocVar.firstChild().firstChild().nodeName()
                tmpDict[currentLocVarName]["node"] = currentLocVar
                tmpDict[currentLocVarName]["value"] = []
                valueNodeList = currentLocVar.firstChild().childNodes()
                for j in range(valueNodeList.count()):
                    currValueNode = valueNodeList.item(j)
                    tmpDict[currentLocVarName]["value"].append(currValueNode.toElement().attribute("value"))
            else:
                tmpDict[currentLocVarName]["type"] = currentLocVar.firstChild().nodeName()
                tmpDict[currentLocVarName]["value"] = currentLocVar.firstChild().toElement().attribute("value")
                tmpDict[currentLocVarName]["node"] = currentLocVar
        
        if self.locVarDict.get(index) == None or tmpDict.keys() != self.locVarDict[index].keys():
            return False
        for locVar in tmpDict.keys():
            if tmpDict[locVar]["type"] != self.locVarDict[index][locVar]["type"]:
                return False
            if tmpDict[locVar]["value"] != self.locVarDict[index][locVar]["value"]:
                return False
            
        return True
        
    def getLocVarsList(self, indexNode):
        '''
        Returns the list of local variables.
        
        :param indexNode: <PrimitiveTree> node, index in locVarsDict.
        :type indexNode: PyQt4.QtXml.QDomNode
        :return: String list.
        '''
        try:
            index = indexNode.toElement().attribute("gui.id")
            return self.locVarDict[index].keys()
        except KeyError:
            print("Couldn't find local variables associated with this node")
            return []
    
    def howManyLocVar(self, indexNode):
        '''
        Returns the number of local variables.
        
        :param indexNode: <PrimitiveTree> node, index in locVarsDict.
        :type indexNode: PyQt4.QtXml.QDomNode
        :return: Int.
        '''
        index = indexNode.toElement().attribute("gui.id")
        return len(self.locVarDict[index].keys())

    def locVarExists(self, indexNode, varName):
        '''
        Looks if a variable exists.
        
        :param indexNode: Node associated with this local variable.
        :param varName: Name of the local variable.
        :type indexNode: PyQt4.QtXml.QDomNode
        :type varName: String
        :return: Boolean.
        '''
        return varName in self.getLocVarsList(indexNode)
    
    def getLocalVarType(self, indexNode, varName):
        '''
        Returns a local variable's type as string.
        
        :param indexNode: <PrimitiveTree> node, index in locVarsDict.
        :param varName: local variable's name.
        :type indexNode: PyQt4.QtXml.QDomNode
        :type varName: String
        :return: String.
        '''
        index = indexNode.toElement().attribute("gui.id")
        return self.locVarDict[index][varName]["type"]
    
    def getLocalVarValue(self, indexNode, varName):
        '''
        Returns a local variable's default value as string.
        
        :param indexNode: <PrimitiveTree> node, index in locVarsDict.
        :param varName: Local variable's name.
        :type indexNode: PyQt4.QtXml.QDomNode
        :type varName: String
        :return: String.
        '''
        index = indexNode.toElement().attribute("gui.id")
        return self.locVarDict[index][varName]["value"]
    
    '''
    !!!!!MODIFIERS SECTION!!!!!!
    Unlike other models, changes are not directly committed in dom
    Since data is used in tree editor, user might decide to cancel changes
    Hence, changes are only forwarded to the dom once user explicitly saves the modified tree
    '''
    
    def removeLocalVar(self, indexNode, varName):
        '''
        Removes a local variable.
        
        :param indexNode: <PrimitiveTree> node, index in locVarsDict.
        :param varName: Local variable's name.
        :type indexNode: PyQt4.QtXml.QDomNode
        :type varName: String
        '''
        index = indexNode.toElement().attribute("gui.id")
        self.locVarDict[index].pop(varName)
        
    def addLocalVar(self, indexNode, varName, varType="Double", varDefaultValue="0"):
        '''
        Adds a local variable.
        
        :param indexNode: <PrimitiveTree> node, index in locVarsDict.
        :param varName: New local variable's name.
        :param varType: Optional - New local variable's type.
        :param varDefaultValue: Optional - New local variable's default value.
        :type indexNode: PyQt4.QtXml.QDomNode
        :type varName: String
        :type varType: String
        :type varDefaultValue: String
        '''
        #Check if local variable is already in model
        compteur = 0
        while varName in self.getLocVarsList(indexNode):
            if compteur == 0:
                print("Warning in BaseLocalVariablesModel::addLocalVar() : cannot add existing local variable", varName)
                print("Renaming local variable")
            varName = varName.rstrip("0123456789")
            varName += str(compteur)
            compteur += 1
            
        index = indexNode.toElement().attribute("gui.id")
        #Add in dict
        self.locVarDict[index][varName] = {}
        self.locVarDict[index][varName]["type"] = varType
        self.locVarDict[index][varName]["value"] = varDefaultValue
        #self.locVarDict[index][varName]["node"] = newLocVarNode
        self.locVarDict[index][varName]["node"] = None
        
    def renameLocalVar(self, indexNode, oldName, newName):
        '''
        Renames a local variable.
        
        :param indexNode: <PrimitiveTree> node, index in locVarsDict.
        :param oldName: Local variable's old name.
        :param newName: New local variable's name.
        :type indexNode: PyQt4.QtXml.QDomNode
        :type oldName: String
        :type newName: String
        '''
        index = indexNode.toElement().attribute("gui.id")
        self.locVarDict[index][newName] = self.locVarDict[index][oldName]
        self.locVarDict[index].pop(oldName)
        #self.locVarDict[index][newName]["node"].toElement().setAttribute("label", newName)
    
    def setLocalVarType(self, indexNode, varName, newType):
        '''
        Modifies a local variable's type.
        
        :param indexNode: <PrimitiveTree> node, index in locVarsDict.
        :param varName: Local variable's name.
        :param newType: New local variable's type.
        :type indexNode: PyQt4.QtXml.QDomNode
        :type varName: String
        :type newType: String
        '''
        index = indexNode.toElement().attribute("gui.id")
        self.locVarDict[index][varName]["type"] = newType
        #self.locVarDict[index][varName]["node"].toElement().setAttribute("type", newType)
        
    def setLocalVarValue(self, indexNode, varName, newValue):
        '''
        Modifies a local variable's default value.
        
        :param indexNode: <PrimitiveTree> node, index in locVarsDict.
        :param varName: Local variable's name.
        :param newValue: New local variable's default value.
        :type indexNode: PyQt4.QtXml.QDomNode
        :type varName: String
        :type newValue: String
        '''
        index = indexNode.toElement().attribute("gui.id")
        self.locVarDict[index][varName]["value"] = newValue
        #self.locVarDict[index][varName]["value"].toElement().setAttribute("value", newValue)
        
    def save(self, indexNode):
        '''
        Tells model to forward changes in the dom tree.
        
        :param indexNode: <PrimitiveTree> node, index in locVarsDict.
        :type indexNode: PyQt4.QtXml.QDomNode
        '''
        index = indexNode.toElement().attribute("gui.id")
        if index not in self.locVarDict.keys():
            #Tree without local variables, do as if nothing happened and leave
            return
        newLocVarNode = indexNode.ownerDocument().createElement("LocalVariables")
        #Clear Node
        for localVariable in self.locVarDict[index].keys():
            newLocVar = newLocVarNode.ownerDocument().createElement("LocalVariable")
            newLocVar.setAttribute("label", localVariable)
            if isinstance(self.locVarDict[index][localVariable]["value"], list):
                newVectorNode = newLocVarNode.ownerDocument().createElement("Vector")
                for values in self.locVarDict[index][localVariable]["value"]:
                    newValueNode = newLocVarNode.ownerDocument().createElement(self.locVarDict[index][localVariable]["type"])
                    newValueNode.setAttribute("value", values)
                    newVectorNode.appendChild(newValueNode)
                newLocVar.appendChild(newVectorNode)
            else:
                newValueNode = newLocVarNode.ownerDocument().createElement(self.locVarDict[index][localVariable]["type"])
                newValueNode.setAttribute("value", self.locVarDict[index][localVariable]["value"])
                newLocVar.appendChild(newValueNode)
                
            newLocVarNode.appendChild(newLocVar)
        #Node created, just Replace it
        indexNode.parentNode().replaceChild(newLocVarNode, indexNode.previousSiblingElement())
        self.parseLocVars(indexNode)
        
class LocVarsModel(QtCore.QAbstractTableModel):
    '''
    Model handling local variables representation.
    '''

    def __init__(self, pTreeNode, parent=None):
        '''
        Constructor.
        
        :param pTreeNode : Associated <PrimitiveTree> dom node, used to get information from baseModel.
        :param parent : Optional - Model's view.
        '''
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.baseModel = BaseLocalVariablesModel()
        self.node = pTreeNode
        self.baseModel.parseLocVars(self.node)
                                         
    def getVarNameFromIndex(self, index):
        '''' 
        Returns a local variable's name.
        
        :param index: Variable's position in model/index.
        :type index: PyQt4.QtCore.QModelIndex
        :return: String
        '''
        return list(self.baseModel.getLocVarsList(self.node))[index.row()]
    
    def getVarTypeFromIndex(self, index):
        '''' 
        Returns a local variable's type as string.
        
        :param index: Variable's position in model/index.
        :type index: PyQt4.QtCore.QModelIndex
        :return: String
        '''
        return self.baseModel.getLocalVarType(self.node, self.baseModel.getLocVarsList(self.node)[index.row()])
    
    def getVarValueFromIndex(self, index):
        '''' 
        Returns a local variable's default Value.
        
        :param index: Variable's position in model/index.
        :type index: PyQt4.QtCore.QModelIndex
        :return: String
        '''
        return self.baseModel.getLocalVarValue(self.node, self.baseModel.getLocVarsList(self.node)[index.row()])
    
    def columnCount(self, parent=QtCore.QModelIndex()):
        '''' 
        Reimplemented from QAbstractTableModel.columnCount(self, parent).
        Column count is fixed to 3 (name, type, default value).
        
        :param parent:
        :type parent: Not used
        :return: Int. Always 3.
        '''
        return 3
    
    def rowCount(self, parent=QtCore.QModelIndex()):
        ''' 
        Reimplemented from QAbstractTableModel.rowCount(self, parent).
        How many local variables do we have.
        
        :param parent:
        :type parent: Not used
        :return: Int.
        '''
        return self.baseModel.howManyLocVar(self.node)
    
    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' 
        Reimplemented from QAbstractTableModel.data(self, index, role=QtCore.Qt.DisplayRole).
        Return data for role at position index in model. Controls what is going to be displayed in the table view.
        
        :param index: Cell's index in model/table.
        :param role: Optional - Qt item role.
        :type index: PyQt4.QtCore.QModelIndex
        :type role: Int
        :return: String | PyQt4.QtGui.QColor
        '''     
        if not index.isValid() or index.row() >= self.rowCount() or index.column() >= self.columnCount(None):
            return None
        
        column = index.column()
        varName = self.getVarNameFromIndex(index)
        
        if role == QtCore.Qt.ForegroundRole:
            return QtCore.Qt.black
                
        if role == QtCore.Qt.DisplayRole:
            if column == 0:
                # Variable's name
                return varName
            elif column == 1:
                # Return the type
                return self.baseModel.getLocalVarType(self.node, varName)
            elif column == 2:
                # Value
                return self.baseModel.getLocalVarValue(self.node, varName)

    def headerData(self, section, orientation, role):
        ''' 
        Reimplemented from QAbstractTableModel.headerData(self, section, orientation, role).
        See QAbstractTableModel's documentation for mode details.
        
        :param section: Model's column or row.
        :param orientation: Horizontal or vertical.
        :param role: Qt item role.
        :type section: Int
        :type orientation: QtCore.Qt.orientation
        :type role: Int
        :return: String. Column or row title.
        '''
        if role != QtCore.Qt.DisplayRole:
            return None
        
        if orientation == QtCore.Qt.Horizontal:
            return ["Name", "Type", "Default Value"][section]
        else:
            return str(section + 1)
    
    def flags(self, index):
        ''' 
        Reimplemented from QAbstractTableModel.flags(self, index).
        See QAbstractTableModel's documentation for mode details.
        
        :param index: Cell's index in model/table.
        :type index: PyQt4.QtCore.QModelIndex
        :return: Int
        '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index) | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled |QtCore.Qt.ItemIsDropEnabled)

    def insertRow(self, rowafter, parent=QtCore.QModelIndex(),varName = "New_variable", varType ="Unknown",varValue="0"):
        ''' 
        Reimplemented from QAbstractTableModel.insertRow(self, row, parent=QtCore.QModelIndex()).
        See QAbstractTableModel's documentation for mode details.
        Inserts a variable in the model/table.
        
        :param rowafter: Insertion row in model/table.
        :param parent: Optional - Parent's index (not really relevant for list views).
        :param varName: Optional - Name of the variable.
        :param varType: Optional - Type of the variable.
        :param varValue: Optional - Value of the variable.
        :type rowafter: Int
        :type parent: PyQt4.QtCore.QModelIndex
        :type varName: String
        :type varType: String
        :type varValue: String
        '''
        self.beginInsertRows(parent, rowafter, rowafter)
        self.baseModel.addLocalVar(self.node,varName,varType,varValue)
        self.endInsertRows()
      
    def removeRow(self, row, parent = QtCore.QModelIndex()):
        ''' 
        Reimplemented from QAbstractTableModel.removeRow(self, row, parent=QtCore.QModelIndex()).
        See QAbstractTableModel's documentation for mode details.
        Removes a row from the model/table.
        
        :param row: Row of the selected index to delete.
        :param parent: Optional - Parent's index (not relevant for QtableView).
        :type row: Int
        :type parent: PyQt4.QtCore.QModelIndex
        '''
        self.beginRemoveRows(parent, row, row)
        self.baseModel.removeLocalVar(self.node, self.baseModel.getLocVarsList(self.node)[row])
        self.endRemoveRows()
        
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        ''' 
        Reimplemented from QAbstractTableModel.setData(self, index, value, role=QtCore.Qt.EditRole).
        Sets data for role at position "index" in model. Modifies model and its underlying data structure.
        
        :param index: Cell's position in model/table.
        :param value: New Value.
        :param role: Qt item role.
        :type index: PyQt4.QtCore.QModelIndex
        :type value: String
        :type role: Int
        :return: Boolean. True = data set correctly.
        '''
        if index.isValid() and role == QtCore.Qt.EditRole:
            if index.column() == 0:
                if value in self.baseModel.getLocVarsList(self.node):
                    print("Cannot set variable's name, " + value + " already exists.")
                    return False
                else:
                    self.baseModel.renameLocalVar(self.node, self.getVarNameFromIndex(index), value)
                    return True
            elif index.column() == 1:
                self.baseModel.setLocalVarType(self.node, self.getVarNameFromIndex(index), value)
                return True
            elif index.column() == 2:
                self.baseModel.setLocalVarValue(self.node, self.getVarNameFromIndex(index), value)
                return True
            else:
                return False
        
