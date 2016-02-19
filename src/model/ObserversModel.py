'''
Created on 2009-12-14

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

from PyQt4 import QtCore, QtGui
        
class ListClockObserversModel(QtCore.QAbstractListModel):
    '''
    Model handling clock's observing processes
    '''
    def __init__(self, rootNode, parent=None,mainWindow=None):
        '''
        @summary Constructor
        @param rootNode : ClockObservers XML Node
        @param parent : model's view
        '''
        QtCore.QAbstractListModel.__init__(self, parent)
        self.rootNode = rootNode
        self.topWObject = mainWindow

    def rowCount(self, parent=QtCore.QModelIndex()):
        ''' 
        @summary : Reimplemented from QAbstractListModel.rowCount(self,parent)
        How many processes observes clock
        @param parent : not used
        '''
        return self.rootNode.toElement().elementsByTagName("Observer").count()
    
    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' 
        @summary : Reimplemented from QAbstractListModel.data(self, index, role=QtCore.Qt.DisplayRole)
        Return data for role at position index in model. Controls what is going to be displayed in the table view.
        @param index : cell's index in model/table
        @param role : Qt item role
        '''
        if not index.isValid():
            return QtCore.QVariant()
        if index.row() >= self.rowCount():
            return QtCore.QVariant()
        
        ligne = index.row()

        if role == QtCore.Qt.CheckStateRole:
            return QtCore.QVariant()                #Discard unwanted checkBoxes

        if role == QtCore.Qt.DisplayRole:
            
            name = self.rootNode.toElement().elementsByTagName("Observer").item(ligne).toElement().attribute("process")
            return QtCore.QVariant(QtCore.QString(name))
        
        return QtCore.QVariant()
    
    def getCurrentObserverNode(self,index):
        '''
        @summary Return node of the observer associated with index
        @param index : cell's position in model/index
        '''
        return self.rootNode.childNodes().item(index.row())
            
    def removeProcess(self,index):
        '''
        @summary Removes a process from the model's observing processes list
        @param index: location in list of the process we want to remove
        '''
        self.beginRemoveRows(index.parent(), index.row(), index.row())
        self.rootNode.removeChild(self.rootNode.childNodes().item(index.row()))
        self.endRemoveRows()
        self.topWObject.dirty = True
        return
    
    def specialRemove(self,indexes):
        ''' 
        @summary : Remove function to delete multiple(possibly non-contiguous) elements in list
        Remove rows from the model/table with rows of deleted indexes
        @param rows : rows of  the deleted indexes
        '''
        observersToDelete = [self.rootNode.childNodes().item(index.row()) for index in indexes]
        for deletedObserver in observersToDelete:
            for i in range(0,self.rootNode.childNodes().count()):
                if deletedObserver == self.rootNode.childNodes().item(i):
                    break
            self.beginRemoveRows(QtCore.QModelIndex(),i,i)
            self.rootNode.removeChild(deletedObserver)
            self.endRemoveRows()
        
        self.topWObject.dirty = True
            
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        ''' 
        @summary : Reimplemented from QAbstractListModel.setData(self, index, value, role=QtCore.Qt.EditRole)
        Sets data for role at position index in model. Modify model and its underlying data structure
        @param index : cell's position in model/table
        @param value : new Value
        @param role : Qt item role
        '''
        if index.isValid() and role == QtCore.Qt.EditRole:
            self.rootNode.childNodes().item(index.row()).toElement().setAttribute("process",value)
            self.topWObject.dirty = True
            return True
        return False
    
    def addObserver(self,row):
        '''
        @summary Adds a process to the model's observing processes list
        '''
        self.beginInsertRows(QtCore.QModelIndex(), row, row)
        newObserver = self.rootNode.ownerDocument().createElement("Observer")
        newObserver.setAttribute("process","")
        #Set attribute default values
        newObserver.setAttribute("target","individuals")
        newObserver.setAttribute("units","other")
        newObserver.setAttribute("start","1")
        newObserver.setAttribute("step","1")
        newObserver.setAttribute("end","0")
        #Insert Observer in dom
        self.rootNode.insertAfter(newObserver, self.rootNode.childNodes().item(row))
        self.topWObject.dirty = True
        self.endInsertRows()
        
    def flags(self, index):
        ''' 
        @summary : Reimplemented from QAbstractListModel.flags(self,index)
        See QAbstractListModel's documentation for mode details
        @param index : cell's index in model/table
        '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        return QtCore.Qt.ItemFlags(QtCore.QAbstractListModel.flags(self, index) | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled)
    
    def supportedDropActions(self):
        ''' 
        @summary : Reimplemented from QAbstractListModel.supportedDropActions(self)
        See QAbstractListModel's documentation for mode details
        This function and her sister function(supportedDragActions) allows the user to drag and drop rows in the model
        This way, user can move variables in the table to group linked variables, to sort them, etc...
        '''
        return QtCore.Qt.DropActions(QtCore.Qt.MoveAction)
    
    def supportedDragActions(self):
        ''' 
        @summary : Reimplemented from QAbstractListModel.supportedDragActions(self)
        See QAbstractListModel's documentation for mode details
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
        @param parentIndex : parent's index(not really relevant for list views)
        '''
        if action == QtCore.Qt.MoveAction:
            if data.hasFormat('application/x-qabstractitemmodeldatalist'):
                bytearray = data.data('application/x-qabstractitemmodeldatalist')
                draggedObjectRow = self.decode_data(bytearray)
                if row == -1:
                    row = parentIndex.row()
                self.swapProcess(draggedObjectRow, row)

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
    
    def swapProcess(self,rowSwitched,rowDropped):
        '''
        @summary Perform a swap operation between two process
        @param rowSwitched : row where the drag operation started
        @param rowDropped : row where the dragged object was dropped
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
        return
    
