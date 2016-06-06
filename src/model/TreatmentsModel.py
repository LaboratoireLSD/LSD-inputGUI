"""
.. module:: TreatmentsModel

.. codeauthor:: Marc-André Gardner

:Created on: 2009-09-16

"""
from PyQt4 import QtCore
from PyQt4.QtGui import QColor
from PyQt4.QtXml import QDomNode
from model.baseTreatmentsModel import BaseTreatmentsModel

class ListTreatmentsModel(QtCore.QAbstractTableModel):
    '''
    Model handling processes listing, perhaps with some supplementary informations.
    '''
    #baseModel is static, shared between the two scenario/tree views
    baseModel = None
    
    def __init__(self, rootNode, clockNode, mode, windowObject, parent=None, scenarioDomTree=None):
        '''
        Constructor.
        
        :param rootNode: Processes XML node.
        :param clockNode: Clock XML node.
        :param mode: "scenarios" or "processes".
        :param windowObject: Application's main window.
        :param parent: Optional - Model's view.
        :param scenarioDomTree: Optional - Scenarios XML node.
        :type rootNode: PyQt4.QtXml.QDomElement
        :type clockNode: PyQt4.QtXml.QDomElement
        :type mode: String
        :type windowObject: :class:`.MainWindow`
        :type parent: :class:`.MainWindow`
        :type scenarioDomTree: PyQt4.QtXml.QDomElement
        '''
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.clockNode = clockNode
        ListTreatmentsModel.baseModel = BaseTreatmentsModel(rootNode, scenarioDomTree, windowObject)
        self.topWObject = windowObject
        if mode == "scenarios":
            self.listScenarios = True
            self.showEnvTarget = bool(self.topWObject.domDocs["settings"].firstChildElement("Models").firstChildElement("Scenario").attribute("showEnv"))
        else:
            self.listScenarios = False
            
    def columnCount(self, parent):
        '''
        Reimplemented from QAbstractTableModel.columnCount(self, parent).
        Column count is fixed to 1 (process name) for processes, 2 or 3 for scenarios.
        
        :param parent:
        :type parent: Not used
        :return: Int.
        '''
        if self.listScenarios:
            if self.showEnvTarget:
                return 3
            return 2
        return 1

    def rowCount(self, parent=QtCore.QModelIndex()):
        ''' 
        Reimplemented from QAbstractTableModel.rowCount(self, parent).
        How many processes/scenarios do we have.
        
        :param parent:
        :type parent: Not used
        :return: Int.
        '''
        if self.listScenarios:
            return ListTreatmentsModel.baseModel.getHowManyScenarios()
        else:
            return ListTreatmentsModel.baseModel.getHowManyTreatments()

    def getTreatmentNameFromIndex(self, index):
        '''
        Returns a process/scenario's name.
        
        :param index: Position of the process in view/model.
        :type index: PyQt4.QtCore.QModelIndex
        :return: String.
        '''
        if index.isValid():
            return ListTreatmentsModel.baseModel.scenarioModelMapper[index.row()] if self.listScenarios else ListTreatmentsModel.baseModel.processesModelMapper[index.row()]
    
    def exists(self, name):
        '''
        Tells if a process/scenario exists in current model.
        
        :param name: Name of the process/scenario in view/model.
        :type name: String
        :return: Boolean.
        '''
        if self.listScenarios:
            return name in ListTreatmentsModel.baseModel.scenarioModelMapper
        return name in ListTreatmentsModel.baseModel.processesModelMapper
    
    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' 
        Reimplemented from QAbstractTableModel.data(self, index, role=QtCore.Qt.DisplayRole).
        Return data for role at position index in model. Controls what is going to be displayed in the table view.
        
        :param index: Cell's index in model/table.
        :param role: Optional - Qt item role.
        :type index: PyQt4.QtCore.QModelIndex
        :type role: Int
        :return: QColor | String.
        ''' 
        if not index.isValid():
            return None
        
        if self.listScenarios and index.row() < ListTreatmentsModel.baseModel.getHowManyScenarios():
            keys = ListTreatmentsModel.baseModel.scenarioModelMapper
        elif not self.listScenarios and index.row() < ListTreatmentsModel.baseModel.getHowManyTreatments():
            keys = ListTreatmentsModel.baseModel.processesModelMapper
        else:
            return None
        
        processName = keys[index.row()]
        
        if role == QtCore.Qt.ForegroundRole:
            if not self.listScenarios:
                errorStatus =  ListTreatmentsModel.baseModel.getProcessValidity(processName)
                if errorStatus == "Valid":
                    return QColor(QtCore.Qt.green)
                elif errorStatus == "Warning":
                    return QColor(255, 215, 0)
                elif errorStatus == "Error":
                    return QColor(QtCore.Qt.red)
                else:
                    return QColor(QtCore.Qt.black)
            
        elif role == QtCore.Qt.DisplayRole:
            if self.listScenarios:
                if index.column() == 0:
                    return processName
                if index.column() ==  1:
                    return self.baseModel.getScenarioLabel(processName)["indProcess"]
                if index.column() ==  2:
                    return self.baseModel.getScenarioLabel(processName)["envProcess"]
            else:    
                return processName

    def insertRow(self, rowAfter, parent=QtCore.QModelIndex(), isScenario=False, name="New_process"):
        ''' 
        Reimplemented from QAbstractTableModel.insertRow(self, row, parent=QtCore.QModelIndex()).
        See QAbstractTableModel's documentation for more details.
        Inserts a process/scenario in the model/table.
        
        :param rowAfter: Insertion row in model/table.
        :param parent: Optional - Parent's index(not really relevant for list views).
        :param isScenario: Optional - Insert a scenario if True.
        :param name: Optional - New processes name.
        :type rowAfter: Int
        :type parent: PyQt4.QtCore.QModelIndex
        :type isScenario: Boolean
        :type name: String
        '''
        self.beginInsertRows(parent, rowAfter, rowAfter)
        ListTreatmentsModel.baseModel.addTreatment(name, QDomNode(), isScenario,rowAfter+1)
        self.endInsertRows()
    
    def sort(self, column, sortingOrder=QtCore.Qt.AscendingOrder):
        '''
        Reimplemented from QAbstractTableModel.sort(column, order=Qt::AscendingOrder).
        Sorts the model.
        
        :param column: Column where the sort action was queried.
        :param sortingOrder: Optional - AscendingOrder or DescendingOrder.
        :type column: Int
        :type sortingOrder: QtCore.SortOrder
        '''
        if sortingOrder == QtCore.Qt.AscendingOrder:
            reversedOrder=True
        else:
            reversedOrder = False 
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        if self.listScenarios:
            ListTreatmentsModel.baseModel.scenarioModelMapper.sort(key=lambda pName: pName.lower(),reverse=reversedOrder)
        else:
            ListTreatmentsModel.baseModel.processesModelMapper.sort(key=lambda pName: pName.lower(),reverse=reversedOrder)
        self.emit(QtCore.SIGNAL("layoutChanged()"))
        
    def insertRowFromDom(self, rowAfter, domNode):
        ''' 
        Inserts a process/scenario in the model/table using a XML DOM.
        
        :param rowAfter: Insertion row in model/table.
        :param domNode: Process's domNode.
        :type rowAfter: Int
        :type domNode: PyQt4.QtXml.QDomNode
        '''
        self.beginInsertRows(QtCore.QModelIndex(),rowAfter,rowAfter)
        ListTreatmentsModel.baseModel.addProcessFromDom(domNode)
        self.endInsertRows()
        
    def removeRow(self, rowToDelete, isScenario=False):
        ''' 
        Reimplemented from QAbstractTableModel.removeRow(self, row, parent=QtCore.QModelIndex()).
        See QAbstractTableModel's documentation for more details.
        Removes a process/scenario from the model/table.
        
        :param rowToDelete: Row of the deleted index.
        :param isScenario: Optional - Remove a scenario if True.
        :type rowToDelete: Int
        :type isScenario: Boolean
        '''
        self.beginRemoveRows(QtCore.QModelIndex(), rowToDelete, rowToDelete)
        if isScenario:
            ListTreatmentsModel.baseModel.removeTreatment(self.baseModel.scenarioModelMapper[rowToDelete])
        else:
            ListTreatmentsModel.baseModel.removeTreatment(self.baseModel.processesModelMapper[rowToDelete],False)
        self.endRemoveRows()

    def specialRemove(self, rows, isScenario=False):
        ''' 
        Remove function to delete multiple(possibly non-contiguous) elements in list.
        Removes multiple processes/scenarios.
        
        :param rows: Rows to delete.
        :param isScenario: Optional - Removes scenario(s) if True.
        :type rows: Int list
        :type isScenario: Boolean
        '''
       
        if isScenario:
            listFuncMapper = self.baseModel.scenarioModelMapper
        else:
            listFuncMapper = self.baseModel.processesModelMapper
            
        processToDelete = [listFuncMapper()[i] for i in rows]
        for process in processToDelete:
            deletedProcessRow = listFuncMapper().index(process)
            self.beginRemoveRows(QtCore.QModelIndex(),deletedProcessRow,deletedProcessRow)
            self.baseModel.removeTreatment(listFuncMapper()[deletedProcessRow],isScenario)
            self.endRemoveRows()
            
    def flags(self, index):
        ''' 
        Reimplemented from QAbstractTableModel.flags(self, index).
        See QAbstractTableModel's documentation for more details.
        
        :param index: Cell's index in model/table.
        :type index: PyQt4.QtCore.QModelIndex
        '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index) | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled)

    def headerData(self, section, orientation, role):
        ''' 
        Reimplemented from QAbstractTableModel.headerData(self, section, orientation, role)
        See QAbstractTableModel's documentation for more details.
        
        :param section: Model's column or row.
        :param orientation: Horizontal or vertical.
        :param role: Qt item role.
        :type section: Int
        :type orientation: Qt.orientation
        :type role: Int
        :return: String.
        '''
        if role != QtCore.Qt.DisplayRole:
            return None
        
        if orientation == QtCore.Qt.Horizontal:
            if section == 0:
                if self.listScenarios:
                    return "Scenario name"
                else:
                    return "Process name"
            #More sections, scenario case
            if section == 1:
                return "Scenario process"
            if section == 2:
                return "Scenario env. process"
                
        else:
            return str(section + 1)
    
    def supportedDropActions(self):
        ''' 
        Reimplemented from QAbstractTableModel.supportedDropActions(self).
        See QAbstractTableModel's documentation for more details.
        This function and her sister function(supportedDragActions) allows the user to drag and drop rows in the model.
        This way, user can move variables in the table to group linked variables, to sort them, etc...
        
        :return: Qt.DropActions
        '''
        return QtCore.Qt.DropActions(QtCore.Qt.MoveAction)
        
    def supportedDragActions(self):
        ''' 
        Reimplemented from QAbstractTableModel.supportedDragActions(self).
        See QAbstractTableModel's documentation for more details.
        
        :return: Qt.DropActions
        '''
        return QtCore.Qt.DropActions(QtCore.Qt.MoveAction)
    
    def dropMimeData(self, data, action, row, column, parentIndex):
        ''' 
        Reimplemented from QAbstractTableModel.dropMimeData(self, data, action, row, column, parentIndex).
        See QAbstractTableModel's documentation for more details.
        Decodes the mimeData dropped when a user performs a drag and drop and modifies model accordingly.
        
        :param data: MimeData, qt's class associated with drag and drop operations.
        :param action: Move or Copy Action(Only move action are allowed in project).
        :param row: Row where the mimeData was dropped.
        :param column: Column where the mimeData was dropped.
        :param parentIndex: Parent's index(not really relevant for table views).
        :type data: QMimeData
        :type action: Qt.DropActions
        :type row: Int
        :type column: Int
        :type parentIndex: PyQt4.QtCore.QModelIndex
        :return: Boolean
        '''
        if action == QtCore.Qt.MoveAction:
            if data.hasFormat('application/x-qabstractitemmodeldatalist'):
                byteArray = data.data('application/x-qabstractitemmodeldatalist')
                draggedObjectRow = self.decode_data(byteArray)
                
                if row == -1:
                    row = parentIndex.row()
                if self.listScenarios == True:
                    mappingDict = ListTreatmentsModel.baseModel.scenarioModelMapper
                    mappingDict.insert(row,mappingDict.pop(draggedObjectRow)) 
                else:
                    mappingDict = ListTreatmentsModel.baseModel.processesModelMapper
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

    def setFixedClockValue(self, newValue):
        '''
        Sets the clock to a fixed amount of time.
        
        :param newValue: New amount of time.
        :type newValue: Object
        '''
        self.clockNode.firstChildElement("PrimitiveTree").removeChild(self.clockNode.firstChildElement("PrimitiveTree").firstChild())
        isEqualNode = self.clockNode.ownerDocument().createElement("Operators_IsEqualComplex")
        tokenClockNode = self.clockNode.ownerDocument().createElement("Data_Clock")
        tokenNode = self.clockNode.ownerDocument().createElement("Data_Value")
        tokenNode.setAttribute("inValue_Type","ULong")
        tokenNode.setAttribute("inValue", str(newValue))
        isEqualNode.appendChild(tokenClockNode)
        isEqualNode.appendChild(tokenNode)
        self.clockNode.firstChildElement("PrimitiveTree").appendChild(isEqualNode)
        self.topWObject.dirty = True


    def setData(self, index, value, role=QtCore.Qt.EditRole):
        ''' 
        Reimplemented from QAbstractTableModel.setData(self, index, value, role=QtCore.Qt.EditRole).
        Sets data for role at position "index" in model. Modifies model and its underlying data structure.
        
        :param index: Cell's position in model/table.
        :param value: New Value.
        :param role: Optional - Qt item role.
        :type index: PyQt4.QtCore.QModelIndex
        :type value: String
        :type role: Int
        :return: Boolean.
        '''
        if index.isValid() and role == QtCore.Qt.EditRole:
            if index.column() == 0:
                self.baseModel.renameTreatment(self.getTreatmentNameFromIndex(index), value)
                return True
            elif index.column() == 1:
                #Scenario case, modifying individual process
                self.baseModel.modifyInd(self.getTreatmentNameFromIndex(index), value)
                return True
            elif index.column() == 2:
                #Scenario case, modifying environment process
                self.baseModel.modifyEnv(self.getTreatmentNameFromIndex(index), value)
                return True

    
