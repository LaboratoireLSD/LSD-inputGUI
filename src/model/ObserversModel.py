"""
.. module:: ObserversModel

.. codeauthor:: Mathieu Gagnon <mathieu.gagnon.10@ulaval.ca>

:Created on: 2009-12-14

"""
from PyQt4 import QtCore, QtGui
        
class ListClockObserversModel(QtCore.QAbstractListModel):
    '''
    Model handling clock's observing processes.
    '''
    def __init__(self, rootNode, parent=None, mainWindow=None):
        '''
        Constructor.
        
        :param rootNode: ClockObservers XML Node.
        :param parent: Optional - Model's view.
        :param mainWindow: Optional - Main visual frame.
        '''
        QtCore.QAbstractListModel.__init__(self, parent)
        self.rootNode = rootNode
        self.topWObject = mainWindow

    def rowCount(self, parent=QtCore.QModelIndex()):
        ''' 
        Reimplemented from QAbstractListModel.rowCount(self, parent).
        How many processes observes clock.
        
        :param parent:
        :type parent: Not used
        :return: Int
        '''
        return self.rootNode.toElement().elementsByTagName("Observer").count()
    
    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' 
        Reimplemented from QAbstractListModel.data(self, index, role=QtCore.Qt.DisplayRole).
        Returns data for role at position "index" in model. Controls what is going to be displayed in the table view.
        
        :param index: Cell's index in model/table.
        :param role: Optional - Qt item role.
        :type index: PyQt4.QtCore.QModelIndex
        :type role: Int
        :return: String
        '''
        if role == QtCore.Qt.DisplayRole:
            return self.rootNode.toElement().elementsByTagName("Observer").item(index.row()).toElement().attribute("process")
    
    def getCurrentObserverNode(self, index):
        '''
        Returns node of the observer associated with index.
        
        :param index: Cell's position in model/index.
        :type index: PyQt4.QtCore.QModelIndex
        :return: PyQt4.QtXml.QDomNode
        '''
        return self.rootNode.childNodes().item(index.row())
            
    def removeProcess(self, index):
        '''
        Removes a process from the model's observing processes list.
        
        :param index: Location in list of the process we want to remove.
        :type index: PyQt4.QtCore.QModelIndex
        '''
        self.beginRemoveRows(index.parent(), index.row(), index.row())
        self.rootNode.removeChild(self.rootNode.childNodes().item(index.row()))
        self.endRemoveRows()
        self.topWObject.dirty = True
    
    def specialRemove(self, indexes):
        ''' 
        Remove function to delete multiple (possibly non-contiguous) elements in list.
        Removes rows from the model/table with rows of deleted indexes.
        
        :param indexes: Rows of the deleted indexes.
        :type indexes: PyQt4.QtCore.QModelIndex list
        '''
        observersToDelete = [self.rootNode.childNodes().item(index.row()) for index in indexes]
        for deletedObserver in observersToDelete:
            for i in range(self.rootNode.childNodes().count()):
                if deletedObserver == self.rootNode.childNodes().item(i):
                    break
            self.beginRemoveRows(QtCore.QModelIndex(), i, i)
            self.rootNode.removeChild(deletedObserver)
            self.endRemoveRows()
        
        self.topWObject.dirty = True
            
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        ''' 
        Reimplemented from QAbstractListModel.setData(self, index, value, role=QtCore.Qt.EditRole).
        Sets data for role at position index in model. Modifies model and its underlying data structure.
        
        :param index: Cell's position in model/table.
        :param value: New Value.
        :param role: Qt item role.
        :type index: PyQt4.QtCore.QModelIndex
        :type value: String
        :type role: Int
        :return: Boolean. True = Data has been set correctly.
        '''
        if index.isValid() and role == QtCore.Qt.EditRole:
            self.rootNode.childNodes().item(index.row()).toElement().setAttribute("process",value)
            self.topWObject.dirty = True
            return True
        return False
    
    def addObserver(self, row):
        '''
        Adds a process to the model's observing processes list.
        
        :param row: Before which row the new observer is added.
        :type row: Int
        '''
        self.beginInsertRows(QtCore.QModelIndex(), row, row)
        newObserver = self.rootNode.ownerDocument().createElement("Observer")
        newObserver.setAttribute("process", "")
        #Set attribute default values
        newObserver.setAttribute("target", "individuals")
        newObserver.setAttribute("units", "other")
        newObserver.setAttribute("start", "1")
        newObserver.setAttribute("step", "1")
        newObserver.setAttribute("end", "0")
        #Insert Observer in dom
        self.rootNode.insertAfter(newObserver, self.rootNode.childNodes().item(row))
        self.topWObject.dirty = True
        self.endInsertRows()
        
    def flags(self, index):
        ''' 
        Reimplemented from QAbstractListModel.flags(self, index).
        See QAbstractListModel's documentation for mode details.
        
        :param index: Cell's index in model/table.
        :type index: PyQt4.QtCore.QModelIndex.
        :return: Int
        '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        return QtCore.Qt.ItemFlags(QtCore.QAbstractListModel.flags(self, index) | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled)
    
    def supportedDropActions(self):
        ''' 
        Reimplemented from QAbstractListModel.supportedDropActions(self).
        See QAbstractListModel's documentation for mode details.
        This function and her sister function (supportedDragActions) allows the user to drag and drop rows in the model.
        This way, user can move variables in the table to group linked variables, to sort them, etc...
        
        :return: QFlags
        '''
        return QtCore.Qt.DropActions(QtCore.Qt.MoveAction)
    
    def supportedDragActions(self):
        ''' 
        Reimplemented from QAbstractListModel.supportedDragActions(self).
        See QAbstractListModel's documentation for mode details.
        
        :return: QFlags
        '''
        return QtCore.Qt.DropActions(QtCore.Qt.MoveAction)
    
    def dropMimeData(self, data, action, row, column, parentIndex):
        ''' 
        Reimplemented from QAbstractTableModel.dropMimeData(self, data, action, row, column, parentIndex).
        See QAbstractTableModel's documentation for mode details.
        Decodes the mimeData dropped when a user performs a drag and drop and modifies model accordingly.
        
        :param data: MimeData, qt's class associated with drag and drop operations.
        :param action: Move or Copy Action (Only move action are allowed in project).
        :param row: Row where the mimeData was dropped.
        :param column: Column where the mimeData was dropped.
        :param parentIndex: Parent's index (not really relevant for list views).
        :type data: PyQt4.QtCore.QMimeData
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
                self.swapProcess(draggedObjectRow, row)

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
    
    def swapProcess(self, rowSwitched, rowDropped):
        '''
        Performs a swap operation between two process.
        
        :param rowSwitched: Row where the drag operation started.
        :param rowDropped: Row where the dragged object was dropped.
        :type rowSwitched: Int
        :type rowDropped: Int
        :raises: Error if rowSwitched or rowDropped is greater than the total number of rows.
        '''
        assert rowSwitched < self.rowCount(), " Error : in BaseObserversModel::swapProcess, trying to swap and index greater than the amount of clock's observers"
        assert rowDropped < self.rowCount(), " Error : in BaseObserversModel::swapProcess, trying to drop and index greater than the amount  of clock's observers"
        #Swap indexes
        SwitchedNode = self.rootNode.toElement().elementsByTagName("Observer").item(rowSwitched)
        DroppedNode = self.rootNode.toElement().elementsByTagName("Observer").item(rowDropped)
        if rowSwitched > rowDropped:
            self.rootNode.insertBefore(SwitchedNode,DroppedNode)
        else:
            self.rootNode.insertAfter(SwitchedNode, DroppedNode)
        self.topWObject.dirty = True
    
class TableObserverDataModel(QtCore.QAbstractTableModel):
    '''
    Model handling attributes of clock observers.
    '''
    def __init__(self, observerNode, parent=None, mainWindow=None):
        '''
        Constructor.
        
        :param observerNode: ClockObservers XML Node.
        :param parent: Optional - Model's view.
        :param mainWindow: Optional - Main visual frame.
        '''
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.observerNode = observerNode
        self.topWObject = mainWindow
        self.rowFields = ["Target", "Units", "Start", "Step", "End"]
        self.rowFieldsDefaultValues = ["individuals", "other", "1", "1", "0"]
        self.headers = ["Field", "Value"]

    def rowCount(self, parent=QtCore.QModelIndex()):
        ''' 
        Reimplemented from QAbstractTableModel.rowCount(self, parent).
        RowCount is fixed to 5 (Target, Units, Start, Step, End).
        
        :param parent:
        :type parent: Not used
        :return: Int. Always 5.
        '''
        return 5
    
    def columnCount(self, parent=QtCore.QModelIndex()):
        ''' 
        Reimplemented from QAbstractTableModel.rowCount(self, parent).
        ColumnCount is fixed to 2 (Field, Value).
        
        :param parent:
        :type parent: Not used
        :return: Int. Always 2.
        '''
        return 2
    
    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' 
        Reimplemented from QAbstractTableModel.data(self, index, role=QtCore.Qt.DisplayRole).
        Returns data for role at position "index" in model. Controls what is going to be displayed in the table view.
        
        :param index: Cell's index in model/table.
        :param role: Optional - Qt item role.
        :type index: PyQt4.QtCore.QModelIndex
        :type role: Int
        :return: String | QColor
        '''
        if not index.isValid() or index.row() >= self.rowCount() or index.column() >= self.columnCount(None):
            return None
        
        if role == QtCore.Qt.BackgroundColorRole:
            if index.column() == 0:
                return QtGui.QColor("lightGray")
            
        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                return self.rowFields[index.row()]
            if index.column() == 1:
                # Modifies attributes.
                # First is the attribute name.
                # Second is the default value of this attribute.
                return self.observerNode.toElement().attribute(str.lower(self.rowFields[index.row()]),
                                                               self.rowFieldsDefaultValues[index.row()])

    
    def headerData(self, section, orientation, role):
        ''' 
        Reimplemented from QAbstractTableModel.headerData(self, section, orientation, role).
        See QAbstractTableModel's documentation for mode details.
        
        :param section: Model's column or row.
        :param orientation: Horizontal or vertical.
        :param role: Qt item role.
        :type section: Int
        :type orientation: Qt.orientation
        :type role: Int
        :return String.
        '''
        if role != QtCore.Qt.DisplayRole:
            return None
        
        if orientation == QtCore.Qt.Horizontal:
            return self.headers[section]
            
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        ''' 
        Reimplemented from QAbstractListModel.setData(self, index, value, role=QtCore.Qt.EditRole).
        Sets data for role at position "index" in model. Modifies model and its underlying data structure.
        
        :param index: Cell's position in model/table.
        :param value: New Value.
        :param role: Optional - Qt item role.
        :type index: PyQt4.QtCore.QModelIndex
        :type value: String
        :type role: Int.
        :return: Boolean. True = Data set correctly.
        '''
        if index.isValid() and role == QtCore.Qt.EditRole:
            if index.column() == 1 and index.row() < self.rowCount(None):
                attribute = str.lower(self.rowFields[index.row()])
                self.observerNode.toElement().setAttribute(attribute, value)
                self.topWObject.dirty = True
                return True
            
        return False
        
    def flags(self, index):
        ''' 
        Reimplemented from QAbstractListModel.flags(self, index).
        See QAbstractListModel's documentation for mode details.
        
        :param index: Cell's index in model/table.
        :type index: PyQt4.QtCore.QModelIndex
        :return: Int.
        '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        if index.column() == 0:
            return QtCore.Qt.ItemFlags(QtCore.QAbstractListModel.flags(self, index))
        
        return QtCore.Qt.ItemFlags(QtCore.QAbstractListModel.flags(self, index) | QtCore.Qt.ItemIsEditable)
    
