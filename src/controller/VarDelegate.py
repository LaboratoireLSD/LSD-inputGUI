
from PyQt4 import QtCore, QtGui

from editor.mainEditorFrame import MainEditorWindow
from model.TreatmentsModel import ListTreatmentsModel


class VarSimDelegate(QtGui.QItemDelegate):
    '''
    This class is responsible of controlling the user interaction with a QTableView.(popTab.tableView_Supp in this case)
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
        varName = index.model().getVarFromIndex(index)
        if index.column() == 0:
            self.editor = QtGui.QLineEdit(parent)
            self.connect(self.editor, QtCore.SIGNAL("returnPressed()"), self.commitAndCloseEditor)
            return self.editor
        if index.column() == 1:
            self.editor = QtGui.QComboBox(parent)
            self.connect(self.editor, QtCore.SIGNAL("currentIndexChanged(int)"), self.commitAndCloseEditor)
            return self.editor
        elif index.column() == 2:
            return
        elif index.column() == 3:
            varName = index.model().getVarFromIndex(index)
            varNode = index.model().baseModel.domNodeDict[index.model().profileName][varName]
            pmtNode = varNode.firstChildElement("PrimitiveTree")
            self.editor = MainEditorWindow(pmtNode.firstChild(),self.topObject, varName)
            self.editor.exec_()
            index.model().baseModel._findDependencies(index.model().profileName,varName)
            return

    def setEditorData(self, editor, index):
        '''
        @summary Overrides QItemDelegate's setEditorData method. Sets the widget's data after createEditor has created it
        @param editor , index : see QItemDelegate's doc for more information
        '''
        baseModel = index.model().baseModel
        varName = index.model().getVarFromIndex(index)
        
        if index.column() == 0:
            text = index.model().data(index, QtCore.Qt.DisplayRole)
            editor.setText(text)
        
        elif index.column() == 1:
            self.editor.addItems(["Double","Float","Int","Bool","String","UInt","Long","ULong"])
            self.editor.setCurrentIndex(self.editor.findText(baseModel.getVarType(index.model().profileName, varName)))
            #On windows, needed to correctly display on first show if combobox is too small for items in list
            self.editor.view().setMinimumWidth(self.calculateListWidth())
            
    def setModelData(self, editor, model, index):
        '''
        @summary Overrides QItemDelegate's setModelData method. Sets the model data after a user interaction with the editor
        @param  editor ,model, index : see QItemDelegate's doc for more information
        '''
        if index.column()  == 0: 
            model.setData(index, self.editor.text())
        elif index.column() == 1:
            model.setData(index, self.editor.currentText())
#        elif index.column() == 3:
#                print("karate!")
#                model.beginResetModel()
#                model.baseModel._updateVarList(model.profileName)
#                model.endResetModel()
    
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
    
    def commitAndCloseEditor(self):
        '''
        @summary Overrides QItemDelegate's commitAndCloseEditor method.
        '''
        #For the moment, emitting both signals seems to call setModelData twice,
        #hence creating index mismatches and overwriting the wrong variables in the model
        #self.emit(QtCore.SIGNAL("commitData(QWidget*)"), self.sender())
        self.emit(QtCore.SIGNAL("closeEditor(QWidget*)"), self.sender())


class VarGeneratorDelegate(QtGui.QItemDelegate):
    '''
    This class is responsible of controlling the user interaction with a QTableView.(simTab.proMgr.tableView in this case)
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
        if index.column() == 0:
            self.editor = QtGui.QComboBox(parent)
            self.connect(self.editor, QtCore.SIGNAL("currentIndexChanged(int)"), self.commitAndCloseEditor)
            return self.editor
        if index.column() == 1 or index.column() == 2 :
            self.editor = QtGui.QSpinBox(parent)
            self.editor.setMaximum(2000000000)
            self.connect(self.editor, QtCore.SIGNAL("editingFinished()"), self.commitAndCloseEditor)
            return self.editor
        else:
            return

    def setEditorData(self, editor, index):
        '''
        @summary Overrides QItemDelegate's setEditorData method. Sets the widget's data after createEditor has created it
        @param editor , index : see QItemDelegate's doc for more information
        '''
        if index.column() == 1 or index.column() == 2:
            value = index.model().data(index, QtCore.Qt.DisplayRole)
            editor.setValue(int(value))
        elif index.column() == 0:
            #This error is expected, since it's a static variable used at run-time
            profiles = ListTreatmentsModel.baseModel.profileDict.keys()
            editor.addItems(profiles)
            #On windows, needed to correctly display on first show if combobox is too small for items in list
            self.editor.view().setMinimumWidth(self.calculateListWidth())
            return
        else:
            return
    
    def setModelData(self, editor, model, index):
        '''
        @summary Overrides QItemDelegate's setModelData method. Sets the model data after a user interaction with the editor
        @param  editor ,model, index : see QItemDelegate's doc for more information
        '''
        if index.column() == 1 or index.column() == 2:
            model.setData(index, self.editor.value())
        elif index.column() == 0:
            model.setData(index, self.editor.currentText())
        else:
            return
        
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
    
    def commitAndCloseEditor(self):
        '''
        @summary Overrides QItemDelegate's commitAndCloseEditor method.
        '''
        #For the moment, emitting both signals seems to call setModelData twice,
        #hence creating index mismatches and overwriting the wrong variables in the model
        #self.emit(QtCore.SIGNAL("commitData(QWidget*)"), self.sender())
        self.emit(QtCore.SIGNAL("closeEditor(QWidget*)"), self.sender())

