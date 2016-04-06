'''
Created on 2010-08-23

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
from PyQt4 import QtCore
from PyQt4.QtGui import QColor
from PyQt4 import QtGui
from model.BaseParametersModel import BaseParametersModel
import copy

class SaComboBoxModel(QtCore.QAbstractItemModel):
    '''
    Model used to list Reference Parameters in a comboBox
    '''

    def __init__(self,paramModel,listModel,parent=None, mainWindow = None):
        '''
        @summary Constructor
        @param paramModel :  Parameters base model
        @param listModel : model listing sensibility analysis and parameters used in them
        @param parent : model's view
        @param mainWindow application's main window
        '''
        QtCore.QAbstractItemModel.__init__(self, parent)
        self.parent = parent
        self.listModel = listModel
        self.modelBase = paramModel
        self.topWObject = mainWindow
             
    def getParams(self):
        '''
        @summary Return all parameters that are not yet part of a sensibility analysis
        '''
        return sorted([param for param in self.modelBase.getBaseModel().getTruncatedRefList() if not self.listModel.exists(param)])
    
    def columnCount(self, parent=QtCore.QModelIndex()):
        '''
        @summary Reimplementation of QAbstactItemModel.columnCount(self,parent=QtCore.QModelIndex())
        Since this model underlies a comboBox, column count is fixed to 1
        Even if it is implicit that column count is going to be one since we apply this model to a combo box,
        Qt complains if it is not overridden
        '''
        return 1
    
    def parent(self, index):
        '''
        @summary Reimplementation of QAbstactItemModel.parent(self,index)
        Return index's parent
        Since this model underlies a comboBox, model items do not really have a parent, so returning and invalid index is ok
        Qt complains if it is not overridden
        '''
        return QtCore.QModelIndex() 
    
    def rowCount(self, parent=QtCore.QModelIndex()):
        ''' 
        @summary : Reimplemented from QAbstractItemModel.rowCount(self,parent)
        How many unused parameters do we have
        @param parent : not used
        '''
        return len(self.getParams())
        
    
    def index(self, row, column, parent = QtCore.QModelIndex()) :
        '''
        @summary : Reimplemented from QAbstractItemModel.index(self, row, column, parent = QtCore.QModelIndex())
        Create a model index if there is data at this position in de model
        @param row,column : position in the model
        @param parent : not used
        '''
        if row >= self.rowCount() or column != 0:
            return QtCore.QModelIndex()  
        else:
            return self.createIndex(row, column)
        
    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' 
        @summary : Reimplemented from QAbstracItemModel.data(self, index, role=QtCore.Qt.DisplayRole)
        Return data for role at position index in model. Controls what is going to be displayed in the table view.
        @param index : cell's index in model/table
        @param role : Qt item role
        ''' 
        if not index.isValid():
            return None
        
        row = index.row()
        
        if role == QtCore.Qt.CheckStateRole:
            return None                # Discard Unwanted checkBoxes
        
        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                #print()
                return self.getParams()[row]
        return None

    def addParam(self,paramNum):
        '''
        @summary Take a parameter from model and move it in the sensibility analysis model
        @param paramNum : position of the parameter to switch in the combobox
        '''
        self.beginRemoveRows(QtCore.QModelIndex(),paramNum,paramNum)
        self.listModel.insertRow(self.listModel.rowCount(),"ref."+self.getParams()[paramNum])
        self.endRemoveRows()
       
    def flags(self, index):
        ''' 
        @summary : Reimplemented from QAbstractItemModel.flags(self,index)
        See QAbstractItemModel's documentation for mode details
        @param index : cell's index in model/table
        '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        return QtCore.Qt.ItemFlags(QtCore.QAbstractItemModel.flags(self, index) )

class SaTableModel(QtCore.QAbstractTableModel):
    '''
    Model used to list sensibility analysis in a tableView
    '''

    def __init__(self,domTree,parent=None, mainWindow = None):
        '''
        @summary Constructor
        @param domTree :  Sensibility analysis XML node
        @param parent : model's view
        @param mainWindow application's main window
        '''
        QtCore.QAbstractListModel.__init__(self, parent)
        self.dom = domTree
        self.analysis = self.getAnalysis()
        self.params = self.getParams()
        self.topWObject = mainWindow
        
    def getAnalysis(self):
        '''
        @summary Return a list containing all the sensibility analysis names
        '''
        listAnalysis = []
        for i in range(0,self.dom.childNodes().count()):
            listAnalysis.append(self.dom.childNodes().item(i).toElement().attribute("name"))
        return listAnalysis
    
    def getAnalysisNode(self, column):
        '''
        @summary return sensibility analysis located at column
        @param column : position of the sensibility analysis in model
        '''
        return self.dom.childNodes().item(column)
    
    def getParams(self):
        '''
        @summary Return all parameters that are found in at least one sensiblity analysis
        '''
        listParams = []
        for i in range(0,self.dom.childNodes().count()):
            currentAnalysis = self.dom.childNodes().item(i)
            for j in range(0,currentAnalysis.childNodes().count()):
                paramName = currentAnalysis.childNodes().item(j).toElement().attribute("name")
                if paramName not in listParams:
                    listParams.append(paramName)
        
        return listParams
         
    def exists(self, paramName):
        '''
        @summary Return if a parameter is found in used parameters list
        '''
        return "ref."+paramName in self.params
    
    def rowCount(self, parent=QtCore.QModelIndex()):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.rowCount(self,parent)
        How many used parameters do we have
        @param parent : not used
        '''
        return len(self.params)
    
    def columnCount(self,parent=QtCore.QModelIndex()):
        '''' 
        @summary : Reimplemented from QAbstractTableModel.columnCount(self,parent)
        How many analysis do we have+ parameters name column + parameters default value column
        @param parent : not used
        '''
        return self.dom.childNodes().count()+2
        
    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.data(self, index, role=QtCore.Qt.DisplayRole)
        Return data for role at position index in model. Controls what is going to be displayed in the table view.
        @param index : cell's index in model/table
        @param role : Qt item role
        ''' 
        if not index.isValid():
            return None

        row = index.row()
        column = index.column()
        if role == QtCore.Qt.CheckStateRole:
            return None                #Discard unwanted checkboxes
        if role == QtCore.Qt.BackgroundRole:
            if column == 0:
                return QColor(220, 220, 220)
        if role == QtCore.Qt.DisplayRole:
            if column == 0:
                refName = self.params[row][4:]
                return refName
            if column == 1:
                basePmtModel = BaseParametersModel()
                initialValue = basePmtModel.getValue(self.params[row])
                return str(initialValue)
            if column <= self.columnCount() and row <=self.rowCount():
                attrName = self.params[row]
                for i in range(0,self.getAnalysisNode(column-2).childNodes().count()):
                    paramNode = self.getAnalysisNode(column-2).childNodes().item(i)
                    
                    if attrName == paramNode.toElement().attribute("name", ""):
                        return str(self.constructData(paramNode))
                return None
                    
        return None

    def getData(self,index):
        '''
        @summary Return value for parameter and sensibility analysis located at index
        @param index : cell's position in view/model
        '''
        row = index.row()
        column = index.column()-2
        attrName = self.params[row]
        currentAnalysisNode = self.getAnalysisNode(column)
        basePmtModel = BaseParametersModel()
        for i in range(0,currentAnalysisNode.childNodes().count()):
            paramNode = currentAnalysisNode.childNodes().item(i)
            if attrName == paramNode.toElement().attribute("name", ""):
                dataList =  self.constructData(paramNode)
                numValues =  basePmtModel.getRefNumValues(attrName) - len(dataList)
                for i in range(0,numValues):
                    dataList.append("")
                
                return dataList
        #No paramNode found, might be a vector item:
        if self.getDataType(index)=="Vector":
            dataList = ["" for i in range(0,basePmtModel.getRefNumValues(attrName))]
            return dataList
        else:
            #Single Item return empty string
            return ""
     
    def getDataType(self,index):
        '''
        @summary Return container type for parameter (vector, scalar)
        @param index : cell's position in view/model
        '''
        attrName = self.params[index.row()]
        basePmtModel = BaseParametersModel()
        return basePmtModel.getContainerType(attrName)
    
    def constructData(self,node):
        '''
        @summary Return value list or scalar depending  of the data type
        @param node : parameter xML node in sensibility analysis
        '''
        if node.firstChild().nodeName() == "Vector":
            valueList = []
            for i in range(0,node.firstChild().childNodes().count()):
                valueList.append(node.firstChild().childNodes().item(i).toElement().attribute("value"))
            return valueList
        
        return node.firstChildElement().attribute("value")

    def setData(self, index, value, tableIndex=0):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.setData(self, index, value, role=QtCore.Qt.EditRole)
        Sets data for role at position index in model. Modify model and its underlying data structure
        @param index : cell's position in model/table
        @param value : new Value
        @param tableIndex : if vector, index in vector
        '''
        currentAnalysisNode = self.getAnalysisNode(index.column()-2)
        attrName = self.params[index.row()]
        for i in range(0,currentAnalysisNode.childNodes().count()):
            paramNode = currentAnalysisNode.childNodes().item(i)
            if attrName == paramNode.toElement().attribute("name", ""):
                if self.getDataType(index) == "Vector":
                    paramNode.firstChildElement().childNodes().item(tableIndex).toElement().setAttribute("value",value)
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
            for i in range(0,numChildNode):
                newValueNode = currentAnalysisNode.ownerDocument().createElement(basePmtModel.getRefType(attrName))
                newVectorNode.appendChild(newValueNode)
            newVariableNode.appendChild(newVectorNode)
            currentAnalysisNode.appendChild(newVariableNode)
            self.setData(index,value,tableIndex)
            self.topWObject.dirty = True
        else:
            basePmtModel = BaseParametersModel()
            newValueNode =  currentAnalysisNode.ownerDocument().createElement(basePmtModel.getRefType(attrName))
            newVariableNode.appendChild(newValueNode)
            currentAnalysisNode.appendChild(newVariableNode)
            self.setData(index,value)
            self.topWObject.dirty = True
        
    def checkForEmptyValues(self,varNode):
        '''
        @summary Since The user can put empty strings in the delegate editor's to tell the system a variable isn't used any longer in 
        a sensibility analysis,  We have to clean up the dom
        @param varNode: node to be cleaned up
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
        @summary : Reimplemented from QAbstractTableModel.headerData(self, section, orientation, role)
        See QAbstractTableModel's documentation for mode details
        @param section : model's column or row
        @param orientation : horizontal or vertical
        @param role : Qt item role
        '''
        
        if role != QtCore.Qt.DisplayRole:
            return None
        
        if orientation == QtCore.Qt.Horizontal:
            
         #   if section in range(2,self.dom.childNodes().count()+2):
         #       return QtCore.QVariant(self.dom.childNodes().item(section-2).toElement().attribute("name"))  
            if section == 0:
                return "Parameters"
            elif section == 1:
                return "Initial value(s)"
            elif section == 2:
                return "Law"
            elif section == 3:
                return "Lower limit"
            elif section == 4:
                return "Upper limit"
            elif section == 5:
                return "Std dev."
            elif section ==6:
                return "Mean (opt.)"
        return None
    
    def setHeaderData(self, section, orientation, value="", role=QtCore.Qt.EditRole):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.setHeaderData(self, section, orientation,value = QtCore.QVariant(), role)
        Change the name of a sensibility analysis, hence its associated table header
        @param section : model's column or row
        @param orientation : horizontal or vertical
        @param value : new header's value
        @param role : Qt item role
        '''
        if role != QtCore.Qt.EditRole:
            return False
        if orientation != QtCore.Qt.Horizontal:
            return False
        if section > self.columnCount():
            return False
        self.getAnalysisNode(section-2).toElement().setAttribute("name", value)
        return True
        
   # def insertColumn(self,column,parent=QtCore.QModelIndex()):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.insertColumn(self, column, parent=QtCore.QModelIndex())
        See QAbstractTableModel's documentation for mode details
        Inserts a sensibility analysis in the model/table
        @param column : insertion column in model/table
        @param parent : parent's index(not really relevant for list views)
        '''
    #    self.beginInsertColumns(parent,column,column)
     #   newAnalysis = self.dom.ownerDocument().createElement("Analysis")
      #  newAnalysis.setAttribute("name","")
     #   self.dom.appendChild(newAnalysis)
    #    self.endInsertColumns()
   #     self.topWObject.dirty = True
    #    return True
    
   # def removeColumn(self,column,parent=QtCore.QModelIndex()):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.removeColumn(self, column , parent=QtCore.QModelIndex())
        See QAbstractTableModel's documentation for mode details
        Removes a column from the model/table
        @param column : column of the deleted index
        @param parent : parent's index (not relevant for QtableView)
        '''
    #    self.beginRemoveColumns(parent,column,column)
     #   self.dom.removeChild(self.dom.childNodes().item(column-2))
      #  self.endRemoveColumns()
     #   self.topWObject.dirty = True
    #    return True
    
    def insertRow(self,row,paramName,parent=QtCore.QModelIndex()):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.insertRow(self, row, parent=QtCore.QModelIndex())
        See QAbstractTableModel's documentation for mode details
        Inserts a parameters in the model/table
        @param row : insertion row in model/table
        @param paramName : name of the parameter
        @param parent : parent's index(not really relevant for list views)
        '''
        self.beginInsertRows(parent,row,row)
        self.params.append(paramName)
        self.endInsertRows()
        return True
        
    def flags(self, index):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.flags(self,index)
        See QAbstractTableModel's documentation for mode details
        @param index : cell's index in model/table
        '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        return QtCore.Qt.ItemFlags(QtCore.QAbstractItemModel.flags(self, index) | QtCore.Qt.ItemIsEditable )
        
