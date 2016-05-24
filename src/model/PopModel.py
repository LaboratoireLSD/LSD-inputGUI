
from PyQt4 import QtCore
from PyQt4.QtGui import QColor

class PopModel(QtCore.QAbstractTableModel):
    '''
    Model handling demography variables representation
    '''

    def __init__(self, baseModel,profile, parent=None):
        '''
        @summary Constructor
        @param baseModel :  Population base model
        @param profile : currently active profile
        @param parent : model's view
        '''
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.baseModel = baseModel
        self.profileName = profile
    
    def getEvalNode(self):
        '''' 
        @summary : Return Accept Function node of the currently selected profile
        '''
        return self.baseModel.getAcceptFunctionNode(self.profileName)
    
    def getVarFromIndex(self, index):
        '''
        @summary : Return variable name
        @param index : variable's position in model/index
        '''
        return list(self.baseModel.getDemoVarsList(self.profileName))[index.row()]
    
    def columnCount(self, parent=QtCore.QModelIndex()):
        '''
        @summary : Reimplemented from QAbstractTableModel.columnCount(self,parent)
        Column count is fixed to 3(name,dependencies and value range)
        @param parent : not used
        '''
        return 3
    
    def rowCount(self, parent=QtCore.QModelIndex()):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.rowCount(self,parent)
        How many demography variables do we have
        @param parent : not used
        '''
        return self.baseModel.howManyDemoVars(self.profileName)
    
    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.data(self, index, role=QtCore.Qt.DisplayRole)
        Return data for role at position index in model. Controls what is going to be displayed in the table view.
        @param index : cell's index in model/table
        @param role : Qt item role
        ''' 
        if not index.isValid() or index.row() >= self.baseModel.howManyDemoVars(self.profileName):
            return None
        
        colonne = index.column()
        varName = self.getVarFromIndex(index)
                
        if role == QtCore.Qt.CheckStateRole:
            if colonne == 0:
                if self.baseModel.isSelected(self.profileName,varName):
                    return QtCore.Qt.Checked
                else:
                    return QtCore.Qt.Unchecked
            return None
        
        if role == QtCore.Qt.ToolTipRole:
            return None
            
        if role == QtCore.Qt.DisplayRole:
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
            
            return ""

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
                return "Depends on"
            elif section == 2:
                return "Range"
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
        if index.column() == 0:
            return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index) | QtCore.Qt.ItemIsUserCheckable)
        return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index))
        
            
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.setData(self, index, value, role=QtCore.Qt.EditRole)
        Sets data for role at position index in model. Modify model and its underlying data structure
        @param index : cell's position in model/table
        @param value : new Value
        @param role : Qt item role
        '''
        if index.isValid() and role == QtCore.Qt.CheckStateRole:
            if index.column() == 0:
                varName = self.getVarFromIndex(index)
                self.baseModel.changeSelection(self.profileName, varName)
                return True
     
        return False

        
class PopModelSim(QtCore.QAbstractTableModel):
    '''
    Model handling population supplementary variables representation
    '''

    def __init__(self, baseModel,profile, parent=None):
        '''
        @summary Constructor
        @param baseModel :  Population base model
        @param profile : currently active profile
        @param parent : model's view
        '''
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.baseModel = baseModel
        self.profileName = profile
                                         
    def getVarFromIndex(self, index):
        '''' 
        @summary : Return variable name
        @param index : variable's position in model/index
        '''
        return self.baseModel.getSimViewVarsList(self.profileName)[index.row()]
    
    def columnCount(self, parent=QtCore.QModelIndex()):
        '''' 
        @summary : Reimplemented from QAbstractTableModel.columnCount(self,parent)
        Column count is fixed to 4(name,type, dependencies, tree )
        @param parent : not used
        '''
        return 4
    
    def rowCount(self, parent=QtCore.QModelIndex()):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.rowCount(self,parent)
        How many demography variables do we have
        @param parent : not used
        '''
        return self.baseModel.howManySimVars(self.profileName)
    

    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.data(self, index, role=QtCore.Qt.DisplayRole)
        Return data for role at position index in model. Controls what is going to be displayed in the table view.
        @param index : cell's index in model/table
        @param role : Qt item role
        '''     
        if not index.isValid() or index.row() >= self.baseModel.howManySimVars(self.profileName):
            return None
        
        colonne = index.column()
        varName = self.getVarFromIndex(index)
                
        if role == QtCore.Qt.CheckStateRole:
            return None                #Discard Unwanted checkboxes
        
        if role == QtCore.Qt.ToolTipRole:
            return None
        
        if role == QtCore.Qt.ForegroundRole:
            if colonne == 0:
                errorStatus =  self.baseModel.getVariableValidity(varName,self.profileName)
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
            if colonne == 0:
                #Variable's name
                return varName
            elif colonne == 1:
                # Type
                base_type = self.baseModel.getVarType(self.profileName,varName)
                return base_type
            
            elif colonne == 2:
                # Dependencies
                list_depd = set(self.baseModel.getVarDepends(self.profileName,varName))
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
            
            return ""

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
                return "Depends on"
            elif section == 3:
                return "Distribution"
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

        return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index) | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled |QtCore.Qt.ItemIsDropEnabled)

    def insertRow(self, rowafter, parent=QtCore.QModelIndex(),name = "New_variable"):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.insertRow(self, row, parent=QtCore.QModelIndex())
        See QAbstractTableModel's documentation for mode details
        Inserts a variable in the model/table
        @param rowafter : insertion row in model/table
        @pram parent : parent's index(not really relevant for list views)
        @param name : name of the variable
        '''
        self.beginInsertRows(parent, rowafter, rowafter)
        self.baseModel.addVar(self.profileName,name, "Unknown", rowafter+1)
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
        self.baseModel.removeVar(self.profileName,self.baseModel.getSimViewVarsList(self.profileName)[row])
        self.endRemoveRows()
        
    def specialRemove(self,rows,parent=QtCore.QModelIndex()):
        ''' 
        @summary : Remove function to delete multiple(possibly non-contiguous) elements in list
        Remove rows from the model/table with rows of deleted indexes
        @param rows : rows of the deleted indexes
        '''
        varToDelete = [self.baseModel.getSimViewVarsList(self.profileName)[i] for i in rows]
        for variable in varToDelete:
            deletedVarRow = self.baseModel.getSimViewVarsList(self.profileName).index(variable)
            self.beginRemoveRows(parent,deletedVarRow,deletedVarRow)
            self.baseModel.removeVar(self.profileName,variable)
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
                if self.baseModel.variableExists(self.profileName, value):
                    print("Cannot set variable's name, " + value + " already exists.")
                    return False
                else:
                    self.baseModel.renameVariable(self.profileName, self.getVarFromIndex(index), value)
                    return True
            elif index.column() == 1:
                self.baseModel.setVarType(self.profileName, self.getVarFromIndex(index), value)
                return True
            else:
                return False
            
    def sort(self,column,sortingOrder = QtCore.Qt.AscendingOrder):
        '''
        @summary Reimplemented from QAbstractTableModel.sort(column, order = Qt::AscendingOrder )
        Sort model
        @param column : column where the sort action was queried
        @param sortingOrder : AscendingOrder or DescendingOrder
        '''
        if column == 0:
            if sortingOrder == QtCore.Qt.AscendingOrder:
                reversedOrder=True
            else:
                reversedOrder = False 
            self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
            self.baseModel.getSimViewVarsList(self.profileName).sort(key=str.lower,reverse=reversedOrder)
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
        @param parentIndex : parent's index(not really relevant for list views)
        '''
        if action == QtCore.Qt.MoveAction:
            if data.hasFormat('application/x-qabstractitemmodeldatalist'):
                byteArray = data.data('application/x-qabstractitemmodeldatalist')
                draggedObjectRow = self.decode_data(byteArray)
                if row == -1:
                    row = parentIndex.row()
                self.baseModel.swapSimVars(draggedObjectRow,row, self.profileName)

            return True
        else:
            return False

    def decode_data(self, byteArray):
        '''
        @summary Qt's mimeData.data('application/x-qabstractitemmodeldatalist') provides a QByteArray which contains
        all the information required when a QAbstractItemView performs a Drag and Drop operation
        First 4 Bytes are : dragged object's original row number
        Next 4 Bytes are : dragged object's original column number
        That's all we need for the moment
        '''
        
        DanDInfo = QtCore.QDataStream(byteArray)
        
        return DanDInfo.readInt32()
    
class SimplePopModel(QtCore.QAbstractTableModel):
    '''
    Simplified PopModel to use with demography editor
    '''

    def __init__(self, baseModel, parent=None):
        '''
        @summary Constructor
        @param baseModel :  Demography base model
        @param parent : model's view
        '''
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.baseModel = baseModel
    
    def getVarFromIndex(self, index):
        '''' 
        @summary : Return variable name
        @param index : variable's position in model/index
        '''
        return self.baseModel.modelMapper[index.row()]
    
    def columnCount(self, parent=QtCore.QModelIndex()):
        '''' 
        @summary : Reimplemented from QAbstractTableModel.columnCount(self,parent)
        Column count is fixed to 5(name,type, dependencies, range, tree )
        @param parent : not used
        '''
        return 5
    
    def rowCount(self, parent=QtCore.QModelIndex()):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.rowCount(self,parent)
        How many demography variables do we have
        @param parent : not used
        '''
        return self.baseModel.howManyVars()

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
        varName = self.getVarFromIndex(index)
                
        if role == QtCore.Qt.CheckStateRole:
            return None                #Discard unwanted checkboxes
        
        if role == QtCore.Qt.ToolTipRole:
            return None
        
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
            
            return ""

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
                return "Depends On"
            elif section == 3:
                return "Range"
            elif section == 4:
                return "Distribution"
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
        
        return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index)  | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled)
            
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
                if self.baseModel.variableExists(value):
                    print("Cannot set variable's name, " + value + " already exists.")
                    return False
                else:
                    self.baseModel.renameVariable(self.getVarFromIndex(index), value)
                    return True
            elif index.column() == 1:
                self.baseModel.setVarType(self.getVarFromIndex(index), value)
                return True
            else:
                return False
    
    def insertRow(self, rowafter, parent=QtCore.QModelIndex(),name = "New_variable"):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.insertRow(self, row, parent=QtCore.QModelIndex())
        See QAbstractTableModel's documentation for mode details
        Inserts a variable in the model/table
        @param rowafter : insertion row in model/table
        @pram parent : parent's index(not really relevant for list views)
        @param name : name of the variable
        '''
        self.beginInsertRows(parent, rowafter, rowafter)
        self.baseModel.addVar(name, "Unknown", rowafter+1)
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
        self.baseModel.removeVar(self.baseModel.modelMapper[row])
        self.endRemoveRows()