class SimpleVarDelegate(QtGui.QItemDelegate):
    '''
    Simplified VarSimDelegate to be used in Demography File Editor
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
        varName = index.model().getVarFromIndex(index)
        if index.column() == 0:
            self.editor = QtGui.QLineEdit(parent)
            self.connect(self.editor, QtCore.SIGNAL("returnPressed()"), self.commitAndCloseEditor)
            return self.editor
        if index.column() == 1:
            self.editor = QtGui.QComboBox(parent)
            self.connect(self.editor, QtCore.SIGNAL("currentIndexChanged(int)"), self.commitAndCloseEditor)
            return self.editor
        elif index.column() == 2:
            return
        elif index.column() == 3:
            return
        elif index.column() == 4:
            varName = index.model().getVarFromIndex(index)
            varNode = index.model().baseModel.domNodeDict[varName]
            pmtNode = varNode.firstChildElement("PrimitiveTree")
            treeEditor = MainEditorWindow(pmtNode.firstChild(),self.topObject, varName)
            #treeEditor
            treeEditor.exec_()
            index.model().getBaseModel()._findDependencies(varName)
            index.model().getBaseModel()._findRange(varName)
            return
    
    def setEditorData(self, editor, index):
        '''
        @summary Overrides QItemDelegate's setEditorData method. Sets the widget's data after createEditor has created it
        @param editor , index : see QItemDelegate's doc for more information
        '''
        baseModel = index.model().getBaseModel()
        varName = index.model().getVarFromIndex(index)
        
        if index.column() == 0:
            text = index.model().data(index, QtCore.Qt.DisplayRole)
            editor.setText(text)
        
        elif index.column() == 1:
            self.editor.addItems(["Double","Float","Int","Bool","String","UInt","Long","ULong"])
            self.editor.setCurrentIndex(self.editor.findText(baseModel.getVarType(varName)))
            #On windows, needed to correctly display on first show if combobox is too small for items in list
            self.editor.view().setMinimumWidth(self.calculateListWidth())
        else:
            return None
    
    def setModelData(self, editor, model, index):
        '''
        @summary Overrides QItemDelegate's setModelData method. Sets the model data after a user interaction with the editor
        @param  editor ,model, index : see QItemDelegate's doc for more information
        '''
        if index.column()  == 0: 
            model.setData(index, self.editor.text())
        elif index.column() == 1:
            model.setData(index, self.editor.currentText())
        else:
            return
    
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
    
    def commitAndCloseEditor(self):
        '''
        @summary Overrides QItemDelegate's commitAndCloseEditor method.
        '''
        #For the moment, emitting both signals seems to call setModelData twice,
        #hence creating index mismatches and overwriting the wrong variables in the model
        #self.emit(QtCore.SIGNAL("commitData(QWidget*)"), self.sender())
        self.emit(QtCore.SIGNAL("closeEditor(QWidget*)"), self.sender())
