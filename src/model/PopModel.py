"""
.. module:: PopModel

.. codeauthor:: Marc-André Gardner

:Created on: 2009-08-25

"""
from PyQt4 import QtCore
from PyQt4.QtGui import QColor
import Definitions

class PopModel(QtCore.QAbstractTableModel):
    '''
    Model handling demography variables representation
    '''

    def __init__(self, baseModel, profile, parent=None):
        '''
        Constructor
        
        :param baseModel:  Population base model.
        :param profile: Currently active profile.
        :param parent: Optional - Model's view.
        '''
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.baseModel = baseModel
        self.profileName = profile
        self.headers = ["Name", "Depends on", "Range"]
    
    def getEvalNode(self):
        '''' 
        Returns the Accept Function node of the currently selected profile.
        
        :return: PyQt4.QtXml.QDomElement. Returns :meth:`.GeneratorBaseModel.getAcceptFunctionNode`.
        '''
        return self.baseModel.getAcceptFunctionNode(self.profileName)
    
    def getVarFromIndex(self, index):
        '''
        Returns a variable name.
        
        :param PyQt4.QtCore.QModelIndex index: Variable's position in model/index.
        :return: String.
        '''
        return list(self.baseModel.getDemoVarsList(self.profileName))[index.row()]
    
    def columnCount(self, parent=QtCore.QModelIndex()):
        '''
        Reimplemented from QAbstractTableModel.columnCount(self, parent).
        Column count is fixed to 3 (Name, Dependencies and Value range).
        
        :param parent: Not used
        :return: Int. Always 3.
        '''
        return 3
    
    def rowCount(self, parent=QtCore.QModelIndex()):
        ''' 
        Reimplemented from QAbstractTableModel.rowCount(self, parent).
        How many demography variables do we have.
        
        :param parent: Not used
        :return: Int. Returns :meth:`.GeneratorBaseModel.howManyDemoVars`.
        '''
        return self.baseModel.howManyDemoVars(self.profileName)
    
    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' 
        Reimplemented from QAbstractTableModel.data(self, index, role=QtCore.Qt.DisplayRole).
        Returns data for role at position "index" in model. Controls what is going to be displayed in the table view.
        
        :param PyQt4.QtCore.QModelIndex index: Cell's index in model/table.
        :param Int role: Qt item role.
        :return: String | Qt::CheckState.
        ''' 
        if not index.isValid() or index.row() >= self.rowCount(None) or index.column() >= self.columnCount(None):
            return None
        
        colonne = index.column()
        varName = self.getVarFromIndex(index)
                
        if role == QtCore.Qt.CheckStateRole:
            if colonne == 0:
                if self.baseModel.isSelected(self.profileName,varName):
                    return QtCore.Qt.Checked
                else:
                    return QtCore.Qt.Unchecked
            
        elif role == QtCore.Qt.DisplayRole:
            if colonne == 0:
                # Variable's name
                return varName
            
            elif colonne == 1:
                # Dependencies
                list_depd = set(self.baseModel.getVarDepends(self.profileName,varName))
                str_depd = ""
                for d in list_depd:
                    str_depd += d
                    str_depd += ', '
                if list_depd:
                    str_depd = str_depd[:-2]
                return str_depd
            
            elif colonne == 2:
                varRange = "["
                if self.baseModel.getVarType(self.profileName, varName) == "String" or self.baseModel.getVarType(self.profileName, varName) == "Bool":
                    for possibleValues in self.baseModel.getVarRange(self.profileName, varName):
                        varRange += possibleValues
                        if possibleValues != self.baseModel.getVarRange(self.profileName, varName)[-1]:
                            varRange += " "
                    return varRange + "]"
                else:
                    #Nota
                    #If we have steps between values, let's say 0-10 20-30 40-50 , displayed range is going to be 0-50
                    #If demography has huge values, array.sort... may overflow
                    #Finally, characters might cause an error when casting to float
                    array = self.baseModel.getVarRange(self.profileName, varName)
                    if array:
                        array.sort(lambda a,b: float(a) - float(b))
                        varRange += array[0]
                        varRange += " - "
                        varRange += array[-1]
                    return varRange + "]"

    def headerData(self, section, orientation, role):
        ''' 
        Reimplemented from QAbstractTableModel.headerData(self, section, orientation, role).
        See QAbstractTableModel's documentation for more details.
        
        :param Int section: Model's column or row.
        :param Qt.orientation orientation: Horizontal or vertical.
        :param Int role: Qt item role.
        :return: String.
        '''
        if role != QtCore.Qt.DisplayRole:
            return None
        
        if orientation == QtCore.Qt.Horizontal:
            return self.headers[section]
        else:
            # Title of the row. Its number.
            return str(section + 1)
    
    def flags(self, index):
        ''' 
        Reimplemented from QAbstractTableModel.flags(self, index).
        See QAbstractTableModel's documentation for more details.
        
        :param index: Cell's index in model/table.
        :type index: PyQt4.QtCore.QModelIndex
        :return: Int
        '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        if index.column() == 0:
            return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index) | QtCore.Qt.ItemIsUserCheckable)
        return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index))
        
            
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        ''' 
        Reimplemented from QAbstractTableModel.setData(self, index, value, role=QtCore.Qt.EditRole).
        Sets data for role at position index in model. Modifies model and its underlying data structure.
        
        :param index: Cell's position in model/table.
        :param value: New Value.
        :param role: Qt item role.
        :type index: PyQt4.QtCore.QModelIndex
        :type value: String
        :type role: Int
        :return: Boolean. True = data set correctly.
        '''
        if index.isValid() and role == QtCore.Qt.CheckStateRole:
            if index.column() == 0:
                varName = self.getVarFromIndex(index)
                self.baseModel.changeSelection(self.profileName, varName)
                return True
     
        return False

        
