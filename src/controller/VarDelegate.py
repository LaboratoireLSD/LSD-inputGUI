"""
.. module:: VarDelegate

.. codeauthor::  Marc-Andre Gardner

:Created on: 2009-08-27

"""
from PyQt4 import QtCore, QtGui

from editor.mainEditorFrame import MainEditorWindow
from model.PrimitiveModel import Primitive
import Definitions


class VarSimDelegate(QtGui.QItemDelegate):
    '''
    This class is responsible of controlling the user interaction with a QTableView.(popTab.tableView_Supp in this case).
    '''

    def __init__(self, parent, windowObject):
        '''
        Constructor.
        
        :param parent: QTableView associated with this delegate.
        :param windowObject: Reference to the editor frame.
        :type parent: PyQt4.QtGui.QTableView
        :type windowObject: :class:`.MainWindow`
        '''
        QtGui.QItemDelegate.__init__(self, parent)
        self.parent = parent
        self.topObject = windowObject
    
    def createEditor(self, parent, option, index):
        '''
        Overrides QItemDelegate's createEditor method. Creates the widget  when a user double click and item of the QTableView.
        
        :param parent: Parent of the new widget.
        :param option:
        :param index: Index for the creation.
        :type option: Not used
        :type index: PyQt4.QtCore.QModelIndex
        :return: PyQt4.QtGui.QLineEdit | PyQt4.QtGui.QComboBox.
        '''
        varName = index.model().getVarFromIndex(index)
        if index.column() == 0:
            self.editor = QtGui.QLineEdit(parent)
            self.connect(self.editor, QtCore.SIGNAL("returnPressed()"), self.commitAndCloseEditor)
            return self.editor
        elif index.column() == 3:
            varName = index.model().getVarFromIndex(index)
            varNode = index.model().baseModel.domNodeDict[index.model().profileName][varName]
            pmtNode = varNode.firstChildElement("PrimitiveTree")
            self.editor = MainEditorWindow(pmtNode.firstChild(), self.topObject, varName)
            self.editor.exec_()
            index.model().baseModel._findDependencies(index.model().profileName, varName)
            
            #Updating the variable's type
            primitive = Primitive(None, None, self, pmtNode.firstChild())
            profile = index.model().profileName
            returnType = primitive._getReturnType()
            #Updates the validity (Valid, Warning, Error or Unknown)
            index.model().baseModel.updateValidationState(varName, primitive, profile)
            index.model().baseModel.setVarType(profile, varName, returnType)

    def setEditorData(self, editor, index):
        '''
        Overrides QItemDelegate's setEditorData method. Sets the widget's data after createEditor has created it
        
        :param PyQt4.QtGui.QWidget editor: Widget to set.
        :param PyQt4.QtCore.QModelIndex index: Index of the widget.
        '''
        
        if index.column() == 0:
            text = index.model().data(index, QtCore.Qt.DisplayRole)
            editor.setText(text)
            
    def setModelData(self, editor, model, index):
        '''
        Overrides QItemDelegate's setModelData method. Sets the model data after a user interaction with the editor.
        
        :param editor: Not used
        :param PyQt4.QtCore.QAbstractItemModel model: Item where to put data.
        :param PyQt4.QtCore.QModelIndex index: Which index to put data.
        '''
        if index.column()  == 0: 
            model.setData(index, self.editor.text())
        elif index.column() == 1:
            model.setData(index, self.editor.currentText())
    
    def calculateListWidth(self):
        '''
        Calculate pixel width of largest item in drop-down list.
        
        :return: Int.
        '''
        fm = QtGui.QFontMetrics(self.editor.view().font())
        minimumWidth = 0
        for i in range(self.editor.count()):
            if fm.width(self.editor.itemText(i)) > minimumWidth:
                minimumWidth = fm.width(self.editor.itemText(i))
        return minimumWidth + 10
    
    def commitAndCloseEditor(self):
        '''
        Overrides QItemDelegate's commitAndCloseEditor method.
        '''
        #For the moment, emitting both signals seems to call setModelData twice,
        #hence creating index mismatches and overwriting the wrong variables in the model
        #self.emit(QtCore.SIGNAL("commitData(QWidget*)"), self.sender())
        self.emit(QtCore.SIGNAL("closeEditor(QWidget*)"), self.sender())


