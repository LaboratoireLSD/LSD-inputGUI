"""
.. module:: Delegate

.. codeauthor::  Majid Mallis

:Created on: 2009-08-14

"""
from PyQt4 import QtGui, QtCore


class Delegate(QtGui.QStyledItemDelegate):
    '''
    This class is responsible of controlling the user interaction with a QTreeView.(advTab.XMLView in this case)
    '''
    def __init__(self, parent):
        '''
        Constructor.
        
        :param parent: QTableView associated with this delegate
        :type parent: PyQt4.QtGui.QTableView
        '''
        QtGui.QStyledItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        '''
        Overrides QItemDelegate's createEditor method. Creates the widget  when a user double click and item of the QTableView.
        
        :param parent: Parent of the new widget.
        :param option:
        :param index: 
        :type option: Not used
        :type index: Not used
        :return: PyQt4.QtGui.QLineEdit.
        '''
        self.editor = QtGui.QLineEdit(parent)
        self.connect(self.editor, QtCore.SIGNAL("returnPressed()"), self.commitAndCloseEditor)
        return self.editor
   
    def setEditorData(self, editor, index):
        '''
        Overrides QItemDelegate's setEditorData method. Sets the widget's data after createEditor has created it
        
        :param editor: Widget to modify.
        :param index: Index of the modification.
        :type editor: PyQt4.QtGui.QWidget
        :type index: PyQt4.QtCore.QModelIndex
        '''
        text = index.model().data(index, QtCore.Qt.DisplayRole)
        editor.setText(text)
   
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
        model.setData(index, self.editor.text())
        
    def commitAndCloseEditor(self):
        '''
        Overrides QItemDelegate's commitAndCloseEditor method.
        '''
        #For the moment, emitting both signals seems to call setModelData twice,
        #hence creating index mismatches and overwriting the wrong variables in the model
        #self.emit(QtCore.SIGNAL("commitData(QWidget*)"), self.sender())
