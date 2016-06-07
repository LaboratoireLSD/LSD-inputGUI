"""
.. module:: treeComponents

.. codeauthor::  Mathieu Gagnon <mathieu.gagnon.10@ulaval.ca>

:Created on: 2010-11-07

"""
from PyQt4 import QtCore, QtGui
from util.DocPrimitive import PrimitiveDict


class ChoiceComboBoxModel(QtCore.QAbstractItemModel):
    '''
    Model used to list Primitive Choices in a comboBox in the tree editor
    '''
    def __init__(self,assocPmt):
        '''
        Constructor.
        
        :param assocPmt: current primitive
        '''
        QtCore.QAbstractItemModel.__init__(self)
        self.pmtChoice = assocPmt
        self.pmtDictRef = PrimitiveDict()
        self.dictNames = []
        self.dictRealNames = {}
        self.listChoices = self.getListOfPmtList()
        
    def getListOfPmtList(self):
        '''
        Return Primitive List and the name of the dictionary they belong to at the beginning of each sublist.
        '''
        tmpDict = {}
        for dictionary in self.pmtDictRef.dictPrimitives.keys():
            if self.pmtDictRef.getDictNameFromFilePath(dictionary) != "":
                tmpDict[self.pmtDictRef.getDictNameFromFilePath(dictionary)] = []
                self.dictNames.append(self.pmtDictRef.getDictNameFromFilePath(dictionary))
        for pmtChoice in self.pmtChoice.getParentPrimitive().guiGetChoicesList(self.pmtChoice.getParentPrimitive().getChildPos(self.pmtChoice)):
            currentDictPath = self.pmtDictRef.getPrimitiveDictPath(pmtChoice)
            currentDictName = self.pmtDictRef.getDictNameFromFilePath(currentDictPath)
            tmpDict[currentDictName].append(pmtChoice)
            self.dictRealNames[pmtChoice] = pmtChoice
            if self.pmtDictRef.dictPrimitives[currentDictPath][pmtChoice].getMappedName() != pmtChoice:
                tmpDict[currentDictName].pop()
                tmpDict[currentDictName].append(self.pmtDictRef.dictPrimitives[currentDictPath][pmtChoice].getMappedName())
                del self.dictRealNames[pmtChoice]
                self.dictRealNames[self.pmtDictRef.dictPrimitives[currentDictPath][pmtChoice].getMappedName()] = pmtChoice
        
        finalList = []
        for dictionary in tmpDict.keys():
            finalList.append(dictionary)
            for pmtChoice in sorted(tmpDict[dictionary]):
                finalList.append(pmtChoice)
            
        return finalList
    
    def columnCount(self, parent=QtCore.QModelIndex()):
        '''
        Reimplementation of QAbstactItemModel.columnCount(self,parent=QtCore.QModelIndex()).
        Since this model underlies a comboBox, column count is fixed to 1.
        Even if it is implicit that column count is going to be one since we apply this model to a combo box.
        Qt complains if it is not overridden.
        
        :param parent:
        :type parent: Not used
        '''
        return 1
    
    def parent(self, index):
        '''
        Reimplementation of QAbstactItemModel.parent(self,index).
        Return index's parent.
        Since this model underlies a comboBox, model items do not really have a parent, so returning an invalid index is ok.
        Qt complains if it is not overridden.
        
        :param index:
        :type index: Not used
        '''
        return QtCore.QModelIndex() 
    
    def rowCount(self, parent=QtCore.QModelIndex()):
        ''' 
        Reimplemented from QAbstractItemModel.rowCount(self,parent).
        How many unused parameters do we have.
        
        :param parent:
        :type parent: Not used
        '''
        return len(self.listChoices)
        
    
    def index(self, row, column, parent = QtCore.QModelIndex()) :
        '''
        Reimplemented from QAbstractItemModel.index(self, row, column, parent = QtCore.QModelIndex()).
        Create a model index if there is data at this position in the model.
        
        :param row: Position in the model
        :param column: position in the model
        :param parent:
        :type row: Int
        :type column: Int
        :type parent: Not used
        '''
        if row >= self.rowCount() or column != 0:
            return QtCore.QModelIndex()  
        else:
            return self.createIndex(row, column)
        
    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' 
        Reimplemented from QAbstracItemModel.data(self, index, role=QtCore.Qt.DisplayRole).
        Return data for role at position index in model. Controls what is going to be displayed in the table view.
        
        :param index: Cell's index in model/table
        :param role: Qt item role
        :type index: QModelIndex
        :type role: Int
        ''' 
        if not index.isValid():
            return None
        
        row = index.row()
        
        if role == QtCore.Qt.CheckStateRole:
            return None                # Discard Unwanted checkBoxes
        
        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                if self.listChoices[row] in self.dictNames:
                    return self.listChoices[row]
                else:
                    return "   " + self.listChoices[row]
       
    def flags(self, index):
        ''' 
        Reimplemented from QAbstractItemModel.flags(self,index).
        See QAbstractItemModel's documentation for more details.
        
        :param index: Cell's index in model/table
        :type index: QModelIndex
        '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        
        if self.data(index) in self.dictNames:
            return QtCore.Qt.ItemFlags(QtCore.Qt.NoItemFlags)
        else:
            return QtCore.Qt.ItemFlags(QtCore.QAbstractItemModel.flags(self, index))