class VarGeneratorDelegate(QtGui.QItemDelegate):
    '''
    This class is responsible of controlling the user interaction with a QTableView.(simTab.proMgr.tableView in this case).
    '''

    def __init__(self, parent, windowObject):
        '''
        Constructor.
        
        :param parent: QTableView associated with this delegate.
        :param windowObject: Reference to the editor frame.
        :type parent: PyQt4.QtGui.QTableView
        :type windowObject: :class:`.MainWindow`
        '''
        QtGui.QItemDelegate.__init__(self, parent)
        self.parent = parent
        self.topObject = windowObject

    def createEditor(self, parent, option, index):
        '''
        Overrides QItemDelegate's createEditor method. Creates the widget when a user double click and item of the QTableView.
        
        :param parent: Parent of the new widget.
        :param option:
        :param index: Index for the creation.
        :type option: Not used
        :type index: PyQt4.QtCore.QModelIndex
        :return: PyQt4.QtGui.QSpinBox | PyQt4.QtGui.QComboBox.
        '''
        if index.column() == 0:
            self.editor = QtGui.QComboBox(parent)
            self.connect(self.editor, QtCore.SIGNAL("currentIndexChanged(int)"), self.commitAndCloseEditor)
        elif index.column() == 1 or index.column() == 2 :
            self.editor = QtGui.QSpinBox(parent)
            self.editor.setMaximum(2000000000)
            self.connect(self.editor, QtCore.SIGNAL("editingFinished()"), self.commitAndCloseEditor)
        
        return self.editor

    def setEditorData(self, editor, index):
        '''
        Overrides QItemDelegate's setEditorData method. Sets the widget's data after createEditor has created it
        
        :param editor: Widget to set.
        :param index: Index of the widget.
        :type editor: PyQt4.QtGui.QWidget
        :type index: PyQt4.QtCore.QModelIndex
        '''
        if index.column() == 1 or index.column() == 2:
            value = index.model().data(index, QtCore.Qt.DisplayRole)
            editor.setValue(int(value))
        elif index.column() == 0:
            profiles = list(index.model().baseModel.profileDict.keys())
            editor.addItems(profiles)
            #On windows, needed to correctly display on first show if combobox is too small for items in list
            self.editor.view().setMinimumWidth(self.calculateListWidth())
    
    def setModelData(self, editor, model, index):
        '''
        Overrides QItemDelegate's setModelData method. Sets the model data after a user interaction with the editor
        
        :param editor:
        :param model:
        :param index: see QItemDelegate's doc for more information
        '''
        if index.column() == 1 or index.column() == 2:
            model.setData(index, self.editor.value())
        elif index.column() == 0:
            model.setData(index, self.editor.currentText())
        
    def calculateListWidth(self):
        '''
        Calculate pixel width of largest item in drop-down list.
        
        :return: Int.
        '''
        fm = QtGui.QFontMetrics(self.editor.view().font())
        minimumWidth = 0
        for i in range(self.editor.count()):
            if fm.width(self.editor.itemText(i)) > minimumWidth:
                minimumWidth = fm.width(self.editor.itemText(i))
        return minimumWidth + 10
    
    def commitAndCloseEditor(self):
        '''
        Overrides QItemDelegate's commitAndCloseEditor method.
        '''
        #For the moment, emitting both signals seems to call setModelData twice,
        #hence creating index mismatches and overwriting the wrong variables in the model
        #self.emit(QtCore.SIGNAL("commitData(QWidget*)"), self.sender())
        self.emit(QtCore.SIGNAL("closeEditor(QWidget*)"), self.sender())

