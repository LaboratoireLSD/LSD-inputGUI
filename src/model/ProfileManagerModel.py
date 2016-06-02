"""
.. module:: ProfileManagerModel

.. codeauthor:: Mathieu Gagnon <mathieu.gagnon.10@ulaval.ca>

:Created on: 2010-04-16

"""
from PyQt4 import QtCore, QtGui
from model.baseVarModel import GeneratorBaseModel

class ProfileManagerModel(QtCore.QAbstractListModel):
    '''
    Model handling profile representation.
    '''

    def __init__(self, parent=None):
        '''
        Constructor.
        :param parent: Optional - Model's view.
        :type parent: QObject
        '''
        QtCore.QAbstractListModel.__init__(self, parent)
        self.baseModel = GeneratorBaseModel()
        self.headers = ["Profiles"]
    
    def rowCount(self, parent=QtCore.QModelIndex()):
        ''' 
        Reimplemented from QAbstractListModel.rowCount(self, parent).
        How many profiles do we have.
        
        :param parent:
        :type parent: Not used
        :return: Int.
        '''
        return len(self.baseModel.profileDict.keys())
    
    def getProfileFromIndex(self, index):
        '''
        Returns a profile's name.
        
        :param index: Profile's position in model/index.
        :type index: PyQt4.QtCore.QModelIndex()
        :return: String
        '''
        return sorted(self.baseModel.profileDict.keys())[index.row()]
    
    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' 
        Reimplemented from QAbstractListModel.data(self, index, role=QtCore.Qt.DisplayRole).
        Returns data for role at position "index" in model. Controls what is going to be displayed in the table view.
        
        :param index: Cell's index in model/table.
        :param role: Qt item role.
        :type index: PyQt4.QtCore.QModelIndex()
        :type role: Int
        :return: QColor | String
        ''' 
        if not index.isValid():
            return None
        
        if role == QtCore.Qt.TextColorRole:
            return QtGui.QColor(0, 0, 0)
        
        elif role != QtCore.Qt.DisplayRole:
            return None

        return self.getProfileFromIndex(index)

    def headerData(self, section, orientation, role):
        ''' 
        Reimplemented from QAbstractListModel.headerData(self, section, orientation, role).
        See QAbstractListModel's documentation for mode details.
        
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
            return str(section + 1)
    
    def flags(self, index):
        ''' 
        Reimplemented from QAbstractListModel.flags(self, index).
        See QAbstractListModel's documentation for mode details.
        
        :param index: Cell's index in model/table.
        :type index: PyQt4.QtCore.QModelIndex()
        :return: Int.
        '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        return QtCore.Qt.ItemFlags(QtCore.QAbstractListModel.flags(self, index))

    def insertProfile(self, parentIndex, row, profileName, demoFileName="", simVarProfileFrom="", acceptFuncProfileFrom=""):
        '''
        Adds a new profile to profiles list.
        
        :param parentIndex: Parent's index (not relevant for list views).
        :param row: Insertion row in model.
        :param profileName: Profile's name.
        :param demoFileName: Optional - Name of the demography file used for the new profile.
        :param simVarProfileFrom: Optional - Name of the profile we copy the simulation variables from, or empty string.
        :param simVarProfileFrom: Optional - Name of the profile we copy the Accept function from, or empty string.
        :type parentIndex: PyQt4.QtCore.QModelIndex()
        :type row: Int
        :type profileName: String
        :type demoFileName: String
        :type simVarProfileFrom: String
        :type simVarProfileFrom: String
        '''
        self.beginInsertRows(parentIndex, row, row)
        self.baseModel.addProfile(profileName,demoFileName,simVarProfileFrom,acceptFuncProfileFrom)
        self.endInsertRows()

    def cloneProfile(self, cloneName, clonedProfileName):
        '''
        Adds new profile to profiles list by cloning an already existing profile.
        
        :param cloneName: New profile's name.
        :param clonedProfileName: Name of the profile we copy the variables from.
        :type cloneName: String
        :type clonedProfileName: String
        '''
        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(),self.rowCount())
        self.baseModel.cloneProfile(cloneName,clonedProfileName)
        self.endInsertRows()

    def removeProfile(self, parentIndex, row):
        '''
        Deletes a profile.
        
        :param parentIndex: Parent's index (not relevant for list views).
        :param row: Position of the deleted profile in model/view.
        :type parentIndex: PyQt4.QtCore.QModelIndex()
        :type row: Int
        '''
        self.beginRemoveRows(parentIndex,row,row)
        self.baseModel.removeProfile(sorted(self.baseModel.profileDict.keys())[row])
        self.endRemoveRows()
            
