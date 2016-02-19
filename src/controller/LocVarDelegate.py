'''
Created on 2011-04-04

@author: Mathieu Gagnon
@contact: mathieu.gagnon.10@ulaval.ca
@organization: Universite Laval

@license

 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''

from PyQt4 import QtCore, QtGui

class LocVarsDelegate(QtGui.QItemDelegate):
    '''
    This class is responsible of controlling the user interaction with a QTableView.(mainEditorFrame.locVarTblView in this case)
    '''
    def __init__(self, parent, windowObject):
        '''
        Constructor
        @param parent QTableView associated with this delegate
        @param windowObject reference to the editor frame
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
            self.editor = QtGui.QLineEdit(parent)
            self.connect(self.editor,QtCore.SIGNAL("returnPressed()"),self.commitAndCloseEditor)
            return self.editor
        elif index.column() == 1:
            self.editor = QtGui.QComboBox(parent)
            self.connect(self.editor, QtCore.SIGNAL("currentIndexChanged(int)"), self.commitAndCloseEditor)
            return self.editor
        elif index.column() == 2:
            #Must check if we edit a vector or a single value
            if not isinstance(index.model().getVarValueFromIndex(index),list):
                self.editor = QtGui.QLineEdit(parent)
                self.connect(self.editor, QtCore.SIGNAL("returnPressed()"), self.commitAndCloseEditor)
                return self.editor
            else:  
                self.editor = QtGui.QComboBox(parent)
                self.editor.setDuplicatesEnabled(True)
                self.editor.setEditable(True)
                self.editor.setInsertPolicy(QtGui.QComboBox.InsertAtCurrent)
                self.connect(self.editor, QtCore.SIGNAL("editTextChanged(const QString)"),self.hook)
                return self.editor
        else:
            return
        
    def setEditorData(self, editor, index):
        '''
        @summary Overrides QItemDelegate's setEditorData method. Sets the widget's data after createEditor has created it
        @param editor , index : see QItemDelegate's doc for more information
        '''
        if index.column() == 0:
            currLocVarName = index.model().getVarNameFromIndex(index)
            editor.setText(currLocVarName)
        elif index.column() == 1:
            #Type case
            currLocVarType = index.model().getVarTypeFromIndex(index)
            self.editor.addItems(["Double","Float","Int","Bool","String","UInt","Long","ULong"])
            editor.setCurrentIndex(editor.findText(currLocVarType))
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
        @summary Overrides QItemDelegate's setModelData method. Sets the model data after a user interaction with the editor
        @param  editor ,model, index : see QItemDelegate's doc for more information
        '''
        baseModel = model.getBaseModel()
        if index.column() == 0:
            if baseModel.locVarExists(model.node, str(editor.text())):
                print("Warning : Local Variable " + str(model.getVarNameFromIndex(index))+" already exists")
            else:
                model.setData(index, QtCore.QVariant(editor.text()))
        elif index.column() == 1:
            model.setData(index,QtCore.QVariant(editor.currentText()))
        elif index.column() == 2:
            if isinstance(self.editor,QtGui.QComboBox):
                values = []
                for i in range(0,editor.count()):
                    values.append(editor.itemText(i))
                model.setData(index,QtCore.QVariant(QtCore.QStringList(values)))
            else:        
                model.setData(index,QtCore.QVariant(editor.text()))
            
    def calculateListWidth(self):
        '''
        @summary Calculate pixel width of largest item in drop-down list 
        '''
        fm = QtGui.QFontMetrics(self.editor.view().font())
        minimumWidth = 0
        for i in range(0,self.editor.count()):
            if fm.width(self.editor.itemText(i)) > minimumWidth:
                minimumWidth = fm.width(self.editor.itemText(i))
        return minimumWidth+30
      
    def hook(self, newText):
        '''
        @summary Little function that allow the editor to correctly update itself when a user edits a vector via an editable comboBox
        @param newText : the new data to use for the update
        '''
        self.editor.setItemText(self.editor.currentIndex(),newText)
        
    def commitAndCloseEditor(self):
        '''
        @summary Overrides QItemDelegate's commitAndCloseEditor method.
        '''
        #For the moment, emitting both signals seems to call setModelData twice,
        #hence creating index mismatches and overwriting the wrong variables in the model
        #self.emit(QtCore.SIGNAL("commitData(QWidget*)"), self.sender())
        self.emit(QtCore.SIGNAL("closeEditor(QWidget*)"), self.sender())