class TableObserverDataModel(QtCore.QAbstractTableModel):
    '''
    Model handling attributes of clock observers
    '''
    def __init__(self, observerNode, parent=None,mainWindow=None):
        '''
        @summary Constructor
        @param rootNode : ClockObservers XML Node
        @param parent : model's view
        '''
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.observerNode = observerNode
        self.topWObject = mainWindow

    def rowCount(self, parent=QtCore.QModelIndex()):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.rowCount(self,parent)
        RowCount is fixed to 4(target,start,step,end)
        @param parent : not used
        '''
        return 5
    
    def columnCount(self, parent=QtCore.QModelIndex()):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.rowCount(self,parent)
        Columncount is fixed to 2
        @param parent : not used
        '''
        return 2
    
    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.data(self, index, role=QtCore.Qt.DisplayRole)
        Return data for role at position index in model. Controls what is going to be displayed in the table view.
        @param index : cell's index in model/table
        @param role : Qt item role
        '''
        if not index.isValid():
            return QtCore.QVariant()
        
        if index.row() >= self.rowCount():
            return QtCore.QVariant()
        
        if role == QtCore.Qt.CheckStateRole:
            return QtCore.QVariant()                #Discard unwanted checkBoxes
        
        if role == QtCore.Qt.BackgroundColorRole:
            if index.column() == 0:
                return QtCore.QVariant(QtGui.QColor("lightGray"))
            
        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                if index.row() == 0:
                    return QtCore.QVariant(QtCore.QString("Target"))
                elif index.row() == 1:
                    return QtCore.QVariant(QtCore.QString("Units"))
                elif index.row() == 2:
                    return QtCore.QVariant(QtCore.QString("Start"))
                elif index.row() == 3:
                    return QtCore.QVariant(QtCore.QString("Step"))
                elif index.row() == 4:
                    return QtCore.QVariant(QtCore.QString("End"))
            if index.column() == 1:
                if index.row() == 0:
                    return QtCore.QVariant(self.observerNode.toElement().attribute("target","individuals"))
                elif index.row() == 1:
                    return QtCore.QVariant(self.observerNode.toElement().attribute("units","other"))
                elif index.row() == 2:
                    return QtCore.QVariant(self.observerNode.toElement().attribute("start","1"))
                elif index.row() == 3:
                    return QtCore.QVariant(self.observerNode.toElement().attribute("step","1"))
                elif index.row() == 4:
                    return QtCore.QVariant(self.observerNode.toElement().attribute("end","0"))

        return QtCore.QVariant()
    
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
                return QtCore.QVariant("Field")
            elif section == 1:
                return QtCore.QVariant("Value")
                return QtCore.QVariant()
        else:
            return QtCore.QVariant()  
        
        return QtCore.QVariant()
            
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        ''' 
        @summary : Reimplemented from QAbstractListModel.setData(self, index, value, role=QtCore.Qt.EditRole)
        Sets data for role at position index in model. Modify model and its underlying data structure
        @param index : cell's position in model/table
        @param value : new Value
        @param role : Qt item role
        '''
        if index.isValid() and role == QtCore.Qt.EditRole:
            if index.column() == 0:
                return False
            elif index.column() == 1:
                if index.row() == 0:
                    self.observerNode.toElement().setAttribute("target",value.toString())
                    self.topWObject.dirty = True
                    return True
                elif index.row() == 1:
                    self.observerNode.toElement().setAttribute("units",value.toString())
                    self.topWObject.dirty = True
                    return True
                elif index.row() == 2:
                    self.observerNode.toElement().setAttribute("start",value.toString())
                    self.topWObject.dirty = True
                    return True
                elif index.row() == 3:
                    self.observerNode.toElement().setAttribute("step",value.toString())
                    self.topWObject.dirty = True
                    return True
                elif index.row() == 4:
                    self.observerNode.toElement().setAttribute("end",value.toString())
                    self.topWObject.dirty = True
                    return True
        return False
        
    def flags(self, index):
        ''' 
        @summary : Reimplemented from QAbstractListModel.flags(self,index)
        See QAbstractListModel's documentation for mode details
        @param index : cell's index in model/table
        '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        if index.column() == 0:
            return QtCore.Qt.ItemFlags(QtCore.QAbstractListModel.flags(self, index))
        
        return QtCore.Qt.ItemFlags(QtCore.QAbstractListModel.flags(self, index) | QtCore.Qt.ItemIsEditable)
    