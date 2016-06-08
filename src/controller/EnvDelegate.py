"""
.. module:: EnvDelegate

.. codeauthor::  Mathieu Gagnon <mathieu.gagnon.10@ulaval.ca>

:Created on: 2009-08-27

"""

from PyQt4 import QtCore, QtGui
import Definitions


class EnvDelegate(QtGui.QItemDelegate):
    '''
    This class is responsible of controlling the user interaction with a QTableView.(envTab.tableView in this case).
    '''

    def __init__(self, parent, windowObject):
        '''
        Constructor.
        
        :param parent: QTableView associated with this delegate.
        :param windowObject: Reference to the MainFrame.
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
        :param index: Index for creation.
        :type option: Not used
        :type index: PyQt4.QtCore.QModelIndex
        :return: PyQt4.QtGui.QLineEdit | PyQt4.QtGui.QComboBox.
        '''
        if index.column() == 0 or index.column() == 2:
            self.editor = QtGui.QLineEdit(parent)
            self.connect(self.editor, QtCore.SIGNAL("returnPressed()"), self.commitAndCloseEditor)
        
        elif index.column() == 1:
            self.editor = QtGui.QComboBox(parent)
            self.connect(self.editor, QtCore.SIGNAL("activated(int)"), self.commitAndCloseEditor)
        
        return self.editor
    
    def setEditorData(self, editor, index):
        '''
        Overrides QItemDelegate's setEditorData method. Sets the widget's data after createEditor has created it.
        
        :param editor: Widget to set.
        :param index: Index of the widget.
        :type editor: PyQt4.QtGui.QWidget
        :type index: PyQt4.QtCore.QModelIndex
        '''
        if index.column() == 0 or index.column()== 2:
            text = str(index.model().data(index, QtCore.Qt.DisplayRole))
            editor.setText(text)
        
        elif index.column() == 1:
            self.editor.addItems(Definitions.baseTypes)
            #On windows, needed to correctly display on first show if combobox is too small for items in list
            self.editor.view().setMinimumWidth(self.calculateListWidth())
            
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
            model.setData(index, self.editor.currentText())
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
    
    def commitAndCloseEditor(self):
        '''
        Overrides QItemDelegate's commitAndCloseEditor method.
        '''
        #For the moment, emitting both signals seems to call setModelData twice,
        #hence creating index mismatches and overwriting the wrong variables in the model
        #self.emit(QtCore.SIGNAL("commitData(QWidget*)"), self.sender())
        self.emit(QtCore.SIGNAL("closeEditor(QWidget*)"), self.sender())

        
