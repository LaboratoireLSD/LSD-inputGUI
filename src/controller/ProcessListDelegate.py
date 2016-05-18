"""
.. module:: ProcessListDelegate

.. codeauthor::  Marc-Andre Gardner

:Created on: 2009-12-03

"""

from PyQt4 import QtCore, QtGui

from model.TreatmentsModel import ListTreatmentsModel


class ProcessListDelegate(QtGui.QItemDelegate):
    '''
    This class is responsible of controlling the user interaction with a QTableView.(treeTab.processesList and simTab.tableView in this case)
    '''
    def __init__(self, parent, windowObject):
        '''
        Constructor
        
        :param parent: QTableView associated with this delegate
        :param windowObject: reference to the MainFrame
        '''
        QtGui.QItemDelegate.__init__(self, parent)
        self.parent = parent
        self.topObject = windowObject

    def createEditor(self, parent, option, index):
        '''
        Overrides QItemDelegate's createEditor method. Creates the widget  when a user double click and item of the QTableView.
        
        :param parent:
        :param option:
        :param index: see QItemDelegate's doc for more information
        '''
        if index.column() == 0:
            self.editor = QtGui.QLineEdit(parent)
            self.connect(self.editor,QtCore.SIGNAL("returnPressed()"),self.commitAndCloseEditor)
            return self.editor
        else:
            #Scenario case
            self.editor = QtGui.QComboBox(parent)
            self.connect(self.editor, QtCore.SIGNAL("currentIndexChanged(int)"), self.commitAndCloseEditor)
            return self.editor
        
    def setEditorData(self, editor, index):
        '''
        Overrides QItemDelegate's setEditorData method. Sets the widget's data after createEditor has created it
        
        :param editor:
        :param index: see QItemDelegate's doc for more information
        '''
        print("TEST", index.model())
        if index.column() == 0:
            currentlyEditedName = index.model().getTreatmentNameFromIndex(index)
            editor.setText(currentlyEditedName)
        else:
            #Scenario case
            currentlyEditedScenario = index.model().getTreatmentNameFromIndex(index)
            #This error is expected, like the two next, because they are static and used at run-time
            processList = ListTreatmentsModel.baseModel.processesModelMapper
            editor.addItems(sorted(processList))
            if index.column() == 1:
                editor.setCurrentIndex(editor.findText(ListTreatmentsModel.baseModel.getScenarioLabel(currentlyEditedScenario)["indProcess"]))
            else:
                editor.setCurrentIndex(editor.findText(ListTreatmentsModel.baseModel.getScenarioLabel(currentlyEditedScenario)["envProcess"]))
            #On windows, needed to correctly display on first show if combobox is too small for items in list
            self.editor.view().setMinimumWidth(self.calculateListWidth())
            
    def setModelData(self, editor, model, index):
        '''
        Overrides QItemDelegate's setModelData method. Sets the model data after a user interaction with the editor
        
        :param editor:
        :param model:
        :param index: see QItemDelegate's doc for more information
        '''
        if index.column() == 0:
            if model.exists(editor.text()):
                print("Warning : Treatment", model.getTreatmentNameFromIndex(index), "already exists")
            else:
                model.setData(index, editor.text())
        elif index.column() == 1:
            model.setData(index, editor.currentText())
        elif index.column() == 2:
            model.setData(index, editor.currentText())
            
    def calculateListWidth(self):
        '''
        Calculate pixel width of largest item in drop-down list 
        '''
        fm = QtGui.QFontMetrics(self.editor.view().font())
        minimumWidth = 0
        for i in range(self.editor.count()):
            if fm.width(self.editor.itemText(i)) > minimumWidth:
                minimumWidth = fm.width(self.editor.itemText(i))
        return minimumWidth + 30
      
    def commitAndCloseEditor(self):
        '''
        Overrides QItemDelegate's commitAndCloseEditor method.
        '''
        #For the moment, emitting both signals seems to call setModelData twice,
        #hence creating index mismatches and overwriting the wrong variables in the model
        #self.emit(QtCore.SIGNAL("commitData(QWidget*)"), self.sender())
        self.emit(QtCore.SIGNAL("closeEditor(QWidget*)"), self.sender())
