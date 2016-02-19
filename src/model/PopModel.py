'''
Created on 2009-08-25

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
        
    def getBaseModel(self):
        '''
        @summary Return base model
        '''
        return self.baseModel
    
    def getProfileName(self):
        '''' 
        @summary : Return currently selected profile
        '''
        return self.profileName
    
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
        return self.baseModel.getDemoViewVarsList(self.profileName)[index.row()]
    
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
            return QtCore.QVariant()
        
        colonne = index.column()
        varName = self.getVarFromIndex(index)
                
        if role == QtCore.Qt.CheckStateRole:
            if colonne == 0:
                if self.baseModel.isSelected(self.profileName,varName):
                    return QtCore.QVariant(QtCore.Qt.Checked)
                else:
                    return QtCore.QVariant(QtCore.Qt.Unchecked)
            return QtCore.QVariant()
        
        if role == QtCore.Qt.ToolTipRole:
            return QtCore.QVariant()
            
        if role == QtCore.Qt.DisplayRole:
            if colonne == 0:
                # Variable's name
                return QtCore.QVariant(QtCore.QString(varName))
            
            elif colonne == 1:
                # Dependencies
                list_depd = set(self.baseModel.getVarDepends(self.profileName,varName))
                str_depd = QtCore.QString("")
                for d in list_depd:
                    str_depd.append(d)
                    str_depd.append(', ')
                if list_depd:
                    str_depd.chop(2)
                return QtCore.QVariant(str_depd)
            
            elif colonne == 2:
                varRange = QtCore.QString("[")
                if str(self.baseModel.getVarType(self.profileName,varName)) == "String" or str(self.baseModel.getVarType(self.profileName,varName)) == "Bool":
                    for possibleValues in self.baseModel.getVarRange(self.profileName,varName):
                        varRange.append(possibleValues)
                        if possibleValues != self.baseModel.getVarRange(self.profileName,varName)[-1]:
                            varRange.append(" ") 
                    return QtCore.QVariant(varRange.append("]"))
                else:
                    #Nota
                    #If we have steps between values, let's say 0-10 20-30 40-50 , displayed range is going to be 0-50
                    #If demography has huge values, array.sort... may overflow
                    #Finally, characters might cause an error when casting to float
                    array = self.baseModel.getVarRange(self.profileName,varName)
                    if array:
                        array = QtCore.QStringList(array)
                        array.removeAll(QtCore.QString(""))
                        array = [str(string) for string in array]
                        array.sort(lambda a,b: cmp(float(a), float(b)))
                        varRange.append(array[0])
                        varRange.append(" - ")
                        varRange.append(array[-1])
                    return QtCore.QVariant(varRange.append("]"))
            
            return QtCore.QVariant(QtCore.QString(""))

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
                return QtCore.QVariant("Depends on")
            elif section == 2:
                return QtCore.QVariant("Range")
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
                self.baseModel.changeSelection(str(self.profileName),varName)
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
    
    def getBaseModel(self):
        '''
        @summary Return base model
        '''
        return self.baseModel
    
    def getProfileName(self):
        '''' 
        @summary : Return currently selected profile
        '''
        return self.profileName
    
    def getVarNode(self,varName):
        '''
        @summary : Return variable's XML node
        @param varName : variable's name
        '''
        return self.baseModel.getVarNode(self.profileName,varName)
                                         
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
            return QtCore.QVariant()
        
        colonne = index.column()
        varName = self.getVarFromIndex(index)
                
        if role == QtCore.Qt.CheckStateRole:
            return QtCore.QVariant()                #Discard Unwanted checkboxes
        
        if role == QtCore.Qt.ToolTipRole:
            return QtCore.QVariant()
        
        if role == QtCore.Qt.ForegroundRole:
            if colonne == 0:
                errorStatus =  self.baseModel.getVariableValidity(varName,self.profileName)
                if errorStatus == "Unknown":
                    return QtCore.QVariant(QColor(QtCore.Qt.black))
                elif errorStatus == "Valid":
                    return QtCore.QVariant(QColor(QtCore.Qt.green))
                elif errorStatus == "Warning":
                    return QtCore.QVariant(QColor(255,215,0))
                elif errorStatus == "Error":
                    return QtCore.QVariant(QColor(QtCore.Qt.red))
                else:
                    return QtCore.QVariant(QColor(QtCore.Qt.black))
                
        if role == QtCore.Qt.DisplayRole:
            if colonne == 0:
                #Variable's name
                return QtCore.QVariant(QtCore.QString(varName))
            elif colonne == 1:
                # Type
                base_type = self.baseModel.getVarType(self.profileName,varName)
                return QtCore.QVariant(QtCore.QString(base_type))
            
            elif colonne == 2:
                # Dependencies
                list_depd = set(self.baseModel.getVarDepends(self.profileName,varName))
                str_depd = QtCore.QString("")
                for d in list_depd:
                    str_depd.append(d)
                    str_depd.append(', ')
                if list_depd:
                    str_depd.chop(2)
                return QtCore.QVariant(str_depd)
                
            elif colonne == 3:
                #Distribution
                return QtCore.QVariant(QtCore.QString("> Click Here <"))
            
            return QtCore.QVariant(QtCore.QString(""))

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
                return QtCore.QVariant("Depends on")
            elif section == 3:
                return QtCore.QVariant("Distribution")
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
                if self.baseModel.variableExists(self.profileName,value.toString()):
                    print("Cannot set variable's name, " + str(value.toString()) + " already exists.")
                    return False
                else:
                    self.baseModel.renameVariable(self.profileName,self.getVarFromIndex(index),value.toString())
                    return True
            elif index.column() == 1:
                self.baseModel.setVarType(self.profileName,self.getVarFromIndex(index),value.toString())
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
                bytearray = data.data('application/x-qabstractitemmodeldatalist')
                draggedObjectRow = self.decode_data(bytearray)
                if row == -1:
                    row = parentIndex.row()
                self.baseModel.swapSimVars(draggedObjectRow,row, self.profileName)

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
        
    def getBaseModel(self):
        '''
        @summary Return base model
        '''
        return self.baseModel
    
    def getVarFromIndex(self, index):
        '''' 
        @summary : Return variable name
        @param index : variable's position in model/index
        '''
        return self.baseModel.getVarsList()[index.row()]
    
    def getVarNode(self,varName):
        '''
        @summary : Return variable's XML node
        @param varName : variable's name
        '''
        return self.baseModel.getVarNode(varName)
    
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
    
    def getDemoNode(self):
        '''
        @summary Return Demography XML node
        '''
        return self.baseModel.getDemoNode()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' 
        @summary : Reimplemented from QAbstractTableModel.data(self, index, role=QtCore.Qt.DisplayRole)
        Return data for role at position index in model. Controls what is going to be displayed in the table view.
        @param index : cell's index in model/table
        @param role : Qt item role
        '''  
        if not index.isValid() or index.row() >= self.rowCount():
            return QtCore.QVariant()
        
        colonne = index.column()
        varName = self.getVarFromIndex(index)
                
        if role == QtCore.Qt.CheckStateRole:
            return QtCore.QVariant()                #Discard unwanted checkboxes
        
        if role == QtCore.Qt.ToolTipRole:
            return QtCore.QVariant()
        
        if role == QtCore.Qt.DisplayRole:
            if colonne == 0:
                #Variable's name
                return QtCore.QVariant(QtCore.QString(varName))
            elif colonne == 1:
                return QtCore.QVariant(self.baseModel.getVarType(varName))
            elif colonne == 2:
                #Dependencies
                list_depd = set(self.baseModel.getVarDepends(varName))
                str_depd = QtCore.QString("")
                for d in list_depd:
                    str_depd.append(d)
                    str_depd.append(', ')
                if list_depd:
                    str_depd.chop(2)
                return QtCore.QVariant(str_depd)
            
            elif colonne == 3:
                varRange = QtCore.QString("[")
                if str(self.baseModel.getVarType(varName)) == "String" or str(self.baseModel.getVarType(varName)) == "Bool":
                    for possibleValues in self.baseModel.getVarRange(varName):
                        varRange.append(possibleValues)
                        if possibleValues != self.baseModel.getVarRange(varName)[-1]:
                            varRange.append(" ") 
                    return QtCore.QVariant(varRange.append("]"))
                else:
                    #Nota
                    #If we have steps between values, let's say 0-10 20-30 40-50 , displayed range is going to be 0-50
                    #If demography has huge values, array.sort... may overflow
                    #Finally, characters might cause an error when casting to float
                    array = self.baseModel.getVarRange(varName)
                    if array:
                        array.sort(lambda a,b: cmp(float(a), float(b)))
                        varRange.append(array[0])
                        varRange.append(" - ")
                        varRange.append(array[-1])
                        return QtCore.QVariant(varRange.append("]"))
            elif colonne == 4:
                # Distribution
                return QtCore.QVariant(QtCore.QString("> Click Here <"))
            
            return QtCore.QVariant(QtCore.QString(""))

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
                return QtCore.QVariant("Depends On")
            elif section == 3:
                return QtCore.QVariant("Range")
            elif section == 4:
                return QtCore.QVariant("Distribution")
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
                if self.baseModel.variableExists(value.toString()):
                    print("Cannot set variable's name, " + str(value.toString()) + " already exists.")
                    return False
                else:
                    self.baseModel.renameVariable(self.getVarFromIndex(index),value.toString())
                    return True
            elif index.column() == 1:
                self.baseModel.setVarType(self.getVarFromIndex(index),value.toString())
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
        self.baseModel.removeVar(self.baseModel.getVarsList()[row])
        self.endRemoveRows()