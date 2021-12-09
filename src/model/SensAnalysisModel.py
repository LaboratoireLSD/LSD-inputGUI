"""
.. module:: SensAnalysisModel

.. codeauthor:: Mathieu Gagnon <mathieu.gagnon.10@ulaval.ca>

:Created on: 2010-08-23

"""
from PyQt4 import QtCore
from PyQt4.QtGui import QColor
from PyQt4 import QtGui
from model.BaseParametersModel import BaseParametersModel

class SaComboBoxModel(QtCore.QAbstractItemModel):
    '''
    Model used to list Reference Parameters in a comboBox
    '''

    def __init__(self, paramModel, listModel, parent=None, mainWindow=None):
        '''
        Constructor.
        
        :param paramModel: Parameters base model.
        :param listModel: Model listing sensibility analysis and parameters used in them.
        :param parent: Optional - Model's view.
        :param mainWindow: Optional - Application's main window.
        :type paramModel: :class:`.ParametersModel`
        :type listModel: :class:`.SaTableModel`
        :type parent: QtGui.QComboBox
        :type mainWindow: :class:`.MainWindow`
        '''
        QtCore.QAbstractItemModel.__init__(self, parent)
        self.parent = parent
        self.listModel = listModel
        self.modelBase = paramModel
        self.topWObject = mainWindow
             
    def getParams(self):
        '''
        Returns all parameters that are not yet part of a sensibility analysis.
        
        :return: String list.
        '''
        return sorted([param for param in self.modelBase.baseModel.getTruncatedRefList() if not self.listModel.exists(param)])
    
    def columnCount(self, parent=QtCore.QModelIndex()):
        '''
        Reimplementation of QAbstactItemModel.columnCount(self, parent=QtCore.QModelIndex()).
        Since this model underlies a comboBox, column count is fixed to 1.
        Even if it is implicit that column count is going to be one since we apply this model to a combo box.
        Qt complains if it is not overridden.
        
        :param parent:
        :type parent: Not used
        :return: Int. Always 1.
        '''
        return 1
    
    def parent(self, index):
        '''
        Reimplementation of QAbstactItemModel.parent(self, index).
        Return index's parent.
        Since this model underlies a comboBox, model items do not really have a parent, so returning and invalid index is ok.
        Qt complains if it is not overridden.
        
        :param index:
        :type index: Not used
        :return: PyQt4.QtCore.QModelIndex(). Returns a brand new object.
        '''
        return QtCore.QModelIndex() 
    
    def rowCount(self, parent=QtCore.QModelIndex()):
        ''' 
        Reimplemented from QAbstractItemModel.rowCount(self, parent).
        How many unused parameters do we have.
        
        :param parent:
        :type parent: Not used
        :return: Int.
        '''
        return len(self.getParams())
    
    def index(self, row, column, parent=QtCore.QModelIndex()) :
        '''
        Reimplemented from QAbstractItemModel.index(self, row, column, parent=QtCore.QModelIndex()).
        Create a model index if there is data at this position in the model.
        
        :param row: Position in the model.
        :param column: Position in the model.
        :param parent:
        :type row: Int
        :type column: Int
        :type parent: Not used
        :return: PyQt4.QtCore.QModelIndex().
        '''
        if row >= self.rowCount() or column != 0:
            return QtCore.QModelIndex()  
        else:
            return self.createIndex(row, column)
        
    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' 
        Reimplemented from QAbstracItemModel.data(self, index, role=QtCore.Qt.DisplayRole).
        Returns data for role at position "index" in model. Controls what is going to be displayed in the table view.
        
        :param index: Cell's index in model/table.
        :param role: Qt item role.
        :type index: PyQt4.QtCore.QModelIndex()
        :type role: Int
        :return: String.
        ''' 
        if not index.isValid() or index.column() >= self.columnCount(None):
            return None
        
        if role == QtCore.Qt.DisplayRole:
            return self.getParams()[index.row()]

    def addParam(self, paramNum):
        '''
        Takes a parameter from model and moves it in the sensibility analysis model.
        
        :param paramNum: Position of the parameter to switch in the combobox.
        :type paramNum: Int
        '''
        self.beginRemoveRows(QtCore.QModelIndex(),paramNum,paramNum)
        self.listModel.insertRow(self.listModel.rowCount(),"ref."+self.getParams()[paramNum])
        self.endRemoveRows()
       
    def flags(self, index):
        ''' 
        Reimplemented from QAbstractItemModel.flags(self, index).
        See QAbstractItemModel's documentation for more details.
        
        :param index: Cell's index in model/table.
        :type index: PyQt4.QtCore.QModelIndex()
        :return: Int.
        '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        return QtCore.Qt.ItemFlags(QtCore.QAbstractItemModel.flags(self, index) )

