"""
.. module:: ParametersModel

.. codeauthor:: Mathieu Gagnon <mathieu.gagnon.10@ulaval.ca>

:Created on: 2010-08-11

"""
from PyQt4 import QtCore
from model.BaseParametersModel import BaseParametersModel
import Definitions

class ParametersModel(QtCore.QAbstractTableModel):
    '''
    Model handling reference parameters listing.
    '''

    def __init__(self, domNode, windowObject=None, parent=None):
        '''
        Constructor.
        
        :param baseModel: Base model contains the data.
        :param windowObject: Application's main window.
        :param parent: Model's view.
        '''
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.baseModel = BaseParametersModel(windowObject,domNode)
        self.headers = ["Name", "Type", "Value", "Curr. used"]
    
    def columnCount(self, parent=QtCore.QModelIndex()):
        '''' 
        Reimplemented from QAbstractTableModel.columnCount(self, parent).
        Column count is fixed to 4 (Name, Type, Value and Curr. used).
        
        :param parent:
        :type parent: Not used
        :return: Int. Always 4.
        '''
        return 4
    
    def rowCount(self, parent=QtCore.QModelIndex()):
        ''' 
        Reimplemented from QAbstractTableModel.rowCount(self, parent).
        How many reference parameters do we have.
        
        :param parent:
        :type parent: Not used
        :return: Int. Returns :meth:`.BaseParametersModel.howManyRefVars`.
        '''
        return self.baseModel.howManyRefVars()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' 
        Reimplemented from QAbstractTableModel.data(self, index, role=QtCore.Qt.DisplayRole).
        Returns data for role at position "index" in model. Controls what is going to be displayed in the table view.
        
        :param index: Cell's index in model/table.
        :param role: Optional - Qt item role.
        :type index: PyQt4.QtCore.QModelIndex()
        :type role: Int
        :return: String | Int.
        '''
        if not index.isValid() or index.row() >= self.baseModel.howManyRefVars() or index.column() >= self.columnCount(None):
            return None
        
        column = index.column()
        varName = self.baseModel.modelMapper[index.row()]
                
        if role == QtCore.Qt.CheckStateRole:
            if column == 3:
                #Indicate if parameter is currently found in dom
                if self.baseModel.isRefUsed(varName):
                    return QtCore.Qt.Checked
                return QtCore.Qt.Unchecked
        
        elif role == QtCore.Qt.DisplayRole:
            if column == 0:
                # Reference's name
                return self.baseModel.getTruncatedRefNameFromIndex(index.row())
            
            elif column == 1:
                # Reference's type
                vector = " list" if self.baseModel.getContainerType(varName) == "Vector" else ""
                return Definitions.typesToDefinitions[self.baseModel.refVars[varName]["type"]] + vector
            
            elif column == 2:
                #Reference's values
                value = self.baseModel.getValue(varName)
                if self.baseModel.getContainerType(varName) == "Scalar":
                    return str(value[0])
                else:
                    return str(value)


    def sort(self, column, sortingOrder=QtCore.Qt.AscendingOrder):
        '''
        Reimplemented from QAbstractTableModel.sort(column, order=Qt::AscendingOrder).
        Sorts the model.
        
        :param column:
        :param sortingOrder: Optional - AscendingOrder or DescendingOrder.
        :type column: Not used
        '''
        reversedOrder = True if sortingOrder == QtCore.Qt.AscendingOrder else False
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self.baseModel.modelMapper.sort(key=str.lower, reverse=reversedOrder)
        self.emit(QtCore.SIGNAL("layoutChanged()"))
        
    def headerData(self, section, orientation, role):
        ''' 
        Reimplemented from QAbstractTableModel.headerData(self, section, orientation, role).
        See QAbstractTableModel's documentation for more details.
        
        :param section: Model's column or row.
        :param orientation: Horizontal or vertical.
        :param role: Qt item role.
        :type section: Int
        :type orientation: QtCore.Qt.orientation
        :type role: Int
        :return: String. Returns rows and columns title.
        '''
        if role != QtCore.Qt.DisplayRole:
            return None
        
        if orientation == QtCore.Qt.Horizontal:
            return self.headers[section]
        else:
            return str(section + 1)
    
    def flags(self, index):
        ''' 
        Reimplemented from QAbstractTableModel.flags(self, index).
        See QAbstractTableModel's documentation for more details.
        
        :param index: Cell's index in model/table.
        :type index: PyQt4.QtCore.QModelIndex()
        :return: Int
        '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        if index.column() == 3:
            #Column contains only a checkbox
            return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index))
            
        return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index)  | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled)
    
    def supportedDropActions(self):
        ''' 
        Reimplemented from QAbstractTableModel.supportedDropActions(self).
        See QAbstractTableModel's documentation for more details.
        This function and her sister function (supportedDragActions) allow the user to drag and drop rows in the model.
        This way, user can move variables in the table to group linked variables, to sort them, etc...
        
        :return: Qt.DropActions
        '''
        return QtCore.Qt.DropActions(QtCore.Qt.MoveAction | QtCore.Qt.CopyAction)
        
    def supportedDragActions(self):
        ''' 
        Reimplemented from QAbstractTableModel.supportedDragActions(self).
        See QAbstractTableModel's documentation for more details.
        
        :return: Qt.DropActions
        '''
        return QtCore.Qt.DropActions(QtCore.Qt.MoveAction)
    
    def insertRow(self, rowafter, parent=QtCore.QModelIndex(), varName="New_variable", value=[0], varType="Double"):
        ''' 
        Reimplemented from QAbstractTableModel.insertRow(self, row, parent=QtCore.QModelIndex()).
        See QAbstractTableModel's documentation for more details.
        Inserts a reference in the model/table.
        
        :param rowafter: Insertion row in model/table.
        :param parent: Parent's index(not really relevant for list views).
        :param varName: Name of the reference.
        :param value: Initial value.
        :param varType: Initial type.
        :type rowafter: Int
        :type parent: PyQt4.QtCore.QModelIndex()
        :type varName: String
        :type value: String
        :type varType: String
        '''
        self.beginInsertRows(parent, rowafter, rowafter)
        self.baseModel.addRef("ref." + varName, varType, value, rowafter + 1)
        self.endInsertRows()
      
    def removeRow(self, row, parent=QtCore.QModelIndex()):
        ''' 
        Reimplemented from QAbstractTableModel.removeRow(self, row , parent=QtCore.QModelIndex()).
        See QAbstractTableModel's documentation for more details.
        Removes a row from the model/table.
        
        :param row: Row of the deleted index.
        :param parent: parent's index (not relevant for QtableView).
        :type row: Int
        :type parent: PyQt4.QtCore.QModelIndex()
        '''
        self.beginRemoveRows(parent, row, row)
        self.baseModel.removeRef(self.baseModel.modelMapper[row])
        self.endRemoveRows()     
    
    def specialRemove(self,rows,parent=QtCore.QModelIndex()):
        ''' 
        Remove function to delete multiple (possibly non-contiguous) elements in list.
        Removes rows from the model/table with rows of deleted indexes.
        
        :param rows: Rows of the deleted indexes.
        :type rows: Int list
        '''
        refToDelete = [self.baseModel.modelMapper[i] for i in rows]
        for referenceToDelete in refToDelete:
            deletedRefRow = self.baseModel.refVars.keys().index(referenceToDelete)
            self.beginRemoveRows(parent,deletedRefRow,deletedRefRow)
            self.baseModel.removeRef(referenceToDelete)
            self.endRemoveRows()
            
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        ''' 
        Reimplemented from QAbstractTableModel.setData(self, index, value, role=QtCore.Qt.EditRole).
        Sets data for role at position "index" in model. Modifies model and its underlying data structure.
        
        :param index: Cell's position in model/table.
        :param value: New Value.
        :param role: Optional - Qt item role.
        :type index: PyQt4.QtCore.QModelIndex()
        :type value: String
        :type role: Int
        :return: Boolean. True = data set correctly.
        '''
        if index.isValid() and role == QtCore.Qt.EditRole:
            if index.column() == 0:
                if self.baseModel.referenceExists(value):
                    print("Cannot set variable's name, " + value + " already exists.")
                    return False
                else:
                    self.baseModel.modifyName(index.row(), value)
                    return True
            elif index.column() == 1:
                self.baseModel.setRefType(index.row(), value)
                return True
            elif index.column() == 2:
                if self.baseModel.getContainerType(self.baseModel.modelMapper[index.row()]) == "Scalar":
                    #If it works, value is scalar
                    self.baseModel.modifyValue(self.baseModel.modelMapper[index.row()], value)
                else:
                    #Vector case
                    self.baseModel.modifyValue(self.baseModel.modelMapper[index.row()], value)
                
                return True

    def dropMimeData(self, data, action, row, column, parentIndex):
        ''' 
        Reimplemented from QAbstractTableModel.dropMimeData(self, data, action, row, column, parentIndex).
        See QAbstractTableModel's documentation for more details.
        Decodes the mimeData dropped when a user performs a drag and drop and modifies model accordingly.
        
        :param data: MimeData, qt's class associated with drag and drop operations.
        :param action: Move or Copy Action (Only move action are allowed in project).
        :param row: Row where the mimeData was dropped.
        :param column: Column where the mimeData was dropped.
        :param parentIndex: Parent's index(not really relevant for table views).
        :type data: QMimeData
        :type action: Qt.DropAction
        :type row: Int
        :type column: Int
        :type parentIndex: PyQt4.QtCore.QModelIndex
        :return: Boolean. 
        '''
        if action == QtCore.Qt.MoveAction:
            if data.hasFormat('application/x-qabstractitemmodeldatalist'):
                byteArray = data.data('application/x-qabstractitemmodeldatalist')
                draggedObjectRow = self.decode_data(byteArray)
                if row == -1:
                    row = parentIndex.row()
                mappingDict = self.baseModel.modelMapper
                mappingDict.insert(row,mappingDict.pop(draggedObjectRow))
            return True
    
    def decode_data(self, byteArray):
        '''
        Qt's mimeData.data('application/x-qabstractitemmodeldatalist') provides a QByteArray which contains
        all the information required when a QAbstractItemView performs a Drag and Drop operation.
        First 4 Bytes are : dragged object's original row number.
        Next 4 Bytes are : dragged object's original column number.
        That's all we need for the moment.
        
        :param byteArray: Byte array containing the original row and column number of the dragged object.
        :type byteArray: QByteArray
        :return: Int
        '''
        DanDInfo = QtCore.QDataStream(byteArray)
        
        return DanDInfo.readInt32()
        