class SimpleVarDelegate(QtGui.QItemDelegate):
    '''
    Simplified VarSimDelegate to be used in Demography File Editor.
    '''

    def __init__(self, parent, windowObject):
        '''
        Constructor
        
        :param parent: QTableView associated with this delegate.
        :param windowObject: Reference to the editor frame.
        :type parent: PyQt4.QtGui.QTableView
        :type windowObject: :class:`.MainWindow`
        '''
        QtGui.QItemDelegate.__init__(self, parent)
        self.parent = parent
        self.topObject = windowObject
        
    def createEditor(self, parent, option, index):
        '''
        Overrides QItemDelegate's createEditor method. Creates the widget  when a user double click and item of the QTableView.
        
        :param parent: Parent of the new widget.
        :param option:
        :param index: Index for the creation.
        :type option: Not used
        :type index: PyQt4.QtCore.QModelIndex
        :return: PyQt4.QtGui.QLineEdit | PyQt4.QtGui.QComboBox.
        '''
        varName = index.model().getVarFromIndex(index)
        if index.column() == 0:
            self.editor = QtGui.QLineEdit(parent)
            self.connect(self.editor, QtCore.SIGNAL("returnPressed()"), self.commitAndCloseEditor)
            return self.editor
        elif index.column() == 1:
            self.editor = QtGui.QComboBox(parent)
            self.connect(self.editor, QtCore.SIGNAL("currentIndexChanged(int)"), self.commitAndCloseEditor)
            return self.editor
        elif index.column() == 4:
            varName = index.model().getVarFromIndex(index)
            varNode = index.model().baseModel.domNodeDict[varName]
            pmtNode = varNode.firstChildElement("PrimitiveTree")
            treeEditor = MainEditorWindow(pmtNode.firstChild(),self.topObject, varName)
            #treeEditor
            treeEditor.exec_()
            index.model().baseModel._findDependencies(varName)
            index.model().baseModel._findRange(varName)
    
    def setEditorData(self, editor, index):
        '''
        Overrides QItemDelegate's setEditorData method. Sets the widget's data after createEditor has created it
        
        :param editor: Widget to set.
        :param index: Index of the widget.
        :type editor: PyQt4.QtGui.QWidget
        :type index: PyQt4.QtCore.QModelIndex
        '''
        baseModel = index.model().baseModel
        varName = index.model().getVarFromIndex(index)
        
        if index.column() == 0:
            text = index.model().data(index, QtCore.Qt.DisplayRole)
            editor.setText(text)
        
        elif index.column() == 1:
            self.editor.addItems(Definitions.baseTypes)
            self.editor.setCurrentIndex(self.editor.findText(baseModel.getVarType(varName)))
            #On windows, needed to correctly display on first show if combobox is too small for items in list
            self.editor.view().setMinimumWidth(self.calculateListWidth())
    
    def setModelData(self, editor, model, index):
        '''
        Overrides QItemDelegate's setModelData method. Sets the model data after a user interaction with the editor.
        
        :param editor:
        :param model: Item where to put data.
        :param index: Which index to put data.
        :type editor: Not used
        :type model: PyQt4.QtCore.QAbstractItemModel
        :type index: PyQt4.QtCore.QModelIndex
        '''
        if index.column()  == 0: 
            model.setData(index, self.editor.text())
        elif index.column() == 1:
            model.setData(index, self.editor.currentText())
    
    def calculateListWidth(self):
        '''
        Calculate pixel width of largest item in drop-down list.
        '''
        fm = QtGui.QFontMetrics(self.editor.view().font())
        minimumWidth = 0
        for i in range(self.editor.count()):
            if fm.width(self.editor.itemText(i)) > minimumWidth:
                minimumWidth = fm.width(self.editor.itemText(i))
        return minimumWidth + 10
    
    def commitAndCloseEditor(self):
        '''
        Overrides QItemDelegate's commitAndCloseEditor method.
        '''
        #For the moment, emitting both signals seems to call setModelData twice,
        #hence creating index mismatches and overwriting the wrong variables in the model
        #self.emit(QtCore.SIGNAL("commitData(QWidget*)"), self.sender())
        self.emit(QtCore.SIGNAL("closeEditor(QWidget*)"), self.sender())
