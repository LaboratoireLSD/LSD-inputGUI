"""
.. module:: MedList

.. codeauthor::  Mathieu Gagnon <mathieu.gagnon.10@ulaval.ca>

:Created on: 2010-01-06

"""

from PyQt4 import QtCore, QtGui
from util.DocPrimitive import PrimitiveDict

#Global variables to modify the look of the application
#AspectRatio = 5
#Height = 30

class MedListView(QtGui.QListWidget):
    '''
    This class is responsible of controlling the refresh of a QGraphicsScene and and the interactions of the user with the scene.
    Most of it is reimplemented from QGraphicsView.
    This class allows a user-friendly display of a xsd file, virtually contained in a PrimitiveDict.
    The user can use this class to drag and add a graphical representation of a primitive.
    '''
    def __init__(self, pmtDict):
        '''
        Constructor.
        
        :param pmtDict: the virtual .xsd to display
        '''
        QtGui.QListWidget.__init__(self)
        #Assign dictionnary
        self.pmtDict = pmtDict
        #temp reference to PrimitiveDict
        pmtDictRef = PrimitiveDict()
        #Set Backgorund color of the viewport
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.All,QtGui.QPalette.Background,QtGui.QColor(224,255,255))
        self.viewport().setPalette(palette)
        self.viewport().setBackgroundRole(QtGui.QPalette.Background)
        #Adding  graphical primitives to the scene
        docPmtInfoList = dict([(self.pmtDict[k].getMappedName() if self.pmtDict[k].getMappedName() else self.pmtDict[k].name ,self.pmtDict[k]) for k in self.pmtDict.keys()])
        keyList = sorted(docPmtInfoList.keys(), key=str.lower)
        for x in keyList:
            #For the moment, Data type primitives are hidden since they are never used in the trees
            if x in [item.getMappedName() for item in pmtDictRef._getPossibleSubstitutions("_genericType", True)]:
                continue
            newListItem = QtGui.QListWidgetItem(docPmtInfoList[x].getMappedName())
            newListItem.setBackgroundColor(QtGui.QColor(224,255,255))
            newListItem.doc = docPmtInfoList[x]
            self.addItem(newListItem)

        #Flags
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    def mouseMoveEvent(self, event):
        '''
        Reimplementation of QGraphicsView.mouseMoveEvent(self,event) virtual function.
        Initiates a drag event.
        
        :param event: see QGraphicsView documentation for more information
        '''
        data = QtCore.QMimeData()
        itemMoved = self.itemAt(event.pos())
        if itemMoved:
            data.setText(itemMoved.doc.name)
            #Next lines allow the item to be seen in the drag operation
            tmpImage = QtGui.QImage(QtCore.QSize(200,60), QtGui.QImage.Format_ARGB32_Premultiplied)
            tmpImage.fill(0)
            tmpPainter = QtGui.QPainter(tmpImage)
            tmpPainter.drawText(QtCore.QRectF(0, 0, 200, 30), QtCore.Qt.AlignLeft, itemMoved.doc.getMappedName()if itemMoved.doc.getMappedName() else itemMoved.doc.name)
            tmpPainter.drawRect(QtCore.QRectF(0, 0, 199, 29))
            tmpPainter.end()
            tmpPixmap = QtGui.QPixmap()
            drag = QtGui.QDrag(self)
            drag.setPixmap(tmpPixmap.fromImage(tmpImage))
            drag.setHotSpot(QtCore.QPoint(75, 15))
            drag.setMimeData(data)
            drag.exec_(QtCore.Qt.MoveAction)
        