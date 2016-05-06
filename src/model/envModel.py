'''
Created on 2010-04-23

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
from model.baseEnvModel import BaseEnvModel

class EnvModel(QtCore.QAbstractTableModel):
    '''
    Model handling population variables display
    '''
    def __init__(self, rootNode, parent=None):
        '''
        @summary Constructor
        @param rootNode : Environment xml node
        @param parent : model's view
        '''
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.baseModel = BaseEnvModel(parent,rootNode.firstChild())
        
    def columnCount(self, parent=QtCore.QModelIndex()):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.columnCount(self,parent)
        Column count is fixed to 3 (name, type and value)
        @param parent : not used
        '''
        return 3
    
    def rowCount(self, parent=QtCore.QModelIndex()):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.rowCount(self,parent)
        How many variables do we have
        @param parent : not used
        '''
        return self.baseModel.howManyVars()
    
    def getVarLists(self):
        ''' 
        @summary Return variables name list
        '''
        return self.baseModel.modelMapper
    
    def variableExists(self,varName):
        ''' 
        @summary Return if variable exists in variable list
        @param varName : variable's name
        '''
        return self.baseModel.variableExists(varName)
    
    def getVarType(self,varName):
        ''' 
        @summary Return variable's type
        @param varName : variable's name
        '''
        return self.baseModel.getVarType(varName)
        
    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.data(self, index, role=QtCore.Qt.DisplayRole)
        Return data for role at position index in model. Controls what is going to be displayed in the table view.
        @param index : cell's index in model/table
        @param role : Qt item role
        '''
        if not index.isValid() or index.row() >= self.rowCount():
            return None
        
        colonne = index.column()
        varName = self.baseModel.getVarNameFromIndex(index)
        
        if role == QtCore.Qt.TextColorRole:
                return QColor(0, 0, 0)
        elif role == QtCore.Qt.BackgroundColorRole:
            return QColor(255, 255, 255)
                
        elif role == QtCore.Qt.CheckStateRole:
            return None                # Discard unwanted checkboxes
        
        if role == QtCore.Qt.ToolTipRole:
            return None
        
        if role == QtCore.Qt.DisplayRole:
            if colonne == 0:
                # Variable Name
                return varName
            elif colonne == 1:
                # Type
                return self.baseModel.getVarType(varName)
            elif colonne == 2:
                # Value
                return self.baseModel.getVarValue(varName)

        return None

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
            if section == 0:
                return "Name"
            elif section == 1:
                return "Type"
            elif section == 2:
                return "Value"
            else:
                return None
        else:
            return str(section + 1)  
        
        return None
    
    def flags(self, index):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.flags(self,index)
        See QAbstractTableModel's documentation for mode details
        @param index : cell's index in model/table
        '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index) | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled)

    def insertRow(self, rowafter, parent=QtCore.QModelIndex()):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.insertRow(self, row, parent=QtCore.QModelIndex())
        See QAbstractTableModel's documentation for mode details
        Inserts a row in the model/table
        @param rowafter : insert row in model/table
        @param parent : parent's index(not really relevant for table views)
        '''
        self.beginInsertRows(parent, rowafter, rowafter)
        self.baseModel.addVar("New_variable", "Unknown", rowafter)
        self.endInsertRows()
        return
            
    def removeRow(self, index,rowToDelete):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.removeRow(self, row , parent=QtCore.QModelIndex())
        See QAbstractTableModel's documentation for mode details
        Removes a row from the model/table
        @param index : cell's position in model/table
        @param rowToDelete : row of the deleted index
        '''
        self.beginRemoveRows(index, rowToDelete, rowToDelete)
        self.baseModel.removeVar(self.baseModel.modelMapper[rowToDelete])
        self.endRemoveRows()
        
    def specialRemove(self,rows,parent=QtCore.QModelIndex()):
        ''' 
        @summary : Remove function to delete multiple(possibly non-contiguous) elements in list
        Remove rows from the model/table with rows of deleted indexes
        @param rows : rows of  the deleted indexes
        '''
        varToDelete = [self.getVarLists()[i] for i in rows]
        for variable in varToDelete:
            deletedVarRow = self.getVarLists().index(variable)
            self.beginRemoveRows(parent,deletedVarRow,deletedVarRow)
            self.baseModel.removeVar(self.baseModel.modelMapper[deletedVarRow])
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
                self.baseModel.renameVariable(self.baseModel.getVarNameFromIndex(index), value)
                return True
            elif index.column() == 1:
                self.baseModel.setVarType(self.baseModel.getVarNameFromIndex(index), value)
                return True
            elif index.column() == 2:
                self.baseModel.setVarValue(self.baseModel.getVarNameFromIndex(index), value)
                return True
            else:
                return False
        return False
                 
    def sort(self,column,sortingOrder = QtCore.Qt.AscendingOrder):
        '''
        @summary Reimplemented from QAbstractTableModel.sort(column, order = Qt::AscendingOrder )
        Sort model
        @param column : column where the sort action was queried
        @param sortingOrder : AscendingOrder or DescendingOrder
        '''
        if sortingOrder == QtCore.Qt.AscendingOrder:
            reversedOrder=True
        else:
            reversedOrder = False 
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        
        self.baseModel.modelMapper.sort(key=str.lower,reverse=reversedOrder)
        self.emit(QtCore.SIGNAL("layoutChanged()"))
        
    def supportedDropActions(self):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.supportedDropActions(self)
        See QAbstractTableModel's documentation for mode details
        This function and her sister function(supportedDragActions) allows the user to drag and drop rows in the model
        This way, user can move variables in the table to group linked variables, to sort them, etc...
        '''
        return QtCore.Qt.DropActions(QtCore.Qt.MoveAction)
        
    def supportedDragActions(self):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.supportedDragActions(self)
        See QAbstractTableModel's documentation for mode details
        '''
        return QtCore.Qt.DropActions(QtCore.Qt.MoveAction)
  
    def dropMimeData(self,data,action,row,column,parentIndex):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.dropMimeData(self,data,action,row,column,parentIndex)
        See QAbstractTableModel's documentation for mode details
        Decode the mimeData dropped when a user performs a drag and drop and modify model accordingly
        @param data : MimeData, qt's class associated with drag and drop operations
        @param action : Move or Copy Action(Only move action are allowed in project)
        @param row : row where the mimeData was dropped
        @param column : column where the mimeData was dropped
        @param parentIndex : parent's index(not really relevant for table views)
        '''
        if action == QtCore.Qt.MoveAction:
            if data.hasFormat('application/x-qabstractitemmodeldatalist'):
                bytearray = data.data('application/x-qabstractitemmodeldatalist')
                draggedObjectRow = self.decode_data(bytearray)
                if row == -1:
                    row = parentIndex.row()
                
                mappingDict = self.baseModel.modelMapper
                mappingDict.insert(row,mappingDict.pop(draggedObjectRow)) 
            return True
        else:
            return False
    
    def decode_data(self, bytearray):
        '''
        @summary Qt's mimeData.data('application/x-qabstractitemmodeldatalist') provides a QByteArray which contains
        all the information required when a QAbstractItemView performs a Drag and Drop operation
        First 4 Bytes are : dragged object's original row number
        Next 4 Bytes are : dragged object's original column number
        That's all we need for the moment
        '''
        
        DanDInfo = QtCore.QDataStream(bytearray)
        
        return DanDInfo.readInt32()
        
