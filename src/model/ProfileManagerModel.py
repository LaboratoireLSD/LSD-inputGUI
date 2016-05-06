
from PyQt4 import QtCore, QtGui
from model.baseVarModel import GeneratorBaseModel

class ProfileManagerModel(QtCore.QAbstractListModel):
    '''
    Model handling profile representation
    '''

    def __init__(self, parent=None):
        '''
        @summary Constructor
        @param parent : model's view
        '''
        QtCore.QAbstractListModel.__init__(self, parent)
        self.baseModel = GeneratorBaseModel()
    
    def getBaseModel(self):
        '''
        @summary Return base model
        '''
        return self.baseModel
    
    def rowCount(self, parent=QtCore.QModelIndex()):
        ''' 
        @summary : Reimplemented from QAbstractListModel.rowCount(self,parent)
        How many profiles do we have
        @param parent : not used
        '''
        return len(self.baseModel.profileDict.keys())
    
    def getProfileFromIndex(self,index):
        '''
        @summary : Return profile name
        @param index : profile's position in model/index
        '''
        return sorted(self.baseModel.profileDict.keys())[index.row()]
    
    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' 
        @summary : Reimplemented from QAbstractListModel.data(self, index, role=QtCore.Qt.DisplayRole)
        Return data for role at position index in model. Controls what is going to be displayed in the table view.
        @param index : cell's index in model/table
        @param role : Qt item role
        ''' 
        if not index.isValid():
            return None
        
        if role == QtCore.Qt.TextColorRole:
            return QtGui.QColor(0, 0, 0)
                
        elif role == QtCore.Qt.CheckStateRole:
            return None                #Discard unwanted checkboxes
        
        elif role == QtCore.Qt.ToolTipRole:
            return None
        
        elif role != QtCore.Qt.DisplayRole:
            return None

        return sorted(self.baseModel.profileDict.keys())[index.row()]

    def headerData(self, section, orientation, role):
        ''' 
        @summary : Reimplemented from QAbstractListModel.headerData(self, section, orientation, role)
        See QAbstractListModel's documentation for mode details
        @param section : model's column or row
        @param orientation : horizontal or vertical
        @param role : Qt item role
        '''
        if role != QtCore.Qt.DisplayRole:
            return None
        
        if orientation == QtCore.Qt.Horizontal:
           
            if section == 0:
                return "Profiles"
        else:
            return str(section + 1)  
        
        return None
    
    def flags(self, index):
        ''' 
        @summary : Reimplemented from QAbstractListModel.flags(self,index)
        See QAbstractListModel's documentation for mode details
        @param index : cell's index in model/table
        '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        return QtCore.Qt.ItemFlags(QtCore.QAbstractListModel.flags(self, index))

    def insertProfile(self, parentIndex, row, profileName, demoFileName="", simVarProfileFrom="", acceptFuncProfileFrom=""):
        '''
        @summary Add new profile to profiles List
        @param parentIndex : parent's index (not relevant for list views)
        @param row : insertion row in model
        @param profileName : profile's name
        @param demoFileName : name of the demography file used for the new profile
        @param simVarProfileFrom : name of the profile we copy the simulation variables from, or empty string
        @param simVarProfileFrom : name of the profile we copy the Accept function from, or empty string
        '''
        self.beginInsertRows(parentIndex, row, row)
        self.baseModel.addProfile(profileName,demoFileName,simVarProfileFrom,acceptFuncProfileFrom)
        self.endInsertRows()

    def cloneProfile(self,cloneName,clonedProfileName):
        '''
        @summary Add new profile to profiles List by cloning and already existing profile
        @param cloneName : new profile's name
        @param clonedProfileName : name of the profile we copy the variables from
        '''
        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(),self.rowCount())
        self.baseModel.cloneProfile(cloneName,clonedProfileName)
        self.endInsertRows()

    def removeProfile(self,parentIndex, row):
        '''
        @summary Delete a profile
        @param parentIndex : parent's index (not relevant for list views)
        @param row : position of the deleted profile in model/view
        '''
        self.beginRemoveRows(parentIndex,row,row)
        self.baseModel.removeProfile(sorted(self.baseModel.profileDict.keys())[row])
        self.endRemoveRows()
            