class SaTableModel(QtCore.QAbstractTableModel):
    '''
    Model used to list sensibility analysis in a tableView.
    '''

    def __init__(self, domTree, parent=None, mainWindow=None):
        '''
        Constructor.
        
        :param domTree: Sensibility analysis XML node.
        :param parent: Optional - Model's view.
        :param mainWindow: Optional - Application's main window.
        :type domTree: PyQt4.QtXml.QDomElement
        :type parent: PyQt4.QtGui.QTableView
        :type mainWindow: :class:`.MainWindow`
        '''
        QtCore.QAbstractListModel.__init__(self, parent)
        self.dom = domTree
        self.params = self.getParams()
        self.topWObject = mainWindow
        self.headers = ["Parameters", "Initial value(s)", "Law",
                        "Lower limit", "Upper limit", "Std dev.",
                        "Mean (opt.)"]
            
    def getAnalysisNode(self, column):
        '''
        Returns the sensibility analysis located at column.
        
        :param column: Position of the sensibility analysis in model.
        :type column: Int
        :return: PyQt4.QtXml.QDomNode
        '''
        return self.dom.childNodes().item(column)
    
    def getParams(self):
        '''
        Returns all parameters that are found in at least one sensibility analysis.
        
        :return: String list.
        '''
        listParams = []
        for i in range(self.dom.childNodes().count()):
            currentAnalysis = self.dom.childNodes().item(i)
            for j in range(currentAnalysis.childNodes().count()):
                paramName = currentAnalysis.childNodes().item(j).toElement().attribute("name")
                if paramName not in listParams:
                    listParams.append(paramName)
        
        return listParams
         
    def exists(self, paramName):
        '''
        Tells if a parameter is found in used parameters list.
        
        :param paramName: Name of the parameter to look for.
        :type paramName: String
        :return: Boolean.
        '''
        return "ref." + paramName in self.params
    
    def rowCount(self, parent=QtCore.QModelIndex()):
        ''' 
        Reimplemented from QAbstractTableModel.rowCount(self, parent).
        How many used parameters do we have.
        
        :param parent:
        :type parent: Not used
        :return: Int.
        '''
        return len(self.params)
    
    def columnCount(self, parent=QtCore.QModelIndex()):
        '''' 
        Reimplemented from QAbstractTableModel.columnCount(self, parent)
        How many analysis do we have + parameters name column + parameters default value column.
        
        :param parent:
        :type parent: Not used
        :return: Int. Number of analysis + 2.
        '''
        return self.dom.childNodes().count() + 2
        
    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' 
        Reimplemented from QAbstractTableModel.data(self, index, role=QtCore.Qt.DisplayRole).
        Return data for role at position index in model. Controls what is going to be displayed in the table view.
        
        :param index: Cell's index in model/table.
        :param role: Optional - Qt item role.
        :type index: PyQt4.QtCore.QModelIndex()
        :type role: Int
        :return: QColor | String
        ''' 
        if not index.isValid():
            return None

        row = index.row()
        column = index.column()
        if role == QtCore.Qt.BackgroundRole:
            if column == 0:
                return QColor(220, 220, 220)
        elif role == QtCore.Qt.DisplayRole:
            if column == 0:
                refName = self.params[row][4:]
                return refName
            if column == 1:
                basePmtModel = BaseParametersModel()
                initialValue = basePmtModel.getValue(self.params[row])
                return str(initialValue)
            if column <= self.columnCount() and row <=self.rowCount():
                attrName = self.params[row]
                for i in range(self.getAnalysisNode(column-2).childNodes().count()):
                    paramNode = self.getAnalysisNode(column-2).childNodes().item(i)
                    
                    if attrName == paramNode.toElement().attribute("name", ""):
                        return str(self.constructData(paramNode))
                    
    def getData(self, index):
        '''
        Returns the value for parameter and sensibility analysis located at index.
        
        :param index: Cell's position in view/model.
        :type index: PyQt4.QtCore.QModelIndex()
        :return: ??
        '''
        # Why dataList.append("")?????? And empty loop???
        row = index.row()
        column = index.column() - 2
        attrName = self.params[row]
        currentAnalysisNode = self.getAnalysisNode(column)
        basePmtModel = BaseParametersModel()
        for i in range(0,currentAnalysisNode.childNodes().count()):
            paramNode = currentAnalysisNode.childNodes().item(i)
            if attrName == paramNode.toElement().attribute("name", ""):
                dataList = self.constructData(paramNode)
                numValues = basePmtModel.getRefNumValues(attrName) - len(dataList)
                for i in range(numValues):
                    dataList.append("")
                
                return dataList
        #No paramNode found, might be a vector item:
        if self.getDataType(index) == "Vector":
            dataList = ["" for i in range(basePmtModel.getRefNumValues(attrName))]
            return dataList
     
    def getDataType(self, index):
        '''
        Returns a container type for parameter (vector, scalar).
        
        :param index: Cell's position in view/model.
        :type index: PyQt4.QtCore.QModelIndex()
        :return: String. Returns :meth:`.BaseParametersModel.getContainerType`.
        '''
        attrName = self.params[index.row()]
        basePmtModel = BaseParametersModel()
        return basePmtModel.getContainerType(attrName)
    
    def constructData(self, node):
        '''
        Returns value list or scalar depending  of the data type.
        
        :param node: Parameter xML node in sensibility analysis.
        :type node: PyQt4.QtXml.QDomNode
        :return: String list | String.
        '''
        if node.firstChild().nodeName() == "Vector":
            valueList = []
            for i in range(node.firstChild().childNodes().count()):
                valueList.append(node.firstChild().childNodes().item(i).toElement().attribute("value"))
            return valueList
        
        return node.firstChildElement().attribute("value")

    def setData(self, index, value, tableIndex=0):
        ''' 
        Reimplemented from QAbstractTableModel.setData(self, index, value, role=QtCore.Qt.EditRole).
        Sets data for role at position "index" in model. Modifies model and its underlying data structure.
        
        :param index: Cell's position in model/table.
        :param value: New Value.
        :param tableIndex : Optional - If vector, index in vector.
        :type index: PyQt4.QtCore.QModelIndex()
        :type value: String
        :type tableIndex: Int
        '''
        currentAnalysisNode = self.getAnalysisNode(index.column()-2)
        attrName = self.params[index.row()]
        for i in range(currentAnalysisNode.childNodes().count()):
            paramNode = currentAnalysisNode.childNodes().item(i)
            if attrName == paramNode.toElement().attribute("name", ""):
                if self.getDataType(index) == "Vector":
                    paramNode.firstChildElement().childNodes().item(tableIndex).toElement().setAttribute("value", value)
                else:
                    paramNode.firstChildElement().setAttribute("value", value)
                self.checkForEmptyValues(paramNode)
                self.topWObject.dirty = True
                return
            
        #if we get there than the analysis doesn't have this variable yet
        newVariableNode = currentAnalysisNode.ownerDocument().createElement("Variable")
        newVariableNode.setAttribute("name", attrName)
        if self.getDataType(index) == "Vector":
            newVectorNode =  currentAnalysisNode.ownerDocument().createElement("Vector")
            basePmtModel = BaseParametersModel()
            numChildNode = basePmtModel.getRefNumValues(attrName)
            for i in range(numChildNode):
                newValueNode = currentAnalysisNode.ownerDocument().createElement(basePmtModel.refVars[attrName]["type"])
                newVectorNode.appendChild(newValueNode)
            newVariableNode.appendChild(newVectorNode)
            currentAnalysisNode.appendChild(newVariableNode)
            self.setData(index,value,tableIndex)
            self.topWObject.dirty = True
        else:
            basePmtModel = BaseParametersModel()
            newValueNode = currentAnalysisNode.ownerDocument().createElement(basePmtModel.refVars[attrName]["type"])
            newVariableNode.appendChild(newValueNode)
            currentAnalysisNode.appendChild(newVariableNode)
            self.setData(index,value)
            self.topWObject.dirty = True
        
    def checkForEmptyValues(self, varNode):
        '''
        Since The user can put empty strings in the delegate editor's to tell the system a variable isn't used any longer in 
        a sensibility analysis,  we have to clean up the dom.
        
        :param varNode: Node to be cleaned up.
        :type varNode: PyQt4.QtXml.QDomNode
        '''
        if varNode.firstChild().nodeName () == "Vector":
            currentValueNode = varNode.firstChildElement().firstChildElement()
            while not currentValueNode.isNull():
                if currentValueNode.attribute("value", ""):
                    return
                else:
                    currentValueNode = currentValueNode.nextSiblingElement()
            #If we get here, than all nodes are empty
            varNode.parentNode().removeChild(varNode)
            
        else:
            currentValueNode = varNode.firstChildElement()
            if currentValueNode.attribute("value", ""):
                return
            #If we get here, than node is empty
            varNode.parentNode().removeChild(varNode)
                    
    def headerData(self, section, orientation, role):
        ''' 
        Reimplemented from QAbstractTableModel.headerData(self, section, orientation, role).
        See QAbstractTableModel's documentation for more details.
        
        :param section: Model's column or row.
        :param orientation: Horizontal or vertical.
        :param role: Qt item role.
        :type section: Int
        :type orientation: Qt.orientation
        :type role: Int
        :return: String
        '''
        
        if role != QtCore.Qt.DisplayRole:
            return None
        
        if orientation == QtCore.Qt.Horizontal and section < len(self.headers):
            return self.headers[section]
    
    def setHeaderData(self, section, orientation, value="", role=QtCore.Qt.EditRole):
        ''' 
        Reimplemented from QAbstractTableModel.setHeaderData(self, section, orientation,value = QtCore.QVariant(), role).
        Changes the name of a sensibility analysis, hence its associated table header.
        
        :param section: Model's column or row.
        :param orientation: Horizontal or vertical.
        :param value: Optional - New header's value.
        :param role: Optional - Qt item role.
        :type section: Int
        :type orientation: Qt.orientation
        :type value: String
        :type role: Int
        :return: Boolean.
        '''
        if role != QtCore.Qt.EditRole:
            return False
        if orientation != QtCore.Qt.Horizontal:
            return False
        if section > self.columnCount():
            return False
        self.getAnalysisNode(section-2).toElement().setAttribute("name", value)
        return True
    
    def insertRow(self, row, paramName, parent=QtCore.QModelIndex()):
        ''' 
        Reimplemented from QAbstractTableModel.insertRow(self, row, parent=QtCore.QModelIndex()).
        See QAbstractTableModel's documentation for more details.
        Inserts a parameters in the model/table.
        
        :param row: Insertion row in model/table.
        :param paramName: Name of the parameter.
        :param parent: Optional - Parent's index(not really relevant for list views).
        :type row: Int
        :type paramName: String
        :type parent: PyQt4.QtCore.QModelIndex()
        :return: Boolean.
        '''
        self.beginInsertRows(parent, row, row)
        self.params.append(paramName)
        self.endInsertRows()
        return True
        
    def flags(self, index):
        ''' 
        Reimplemented from QAbstractTableModel.flags(self, index).
        See QAbstractTableModel's documentation for more details.
        
        :param index: Cell's index in model/table.
        :type index: PyQt4.QtCore.QModelIndex()
        :return: Int.
        '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        return QtCore.Qt.ItemFlags(QtCore.QAbstractItemModel.flags(self, index) | QtCore.Qt.ItemIsEditable )
        
