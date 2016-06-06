"""
.. module:: SensAnalysisDelegate

.. codeauthor::  Mathieu Gagnon <mathieu.gagnon.10@ulaval.ca>

:Created on: 2010-08-24

"""

from PyQt4 import QtCore, QtGui

class SensAnalysisDelegate(QtGui.QItemDelegate):
    '''
    This class is responsible of controlling the user interaction with a QTableView.(saTab.saList in this case).
    '''
    def __init__(self, parent):
        '''
        Constructor.
        
        :param parent: QTableView associated with this delegate.
        :type parent: PyQt4.QtGui.QTableView
        '''
        QtGui.QItemDelegate.__init__(self, parent)
        self.parent = parent

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
        if index.column() <=1:
            return
        if index.model().getDataType(index) == "Vector":
            self.editor = QtGui.QComboBox(parent)
            self.editor.setDuplicatesEnabled(True)
            self.editor.setEditable(True)
            self.editor.setInsertPolicy(QtGui.QComboBox.InsertAtCurrent)
            self.connect(self.editor, QtCore.SIGNAL("editTextChanged(const QString)"),self.hook)
        else:
            self.editor = QtGui.QLineEdit(parent)
        
        self.editor.setInputMethodHints(QtCore.Qt.ImhFormattedNumbersOnly)
        return self.editor
    
    def hook(self, newText):
        '''
        Little function that allows the editor to correctly update itself when a user edits a vector via an editable comboBox.
        
        :param newText: The new data to use for the update.
        :type newText: String
        '''
        self.editor.setItemText(self.editor.currentIndex(), newText)
        
    def setEditorData(self, editor, index):
        '''
        Overrides QItemDelegate's setEditorData method. Sets the widget's data after createEditor has created it.
        
        :param editor: Widget to set.
        :param index: Index of the widget.
        :type editor: PyQt4.QtGui.QWidget
        :type index: PyQt4.QtCore.QModelIndex
        '''
        if isinstance(editor, QtGui.QComboBox):
            editor.addItems(index.model().getData(index))
            #On windows, needed to correctly display on first show if combobox is too small for items in list
            self.editor.view().setMinimumWidth(self.calculateListWidth())
        else:
            editor.setText(index.model().getData(index))
    
    def setModelData(self, editor, model, index):
        '''
        Overrides QItemDelegate's setModelData method. Sets the model data after a user interaction with the editor
        
        :param editor: Widget that contains the data.
        :param model: 
        :param index: Which index to put data.
        :type editor: PyQt4.QtGui.QWidget
        :type model: Not used
        :type index: PyQt4.QtCore.QModelIndex
        '''
        if isinstance(editor, QtGui.QComboBox):
            for i in range(editor.count()):
                index.model().setData(index, editor.itemText(i),i)     
        else:
            index.model().setData(index, editor.text())
    
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
        return minimumWidth
        
    def commitAndCloseEditor(self):
        '''
        Overrides QItemDelegate's commitAndCloseEditor method.
        '''
        #For the moment, emitting both signals seems to call setModelData twice,
        #hence creating index mismatches and overwriting the wrong variables in the model
        #self.emit(QtCore.SIGNAL("commitData(QWidget*)"), self.sender())
        self.emit(QtCore.SIGNAL("closeEditor(QWidget*)"), self.sender())
