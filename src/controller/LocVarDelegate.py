"""
.. module:: LocVarDelegate

.. codeauthor::  Mathieu Gagnon <mathieu.gagnon.10@ulaval.ca>

:Created on: 2011-04-04

"""

from PyQt4 import QtCore, QtGui
import Definitions

class LocVarsDelegate(QtGui.QItemDelegate):
    '''
    This class is responsible of controlling the user interaction with a QTableView.(mainEditorFrame.locVarTblView in this case).
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
        if index.column() == 0:
            self.editor = QtGui.QLineEdit(parent)
            self.connect(self.editor,QtCore.SIGNAL("returnPressed()"),self.commitAndCloseEditor)
        elif index.column() == 1:
            self.editor = QtGui.QComboBox(parent)
            self.connect(self.editor, QtCore.SIGNAL("currentIndexChanged(int)"), self.commitAndCloseEditor)
        elif index.column() == 2:
            #Must check if we edit a vector or a single value
            if not isinstance(index.model().getVarValueFromIndex(index),list):
                self.editor = QtGui.QLineEdit(parent)
                self.connect(self.editor, QtCore.SIGNAL("returnPressed()"), self.commitAndCloseEditor)
            else:  
                self.editor = QtGui.QComboBox(parent)
                self.editor.setDuplicatesEnabled(True)
                self.editor.setEditable(True)
                self.editor.setInsertPolicy(QtGui.QComboBox.InsertAtCurrent)
                self.connect(self.editor, QtCore.SIGNAL("editTextChanged(const QString)"),self.hook)
        
        return self.editor
        
    def setEditorData(self, editor, index):
        '''
        Overrides QItemDelegate's setEditorData method. Sets the widget's data after createEditor has created it.
        
        :param editor: Widget to set.
        :param index: Index of the widget.
        :type editor: PyQt4.QtGui.QWidget
        :type index: PyQt4.QtCore.QModelIndex
        '''
        if index.column() == 0:
            currLocVarName = index.model().getVarNameFromIndex(index)
            editor.setText(currLocVarName)
        elif index.column() == 1:
            #Type case
            currLocVarType = index.model().getVarTypeFromIndex(index)
            self.editor.addItems(list(map(Definitions.typeToDefinition, Definitions.baseTypes)))
            editor.setCurrentIndex(editor.findText(Definitions.typeToDefinition(currLocVarType)))
            self.editor.view().setMinimumWidth(self.calculateListWidth())
        elif index.column() == 2:
            #Value case
            currLocVarValue = index.model().getVarValueFromIndex(index)
            if isinstance(editor,QtGui.QComboBox):
                editor.addItems(currLocVarValue)
                #On windows, needed to correctly display on first show if combobox is too small for items in list
                self.editor.view().setMinimumWidth(self.calculateListWidth())
            else:
                editor.setText(currLocVarValue)
            
    def setModelData(self, editor, model, index):
        '''
        Overrides QItemDelegate's setModelData method. Sets the model data after a user interaction with the editor.
        
        :param editor: Widget that contains the data.
        :param model: Item where to put data.
        :param index: Which index to put data.
        :type editor: PyQt4.QtGui.QWidget
        :type model: PyQt4.QtCore.QAbstractItemModel
        :type index: PyQt4.QtCore.QModelIndex
        '''
        baseModel = model.baseModel
        if index.column() == 0:
            if baseModel.locVarExists(model.node, editor.text()):
                print("Warning : Local Variable " + str(model.getVarNameFromIndex(index))+" already exists")
            else:
                model.setData(index, editor.text())
        elif index.column() == 1:
            model.setData(index, editor.currentText())
        elif index.column() == 2:
            if isinstance(self.editor,QtGui.QComboBox):
                values = []
                for i in range(editor.count()):
                    values.append(editor.itemText(i))
                model.setData(index, values)
            else:        
                model.setData(index, editor.text())
            
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
        return minimumWidth + 30
      
    def hook(self, newText):
        '''
        Little function that allows the editor to correctly update itself when a user edits a vector via an editable comboBox.
        
        :param newText: The new data to use for the update.
        :type newText: String
        '''
        self.editor.setItemText(self.editor.currentIndex(),newText)
        
    def commitAndCloseEditor(self):
        '''
        Overrides QItemDelegate's commitAndCloseEditor method.
        '''
        #For the moment, emitting both signals seems to call setModelData twice,
        #hence creating index mismatches and overwriting the wrong variables in the model
        #self.emit(QtCore.SIGNAL("commitData(QWidget*)"), self.sender())
        self.emit(QtCore.SIGNAL("closeEditor(QWidget*)"), self.sender())
