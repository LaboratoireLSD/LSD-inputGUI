"""
.. module:: envModel

.. codeauthor:: Mathieu Gagnon <mathieu.gagnon.10@ulaval.ca>

:Created on: 2010-04-23

"""
from PyQt4 import QtCore
from PyQt4.QtGui import QColor
from model.baseEnvModel import BaseEnvModel
import Definitions

class EnvModel(QtCore.QAbstractTableModel):
    '''
    Model handling population variables display
    '''
    def __init__(self, rootNode, parent=None):
        '''
        Constructor.
        
        :param rootNode: Environment xml node.
        :param parent: Model's view.
        :type rootNode: PyQt4.QtXml.QDomElement
        :type parent: QObject
        '''
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.baseModel = BaseEnvModel(parent,rootNode.firstChild())
        
    def columnCount(self, parent=QtCore.QModelIndex()):
        ''' 
        Reimplemented from QAbstractTableModel.columnCount(self, parent).
        Column count is fixed to 3 (name, type and value).
        Always returns 3.
        
        :param parent:
        :type parent: Not used
        :return: Int. Always 3.
        '''
        return 3
    
    def rowCount(self, parent=QtCore.QModelIndex()):
        ''' 
        Reimplemented from QAbstractTableModel.rowCount(self, parent).
        How many variables do we have in the "environment" tab.
        
        :param parent:
        :type parent: Not used
        :return: Int. Total number of environment variables
        '''
        return self.baseModel.howManyVars()
    
    def getVarLists(self):
        ''' 
        Returns variables name list.
        
        :return: PyQt4.QtXml.QDomElement.
        '''
        return self.baseModel.modelMapper
    
    def variableExists(self, varName):
        ''' 
        Tells if variable exists in variable list.
        
        :param varName: Variable's name.
        :type varName: String
        :return: Boolean. True = Variable exists.
        '''
        return self.baseModel.variableExists(varName)
    
    def getVarType(self, varName):
        ''' 
        Returns a variable's type.
        
        :param varName: Variable's name.
        :type varName: String
        :return: String. Type of the variable as string.
        '''
        return self.baseModel.getVarType(varName)
        
    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' 
        Reimplemented from QAbstractTableModel.data(self, index, role=QtCore.Qt.DisplayRole).
        Returns data for role at position "index" in model. Controls what is going to be displayed in the table view.
        
        :param index: Cell's index in model/table.
        :param role: Optional - Qt item role.
        :type index: QModelIndex
        :type role: Int.
        :return: QColor | String
        '''
        if not index.isValid() or index.row() >= self.rowCount():
            return None
        
        varName = self.baseModel.getVarNameFromIndex(index)
        
        if role == QtCore.Qt.TextColorRole:
                return QColor(0, 0, 0)
        elif role == QtCore.Qt.BackgroundColorRole:
            return QColor(255, 255, 255)
        
        if role == QtCore.Qt.DisplayRole and index.row() <= self.columnCount(None):
            #Returns a variable information. 
            #Column 1 = its name, column 2 = its type and column 3 = its value. All string
            return [varName, Definitions.typeToDefinition(self.baseModel.getVarType(varName)), self.baseModel.getVarValue(varName)][index.column()]

    def headerData(self, section, orientation, role):
        ''' 
        Reimplemented from QAbstractTableModel.headerData(self, section, orientation, role).
        See QAbstractTableModel's documentation for more details.
        
        :param section: Model's column or row.
        :param orientation: Horizontal or vertical.
        :param role: Qt item role.
        :type section: Int.
        :type orientation: Qt.orientation
        :type role: Int.
        :return: String. Name of the header if orientation is horizontal. Number of row as string otherwise.
        '''
        if role != QtCore.Qt.DisplayRole:
            return None
        
        if orientation == QtCore.Qt.Horizontal:
            return ["Name", "Type", "Value"][section]
        else:
            #Return
            return str(section + 1)
    
    def flags(self, index):
        ''' 
        Reimplemented from QAbstractTableModel.flags(self, index).
        See QAbstractTableModel's documentation for more details.
        
        :param index: Cell's index in model/table.
        :return: Int.
        '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index) | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled)

    def insertRow(self, rowafter, parent=QtCore.QModelIndex()):
        ''' 
        Reimplemented from QAbstractTableModel.insertRow(self, row, parent=QtCore.QModelIndex()).
        See QAbstractTableModel's documentation for more details.
        Inserts a row in the model/table.
        
        :param rowafter: Insert row in model/table.
        :param parent: Parent's index(not really relevant for table views).
        :type rowafter: Int
        :type parent: QModelIndex
        '''
        self.beginInsertRows(parent, rowafter, rowafter)
        self.baseModel.addVar("New_variable", "Unknown", rowafter)
        self.endInsertRows()
            
    def removeRow(self, index, rowToDelete):
        ''' 
        Reimplemented from QAbstractTableModel.removeRow(self, row , parent=QtCore.QModelIndex()).
        See QAbstractTableModel's documentation for more details.
        Removes a row from the model/table.
        
        :param index: Cell's position in model/table.
        :param rowToDelete: Row of the deleted index.
        :type index: PyQt4.QtCore.QModelIndex
        :type rowToDelete: Int
        '''
        self.beginRemoveRows(index, rowToDelete, rowToDelete)
        self.baseModel.removeVar(self.baseModel.modelMapper[rowToDelete])
        self.endRemoveRows()
        
    def specialRemove(self, rows, parent=QtCore.QModelIndex()):
        ''' 
        Remove function to delete multiple(possibly non-contiguous) elements in list.
        Removes rows from the model/table with rows of deleted indexes.
        
        :param rows: Rows of the selected indexes to delete.
        :type rows: Int list
        '''
        varToDelete = [self.getVarLists()[i] for i in rows]
        for variable in varToDelete:
            deletedVarRow = self.getVarLists().index(variable)
            self.beginRemoveRows(parent,deletedVarRow,deletedVarRow)
            self.baseModel.removeVar(self.baseModel.modelMapper[deletedVarRow])
            self.endRemoveRows()
            
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        ''' 
        Reimplemented from QAbstractTableModel.setData(self, index, value, role=QtCore.Qt.EditRole).
        Sets data for role at position index in model. Modify model and its underlying data structure.
        
        :param index: Cell's position in model/table.
        :param value: New Value.
        :param role: Optional - Qt item role.
        :type index: PyQt4.QtCore.QModelIndex
        :type value: String
        :type role: Int
        :return: Boolean. True = data has been set correctly.
        '''
        if not index.isValid() or role != QtCore.Qt.EditRole or index.column() > 2:
            return False
            
        if index.column() == 0:
            self.baseModel.renameVariable(self.baseModel.getVarNameFromIndex(index), value)
        elif index.column() == 1:
            self.baseModel.setVarType(self.baseModel.getVarNameFromIndex(index), value)
        elif index.column() == 2:
            self.baseModel.setVarValue(self.baseModel.getVarNameFromIndex(index), value)
            
        return True
                 
    def sort(self, column, sortingOrder = QtCore.Qt.AscendingOrder):
        '''
        Reimplemented from QAbstractTableModel.sort(column, order = Qt::AscendingOrder).
        Sorts the model.
        
        :param column: Column where the sort action was queried.
        :param sortingOrder: AscendingOrder or DescendingOrder.
        :type column: Not used
        :type sortingOrder: Int
        '''
        reversedOrder = True if sortingOrder == QtCore.Qt.AscendingOrder else False
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        
        self.baseModel.modelMapper.sort(key=str.lower,reverse=reversedOrder)
        self.emit(QtCore.SIGNAL("layoutChanged()"))
        
    def supportedDropActions(self):
        ''' 
        Reimplemented from QAbstractTableModel.supportedDropActions(self).
        See QAbstractTableModel's documentation for more details.
        This function and her sister function "supportedDragActions" allow the user to drag and drop rows in the model.
        This way, user can move variables in the table to group linked variables, to sort them, etc...
        
        :return: QFlags
        '''
        return QtCore.Qt.DropActions(QtCore.Qt.MoveAction)
        
    def supportedDragActions(self):
        ''' 
        Reimplemented from QAbstractTableModel.supportedDragActions(self).
        See QAbstractTableModel's documentation for more details.
        
        :return: QFlags
        '''
        return QtCore.Qt.DropActions(QtCore.Qt.MoveAction)
  
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
        # Only "Move" action is accepted
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
        
