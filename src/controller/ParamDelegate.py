'''
Created on 2010-10-04

@author:  Mathieu Gagnon
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


class ParamDelegate(QtGui.QItemDelegate):
    '''
    This class is responsible of controlling the user interaction with a QTableView.(paramTab.tableView in this case)
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
            self.editor = QtGui.QLineEdit(parent)
            self.connect(self.editor, QtCore.SIGNAL("returnPressed()"), self.commitAndCloseEditor)
            return self.editor
        
        if index.column() == 1:
            self.editor = QtGui.QComboBox(parent)
            self.connect(self.editor, QtCore.SIGNAL("activated(int)"), self.commitAndCloseEditor)
            return self.editor
        
        elif index.column() == 2:
            refName = index.model().getBaseModel().getRefNameFromIndex(index.row())
            if index.model().getBaseModel().getContainerType(refName) == "Scalar":
                self.editor = QtGui.QLineEdit(parent)
                self.connect(self.editor, QtCore.SIGNAL("returnPressed()"), self.commitAndCloseEditor)
                return self.editor
            else:  
                self.editor = QtGui.QComboBox(parent)
                self.editor.setDuplicatesEnabled(True)
                self.editor.setEditable(True)
                self.editor.setInsertPolicy(QtGui.QComboBox.InsertAtCurrent)
                self.editor.setCompleter(None)
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
            originalData = index.model().data(index, QtCore.Qt.DisplayRole)
            editor.setText(originalData)
        
        elif index.column() == 1:
            self.editor.addItems(["Bool","Double","Float","Int","Long","String","ULong","UInt"])
            self.editor.setCurrentIndex(self.editor.findText(index.model().data(index, QtCore.Qt.DisplayRole).toString()))
            #On windows, needed to correctly display on first show if combobox is too small for items in list
            self.editor.view().setMinimumWidth(self.calculateListWidth())
        elif index.column() == 2:
            refName = index.model().getBaseModel().getRefNameFromIndex(index.row())
            if isinstance(editor,QtGui.QComboBox):
                editor.addItems(index.model().getBaseModel().getValue(refName))
                #On windows, needed to correctly display on first show if combobox is too small for items in list
                self.editor.view().setMinimumWidth(self.calculateListWidth())
            else:
                editor.setText(index.model().getBaseModel().getValue(refName)[0])
                
    def setModelData(self, editor, model, index):
        '''
        @summary Overrides QItemDelegate's setModelData method. Sets the model data after a user interaction with the editor
        @param  editor ,model, index : see QItemDelegate's doc for more information
        '''
        if isinstance(editor, QtGui.QComboBox):
            if index.column() == 1:
                model.setData(index, self.editor.currentText())
            else:
                values = []
                for i in range(editor.count()):
                    values.append(editor.itemText(i))
                model.setData(index, values)
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
    
    def hook(self, newText):
        '''
        @summary Little function that allow the editor to correctly update itself when a user edits a vector via an editable comboBox
        @param newText : the new data to use for the update
        For some reasons, cursor moves when doing so, so we save curosr position and resets it after changing text
        For some other resons, reseting cursor sometimes select text, so we unselect it
        '''
        cursorPosAt = self.editor.lineEdit().cursorPosition()
        self.editor.setItemText(self.editor.currentIndex(),newText)
        self.editor.lineEdit().setCursorPosition(cursorPosAt)
        
    def commitAndCloseEditor(self):
        '''
        @summary Overrides QItemDelegate's commitAndCloseEditor method.
        '''
        #For the moment, emitting both signals seems to call setModelData twice,
        #hence creating index mismatches and overwriting the wrong variables in the model
        #self.emit(QtCore.SIGNAL("commitData(QWidget*)"), self.sender())
        self.emit(QtCore.SIGNAL("closeEditor(QWidget*)"), self.sender())

        
