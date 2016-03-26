'''
Created on 2009-08-14

@author:  Majid Malis
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


from PyQt4 import QtCore
from PyQt4 import QtXml


class DomItem:
    '''
    This class represents a xml dom node (node and his location)
    '''
    def __init__(self, node, row, parent=None):
        '''
        @summary Constructor
        @param node: the node to assign to this DomItem
        @param row: the row of node in his parent childNodes list
        @param parent: the parent of the given node
        '''
        self.domNode = node
        # Record the item's location within its parent.
        self.rowNumber = row
        self.parentItem = parent
        self.childItems = {}

    def parent(self):
        '''
        @summary Return Parent
        '''
        return self.parentItem

    def row(self):
        '''
        @summary Return row
        '''
        return self.rowNumber

    def node(self):
        '''
        @summary XML node
        '''
        return self.domNode

    def child(self, i):
        '''
        @Return child at position i
        If there is a node at position i but no Dom item has been created yet for this child, create one and add it to child list
        @param i : position in child list
        '''
        if i in self.childItems:
            return self.childItems[i]

        if i >= 0 and i < self.domNode.childNodes().count():
            childNode = self.domNode.childNodes().item(i)
            childItem = DomItem(childNode, i, self)
            self.childItems[i] = childItem
            return childItem

        return 0
    
    def insertBefore(self, newChild, refChild):
        '''
        @Insert child before an other child in child list
        @param newChild, refChild : newChild is child to insert before refChild
        '''
        parent = refChild.parent()
        if parent is None:
            return None
        else:
            parent.node().insertBefore(newChild.node(), refChild.node())
    
    
class DomModel(QtCore.QAbstractItemModel):
    '''
    This class implements a model used with DOM items. It allows the representation of a xml dom in a QTreeView
    Most of it is reimplemented from QAbstractItemModel
    '''
    def __init__(self, document, parent=None):
        '''
        @summary Constructor
        @param document : xml dom root node
        @param parent : application's main Window
        '''
        QtCore.QAbstractItemModel.__init__(self, parent)
        self.parentWidget = parent
        self.rootItem = DomItem(document, 0)

    def columnCount(self, parent):
        ''' 
        @summary : Reimplemented from QAbstractItemModel.columnCount(self,parent)
        Column count is fixed to 3 (name, value and attribute)
        @param parent : parent DomItem
        '''
        return 3

    def flags(self, index):
        ''' 
        @summary : Reimplemented from QAbstractItemModel.flags(self,index)
        See QAbstractItemModel's documentation for mode details
        @param index : position in model
        '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index) | QtCore.Qt.ItemIsEditable)

    def headerData(self, section, orientation, role):
        ''' 
        @summary : Reimplemented from QAbstractItemModel.headerData(self, section, orientation, role)
        See QAbstractItemModel's documentation for mode details
        @param section : model's column or row
        @param orientation : horizontal or vertical
        @param role : Qt item role
        '''
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if section == 0:
                return self.tr("Name")
            elif section == 1:
                return self.tr("Attribute")
            elif section == 2:
                return self.tr("Value")
            else:
                return ""

        return ""

    def index(self, row, column, parent=QtCore.QModelIndex()):
        ''' 
        @summary : Reimplemented from QAbstractItemModel.index(self, row, column, parent=QtCore.QModelIndex())
        See QAbstractItemModel's documentation for mode details
        @param row : row position in model
        @param column : column position in model
        @param parent : index of the parent DomItem in model
        '''
        if row < 0 or column < 0 or row >= self.rowCount(parent) or column >= self.columnCount(parent):
            return QtCore.QModelIndex()

        if parent.isValid():
            parentItem = parent.internalPointer()
        else:
            parentItem = self.rootItem

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def rowCount(self, parent):
        ''' 
        @summary : Reimplemented from QAbstractItemModel.rowCount(self,parent)
        Position in parent's xml dom
        @param parent : index of the parent DomItem in model
        '''
        if parent.column() > 0:
            return 0

        if parent.isValid():
            parentItem = parent.internalPointer()
        else:
            parentItem = self.rootItem

        return parentItem.node().childNodes().count()
    
    def parent(self, child):
        ''' 
        @summary : Reimplemented from QAbstractItemModel.parent(self, child)
        Return child's parent
        @param child : index of the child DomItem in model
        '''
        if not child.isValid():
            return QtCore.QModelIndex()

        childItem = child.internalPointer()
        parentItem = childItem.parent()

        if not parentItem or parentItem == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def data(self, index, role=QtCore.Qt.EditRole):
        ''' 
        @summary : Reimplemented from QAbstractItemModel.data(self, index, role=QtCore.Qt.EditRole)
        Return data for role at position index in model. Controls what is going to be displayed in the tree view.
        @param index : index of the DomItem in model
        @param role : Qt item role
        '''
        
        if not index.isValid():
            return ""

        if role != QtCore.Qt.DisplayRole:
            return ""

        item = index.internalPointer()

        node = item.node()
        names = []
        values = []
        attributeMap = node.attributes()

        if index.column() == 0:
            return node.nodeName()
       
        elif index.column() == 1:
            for i in range(0, attributeMap.count()):
                attribute = attributeMap.item(i)
                names.append(attribute.nodeName())

            return names.join("\n")
        elif index.column() == 2:
            for i in range(0, attributeMap.count()):
                attribute = attributeMap.item(i)
                values.append(attribute.nodeValue())
            return values.join("\n")
        else:
            return ""
        
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        ''' 
        @summary : Reimplemented from QAbstractItemModel.setData(self, index, value, role=QtCore.Qt.EditRole)
        Sets data for role at position index in model. Modify model and its underlying data structure
        @param index : index of the DomItem in model
        @param value : new Value
        @param role : Qt item role
        '''
        if index.isValid():
            item = index.internalPointer()
            node = item.node()
            parent = item.parent()
            row = parent.node().childNodes().length()
            parentModelIndex = self.createIndex(parent.row(), 0, parent)
            attributeMap = node.attributes()
            
            if index.column() == 0:
                ''' Add a new child '''
                child = QtXml.QDomNode()
                self.beginInsertRows(parentModelIndex, row, row)
                parent.node().appendChild(child)
                self.endInsertRows()                
                index = self.createIndex(row, 0, child)
                
            elif index.column() == 1:
                ''' Add a new attribute '''
                child = QtXml.QDomNode()
                self.beginInsertRows(parentModelIndex, row, row)
                parent.node().appendChild(child)
                self.endInsertRows()                
                index = self.createIndex(row, 0, child)
               
            elif index.column() == 2:
                for i in range(0, attributeMap.count()):
                    attribute = attributeMap.item(i)
                    attribute.setNodeValue(value)
                    
                self.parentWidget.dirty = True
                self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
                return True
            
            return False
    
    def insertRows(self, position, rows=1, index=QtCore.QModelIndex()):
        ''' 
        @summary : Reimplemented from QAbstractItemModel.insertRows(row, count, parent = QModelIndex())
        Inserts a row in the model(a DomItem)
        @param position : position to start insertion
        @param rows : number of rows to add(fixed to 1)
        @param index :  index of the parent DomItem in model
        '''
        if not index.isValid():
            return False
            
        item = index.internalPointer()
        parent = item.parent()
        parentModelIndex = self.createIndex(parent.row(), 0, parent)
            
        self.beginInsertRows(parentModelIndex, position, position + rows - 1)
        for row in range(rows):
            newNodeItem = DomItem(QtXml.QDomNode(), row, parent)
            parent.insertBefore(newNodeItem, parent.child(position + row))
            
        self.endInsertRows()
        self.parentWidget.dirty = True
        return True