class PopModelSim(QtCore.QAbstractTableModel):
    '''
    Model handling population supplementary variables representation.
    '''

    def __init__(self, baseModel, profile, parent=None):
        '''
        Constructor.
        
        :param baseModel: Population base model.
        :param profile: Currently active profile.
        :param parent: Optional - Model's view.
        '''
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.baseModel = baseModel
        self.profileName = profile
        self.headers = ["Name", "Type", "Depends on", "Distribution"]
                                         
    def getVarFromIndex(self, index):
        '''' 
        Returns a variable name.
        
        :param index: Variable's position in model/index.
        :type index: PyQt4.QtCore.QModelIndex
        :return: String
        '''
        return self.baseModel.getSimViewVarsList(self.profileName)[index.row()]
    
    def columnCount(self, parent=QtCore.QModelIndex()):
        '''' 
        Reimplemented from QAbstractTableModel.columnCount(self, parent).
        Column count is fixed to 4 (Name, Type, Dependencies, Distribution).
        
        :param parent: Not used
        :return: Int. Always 4.
        '''
        return 4
    
    def rowCount(self, parent=QtCore.QModelIndex()):
        ''' 
        Reimplemented from QAbstractTableModel.rowCount(self, parent).
        How many demography variables do we have.
        
        :param parent: Not used
        :return: Int. Returns :meth`.GeneratorBaseModel.howManySimVars`.
        '''
        return self.baseModel.howManySimVars(self.profileName)
    

    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' 
        Reimplemented from QAbstractTableModel.data(self, index, role=QtCore.Qt.DisplayRole).
        Returns data for role at position "index" in model. Controls what is going to be displayed in the table view.
        
        :param PyQt4.QtCore.QModelIndex index: Cell's index in model/table.
        :param Int role: Qt item role.
        :return: QColor | String.
        '''     
        if not index.isValid() or index.row() >= self.rowCount(None) or index.column() >= self.columnCount(None):
            return None
        
        colonne = index.column()
        varName = self.getVarFromIndex(index)
        
        if role == QtCore.Qt.ForegroundRole:
            if colonne == 0:
                errorStatus = self.baseModel.getVariableValidity(varName, self.profileName)
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
                
        elif role == QtCore.Qt.DisplayRole:
            if colonne == 0:
                #Variable's name
                return varName
            elif colonne == 1:
                # Type
                return Definitions.typeToDefinition(self.baseModel.getVarType(self.profileName, varName))
            
            elif colonne == 2:
                # Dependencies
                list_depd = set(self.baseModel.getVarDepends(self.profileName, varName))
                str_depd = ""
                for d in list_depd:
                    str_depd += d
                    str_depd += ", "
                if list_depd:
                    str_depd = str_depd[:-2]
                return str_depd
                
            elif colonne == 3:
                #Distribution
                return "> Click Here <"

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
        
        if orientation == QtCore.Qt.Horizontal:
            return self.headers[section]
        else:
            # Returns the row number.
            return str(section + 1)
    
    def flags(self, index):
        ''' 
        Reimplemented from QAbstractTableModel.flags(self, index).
        See QAbstractTableModel's documentation for more details.
        
        :param index: Cell's index in model/table.
        :type index: PyQt4.QtCore.QModelIndex
        :return: Int
        '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index) | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled |QtCore.Qt.ItemIsDropEnabled)

    def insertRow(self, rowafter, parent=QtCore.QModelIndex(), name="New_variable"):
        ''' 
        Reimplemented from QAbstractTableModel.insertRow(self, row, parent=QtCore.QModelIndex()).
        See QAbstractTableModel's documentation for more details.
        Inserts a variable in the model/table.
        
        :param rowafter: Insertion row in model/table.
        :pram parent: Optional - Parent's index(not really relevant for list views).
        :param name: Optional - Name of the variable.
        :type rowafter: Int
        :type parent: PyQt4.QtCore.QModelIndex
        :type name: String
        '''
        self.beginInsertRows(parent, rowafter, rowafter)
        self.baseModel.addVar(self.profileName, name, "Unknown", rowafter+1)
        self.endInsertRows()
      
    def removeRow(self, row, parent=QtCore.QModelIndex()):
        ''' 
        Reimplemented from QAbstractTableModel.removeRow(self, row, parent=QtCore.QModelIndex()).
        See QAbstractTableModel's documentation for more details.
        Removes a row from the model/table.
        
        :param row: Row of the deleted index.
        :param parent: Optional - Parent's index (not relevant for QtableView).
        :type row: Int
        :type parent: PyQt4.QtCore.QModelIndex
        '''
        self.beginRemoveRows(parent, row, row)
        self.baseModel.removeVar(self.profileName,self.baseModel.getSimViewVarsList(self.profileName)[row])
        self.endRemoveRows()
        
    def specialRemove(self, rows, parent=QtCore.QModelIndex()):
        ''' 
        Remove function to delete multiple(possibly non-contiguous) elements in list.
        Removes rows from the model/table with rows of deleted indexes.
        
        :param rows: Rows of the deleted indexes.
        :param parent: Optional - Parent's row
        :type rows: Int list
        :type parent: PyQt4.QtCore.QModelIndex
        '''
        varToDelete = [self.baseModel.getSimViewVarsList(self.profileName)[i] for i in rows]
        for variable in varToDelete:
            deletedVarRow = self.baseModel.getSimViewVarsList(self.profileName).index(variable)
            self.beginRemoveRows(parent,deletedVarRow,deletedVarRow)
            self.baseModel.removeVar(self.profileName,variable)
            self.endRemoveRows()
        
        
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        ''' 
        Reimplemented from QAbstractTableModel.setData(self, index, value, role=QtCore.Qt.EditRole).
        Sets data for role at position "index" in model. Modifies model and its underlying data structure.
        
        :param index: Cell's position in model/table.
        :param value: New Value.
        :param role: Qt item role.
        :type index: PyQt4.QtCore.QModelIndex
        :type value: String
        :type role: Int
        :return: Boolean. True = data set correctly.
        '''
        if index.isValid() and role == QtCore.Qt.EditRole:
            if index.column() == 0:
                if self.baseModel.variableExists(self.profileName, value):
                    print("Cannot set variable's name, " + value + " already exists.")
                    return False
                else:
                    self.baseModel.renameVariable(self.profileName, self.getVarFromIndex(index), value)
                    return True
            elif index.column() == 1:
                self.baseModel.setVarType(self.profileName, self.getVarFromIndex(index), value)
                return True
            
    def sort(self, column, sortingOrder=QtCore.Qt.AscendingOrder):
        '''
        Reimplemented from QAbstractTableModel.sort(column, order=Qt::AscendingOrder).
        Sorts model.
        
        :param column: Column where the sort action was queried.
        :param sortingOrder: AscendingOrder or DescendingOrder.
        :type column: Int
        :type sortingOrder: QtCore.Qt.SortOrder
        '''
        if column == 0:
            reversedOrder = True if sortingOrder == QtCore.Qt.AscendingOrder else False
            self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
            self.baseModel.getSimViewVarsList(self.profileName).sort(key=str.lower,reverse=reversedOrder)
            self.emit(QtCore.SIGNAL("layoutChanged()"))
             
    def supportedDropActions(self):
        ''' 
        Reimplemented from QAbstractTableModel.supportedDropActions(self).
        See QAbstractTableModel's documentation for more details.
        This function and her sister function(supportedDragActions) allows the user to drag and drop rows in the model.
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
        :param parentIndex: Parent's index(not really relevant for list views).
        :type data: QMimeData
        :type action: Qt::DropAction
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
                self.baseModel.swapSimVars(draggedObjectRow,row, self.profileName)

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
    
class SimplePopModel(QtCore.QAbstractTableModel):
    '''
    Simplified PopModel to use with demography editor
    '''

    def __init__(self, baseModel, parent=None):
        '''
        Constructor.
        
        :param baseModel: Demography base model.
        :param parent: Optional - Model's view.
        '''
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.baseModel = baseModel
        self.headers = ["Name", "Type", "Depends on", "Range", "Distribution"]
    
    def getVarFromIndex(self, index):
        '''' 
        Returns a variable's name.
        
        :param index: Variable's position in model/index.
        :type index: PyQt4.QtCore.QModelIndex
        :return: String
        '''
        return self.baseModel.modelMapper[index.row()]
    
    def columnCount(self, parent=QtCore.QModelIndex()):
        '''' 
        Reimplemented from QAbstractTableModel.columnCount(self, parent).
        Column count is fixed to 5 (Name, tType, Dependencies, Range, Tree).
        
        :param parent:
        :type parent: Not used
        :return: Int. Always 5.
        '''
        return 5
    
    def rowCount(self, parent=QtCore.QModelIndex()):
        ''' 
        Reimplemented from QAbstractTableModel.rowCount(self, parent).
        How many demography variables do we have.
        
        :param parent:
        :type parent: Not used
        :return: Int. Returns :meth:`.SimpleBaseVarModel.howManyVars`.
        '''
        return self.baseModel.howManyVars()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' 
        Reimplemented from QAbstractTableModel.data(self, index, role=QtCore.Qt.DisplayRole).
        Returns data for role at position "index" in model. Controls what is going to be displayed in the table view.
        
        :param index: Cell's index in model/table.
        :param role: Qt item role.
        :type index: PyQt4.QtCore.QModelIndex
        :type role: Int
        :return: String.
        '''  
        if not index.isValid() or index.row() >= self.rowCount() or index.column() >= self.columnCount(None):
            return None
        
        colonne = index.column()
        varName = self.getVarFromIndex(index)
        
        if role == QtCore.Qt.DisplayRole:
            if colonne == 0:
                #Variable's name
                return varName
            elif colonne == 1:
                return self.baseModel.getVarType(varName)
            elif colonne == 2:
                #Dependencies
                list_depd = set(self.baseModel.getVarDepends(varName))
                str_depd = ""
                for d in list_depd:
                    str_depd += d
                    str_depd += ", "
                if list_depd:
                    str_depd = str_depd[:-2]
                return str_depd
            
            elif colonne == 3:
                varRange = "["
                if self.baseModel.getVarType(varName) == "String" or self.baseModel.getVarType(varName) == "Bool":
                    for possibleValues in self.baseModel.getVarRange(varName):
                        varRange += possibleValues
                        if possibleValues != self.baseModel.getVarRange(varName)[-1]:
                            varRange += " "
                    return varRange + "]"
                else:
                    #Nota
                    #If we have steps between values, let's say 0-10 20-30 40-50 , displayed range is going to be 0-50
                    #If demography has huge values, array.sort... may overflow
                    #Finally, characters might cause an error when casting to float
                    array = self.baseModel.getVarRange(varName)
                    if array:
                        array.sort(lambda a,b: float(a) - float(b))
                        varRange += array[0]
                        varRange += " - "
                        varRange += array[-1]
                        return varRange + "]"
            elif colonne == 4:
                # Distribution
                return "> Click Here <"

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
        
        if orientation == QtCore.Qt.Horizontal:
            return self.headers[section]
        else:
            # Returns the row number
            return str(section + 1)
    
    def flags(self, index):
        ''' 
        Reimplemented from QAbstractTableModel.flags(self, index).
        See QAbstractTableModel's documentation for more details.
        
        :param index: Cell's index in model/table.
        :type index: PyQt4.QtCore.QModelIndex
        :return: Int
        '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        
        return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index)  | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled)
            
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        ''' 
        Reimplemented from QAbstractTableModel.setData(self, index, value, role=QtCore.Qt.EditRole).
        Sets data for role at position index in model. Modify model and its underlying data structure.
        
        :param index: Cell's position in model/table.
        :param value: New Value.
        :param role: Qt item role.
        :type index: PyQt4.QtCore.QModelIndex
        :type value: String
        :type role: Int
        :return: Boolean. True = data set correctly.
        '''
        if index.isValid() and role == QtCore.Qt.EditRole:
            if index.column() == 0:
                if self.baseModel.variableExists(value):
                    print("Cannot set variable's name, " + value + " already exists.")
                    return False
                else:
                    self.baseModel.renameVariable(self.getVarFromIndex(index), value)
                    return True
            elif index.column() == 1:
                self.baseModel.setVarType(self.getVarFromIndex(index), value)
                return True
    
    def insertRow(self, rowafter, parent=QtCore.QModelIndex(), name="New_variable"):
        ''' 
        Reimplemented from QAbstractTableModel.insertRow(self, row, parent=QtCore.QModelIndex()).
        See QAbstractTableModel's documentation for more details.
        Inserts a variable in the model/table.
        
        :param rowafter: Insertion row in model/table.
        :param parent: Optional - Parent's index(not really relevant for list views).
        :param name: Optional - Name of the variable.
        :type rowafter: Int
        :type parent: PyQt4.QtCore.QModelIndex
        :type name: String
        '''
        self.beginInsertRows(parent, rowafter, rowafter)
        self.baseModel.addVar(name, "Unknown", rowafter+1)
        self.endInsertRows()

      
    def removeRow(self, row, parent=QtCore.QModelIndex()):
        ''' 
        Reimplemented from QAbstractTableModel.removeRow(self, row, parent=QtCore.QModelIndex()).
        See QAbstractTableModel's documentation for more details.
        Removes a row from the model/table.
        
        :param row: Row of the deleted index.
        :param parent: Optional - Parent's index (not relevant for QtableView).
        :type row: Int
        :type parent: PyQt4.QtCore.QModelIndex
        '''
        self.beginRemoveRows(parent, row, row)
        self.baseModel.removeVar(self.baseModel.modelMapper[row])
        self.endRemoveRows()
