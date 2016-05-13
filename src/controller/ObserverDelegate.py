
from PyQt4 import QtCore, QtGui
from model.baseTreatmentsModel import BaseTreatmentsModel

class ObserverDelegate(QtGui.QItemDelegate):
    '''
    This class is responsible of controlling the user interaction with a QListView.(obsTab.clockObservers in this case)
    '''

    def __init__(self, parent, windowObject):
        '''
        Constructor
        @param parent QTableView associated with this delegate
        @param windowObject reference to the MainFrame
        '''
        QtGui.QItemDelegate.__init__(self, parent)
        self.parent = parent
        self.topObject = windowObject

    
    def createEditor(self, parent, option, index):
        '''
        @summary Overrides QItemDelegate's createEditor method. Creates the widget  when a user double click and item of the QTableView.
        @param parent, option, index : see QItemDelegate's doc for more information
        '''
        self.editor = QtGui.QComboBox(parent)
        self.connect(self.editor,QtCore.SIGNAL("activated(int)"),self.commitAndCloseEditor)
        return self.editor
    
    def setEditorData(self, editor, index):
        '''
        @summary Overrides QItemDelegate's setEditorData method. Sets the widget's data after createEditor has created it
        @param editor , index : see QItemDelegate's doc for more information
        '''
        if index.column() == 0:
            baseTrModel = BaseTreatmentsModel()
            processes =  baseTrModel.getTreatmentsDict().keys()
            processes.sort(key=lambda x: x.lower())
            editor.addItems(processes)
            #On windows, needed to correctly display on first show if combobox is too small for items in list
            self.editor.view().setMinimumWidth(self.calculateListWidth())
        elif index.column() == 1:
            editor.addItems(["current_individual","environment","individuals"])
            #On windows, needed to correctly display on first show if combobox is too small for items in list
            self.editor.view().setMinimumWidth(self.calculateListWidth())
    
    def setModelData(self, editor, model, index):
        '''
        @summary Overrides QItemDelegate's setModelData method. Sets the model data after a user interaction with the editor
        @param  editor ,model, index : see QItemDelegate's doc for more information
        '''
        model.setData(index,self.editor.currentText())
        
    def calculateListWidth(self):
        '''
        @summary Calculate pixel width of largest item in drop-down list 
        '''
        fm = QtGui.QFontMetrics(self.editor.view().font())
        minimumWidth = 0
        for i in range(self.editor.count()):
            if fm.width(self.editor.itemText(i)) > minimumWidth:
                minimumWidth = fm.width(self.editor.itemText(i))
        return minimumWidth + 10
    
    def updateEditorGeometry(self, editor, option, index):
        '''
        @summary Overrides QItemDelegate's updateEditorGeometryQWidget method.
        @param editor, option, index: see QItemDelegate's doc for more information
        '''
        editor.setGeometry(option.rect)
        
    def commitAndCloseEditor(self):
        '''
        @summary Overrides QItemDelegate's commitAndCloseEditor method.
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
        @param parent QTableView associated with this delegate
        @param windowObject reference to the MainFrame
        '''
        QtGui.QItemDelegate.__init__(self, parent)
        self.parent = parent
        self.topObject = windowObject

    def createEditor(self, parent, option, index):
        '''
        @summary Overrides QItemDelegate's createEditor method. Creates the widget  when a user double click and item of the QTableView.
        @param parent, option, index : see QItemDelegate's doc for more information
        '''
        if index.row() == 0 or index.row() == 1:
            self.editor = QtGui.QComboBox(parent)
            self.connect(self.editor,QtCore.SIGNAL("activated(int)"),self.commitAndCloseEditor)
        else:
            #editor is a line edit where only unsigned integer can be entered
            self.editor = QtGui.QLineEdit(parent)
            self.connect(self.editor, QtCore.SIGNAL("returnPressed()"), self.commitAndCloseEditor)
            if index.row() == 4:
                validator = QtGui.QIntValidator()
                validator.setBottom(0)
            else:
                validator = QtGui.QIntValidator()
                validator.setBottom(0)
            self.editor.setValidator(validator)
                
        return self.editor
    
    def setEditorData(self, editor, index):
        '''
        @summary Overrides QItemDelegate's setEditorData method. Sets the widget's data after createEditor has created it
        @param editor , index : see QItemDelegate's doc for more information
        '''
        if index.row() == 0:
            editor.addItems(["current_individual","environment","individuals"])
            #On windows, needed to correctly display on first show if combobox is too small for items in list
            self.editor.view().setMinimumWidth(self.calculateListWidth())
        if index.row() == 1:
            editor.addItems(["day","month","year","other"])
            #On windows, needed to correctly display on first show if combobox is too small for items in list
            self.editor.view().setMinimumWidth(self.calculateListWidth())
        else:
            if isinstance(editor, QtGui.QComboBox):
                editor.setCurrentIndex(index.row())
            else:
                editor.setText(index.model().data(index))
            
    
    def setModelData(self, editor, model, index):
        '''
        @summary Overrides QItemDelegate's setModelData method. Sets the model data after a user interaction with the editor
        @param  editor ,model, index : see QItemDelegate's doc for more information
        '''
        if index.row() == 0 or index.row() == 1: 
            model.setData(index, self.editor.currentText())
        else:
            model.setData(index, self.editor.text())
            
    def calculateListWidth(self):
        '''
        @summary Calculate pixel width of largest item in drop-down list 
        '''
        fm = QtGui.QFontMetrics(self.editor.view().font())
        minimumWidth = 0
        for i in range(self.editor.count()):
            if fm.width(self.editor.itemText(i)) > minimumWidth:
                minimumWidth = fm.width(self.editor.itemText(i))
        return minimumWidth + 10
    
    def updateEditorGeometry(self, editor, option, index):
        '''
        @summary Overrides QItemDelegate's updateEditorGeometryQWidget method.
        @param editor, option, index: see QItemDelegate's doc for more information
        '''
        editor.setGeometry(option.rect)
        
    def commitAndCloseEditor(self):
        '''
        @summary Overrides QItemDelegate's commitAndCloseEditor method.
        '''
        #For the moment, emitting both signals seems to call setModelData twice,
        #hence creating index mismatches and overwriting the wrong variables in the model
        #self.emit(QtCore.SIGNAL("commitData(QWidget*)"), self.sender())
        self.emit(QtCore.SIGNAL("closeEditor(QWidget*)"), self.sender())

