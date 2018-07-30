"""
.. module:: GeneratorManagerModel

.. codeauthor:: Mathieu Gagnon <mathieu.gagnon.10@ulaval.ca>

:Created on: 2010-04-16

"""
from PyQt4 import QtCore
from PyQt4.QtGui import QColor

class GeneratorManagerModel(QtCore.QAbstractTableModel):
    '''
    Model handling population generation representation
    '''

    def __init__(self, baseModel, parent=None, mainWindow=None):
        '''
        Constructor. 
        
        :param baseModel: Base model that contains the data.
        :param parent: Optional - Model's view.
        :param mainWindow: Optional - The main visual frame.
        :type baseModel: :class:`.GeneratorBaseModel`
        :type parent: PyQt4.QtGui.QTableView
        :type mainWindow: frame.MainFrame.MainWindow
        '''
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.baseModel = baseModel
        self.topWObject = mainWindow
    
    def columnCount(self, parent=QtCore.QModelIndex()):
        '''' 
        Reimplemented from QAbstractTableModel.columnCount(self, parent).
        Column count is fixed to 3 (profile, size and time).
        
        :param parent:
        :type parent: Not used
        :return: Int. Always returns 3.
        '''
        return 3
    
    def rowCount(self, parent=QtCore.QModelIndex()):
        ''' 
        Reimplemented from QAbstractTableModel.rowCount(self, parent).
        How many variables do we have.
        
        :param parent:
        :type parent: Not used
        :return: Int. Returns :meth:`.GeneratorBaseModel.howManyGeneration`
        '''
        return self.baseModel.howManyGeneration()
    
    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' 
        Reimplemented from QAbstractTableModel.data(self, index, role=QtCore.Qt.DisplayRole).
        Return data for role at position index in model. Controls what is going to be displayed in the table view.
        
        :param index: Cell's index in model/table.
        :param role: Optional - Qt item role.
        :type index: PyQt4.QtCore.QModelIndex
        :type role: Int
        :return: String | QColor.
        '''
        if not index.isValid():
            return ""
        
        colonne = index.column()
        varNode = self.baseModel.sourceDom.childNodes().item(index.row()).toElement()
        
        if role == QtCore.Qt.TextColorRole:
            return QColor(0, 0, 0)
        elif role != QtCore.Qt.DisplayRole or colonne >= self.columnCount(None):
            return None
       
        # 1st column = Profile Name.
        # 2nd column = Number of individuals to generate.
        # 3rd column = Time of generation.
        return [varNode.attribute("profile"), varNode.attribute("size"), varNode.attribute("time")][colonne]

    def headerData(self, section, orientation, role):
        ''' 
        Reimplemented from QAbstractTableModel.headerData(self, section, orientation, role).
        See QAbstractTableModel's documentation for more details.
        Returns the title of the header or the title of the row.
        
        :param section: Model's column or row.
        :param orientation: horizontal or vertical.
        :param role: Qt item role
        :type section: Int
        :type orientation: Qt.orientation
        :type role: Int
        :return: String
        '''
        if role != QtCore.Qt.DisplayRole:
            return None
        
        if orientation == QtCore.Qt.Horizontal and section < self.columnCount(None):
            # Returns the header title
            return ["Profile name", "Individuals quantity", "Clock value"][section]
        else:
            # Returns the row title (Number of the row in this case)
            return str(section + 1)
    
    def flags(self, index):
        ''' 
        Reimplemented from QAbstractTableModel.flags(self, index).
        See QAbstractTableModel's documentation for more details.
        
        :param index: Cell's index in model/table.
        :type index: PyQt4.QtCore.QModelIndex
        :return: Int.
        '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index) | QtCore.Qt.ItemIsEditable)

    def insertRow(self, rowafter, parent=QtCore.QModelIndex()):
        ''' 
        Reimplemented from QAbstractTableModel.insertRow(self, row, parent=QtCore.QModelIndex()).
        See QAbstractTableModel's documentation for more details.
        Inserts a row in the model/table.
        
        :param rowafter: Insert row in model/table.
        :param parent: Optional - Parent's index (not really relevant for table views).
        :type rowafter: Int
        :type parent: PyQt4.Qtcore.QModelIndex
        '''
        self.beginInsertRows(parent, rowafter, rowafter)
        newGenNode = self.baseModel.sourceDom.ownerDocument().createElement("SubPopulation")
        newGenNode.setAttribute("profile", "")
        newGenNode.setAttribute("time", "0")
        newGenNode.setAttribute("size", "0")
        self.baseModel.sourceDom.appendChild(newGenNode)
        self.endInsertRows()
        self.topWObject.dirty = True
    
    def removeRow(self, row, parent=QtCore.QModelIndex()):
        ''' 
        Reimplemented from QAbstractTableModel.removeRow(self, row, parent = QtCore.QModelIndex()).
        See QAbstractTableModel's documentation for more details.
        Removes a row from the model/table.
        
        :param index: Cell's position in model/table.
        :param rowToDelete: Row of the deleted index.
        :type row: Int
        :type parent: PyQt4.QtCore.QModelIndex
        '''
        self.beginRemoveRows(parent, row, row)
        self.baseModel.sourceDom.removeChild(self.baseModel.sourceDom.childNodes().item(row))
        self.endRemoveRows()
        self.topWObject.dirty = True
    
    def specialRemove(self, indexes):
        ''' 
        Remove function to delete multiple (possibly non-contiguous) elements in list.
        Removes rows from the model/table with rows of deleted indexes.
        
        :param indexes: Rows of the deleted indexes.
        :type indexes: Int list
        '''
        profilesNode = self.baseModel.sourceDom.childNodes()
        profileToDelete = [profilesNode.item(index) for index in indexes]
        for deletedProfile in profileToDelete:
            for i in range(self.baseModel.sourceDom.childNodes().count()):
                if deletedProfile == self.baseModel.sourceDom.childNodes().item(i):
                    break
            self.beginRemoveRows(QtCore.QModelIndex(), i, i)
            self.baseModel.sourceDom.removeChild(deletedProfile)
            self.endRemoveRows()
        
        self.topWObject.dirty = True

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        ''' 
        Reimplemented from QAbstractTableModel.setData(self, index, value, role=QtCore.Qt.EditRole).
        Sets data for role at position "index" in model. Modifies model and its underlying data structure.
        
        :param index: QModelIndex - Cell's position in model/table.
        :param value: QVariant - New Value.
        :param role: Optional - Qt item role.
        :return: Boolean.
        '''
        if index.isValid() and role == QtCore.Qt.EditRole:
            column = index.column()
            varNode = self.baseModel.sourceDom.childNodes().item(index.row())
            if column == 0:
                varNode.toElement().setAttribute("profile", value)
                self.topWObject.dirty = True
                return True
            if column == 1:
                varNode.toElement().setAttribute("size", value)
                self.topWObject.dirty = True
                return True
            elif column == 2:
                varNode.toElement().setAttribute("time", value)
                self.topWObject.dirty = True
                return True
        
        print("Warning : In ProfileManagerModel::setData, value cannot be casted to long!")
        return False
