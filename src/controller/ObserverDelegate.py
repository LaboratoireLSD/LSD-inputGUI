"""
.. module:: ObserverDelegate

.. codeauthor::  Mathieu Gagnon <mathieu.gagnon.10@ulaval.ca>

:Created on: 2009-12-16

"""
from PyQt4 import QtCore, QtGui
from model.baseTreatmentsModel import BaseTreatmentsModel

class ObserverDelegate(QtGui.QItemDelegate):
    '''
    This class is responsible of controlling the user interaction with a QListView.(obsTab.clockObservers in this case).
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
        :param index: 
        :type option: Not used
        :type index: Not used
        :return: PyQt4.QtGui.QComboBox.
        '''
        self.editor = QtGui.QComboBox(parent)
        self.connect(self.editor,QtCore.SIGNAL("activated(int)"), self.commitAndCloseEditor)
        return self.editor
    
    def setEditorData(self, editor, index):
        '''
        Overrides QItemDelegate's setEditorData method. Sets the widget's data after createEditor has created it
        
        :param editor: Widget to set.
        :param index: Index of the widget.
        :type editor: PyQt4.QtGui.QWidget
        :type index: PyQt4.QtCore.QModelIndex
        '''
        #Text that the current cell contains
        selectedText = self.parent.model().data(index)
        baseTrModel = BaseTreatmentsModel()
        processes = list(baseTrModel.getTreatmentsDict().keys())
        processes.sort(key=lambda x: x.lower())
        editor.addItems(processes)
        #Set the current index of the QComboBox in connection with the selectedText
        editor.setCurrentIndex(processes.index(selectedText))
        #On windows, needed to correctly display on first show if combobox is too small for items in list
        self.editor.view().setMinimumWidth(self.calculateListWidth())
    
    def setModelData(self, editor, model, index):
        '''
        Overrides QItemDelegate's setModelData method. Sets the model data after a user interacts with the editor.
        
        :param editor:
        :param model: Item where to put data.
        :param index: Which index to put data.
        :type editor: Not used
        :type model: PyQt4.QtCore.QAbstractItemModel
        :type index: PyQt4.QtCore.QModelIndex
        '''
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
    
    def updateEditorGeometry(self, editor, option, index):
        '''
        Overrides QItemDelegate's updateEditorGeometryQWidget method.
        
        :param editor: Widget to update.
        :param option: Parameters to update.
        :param index:
        :type editor: PyQt4.QtGui.QWidget
        :type option: PyQt4.QtGui.QStyleOptionViewItem
        :type index: Not used
        '''
        editor.setGeometry(option.rect)
        
    def commitAndCloseEditor(self):
        '''
        Overrides QItemDelegate's commitAndCloseEditor method.
        '''
        #For the moment, emitting both signals seems to call setModelData twice,
        #hence creating index mismatches and overwriting the wrong variables in the model
        #self.emit(QtCore.SIGNAL("commitData(QWidget*)"), self.sender())
        self.emit(QtCore.SIGNAL("closeEditor(QWidget*)"), self.sender())

class ObserverDataDelegate(QtGui.QItemDelegate):
    '''
    This class is responsible of controlling the user interaction with a QTableView.(obsTab.clockObserversData in this case)
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
        if index.row() == 0 or index.row() == 1:
            self.editor = QtGui.QComboBox(parent)
            self.connect(self.editor, QtCore.SIGNAL("activated(int)"), self.commitAndCloseEditor)
        else:
            #editor is a line edit where only unsigned integer can be entered
            self.editor = QtGui.QLineEdit(parent)
            self.connect(self.editor, QtCore.SIGNAL("returnPressed()"), self.commitAndCloseEditor)
            validator = QtGui.QIntValidator()
            validator.setBottom(0)
            self.editor.setValidator(validator)
                
        return self.editor
    
    def setEditorData(self, editor, index):
        '''
        Overrides QItemDelegate's setEditorData method. Sets the widget's data after createEditor has created it.
        
        :param editor: Widget to set.
        :param index: Index of the widget.
        :type editor: PyQt4.QtGui.QWidget
        :type index: PyQt4.QtCore.QModelIndex
        '''
        if index.row() == 0:
            selectedText = self.parent.model().data(index)
            editorItems = ["current_individual","environment","individuals"]
            editor.addItems(editorItems)
            editor.setCurrentIndex(editorItems.index(selectedText))
            #On windows, needed to correctly display on first show if combobox is too small for items in list
            self.editor.view().setMinimumWidth(self.calculateListWidth())
        elif index.row() == 1:
            selectedText = self.parent.model().data(index)
            editorItems = ["day","month","year","other"]
            editor.addItems(editorItems)
            editor.setCurrentIndex(editorItems.index(selectedText))
            #On windows, needed to correctly display on first show if combobox is too small for items in list
            self.editor.view().setMinimumWidth(self.calculateListWidth())
        else:
            editor.setText(index.model().data(index))
            
    
    def setModelData(self, editor, model, index):
        '''
        Overrides QItemDelegate's setModelData method. Sets the model data after a user interaction with the editor
        
        :param editor:
        :param model: Item where to put data.
        :param index: Which index to put data.
        :type editor: Not used
        :type model: PyQt4.QtCore.QAbstractItemModel
        :type index: PyQt4.QtCore.QModelIndex
        '''
        if index.row() == 0 or index.row() == 1: 
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
    
    def updateEditorGeometry(self, editor, option, index):
        '''
        Overrides QItemDelegate's updateEditorGeometryQWidget method.
        
        :param editor:
        :param option:
        :param index: see QItemDelegate's doc for more information
        '''
        editor.setGeometry(option.rect)
        
    def commitAndCloseEditor(self):
        '''
        Overrides QItemDelegate's commitAndCloseEditor method.
        '''
        #For the moment, emitting both signals seems to call setModelData twice,
        #hence creating index mismatches and overwriting the wrong variables in the model
        #self.emit(QtCore.SIGNAL("commitData(QWidget*)"), self.sender())
        self.emit(QtCore.SIGNAL("closeEditor(QWidget*)"), self.sender())

