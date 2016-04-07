'''
Created on 2009-09-16

@author:  Marc Andre Gardner
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
from PyQt4.QtXml import QDomNode
from model.baseTreatmentsModel import BaseTreatmentsModel

class ListTreatmentsModel(QtCore.QAbstractTableModel):
    '''
    Model handling processes listing, perhaps with some supplementary informations
    '''
    #baseModel is static, shared between the two scenario/tree views
    baseModel = None
    
    def __init__(self, rootNode, clockNode, mode, windowObject,parent=None, scenarioDomTree = None):
        '''
        @summary Constructor
        @param rootNode :  Processes XML node
        @param clockNode : Clock XML node
        @param mode : "scenarios" or "processes"
        @param windowObject : application's main window
        @param parent : model's view
        @param scenarioDomTree : Scenarios XML node
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

    def getBaseModel(self):
        '''
        @summary Return base model
        '''
        return ListTreatmentsModel.baseModel

    def columnCount(self, parent):
        '''
        @summary : Reimplemented from QAbstractTableModel.columnCount(self,parent)
        Column count is fixed to 1(process name) for processes, 2 or 3 for scenarios
        @param parent : not used
        '''
        if self.listScenarios:
            if self.showEnvTarget:
                return 3
            return 2
        return 1

    def rowCount(self, parent=QtCore.QModelIndex()):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.rowCount(self,parent)
        How many processes/scenarios do we have
        @param parent : not used
        '''
        if self.listScenarios:
            return ListTreatmentsModel.baseModel.getHowManyScenarios()
        else:
            return ListTreatmentsModel.baseModel.getHowManyTreatments()

    def getTreatmentNameFromIndex(self, index):
        '''
        @summary Return process/scenario's name
        @param index: position of the process in view/model
        '''
        if index.isValid():
            return ListTreatmentsModel.baseModel.getViewScenariosDict()[index.row()] if self.listScenarios else ListTreatmentsModel.baseModel.getViewTreatmentsDict()[index.row()]
    
    def exists(self,name):
        '''
        @summary Return if process/scenario exists in current model
        @param name: name of the process/scenario in view/model
        '''
        if self.listScenarios:
            return name in ListTreatmentsModel.baseModel.getViewScenariosDict()
        return name in ListTreatmentsModel.baseModel.getViewTreatmentsDict()
    
    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.data(self, index, role=QtCore.Qt.DisplayRole)
        Return data for role at position index in model. Controls what is going to be displayed in the table view.
        @param index : cell's index in model/table
        @param role : Qt item role
        ''' 
        if not index.isValid():
            return None
        if index.row() >= ListTreatmentsModel.baseModel.getHowManyTreatments() and not self.listScenarios or index.row() >= ListTreatmentsModel.baseModel.getHowManyScenarios() and self.listScenarios:
            return None
        
        if self.listScenarios:
            keys = ListTreatmentsModel.baseModel.getViewScenariosDict()
        else:
            keys = ListTreatmentsModel.baseModel.getViewTreatmentsDict()
        
        processName = keys[index.row()]
        
        if role == QtCore.Qt.CheckStateRole:
            return None                #Discard unwanted checkboxes
        if role == QtCore.Qt.ForegroundRole:
            if not self.listScenarios:
                errorStatus =  ListTreatmentsModel.baseModel.getProcessValidity(processName)
                if errorStatus == "Unknown":
                    return QColor(QtCore.Qt.black)
                elif errorStatus == "Valid":
                    return QColor(QtCore.Qt.green)
                elif errorStatus == "Warning":
                    return QColor(255, 215, 0)
                elif errorStatus == "Error":
                    return QColor(QtCore.Qt.red)
                else:
                    return QColor(QtCore.Qt.black)
            
        if role == QtCore.Qt.DisplayRole:
            if self.listScenarios:
                if index.column() == 0:
                    return processName
                if index.column() ==  1:
                    return self.baseModel.getScenarioLabel(processName)["indProcess"]
                if index.column() ==  2:
                    return self.baseModel.getScenarioLabel(processName)["envProcess"]
            else:    
                return processName
            
        return None

    def insertRow(self, rowafter, parent=QtCore.QModelIndex(), isScenario = False,name = "New_process"):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.insertRow(self, row, parent=QtCore.QModelIndex())
        See QAbstractTableModel's documentation for mode details
        Inserts a process/scanrio in the model/table
        @param rowafter : insertion row in model/table
        @pram parent : parent's index(not really relevant for list views)
        @param isScenario : insert a scenario if True
        @param name = new processes name
        '''
        self.beginInsertRows(parent, rowafter, rowafter)
        ListTreatmentsModel.baseModel.addTreatment(name, QDomNode(), isScenario,rowafter+1)
        self.endInsertRows()
        return
    
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
        if self.listScenarios:
            ListTreatmentsModel.baseModel.scenarioModelMapper.sort(key=lambda pName: pName.lower(),reverse=reversedOrder)
        else:
            ListTreatmentsModel.baseModel.processesModelMapper.sort(key=lambda pName: pName.lower(),reverse=reversedOrder)
        self.emit(QtCore.SIGNAL("layoutChanged()"))
        
    def insertRowFromDom(self,rowAfter,domNode):
        ''' 
        @summary Inserts a process/scenario in the model/table using a XML DOM
        @param rowafter : insertion row in model/table
        @pram domNode : process's domNode
        '''
        self.beginInsertRows(QtCore.QModelIndex(),rowAfter,rowAfter)
        ListTreatmentsModel.baseModel.addProcessFromDom(domNode)
        self.endInsertRows()
        
    def removeRow(self, rowToDelete,isScenario = False):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.removeRow(self, row , parent=QtCore.QModelIndex())
        See QAbstractTableModel's documentation for mode details
        Removes a process/scenario from the model/table
        @param rowToDelete : row of the deleted index
        @param parent : parent's index (not relevant for QtableView)
        '''
        self.beginRemoveRows(QtCore.QModelIndex(), rowToDelete, rowToDelete)
        if isScenario:
            ListTreatmentsModel.baseModel.removeTreatment(self.baseModel.getViewScenariosDict()[rowToDelete])
        else:
            ListTreatmentsModel.baseModel.removeTreatment(self.baseModel.getViewTreatmentsDict()[rowToDelete],False)
        self.endRemoveRows()

    def specialRemove(self,rows,isScenario = False):
        ''' 
        @summary : Remove function to delete multiple(possibly non-contiguous) elements in list
        Remove multiple processes/scenarios
        @param rows : rows of  the deleted indexes
        '''
       
        if isScenario:
            listFuncMapper = self.baseModel.getViewScenariosDict
        else:
            listFuncMapper = self.baseModel.getViewTreatmentsDict
            
        processToDelete = [listFuncMapper()[i] for i in rows]
        for process in processToDelete:
            deletedProcessRow = listFuncMapper().index(process)
            self.beginRemoveRows(QtCore.QModelIndex(),deletedProcessRow,deletedProcessRow)
            self.baseModel.removeTreatment(listFuncMapper()[deletedProcessRow],isScenario)
            self.endRemoveRows()
            
    def flags(self, index):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.flags(self,index)
        See QAbstractTableModel's documentation for mode details
        @param index : cell's index in model/table
        '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index) | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled)

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
        
        return None
    
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
                if self.listScenarios == True:
                    mappingDict = ListTreatmentsModel.baseModel.getViewScenariosDict()
                    mappingDict.insert(row,mappingDict.pop(draggedObjectRow)) 
                else:
                    mappingDict = ListTreatmentsModel.baseModel.getViewTreatmentsDict()
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
        
    def getClockNode(self):
        '''
        @summary Return Clock's XML node
        '''
        return self.clockNode

    def setFixedClockValue(self,newValue):
        '''
        @summary Sets the clock to a fixed amount of time
        @param newValue : new amount of time
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
        return


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
            else:
                return False

    
