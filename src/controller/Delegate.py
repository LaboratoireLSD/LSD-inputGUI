'''
Created on 2009-08-14

@author: Majid Mallis
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

from PyQt4 import QtGui, QtCore


class Delegate(QtGui.QStyledItemDelegate):
    '''
    This class is responsible of controlling the user interaction with a QTreeView.(advTab.XMLView in this case)
    '''
    def __init__(self, parent):
        '''
        Constructor
        @param parent QTableView associated with this delegate        
        '''
        QtGui.QStyledItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        '''
        @summary Overrides QItemDelegate's createEditor method. Creates the widget  when a user double click and item of the QTableView.
        @param parent, option, index : see QItemDelegate's doc for more information
        '''
        self.editor = QtGui.QLineEdit(parent)
        self.connect(self.editor, QtCore.SIGNAL("returnPressed()"), self.commitAndCloseEditor)
        return self.editor
   
    def setEditorData(self, editor, index):
        '''
        @summary Overrides QItemDelegate's setEditorData method. Sets the widget's data after createEditor has created it
        @param editor , index : see QItemDelegate's doc for more information
        '''
        text = str(
                   index.model().data(
                   index, QtCore.Qt.DisplayRole).toString())
        editor.setText(text)
   
    def setModelData(self, editor, model, index):
        '''
        @summary Overrides QItemDelegate's setModelData method. Sets the model data after a user interaction with the editor
        @param  editor ,model, index : see QItemDelegate's doc for more information
        '''
        model.setData(index, str(self.editor.text()))
        
    def commitAndCloseEditor(self):
        '''
        @summary Overrides QItemDelegate's commitAndCloseEditor method.
        '''
        #For the moment, emitting both signals seems to call setModelData twice,
        #hence creating index mismatches and overwriting the wrong variables in the model
        #self.emit(QtCore.SIGNAL("commitData(QWidget*)"), self.sender())
