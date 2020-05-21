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

from PyQt4 import QtCore
from model.BaseParametersModel import BaseParametersModel

class ParametersModel(QtCore.QAbstractTableModel):
    '''
    Model handling reference parameters listing
    '''

    def __init__(self,  domNode , windowObject=None, parent=None):
        '''
        @summary Constructor
        @param baseModel : base model contains the data
        @param windowObject : application's main window
        @param parent : model's view
        '''
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.baseModel = BaseParametersModel(windowObject,domNode)
        
    def getBaseModel(self):
        '''
        @summary Return base model
        '''
        return self.baseModel
    
    def columnCount(self, parent=QtCore.QModelIndex()):
        '''' 
        @summary : Reimplemented from QAbstractTableModel.columnCount(self,parent)
        Column count is fixed to 3(name,type and value)
        @param parent : not used
        '''
        return 5
    
    def rowCount(self, parent=QtCore.QModelIndex()):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.rowCount(self,parent)
        How many reference parameters do we have
        @param parent : not used
        '''
        return self.baseModel.howManyRefVars()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.data(self, index, role=QtCore.Qt.DisplayRole)
        Return data for role at position index in model. Controls what is going to be displayed in the table view.
        @param index : cell's index in model/table
        @param role : Qt item role
        '''
        if not index.isValid() or index.row() >= self.baseModel.howManyRefVars():
            return QtCore.QVariant()
        
        column = index.column()
        varName = self.baseModel.getRefNameFromIndex(index.row())
                
        if role == QtCore.Qt.CheckStateRole:
            if column == 3:
                #Indicate if parameter is currently found in dom
                if self.baseModel.isRefUsed(varName):
                    return QtCore.QVariant(QtCore.Qt.Checked)
                return QtCore.QVariant(QtCore.Qt.Unchecked)
            else:
                return QtCore.QVariant()                #Discard unwanted checkboxes
        
        if role == QtCore.Qt.ToolTipRole:
            return QtCore.QVariant()
        
        if role == QtCore.Qt.DisplayRole:
            if column == 0:
                # Reference's name
                return QtCore.QVariant(self.baseModel.getTruncatedRefNameFromIndex(index.row()))
            
            elif column == 1:
                # Reference's type
                type = self.baseModel.getRefType(varName)
                return QtCore.QVariant(QtCore.QString(type))
            
            elif column == 2:
                #Reference's values
                value = self.baseModel.getValue(varName)
                if self.baseModel.getContainerType(varName) == "Scalar":
                    return  QtCore.QVariant(QtCore.QString(str(value[0])))
                else:
                    return  QtCore.QVariant(QtCore.QString(str(value)))
            # diep 24-3-2020 show Location
            elif column == 4:
                return QtCore.QVariant(QtCore.QString(self.baseModel.isRefLoc(varName)))

            return QtCore.QVariant()


    def sort(self,column,sortingOrder = QtCore.Qt.AscendingOrder):
        '''
        @summary Reimplemented from QAbstractTableModel.sort(column, order = Qt::AscendingOrder )
        Sort model
        @param column, column where the sort action was queried
        @param sortingOrder : AscendingOrder or DescendingOrder
        '''
        if sortingOrder == QtCore.Qt.AscendingOrder:
            reversedOrder=True
        else:
            reversedOrder = False 
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self.baseModel.modelMapper.sort(key=str.lower,reverse=reversedOrder)
        self.emit(QtCore.SIGNAL("layoutChanged()"))
        
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
                return QtCore.QVariant("Value")
            elif section == 3:
                return QtCore.QVariant("Curr. used")
            #diep 24-3-2020 show Loc
            elif section == 4:
                return QtCore.QVariant("Used in Process")
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
        if index.column() == 3:
            #Column contains only a checkbox
            return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index))
            
        return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index)  | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled)
    
    def supportedDropActions(self):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.supportedDropActions(self)
        See QAbstractTableModel's documentation for mode details
        This function and her sister function(supportedDragActions) allows the user to drag and drop rows in the model
        This way, user can move variables in the table to group linked variables, to sort them, etc...
        '''
        return QtCore.Qt.DropActions(QtCore.Qt.MoveAction | QtCore.Qt.CopyAction)
        
    def supportedDragActions(self):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.supportedDragActions(self)
        See QAbstractTableModel's documentation for mode details
        '''
        return QtCore.Qt.DropActions(QtCore.Qt.MoveAction)
    
    def insertRow(self, rowafter, parent=QtCore.QModelIndex(),name = "New_variable", value = [0], type="Double"):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.insertRow(self, row, parent=QtCore.QModelIndex())
        See QAbstractTableModel's documentation for mode details
        Inserts a reference in the model/table
        @param rowafter : insertion row in model/table
        @pram parent : parent's index(not really relevant for list views)
        @param name : name of the reference
        @param value : initial value
        @param type : initial type
        '''
        self.beginInsertRows(parent, rowafter, rowafter)
        self.baseModel.addRef("ref."+name, type, value, rowafter+1)
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
        self.baseModel.removeRef(self.baseModel.getRefNameFromIndex(row))
        self.endRemoveRows()     
    
    def specialRemove(self,rows,parent=QtCore.QModelIndex()):
        ''' 
        @summary : Remove function to delete multiple(possibly non-contiguous) elements in list
        Remove rows from the model/table with rows of deleted indexes
        @param rows : rows of  the deleted indexes
        '''
        refToDelete = [self.baseModel.getRefNameFromIndex(i) for i in rows]
        for referenceToDelete in refToDelete:
            deletedRefRow = self.baseModel.getRefList().index(referenceToDelete)
            self.beginRemoveRows(parent,deletedRefRow,deletedRefRow)
            self.baseModel.removeRef(referenceToDelete)
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
                if self.baseModel.referenceExists(value.toString()):
                    print("Cannot set variable's name, " + str(value.toString()) + " already exists.")
                    return False
                else:
                    self.baseModel.modifyName(index.row(),value.toString())
                    return True
            elif index.column() == 1:
                self.baseModel.setRefType(index.row(),value.toString())
                return True
            elif index.column() == 2:
                if self.baseModel.getContainerType(self.baseModel.getRefNameFromIndex(index.row())) == "Scalar":
                    #If it works, value is scalar
                    self.baseModel.modifyValue(self.baseModel.getRefNameFromIndex(index.row()),value.toString())
                else:
                    #Vector case
                    self.baseModel.modifyValue(self.baseModel.getRefNameFromIndex(index.row()),value.toStringList())
            else:
                return False

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
        
