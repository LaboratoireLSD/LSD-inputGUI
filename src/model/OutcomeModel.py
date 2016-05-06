
from PyQt4 import QtCore
from PyQt4.QtGui import QColor
from model.baseVarModel import GeneratorBaseModel

class OutcomeListProfileModel(QtCore.QAbstractListModel):
    '''
    Model handling profiles listing
    '''

    def __init__(self, baseModel, parent=None):
        '''
        @summary Constructor
        @param baseModel : population baseModel
        @param parent : model's view
        '''
        QtCore.QAbstractListModel.__init__(self, parent)
        self.baseModel = baseModel
        
    def getBaseModel(self):
        '''
        @summary Return base model
        '''
        return self.baseModel
    
    def rowCount(self, parent=QtCore.QModelIndex()):
        '''' 
        @summary : Reimplemented from QAbstractListModel.rowCount(self,parent)
        How many profiles do we have
        @param parent : not used
        '''
        return self.baseModel.howManyProfiles()
    
    def getVarNameFromIndex(self,index):
        '''
        @summary Return profile's name
        @param index : position of profile in model/view
        '''
        return self.baseModel.profileDict.keys()[index.row()]
    
    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' 
        @summary : Reimplemented from QAbstractListModel.data(self, index, role=QtCore.Qt.DisplayRole)
        Return data for role at position index in model. Controls what is going to be displayed in the table view.
        @param index : cell's index in model/table
        @param role : Qt item role
        '''    
        if not index.isValid() or index.row() >= self.rowCount():
            return None
        
        row = index.row()
        if role == QtCore.Qt.TextColorRole:
                return QColor(0, 0, 0)
        elif role == QtCore.Qt.BackgroundColorRole:
            return QColor(255, 255, 255)
                
        elif role == QtCore.Qt.CheckStateRole:
            return None                # Discard Unwanted checkBoxes
        
        if role == QtCore.Qt.ToolTipRole:
            return None
        
        if role == QtCore.Qt.DisplayRole:
            return self.baseModel.profileDict.keys()[row]
            
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
    
class OutcomeVarModel(QtCore.QAbstractListModel):
    '''
    Model handling outcome variable listing for population variables
    '''

    def __init__(self, baseModel,outputNode,profile,parent=None,mainWindow = None):
        '''
        @summary Constructor
        @param baseModel : population baseModel
        @param outputNode : OutComes XML node
        @param profile : currently selected profile
        @param parent : model's view
        '''
        QtCore.QAbstractListModel.__init__(self, parent)
        self.baseModel = baseModel
        self.domNode = outputNode
        self.profile = profile
        self.topWObject = mainWindow
        
    def rowCount(self, parent=QtCore.QModelIndex()):
        '''' 
        @summary : Reimplemented from QAbstractListModel.rowCount(self,parent)
        How many population variables do we have
        @param parent : not used
        '''
        return self.baseModel.howManySimVars(self.profile) + self.baseModel.howManyDemoVars(self.profile)
    
    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' 
        @summary : Reimplemented from QAbstractListModel.data(self, index, role=QtCore.Qt.DisplayRole)
        Return data for role at position index in model. Controls what is going to be displayed in the table view.
        @param index : cell's index in model/table
        @param role : Qt item role
        ''' 
        if not index.isValid() or index.row() >= self.rowCount():
            return None

        row = index.row()
        if row < self.baseModel.howManyDemoVars(self.profile):
            varName = sorted(self.baseModel.getDemoVarsList(self.profile))[row]
        else:
            row = row-self.baseModel.howManyDemoVars(self.profile)
            varName = sorted(self.baseModel.getSimVarsList(self.profile))[row]
        
        if role == QtCore.Qt.TextColorRole:
                return QColor(0, 0, 0)
        elif role == QtCore.Qt.BackgroundColorRole:
            return QColor(255, 255, 255)
                
        elif role == QtCore.Qt.CheckStateRole:
            if self.selectedVar(varName):
                return QtCore.Qt.Checked
            return QtCore.Qt.Unchecked
        if role == QtCore.Qt.ToolTipRole:
            return None
        
        if role == QtCore.Qt.DisplayRole:
            return varName
            
        return None
    
    def selectedVar(self, varName):
        '''
        @summary Return if variable is currently selected as being an outcome
        @varName variable's name
        '''
        popNode = self.domNode.firstChildElement("Population")
        subPopList = popNode.elementsByTagName("SubPopulation")
        for i in range(subPopList.count()):
            if subPopList.item(i).toElement().attribute("profile", "") == self.profile:
                profileNode = subPopList.item(i)
                profileNodeVarList =  profileNode.toElement().elementsByTagName("Variable")
                for j in range(profileNodeVarList.count()):
                    if profileNodeVarList.item(j).toElement().attribute("label", "") == varName:
                        return True
                return False
        return False
             
    def flags(self, index):
        ''' 
        @summary : Reimplemented from QAbstractListModel.flags(self,index)
        See QAbstractListModel's documentation for mode details
        @param index : cell's index in model/table
        '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        
        #Look if variable is a Demography Variable
    #    if index.row() < self.baseModel.howManyDemoVars(self.profile):
    #        varName = sorted(self.baseModel.getDemoVarsList(self.profile))[index.row()]
    #        if not self.baseModel.isSelected(self.profile,varName):
                #If it is currently a selected variable, unset it
    #            if self.selectedVar(varName):
    #                self.setData(index,0, QtCore.Qt.CheckStateRole)
                #Variable is not selected, don't let the user modify it
    #            return QtCore.Qt.NoItemFlags
            
        return QtCore.Qt.ItemFlags(QtCore.QAbstractListModel.flags(self, index) | QtCore.Qt.ItemIsUserCheckable)
     
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        ''' 
        @summary : Reimplemented from QAbstractListModel.setData(self, index, value, role=QtCore.Qt.EditRole)
        Sets data for role at position index in model. Modify model and its underlying data structure
        @param index : cell's position in model/table
        @param value : new Value
        @param role : Qt item role
        '''
        if index.isValid() and role == QtCore.Qt.CheckStateRole:
            if index.column() == 0:
                varName = self.data(index, QtCore.Qt.DisplayRole)
                popNode = self.domNode.firstChildElement("Population")
                subPopList = popNode.elementsByTagName("SubPopulation")
                for i in range(subPopList.count()):
                    if subPopList.item(i).toElement().attribute("profile", "") == self.profile:
                        profileNode = subPopList.item(i)
                        profileNodeVarList =  profileNode.toElement().elementsByTagName("Variable")
                        for j in range(profileNodeVarList.count()):
                            if profileNodeVarList.item(j).toElement().attribute("label", "") == varName:
                                profileNode.removeChild(profileNodeVarList.item(j))
                                self.topWObject.dirty = True
                                return True
                        newVarNode = profileNode.ownerDocument().createElement("Variable")
                        newVarNode.setAttribute("label",varName)
                        
                        last = False
                        for j in range(profileNodeVarList.count()+1):
                            if j == profileNodeVarList.count():
                                last = True
                            elif varName < profileNodeVarList.item(j).toElement().attribute("label", ""):
                                where = profileNodeVarList.item(j).toElement()
                                break
                        if last:
                            profileNode.appendChild(newVarNode)
                        else:
                            profileNode.insertBefore(newVarNode,where)
                        self.topWObject.dirty = True
                        return True
                newProfileNode = popNode.ownerDocument().createElement("SubPopulation")
                newProfileNode.setAttribute("profile",self.profile)
                newVarNode = popNode.ownerDocument().createElement("Variable")
                newVarNode.setAttribute("label", varName)
                newProfileNode.appendChild(newVarNode)
                popNode.appendChild(newProfileNode)
                self.topWObject.dirty = True
                return True
            
            return False
            
class OutcomeEnvModel(QtCore.QAbstractListModel):
    '''
    Model handling outcome variable listing for environment variables
    '''

    def __init__(self, envModel, outputNode, parent=None, mainWindow=None):
        '''
        @summary Constructor
        @param envModel : environment baseModel
        @param outputNode : OutComes XML node
        @param parent : model's view
        '''
        QtCore.QAbstractListModel.__init__(self, parent)
        self.envModel = envModel
        self.domNode = outputNode
        self.topWObject = mainWindow
        
    def rowCount(self, parent=QtCore.QModelIndex()):
        '''' 
        @summary : Reimplemented from QAbstractListModel.rowCount(self,parent)
        How many environment variables do we have
        @param parent : not used
        '''
        return self.envModel.rowCount()
       
    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' 
        @summary : Reimplemented from QAbstractListModel.data(self, index, role=QtCore.Qt.DisplayRole)
        Return data for role at position index in model. Controls what is going to be displayed in the table view.
        @param index : cell's index in model/table
        @param role : Qt item role
        '''
        if not index.isValid() or index.row() >= self.rowCount():
            return None
        
        row = index.row()
        varName = sorted(self.envModel.getVarLists())[row]
        
        if role == QtCore.Qt.TextColorRole:
                return QColor(0, 0, 0)
        elif role == QtCore.Qt.BackgroundColorRole:
            return QColor(255, 255, 255)
                
        elif role == QtCore.Qt.CheckStateRole:
            if self.selectedVar(varName):
                return QtCore.Qt.Checked
            return QtCore.Qt.Unchecked
        if role == QtCore.Qt.ToolTipRole:
            return None
        
        if role == QtCore.Qt.DisplayRole:
            return varName
            
        return None
    
    def selectedVar(self, varName):
        '''
        @summary Return if variable is currently selected has being an outcome
        @varName variable's name
        '''
        envNode = self.domNode.firstChildElement("Environment")
        varList = envNode.elementsByTagName("Variable")
        for i in range(varList.count()):
            if varList.item(i).toElement().attribute("label", "") == varName:
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

        return QtCore.Qt.ItemFlags(QtCore.QAbstractListModel.flags(self, index) | QtCore.Qt.ItemIsUserCheckable)
            
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        ''' 
        @summary : Reimplemented from QAbstractListModel.setData(self, index, value, role=QtCore.Qt.EditRole)
        Sets data for role at position index in model. Modify model and its underlying data structure
        @param index : cell's position in model/table
        @param value : new Value
        @param role : Qt item role
        '''
        if index.isValid() and role == QtCore.Qt.CheckStateRole:
            if index.column() == 0:
                varName = self.data(index, QtCore.Qt.DisplayRole)
                envNode = self.domNode.firstChildElement("Environment")
                varList = envNode.elementsByTagName("Variable")
                for i in range(varList.count()):
                    if varList.item(i).toElement().attribute("label", "") == varName:
                        envNode.removeChild(varList.item(i))
                        self.topWObject.dirty = True
                        return True
                    
                newVarNode = envNode.ownerDocument().createElement("Variable")
                newVarNode.setAttribute("label", varName)
                envNode.appendChild(newVarNode)
                self.topWObject.dirty = True
                return True
        return False

