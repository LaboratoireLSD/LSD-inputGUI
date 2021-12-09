"""
.. module:: ParamDelegate

.. codeauthor::  Mathieu Gagnon <mathieu.gagnon.10@ulaval.ca>

:Created on: 2010-10-04

"""
from PyQt4 import QtCore, QtGui
import Definitions


class ParamDelegate(QtGui.QItemDelegate):
    '''
    This class is responsible of controlling the user interaction with a QTableView.(paramTab.tableView in this case)
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
        Overrides QItemDelegate's createEditor method. Creates the widget  when a user double click an item of the QTableView.
        
        :param parent: Parent of the new widget.
        :param option:
        :param index: Index for the creation.
        :type option: Not used
        :type index: PyQt4.QtCore.QModelIndex
        :return: PyQt4.QtGui.QLineEdit | PyQt4.QtGui.QComboBox.
        '''
        if index.column() == 0:
            self.editor = QtGui.QLineEdit(parent)
            self.connect(self.editor, QtCore.SIGNAL("returnPressed()"), self.commitAndCloseEditor)
        
        elif index.column() == 1:
            self.editor = QtGui.QComboBox(parent)
            self.connect(self.editor, QtCore.SIGNAL("activated(int)"), self.commitAndCloseEditor)
        
        elif index.column() == 2:
            refName = index.model().baseModel.modelMapper[index.row()]
            if index.model().baseModel.getContainerType(refName) == "Scalar":
                self.editor = QtGui.QLineEdit(parent)
                self.connect(self.editor, QtCore.SIGNAL("returnPressed()"), self.commitAndCloseEditor)
            else:  
                self.editor = QtGui.QComboBox(parent)
                self.editor.setDuplicatesEnabled(True)
                self.editor.setEditable(True)
                self.editor.setInsertPolicy(QtGui.QComboBox.InsertAtCurrent)
                self.editor.setCompleter(None)
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
            originalData = index.model().data(index, QtCore.Qt.DisplayRole)
            editor.setText(originalData)
        
        elif index.column() == 1:
            #Map the base types to appear as their full name in the combobox
            items = map(Definitions.typeToDefinition, Definitions.baseTypes)
            self.editor.addItems(sorted(items,key=str.lower))
            #Partitioning the text in the combobox and keeping only the definition without the word " list"
            self.editor.setCurrentIndex(self.editor.findText(index.model().data(index, QtCore.Qt.DisplayRole).partition(" list")[0]))
            #On windows, needed to correctly display on first show if combobox is too small for items in list
            self.editor.view().setMinimumWidth(self.calculateListWidth())
        elif index.column() == 2:
            refName = index.model().baseModel.modelMapper[index.row()]
            if isinstance(editor, QtGui.QComboBox):
                editor.addItems(index.model().baseModel.getValue(refName))
                #On windows, needed to correctly display on first show if combobox is too small for items in list
                self.editor.view().setMinimumWidth(self.calculateListWidth())
            else:
                editor.setText(index.model().baseModel.getValue(refName)[0])
                
    def setModelData(self, editor, model, index):
        '''
        Overrides QItemDelegate's setModelData method. Sets the model data after a user interaction with the editor
        
        :param editor: Widget that contains the data.
        :param model: Item where to put data.
        :param index: Which index to put data.
        :type editor: PyQt4.QtGui.QWidget
        :type model: PyQt4.QtCore.QAbstractItemModel
        :type index: PyQt4.QtCore.QModelIndex
        '''
        if isinstance(editor, QtGui.QComboBox):
            if index.column() == 1:
                #Since the combobox contains the full name of the base types, we change them back to their real type.
                model.setData(index, Definitions.definitionToType(self.editor.currentText()))
            else:
                values = []
                for i in range(editor.count()):
                    values.append(editor.itemText(i))
                model.setData(index, values)
        else: 
            model.setData(index, self.editor.text())
            
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
    
    def hook(self, newText):
        '''
        Little function that allows the editor to correctly update itself when a user edits a vector via an editable comboBox.
        
        :param newText: The new data to use for the update.
        :type newText: String
        '''
        
        #For some reasons, cursor moves when doing so, so we save cursor position and resets it after changing text
        #For some other reasons, reseting cursor sometimes select text, so we unselect it
        cursorPosAt = self.editor.lineEdit().cursorPosition()
        self.editor.setItemText(self.editor.currentIndex(),newText)
        self.editor.lineEdit().setCursorPosition(cursorPosAt)
        
    def commitAndCloseEditor(self):
        '''
        Overrides QItemDelegate's commitAndCloseEditor method.
        '''
        #For the moment, emitting both signals seems to call setModelData twice,
        #hence creating index mismatches and overwriting the wrong variables in the model
        #self.emit(QtCore.SIGNAL("commitData(QWidget*)"), self.sender())
        self.emit(QtCore.SIGNAL("closeEditor(QWidget*)"), self.sender())

        
