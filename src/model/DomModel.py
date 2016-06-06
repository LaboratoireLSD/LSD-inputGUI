"""
.. module:: DomModel

.. codeauthor:: Majid Malis

:Created on: 2009-08-14

"""
from PyQt4 import QtCore
from PyQt4 import QtXml


class DomItem:
    '''
    This class represents a xml dom node (node and his location).
    '''
    def __init__(self, node, row, parent=None):
        '''
        Constructor.
        
        :param node: The node to assign to this DomItem
        :param row: The row of node in his parent childNodes list
        :param parent: Optional - The parent of the given node
        '''
        self.domNode = node
        # Record the item's location within its parent.
        self.rowNumber = row
        self.parentItem = parent
        self.childItems = {}

    def child(self, pos):
        '''
        Returns the child at position 'pos'
        If there is a node at position 'pos' but no Dom item has been created yet for this child, create one and add it to child list.
        
        :param pos: Position in child list.
        :type pos: Int
        :return: 
        '''
        if pos in self.childItems:
            return self.childItems[pos]

        if pos >= 0 and pos < self.domNode.childNodes().count():
            childNode = self.domNode.childNodes().item(pos)
            childItem = DomItem(childNode, pos, self)
            self.childItems[pos] = childItem
            return childItem
    
    def insertBefore(self, newChild, refChild):
        '''
        Inserts a child before another child in child list.
        
        :param newChild: New child to insert.
        :param refChild: Child where the new one needs to be inserted before.
        :type newChild:
        :type refchild:
        '''
        parent = refChild.parent()
        if parent:
            parent.node().insertBefore(newChild.node(), refChild.node())
    
    
class DomModel(QtCore.QAbstractItemModel):
    '''
    This class implements a model used with DOM items. It allows the representation of a xml dom in a QTreeView.
    Most of it is reimplemented from QAbstractItemModel.
    '''
    def __init__(self, document, parent=None):
        '''
        Constructor.
        
        :param document: xml dom root node.
        :param parent: Optional - Application's main Window.
        '''
        QtCore.QAbstractItemModel.__init__(self, parent)
        self.parentWidget = parent
        self.rootItem = DomItem(document, 0)

    def columnCount(self, parent):
        ''' 
        Reimplemented from QAbstractItemModel.columnCount(self,parent).
        Column count is fixed to 3 (name, value and attribute).
        
        :param parent: Parent DomItem
        :return: Int. Always returns 3.
        '''
        return 3

    def flags(self, index):
        ''' 
        Reimplemented from QAbstractItemModel.flags(self,index).
        See QAbstractItemModel's documentation for more details.
        
        :param index: Position in model.
        :type index: QModelIndex
        :return: Int.
        '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index) | QtCore.Qt.ItemIsEditable)

    def headerData(self, section, orientation, role):
        ''' 
        Reimplemented from QAbstractItemModel.headerData(self, section, orientation, role).
        See QAbstractItemModel's documentation for more details.
        
        :param section: Model's column or row
        :param orientation: Horizontal or vertical
        :param role: Qt item role
        :type section: Int
        :type orientation: Qt.Orientation
        :type role: Int
        :return: String
        '''
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if section == 0:
                return self.tr("Name")
            elif section == 1:
                return self.tr("Attribute")
            elif section == 2:
                return self.tr("Value")

    def index(self, row, column, parent=QtCore.QModelIndex()):
        ''' 
        Reimplemented from QAbstractItemModel.index(self, row, column, parent=QtCore.QModelIndex()).
        See QAbstractItemModel's documentation for more details.
        
        :param row: Row position in model.
        :param column: Column position in model.
        :param parent: Optional - Index of the parent DomItem in model.
        :type row: Int
        :type column: Int
        :type parent: QModelIndex
        :return: QModelIndex.
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
        Reimplemented from QAbstractItemModel.rowCount(self, parent).
        Position in parent's xml dom.
        
        :param parent: Index of the parent DomItem in model.
        :type parent: QModelIndex
        :return: Int.
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
        Reimplemented from QAbstractItemModel.parent(self, child).
        Returns a child's parent.
        
        :param child: Index of the child DomItem in model.
        :type child: QModelIndex
        :return: QModelIndex.
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
        Reimplemented from QAbstractItemModel.data(self, index, role=QtCore.Qt.EditRole).
        Returns the data for role at position index in model. Controls what is going to be displayed in the tree view.
        
        :param index: Index of the DomItem in model.
        :param role:  Optional - Qt item role.
        :type index: QModelIndex
        :type role: Int
        :return: String
        '''
        
        if not index.isValid() or role != QtCore.Qt.DisplayRole:
            return

        node = index.internalPointer().node()
        data = []
        attributeMap = node.attributes()

        if index.column() == 0:
            return node.nodeName()
       
        for i in range(attributeMap.count()):
            attribute = attributeMap.item(i)
            if index.column() == 1:
                data.append(attribute.nodeName())
            elif index.column() == 2:
                data.append(attribute.nodeValue())
            else:
                return

        return data.join("\n")
        
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        ''' 
        Reimplemented from QAbstractItemModel.setData(self, index, value, role=QtCore.Qt.EditRole).
        Sets data for role at position index in model. Modifies model and its underlying data structure.
        
        :param index: Index of the DomItem in model.
        :param value: New Value.
        :param role: Qt item role.
        :type index: QModelIndex
        :type value: QVariant
        :type role: Int
        :return: Boolean. 
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
                for i in range(attributeMap.count()):
                    attribute = attributeMap.item(i)
                    attribute.setNodeValue(value)
                    
                self.parentWidget.dirty = True
                self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
            
            return True
    
    def insertRows(self, position, rows=1, index=QtCore.QModelIndex()):
        ''' 
        Reimplemented from QAbstractItemModel.insertRows(row, count, parent = QModelIndex()).
        Inserts a row in the model(a DomItem).
        
        :param position: Position to start insertion.
        :param rows: Number of rows to add(fixed to 1).
        :param index: Index of the parent DomItem in model.
        :type position: Int
        :type rows: Int list
        :type index: QModelIndex
        :return: Boolean. True = Insertion is ok.
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
