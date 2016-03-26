'''
Created on 2010-01-06

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

from PyQt4 import QtCore, QtGui, QtXml
from model.PrimitiveModel import Primitive as treeEditorPmtModel
from model.LocalVariableModel import LocVarsModel
from editor.MedList import MedListView
from PyQt4.QtSvg import QSvgGenerator
from editor.treeComponents import ChoiceComboBoxModel

#Global variables to modify the look of the application
glob_Width = 150
glob_Height = 35
glob_RowDist = 200
glob_ColDist = 55

class MedTreeView(QtGui.QGraphicsView):
    '''
    This class is responsible of controlling the refresh of a QGraphicsScene and and the interactions of the user with the scene
    Most of it is reimplemented from QGraphicsView
    This class allows a user-friendly display of a xml file
    This class implements tools to allow quick and easy modification of xml files
    '''
    
    def __init__(self,domNode = QtXml.QDomNode(),mainWindow=None):
        '''
        @summary Constructor
        @param mainWindow : application's mainWindow
        @param domNode : xml dom node, root of the xml tree we want to display
        '''
        #Initialize scene
        QtGui.QGraphicsView.__init__(self)
        self.setScene(QtGui.QGraphicsScene())
        self.scene().setBackgroundBrush(QtGui.QBrush(QtGui.QColor(173,216,250)))
        self.mainWindow = mainWindow
        #Dom Node of the tree
        self.dom = domNode
        #Pointer to local variable model
        self.locVarModel = None
        #Drawing flags
        self.setAcceptDrops(True)
        #Variable to emulate focused Item(needed cause focused Item loses focus when we click out of the scene)
        self.currentItem = None
        #Model Load
        self.primitive = treeEditorPmtModel(None, None,self, self.dom)
        #Stack for undo/redo commands
        self.undoStack = QtGui.QUndoStack()
        
        #Loading and updating View
        treeHeight, mainGroup = self._loadTree(self.primitive,0,0,0)
        self.scene().addItem(mainGroup)
        
    
    def _loadTree(self,primitive,row,column,parentRow):
        '''
        This is a recursive function
        @summary Constructs the graphical elements that will be displayed
        @param primitive : PrimitiveModel.Primitive instance, root of the xml dom we want to display
        @params row, column, parentRow : needed to correctly position the graphical objects in the scene
        '''              
        #Initialize relative row number(relative row is the row in the subtree)
        relRow=0

        #if primitive has children
        if primitive.countChildren() != 0 :
            #Create graphical object
            if primitive.isRootPmt:
                #Start at 0 if it is root node
                newGraphItem = MedTreeItem(QtCore.QPointF(0,row*glob_ColDist),QtCore.QPointF(glob_Width,glob_Height),self)
            else:
                newGraphItem = MedTreeItem(QtCore.QPointF(glob_RowDist,row*glob_ColDist),QtCore.QPointF(glob_Width,glob_Height),self)

            #Make a link between graphic item and model item via a primitive
            newGraphItem.setPrimitive(primitive)
            newGraphItem.connect(primitive,QtCore.SIGNAL("ErrorFound()"),newGraphItem.paintHook)
            self.connect(primitive,QtCore.SIGNAL("ErrorFound()"),self.updateErrorLog)
            #Testing if root node
            if not primitive.isRootPmt:
                #Drawing line to parent
                if not row :
                    newGraphItem.parentLine = QtGui.QGraphicsLineItem(-(glob_RowDist-(glob_Width)),glob_Height/2,0,glob_Height/2,newGraphItem)
                    newGraphItem.parentLine.setPen(QtGui.QPen(QtCore.Qt.DashLine))
                else:
                    newGraphItem.parentLine = QtGui.QGraphicsLineItem(-(glob_RowDist-(glob_Width))/2,glob_Height/2,0,glob_Height/2,newGraphItem)
                    newGraphItem.parentLine.setPen(QtGui.QPen(QtCore.Qt.DashLine))
                if primitive.guiGetBranchInfo():
                    #Draw Comment if needed
                    newGraphItem.info = QtGui.QGraphicsTextItem(primitive.guiGetBranchInfo(),newGraphItem)
                    newGraphItem.info.setFont(QtGui.QFont("Helvetica",9))          
                    newGraphItem.info.setTextWidth(150)
                    newGraphItem.info.setPos(QtCore.QPointF(0,-newGraphItem.info.boundingRect().height()))
                    newGraphItem.info.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
                #Draw choice list
                #newGraphItem.choiceList = MedTreeArrow(QtCore.QPointF(125,38),newGraphItem)
                
            #Draw Cross Item   
            newGraphItem.cross=MedTreeCross(QtCore.QPointF(glob_RowDist-31,3),QtCore.QPointF(12,12),self)
            newGraphItem.cross.setParentItem(newGraphItem)
            
            #Cycle through all children
            for i in range (0,primitive.countChildren()):
                #Recursion+add number of row
                rowInc, item = self._loadTree(primitive.guiGetChild(i),relRow,column+1,row)
                item.setParentItem(newGraphItem)
                item.setZValue(primitive.countChildren()-i)
                if i:
                    if item.getPrimitive().guiGetBranchTag():   
                        #Draw branch tag if needed
                        item.branchTagEditor = MedTreeEditableBranchTag(item,item.getPrimitive().guiGetBranchTag()[2])
                relRow+=rowInc
            
            #Draw Line to children
            if primitive.countChildren() > 1:
                newGraphItem.childrenLine = QtGui.QGraphicsLineItem(175,glob_Height/2,175,newGraphItem.graphicalPmtList[-1].pos().y()+glob_Height/2,newGraphItem)
                newGraphItem.childrenLine.setPen(QtGui.QPen(QtCore.Qt.DashLine))
            #Draw asterisk if items has comment
            if primitive.hasUserComment():#
                newAsteriskItem = QtGui.QGraphicsTextItem("*",newGraphItem)
                newAsteriskItem.setPos(QtCore.QPointF(135,-22))
                newAsteriskItem.setDefaultTextColor(QtCore.Qt.white)
                newAsteriskItem.setFont(QtGui.QFont("DejaVu [Serif]",18))
                newGraphItem.asterisk = newAsteriskItem
                
            #Return relative row and graphical item
            return relRow, newGraphItem
        
        #Simple case : Primitive has no child    
        else:
            #Create graphical object
            if primitive.isRootPmt:
                #Start at 0 if it is root node
                newGraphItem = MedTreeItem(QtCore.QPointF(0,row*glob_ColDist),QtCore.QPointF(glob_Width,glob_Height),self)
            else:
                newGraphItem = MedTreeItem(QtCore.QPointF(glob_RowDist,row*glob_ColDist),QtCore.QPointF(glob_Width,glob_Height),self)
            #Make a link between graphic item and model item via a primitive
            newGraphItem.setPrimitive(primitive)
            newGraphItem.connect(primitive,QtCore.SIGNAL("ErrorFound()"),newGraphItem.paintHook)
            self.connect(primitive,QtCore.SIGNAL("ErrorFound()"),self.updateErrorLog)
            #Testing if root node
            if not primitive.isRootPmt:
                #Drawing line to parent
                if not row :
                    newGraphItem.parentLine = QtGui.QGraphicsLineItem(-(glob_RowDist-(glob_Width)),glob_Height/2,0,glob_Height/2,newGraphItem)
                    newGraphItem.parentLine.setPen(QtGui.QPen(QtCore.Qt.DashLine))
                else:
                    newGraphItem.parentLine = QtGui.QGraphicsLineItem(-(glob_RowDist-(glob_Width))/2,glob_Height/2,0,glob_Height/2,newGraphItem)
                    newGraphItem.parentLine.setPen(QtGui.QPen(QtCore.Qt.DashLine))
                if primitive.guiGetBranchInfo():
                    #Draw Info if needed
                    newGraphItem.info = QtGui.QGraphicsTextItem(primitive.guiGetBranchInfo(),newGraphItem)
                    newGraphItem.info.setFont(QtGui.QFont("Helvetica",9))          
                    newGraphItem.info.setTextWidth(150)
                    newGraphItem.info.setPos(QtCore.QPointF(0,-newGraphItem.info.boundingRect().height()))
                    newGraphItem.info.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
                #Draw choice list
                #newGraphItem.choiceList = MedTreeArrow(QtCore.QPointF(125,38),newGraphItem)
            
            #Draw asterisk if items has comment
            if primitive.hasUserComment():#
                newAsteriskItem = QtGui.QGraphicsTextItem("*",newGraphItem)
                newAsteriskItem.setPos(QtCore.QPointF(135,-22))
                newAsteriskItem.setDefaultTextColor(QtCore.Qt.white)
                newAsteriskItem.setFont(QtGui.QFont("DejaVu [Serif]",18))
                newGraphItem.asterisk = newAsteriskItem
            
            #Return relative row and graphical item
            return 1, newGraphItem
        
    def addChild(self):
        '''
        Simple addChild function
        '''
        if isinstance(self.currentItem, MedTreeItem):
            self.undoStack.push(CommandAddChild(self))
        
    def addSiblingAfter(self):
        '''
        Simple addSiblingAfter function
        '''
        if isinstance(self.currentItem, MedTreeItem):
            if self.currentItem.getPrimitive().getParentPrimitive():
                self.undoStack.push(CommandAddSA(self))
                self.updateDirtyState()
                
    def addSiblingBefore(self):
        '''
        Simple addSiblingAfter function
        '''
        if isinstance(self.currentItem, MedTreeItem):
            if self.currentItem.getPrimitive().getParentPrimitive():
                self.undoStack.push(CommandAddSB(self))
                self.updateDirtyState()
                
    def addMultipleChildren(self,numChildToAdd):
        '''
        Simple addMultipleChildren function
        '''
        if isinstance(self.currentItem, MedTreeItem):
            self.undoStack.push(CommandAddMC(self,numChildToAdd))
            self.updateDirtyState()
            
    def copy(self):
        '''
        @summary Simple copy function
        Looks if a MedTreeItem is currently selected and pastes it(and all its subtree) to MainEditorWindow's clipboard variable
         '''
        if isinstance(self.currentItem,MedTreeItem):
            self.mainWindow.clipboard = self.currentItem.getPrimitive()._writeDom(self.dom.ownerDocument())
            self.updateDirtyState()
            
    def paste(self):
        '''
        Simple paste function
        '''
        if isinstance(self.currentItem,MedTreeItem):
            if self.mainWindow.clipboard:
                self.undoStack.push(CommandPaste(self))
                self.updateDirtyState()
                
    def cut(self):
        '''
        @summary Simple cut function
        '''
        if isinstance(self.currentItem,MedTreeItem):
            self.undoStack.push(CommandCut(self))
            self.updateDirtyState()
            
    def save(self):
        '''
        @summary Saves DOM
        '''
        parentNode = self.dom.parentNode()
        self.dom.parentNode().replaceChild(self.primitive._writeDom(self.dom.ownerDocument()),self.dom)
        self.dom = parentNode.firstChild()
        self.saveLocals()
        
    def saveLocals(self):
        '''
        @summary Saves Local Variables
        '''
        if self.locVarModel:
            self.locVarModel.getBaseModel().save(self.dom.parentNode())
        self.updateDirtyState()
        
    def getLocVarModel(self):
        '''
        @summary Return Local Variable Model associated with this tree
        Create one if it doesn't exist
        '''
        if not self.locVarModel:
            self.locVarModel = LocVarsModel(self.dom.parentNode())
        return self.locVarModel
    
    def dragEnterEvent(self,event):
        '''
        @summary Reimplementation of virtual function QtGraphicsView.dragEnterEvent(self,event)
        Ensure event come from a MedListView
        @param event : see QGraphicsView documentation for more information
        '''
        if not isinstance(event.source(),MedListView):
            event.ignore()
        else:
            self.clearFocus()
            event.acceptProposedAction()

    def dragLeaveEvent(self,event):
        '''
        @summary Reimplementation of virtual function QtGraphicsView.dragLeaveEvent(self,event)
        Ignore the event, or else Qt will complain receiving a dragLeaveEvent before a dragEnterEvent
        @param event : see QGraphicsView documentation for more information
        '''
        event.ignore()
        
    def dropEvent (self, event):
        '''
        @summary Reimplementation of virtual function QtGraphicsView.droptEvent(self,event)
        Takes MimeData previously created by the drag event from a MedList
        Main idea : - do nothing if the drop operation comes from a drag event initiated by self(medTreeView)
                    - ensure the drop event landed on a MedTreeItem, a graphical representation of a primitive
                    - Create CommandDropChild, that will take care of the model and tree management
        @param event : see QGraphicsView documentation for more information
        '''
        if event.source() == self:
            #Source is self : do nothing
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            #Source is other : update Tree
            #Keep reference on currentItem
            itemToUpdate = self.currentItem
            #Look if there is an object under the mouse Pointer
            if not self.scene().itemAt(self.mapToScene(event.pos())) == None:
                replacedItem = self.scene().itemAt(self.mapToScene(event.pos()))
                #Look if this object belongs to model
                if isinstance(replacedItem,MedTreeItem):
                    #Test if it is root Node
                    if not replacedItem.pmt.isRootPmt:
                        #clear Current item
                        self.currentItem = None
                        if isinstance(itemToUpdate,MedTreeItem):
                            #Make sure last current Item is repainted to avoid item being rendered as still selected
                            #Do it before tree is modified, because if modifying tree trashes this item a runtime error will occur
                            itemToUpdate.paintHook()
                    #Create and push CommandDropChild on undo stack
                    self.undoStack.push(CommandDropChild(self,replacedItem,event.mimeData().text()))
                    self.updateDirtyState()
                    
                        
        QtGui.QGraphicsView.dropEvent(self,event)
    
    def keyPressEvent(self,event):
        '''
        @summary Reimplementation of virtual function QtGraphicsView.dragLeaveEvent(self,event)
        Test which key(s) has been pressed and call corresponding function
        @param event : see QGraphicsView documentation for more information
        '''
        if self.scene().focusItem() == self.currentItem and self.currentItem:
            if event.key() == QtCore.Qt.Key_P:
                #Code to save self.dom(a QDomNode) in a xml file for debugging
                domToSave = self.primitive._writeDom()
                FilePointer = QtCore.QFile("Tests/EditorTest.xml")
                if not FilePointer.open(QtCore.QIODevice.ReadWrite | QtCore.QIODevice.Truncate):
                    print("File cannot be opened")
                else:
                    domToSave.save(QtCore.QTextStream(FilePointer),2)
                    print("print Succeeded")
            #Dump debugging actions
            elif event.key() == QtCore.Qt.Key_X:
                if isinstance(self.currentItem,MedTreeItem):
                    self.currentItem.dumpModelInfos()
            #Call cut function
            elif event.key() == QtCore.Qt.Key_Delete or event.key() == QtCore.Qt.Key_Backspace:
                if not isinstance(self.scene().focusItem(), QtGui.QGraphicsTextItem):
                    self.cut()
                    event.accept()
            
            #Allow Tree Navigation using arrow keys
            #Update manipulations need to be done or else painting is not done until a refresh is requested by Qt's paint system
            elif event.key() == QtCore.Qt.Key_Up:
                if self.currentItem.parentItem():
                    if not self.currentItem.parentItem().graphicalPmtList[0] == self.currentItem:
                        lUpdatePtr = self.currentItem
                        self.currentItem = self.currentItem.parentItem().graphicalPmtList[self.currentItem.parentItem().graphicalPmtList.index(self.currentItem)-1]
                        self.centerOn(self.currentItem)
                        self.currentItem.paintHook()
                        lUpdatePtr.paintHook()
                        self.generalUpdate()
            elif event.key() == QtCore.Qt.Key_Down:
                if self.currentItem.parentItem():
                    if not self.currentItem.parentItem().graphicalPmtList[-1] == self.currentItem:
                        lUpdatePtr = self.currentItem
                        self.currentItem = self.currentItem.parentItem().graphicalPmtList[self.currentItem.parentItem().graphicalPmtList.index(self.currentItem)+1]
                        self.centerOn(self.currentItem)
                        self.currentItem.paintHook()
                        lUpdatePtr.paintHook()
                        self.generalUpdate()
            elif event.key() == QtCore.Qt.Key_Left:
                if self.currentItem.parentItem():
                    lUpdatePtr = self.currentItem
                    self.currentItem = self.currentItem.parentItem()
                    self.centerOn(self.currentItem)
                    self.currentItem.paintHook()
                    lUpdatePtr.paintHook()
                    self.generalUpdate()
            elif event.key() == QtCore.Qt.Key_Right:
                if self.currentItem.graphicalPmtList:
                    lUpdatePtr = self.currentItem
                    self.currentItem = self.currentItem.graphicalPmtList[0]
                    self.centerOn(self.currentItem)
                    self.currentItem.paintHook()
                    lUpdatePtr.paintHook()
                    self.generalUpdate()
            
        QtGui.QGraphicsView.keyPressEvent(self,event)
        
        
    def mouseDoubleClickEvent(self,event):
        '''
        @summary Reimplementation of QGraphicsView'.mouseDoubleClickEvent(self,event) virtual function
        Open a new MedTreeView if clicked primitive has a doubleClickBehavior(TokenCallProcess and TokenPushProcess for the moment)
        @param event : see QGraphicsView documentation for more information
        '''
        
        if isinstance(self.currentItem,MedTreeItem):
            if self.currentItem.getPrimitive().guiDoubleClickBehavior():
                self.mainWindow.openTab(self.currentItem.getPrimitive().getAttributeByName("inLabel").getValue())
                return
        
        QtGui.QGraphicsView.mouseDoubleClickEvent(self,event)
        
                   
    def mousePressEvent(self,event):
        '''
        @summary Reimplementation of QGraphicsView.mousePressEvent(self,event) virtual function
        Main idea : a mouse press event can be performed to choose a primitive so the user can see its attributes(properties)
        Hence, call an update on the properties/error/definition/comment tabs
        @param event : see QGraphicsView documentation for more information
        '''
        #First, look if item is a proxy widget
        if isinstance(self.scene().focusItem(),QtGui.QGraphicsProxyWidget):
            #Find its parent(in our case, the comboBox's proxy)
            proxyToDelete = self.scene().focusItem().parentItem()
            if not self.scene().itemAt(self.mapToScene(event.pos())) == self.scene().focusItem():
                #User clicked out of popup list, delete proxy immediately
                QtGui.QGraphicsView.mousePressEvent(self,event)
                self.scene().removeItem(proxyToDelete)
                return
        
        
        QtGui.QGraphicsView.mousePressEvent(self,event)
       
        #Keep reference on currentItem to later call an update
        itemToUpdate = self.currentItem
        
        if isinstance(self.scene().focusItem(),MedTreeItem):
            self.currentItem = self.scene().focusItem()
        elif not self.scene().focusItem():
            self.currentItem = None
        
        #Call a a refresh
        if isinstance(itemToUpdate,MedTreeItem):
            itemToUpdate.paintHook()
        
        self.updateProperties()
        self.updateComAndDef()
        self.updateErrorLog()
        
        if event.button() == QtCore.Qt.RightButton and self.currentItem:
            self.mainWindow.popNodeMenu(event.globalPos())
        
        #event.accept()

#    def focusOutEvent(self,event):
#        '''
#        @summary Reimplementation of QGraphicsView.focusOutEvent(self,event) virtual function
#        Look if a MedTreeComboBox is presently the focus item
#        If so delete it, else do as usual
#        @param event : see QGraphicsView documentation for more information
#        '''
#        #First, look if item is a proxy widget
#        if isinstance(self.scene().focusItem(),QtGui.QGraphicsProxyWidget):
#            #Find its parent(in our case, the comboBox's proxy)
#            proxyToDelete = self.scene().focusItem().parentItem()
#            #User clicked out of popup list, delete proxy immediately
#            self.scene().removeItem(proxyToDelete)
#            
#        QtGui.QGraphicsView.focusOutEvent(self,event)
    
    def wheelEvent(self,event):
        '''
        @summary Reimplementation of QGraphicsView.wheelEvent(self,event) virtual function
        Allow Ctrl-wheel to scroll horizontally, else do as usual
        @param event : see QGraphicsView documentation for more information
        '''
        if event.modifiers() == QtCore.Qt.ControlModifier:
            if event.delta() > 0:
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value()-self.horizontalScrollBar().singleStep())
            else:
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value()+self.horizontalScrollBar().singleStep())
            event.accept()
        else:
            QtGui.QGraphicsView.wheelEvent(self,event) 
            
    def _updateTree(self,modifiedItem,assocPmt):
        '''
        @summary Update modifiedItem's subTree
        @param modifiedItem : MedTreeItem being modified
        @param assocPmt : The  primitive associated with the modified object
        '''
        if modifiedItem.parentItem() == None:
            #First primitive of the tree, then reload Tree
            self.scene().clear()
            treeHeight, newSubTree = self._loadTree(assocPmt, 0,0, 0)
            self.scene().addItem(newSubTree)
            return newSubTree
        
        #Gather information about current positions of the graphical items
        row = modifiedItem.getRow()
        column  = modifiedItem.getColumn()
        parentRow = modifiedItem.parentItem().getRow()
        
        #Reload modified Item and its subtree
        modifiedItem.collapseSubTree(True)
        treeHeight, newSubTree = self._loadTree(assocPmt, row, column, parentRow)
        newSubTree.collapseSubTree()
        #Set Parent Item and update parent's list of graphical primitives
        newSubTree.setParentItem(modifiedItem.parentItem(),False)
        modifiedItem.parentItem().graphicalPmtList[modifiedItem.parentItem().graphicalPmtList.index(modifiedItem)] = newSubTree 
        
        newSubTree.stackBefore(modifiedItem)
        newSubTree.setZValue(modifiedItem.zValue())
        self.scene().removeItem(modifiedItem)
        newSubTree.expandSubTree(True)
        newSubTree.manageBranchTag()
        return newSubTree
    
    def _updateTreeHook(self,text):
        '''
        @summary Called when a medTreeItem is changed using the comboBox method
        Main idea : do like the normal _updateTree but delete arrow first to avoid seg faults
        @param text : name of the primitive we want this node to become
        '''
        arrow = self.sender().proxyParent.parentItem()
        replacedItem = self.sender().proxyParent.parentItem().parentItem()
        realPmtName =  self.sender().model().dictRealNames[str(text).lstrip()]
        #Hide arrow before deleting it or else it pops top corner left before getting trashed
        arrow.setVisible(False)
        arrow.setParentItem(None)
        arrow.deleteLater()
        pmtPos = replacedItem.parentItem().getPrimitive().guiGetChildPos(replacedItem.getPrimitive())
        replacedItem.getPrimitive().getParentPrimitive().guiSetModelData(realPmtName,pmtPos)
        #Update Tree
        self.currentItem = self._updateTree(replacedItem,replacedItem.getPrimitive().getParentPrimitive().guiGetChild(pmtPos))
        self.generalUpdate()
    
    def generalUpdate(self):
        '''
        @summary Call three update functions
        '''
        self.updateProperties()
        self.updateComAndDef()
        self.updateErrorLog()
        
    def updateProperties(self):
        '''
        @summary Create and show the widgets that contain the information about currentItem's primitive attributes
        '''
        #Clear the current tab widget containing the properties of the last selected item
        for i in range(0,self.mainWindow.tabWidget_3.count()):
            if str(self.mainWindow.tabWidget_3.tabText(i)) == "Properties":
                self.mainWindow.tabWidget_3.removeTab(i)
                
        if isinstance(self.currentItem,MedTreeItem):
            #Create a new one
            self.propertyWidget = QtGui.QWidget()
            
            #Get the attribute layout from the primitive
            tmpPmt = self.currentItem.getPrimitive()
            layoutAttributes = tmpPmt.guiGetAttrLayout()
            self.propertyWidget.setLayout(layoutAttributes)
            
            #Add widget to the mainEditorFrame corresponding tab widget
            self.mainWindow.tabWidget_3.insertTab(0,self.propertyWidget,"Properties")
            self.mainWindow.tabWidget_3.setCurrentIndex(0)
    
    def updateComAndDef(self):
        '''
        @summary Create and show the widgets that contain the definition of the currently selected variable and the comment associated to it, if any
        '''
        self.mainWindow.tab_Widget_4.clear()
        if isinstance(self.currentItem,MedTreeItem):
            commentTab = self.currentItem.getPrimitive().guiCreateEditor(self.mainWindow.tab_Widget_4)
            self.currentItem.connect(commentTab,QtCore.SIGNAL("textChanged()"),self.currentItem.manageAsterisk)
            
    def updateErrorLog(self):
        '''
        @summary Create the error log located next to the Properties tab
        '''
        for i in range(0,self.mainWindow.tabWidget_3.count()):
            if str(self.mainWindow.tabWidget_3.tabText(i)) == "Errors":
                self.mainWindow.tabWidget_3.removeTab(i)
        if isinstance(self.currentItem,MedTreeItem):
            if self.currentItem.getPrimitive().guiGetEvents():
                self.errorLogWidget = QtGui.QListWidget()  
                for events in  self.currentItem.getPrimitive().guiGetEvents():
                    self.errorLogWidget.addItem(events.generateEventMsg())
                
                self.mainWindow.tabWidget_3.addTab(self.errorLogWidget,"Errors")   
        
    def updateDirtyState(self):
        '''
        Look if file is dirty
        If so, add asterisk(*) to tab's name
        '''
        currText =  self.mainWindow.tabWidget_2.tabText(self.mainWindow.tabWidget_2.indexOf(self))
        if not self.primitive._checkForSimilarDoms(self.dom):
            currText = str(currText).rstrip('*')+'*'
            self.mainWindow.tabWidget_2.setTabText(self.mainWindow.tabWidget_2.indexOf(self),currText)
            return
        self.mainWindow.tabWidget_2.setTabText(self.mainWindow.tabWidget_2.indexOf(self),str(currText).rstrip('*'))
        
    def printSVGFile(self, svgFilePath=""):
        '''
        @summary Prints a .svg of the tree
        @param svgFilePath : filePath we want the picture to be saved to
        '''
        if not svgFilePath:
            svgFilePath = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save SVG file"),
                                                            "", self.tr("SVG files (*.svg);;All files (*);;"))
            return
        
        if str(svgFilePath).rpartition(".")[2] != "svg":
            svgFilePath+=".svg"
        
        blackAndWhite = QtGui.QInputDialog.getItem(self, self.tr("Picture options"), self.tr("Colors") , ["RGB","Grayscale"],0,False)
        if blackAndWhite == "RGB":
            gen = QSvgGenerator()
            gen.setFileName(svgFilePath)
            gen.setSize(QtCore.QSize(self.sceneRect().width(), self.sceneRect().height()))
            gen.setViewBox(self.sceneRect())
            painter = QtGui.QPainter(gen)
            self.scene().render(painter,self.sceneRect())
            painter.end()
        else:
            #Grayscale painting requires manipulations, since Qt doesn't offer any built-in functions to paint in grayscale
            tmpImage = QtGui.QImage(self.scene().sceneRect().width(),self.scene().sceneRect().height(),QtGui.QImage.Format_RGB32)
            painter = QtGui.QPainter(tmpImage)
            self.scene().setBackgroundBrush(QtGui.QBrush(QtGui.QColor(255,255,255)))
            self.scene().render(painter)
            painter.end()
            self.scene().setBackgroundBrush(QtGui.QBrush(QtGui.QColor(173,216,250)))
            grayScaleImage = QtGui.QImage(tmpImage.width(),tmpImage.height(),QtGui.QImage.Format_RGB32)
            progress = QtGui.QProgressDialog("Converting to gray scale","Cancel",0,0)
            progress.open()
            QtGui.QApplication.processEvents()
            for x in range(0,tmpImage.width()):
                QtGui.QApplication.processEvents()
                for y in range(0,tmpImage.height()):
                    value = 0.3*((tmpImage.pixel(x,y)-4278190080)>>16)+0.59*((tmpImage.pixel(x,y)-4278190080)>>8&255)+0.11*((tmpImage.pixel(x,y)-4278190080)&255)
                    pixelColor = QtGui.qRgb(int(value), int(value), int(value))
                    grayScaleImage.setPixel(x, y, pixelColor)
            progress.reset()
            #Use python byte for fast access
#            imgData = []
#            for x in range(0,tmpImage.width()):
#                for y in range(0,tmpImage.height()):
#                    value = 0.3*((tmpImage.pixel(x,y)-4278190080)>>16)+0.59*((tmpImage.pixel(x,y)-4278190080)>>8&255)+0.11*((tmpImage.pixel(x,y)-4278190080)&255)
#                    imgData.extend([255,int(value),int(value),int(value)])
#            grayScaleImage = QtGui.QImage(bytes(imgData),tmpImage.width(),tmpImage.height(),QtGui.QImage.Format_RGB32)
            #Save file
            progress.deleteLater()
            gen = QSvgGenerator()
            gen.setFileName(svgFilePath)
            gen.setSize(QtCore.QSize(grayScaleImage.width(), grayScaleImage.height()))
            gen.setViewBox(QtCore.QRect(0,0,grayScaleImage.width(),grayScaleImage.height()))
            painter = QtGui.QPainter(gen)
            painter.drawImage(QtCore.QRect(0,0,grayScaleImage.width(),grayScaleImage.height()),grayScaleImage)
            painter.end()

    def printPreview(self):
        '''
        @summary Prints a .png preview of the tree
        '''
        maxSize = 32767
        #First, ensure image is not bigger or equal to 32768 x 32768 pixels, qt's x11 maximum authorized pixmap size
        if self.sceneRect().width() >maxSize or self.sceneRect().height() >maxSize:
            pixmap = QtGui.QPixmap(150,100)
            painter = QtGui.QPainter(pixmap)
            painter.fillRect(QtCore.QRectF(0,0,150,100),QtGui.QBrush(QtGui.QColor(173,216,250)))
            painter.drawText(QtCore.QPointF(0,50), "No preview available")
            painter.end()
        else:
            #Old Method, slow with some kind of trees
            pixmap = QtGui.QImage(self.sceneRect().width(),self.sceneRect().height(),QtGui.QImage.Format_RGB32)
            #pixmap = QtGui.QPixmap(self.sceneRect().width(),self.sceneRect().height())
            painter = QtGui.QPainter(pixmap)
            #self.render(painter)
            self.scene().render(painter)
            painter.end()
            
        return pixmap
'''
Undo/Redo system
'''
class CommandAddChild(QtGui.QUndoCommand):
    '''
    Class embedding the addChild function, hence allowing the undo/redo functionalities
    '''
    def __init__(self, parentView,description="Paste"):
        QtGui.QUndoCommand.__init__(self,description)
        self.parentView = parentView
        #Redo flag
        self.firstFlag = True
        #Undo info
        self.currentDom = self.parentView.primitive._writeDom(self.parentView.dom.ownerDocument())
        self.oldCrossState = [item.activated for item in self.parentView.scene().items() if isinstance(item,MedTreeCross)]
        
    def redo(self):
        '''
        @summary Adds a child to the currently selected graphical representation of a primitive, hence adding it into the model
        '''
        if self.firstFlag:
            #Add primitive to model
            self.parentView.currentItem.getPrimitive().guiAddChild("Control_Nothing", self.parentView.currentItem.getPrimitive().countChildren())
            #Create graphical primitive
            if self.parentView.currentItem.graphicalPmtList:
                childOffset = 0
                if self.parentView.currentItem.graphicalPmtList[-1].cross:
                    if self.parentView.currentItem.graphicalPmtList[-1].cross.activated:
                        #Child located above has a subTree, compute height of this subTree
                        childOffset = self.parentView.currentItem.graphicalPmtList[-1].cross._calculateAmountOfSpace()
                treeHeight, newGraphicalPmt = self.parentView._loadTree(self.parentView.currentItem.getPrimitive().guiGetChild(-1),self.parentView.currentItem.graphicalPmtList[-1].getRow()+childOffset/glob_ColDist+1,self.parentView.currentItem.getColumn()+1,self.parentView.currentItem.getRow())
                
                #Translate items located below
                yPos = self.parentView.currentItem.graphicalPmtList[-1].scenePos().y()+childOffset
                for item in self.parentView.scene().items(QtCore.QRectF(0,yPos+glob_Height,self.parentView.scene().sceneRect().width(),self.parentView.scene().sceneRect().height()-yPos)):
                    if item.parentItem().scenePos().y() < yPos+glob_Height and isinstance(item,MedTreeItem):
                            item.moveBy(0,glob_ColDist)
            else:
                #The added child will be the first child added, create and add
                treeHeight, newGraphicalPmt = self.parentView._loadTree(self.parentView.currentItem.getPrimitive().guiGetChild(-1),0,self.parentView.currentItem.getColumn()+1,self.parentView.currentItem.getRow())
                self.parentView.currentItem.cross = MedTreeCross(QtCore.QPointF(glob_RowDist-31,3),QtCore.QPointF(12,12),self.parentView)
                self.parentView.currentItem.cross.setParentItem(self.parentView.currentItem)
            
            #Adjust z value of siblings
            for item in self.parentView.currentItem.graphicalPmtList:
                item.setZValue(item.zValue()+1)
            #Add to scene
            newGraphicalPmt.setParentItem(self.parentView.currentItem)
            self.parentView.currentItem.lookForLineModif()
            newGraphicalPmt.manageBranchTag()
            if len(self.parentView.currentItem.graphicalPmtList)==2:
                #A second child was added to the current item, create vertical line
                self.parentView.currentItem.childrenLine = QtGui.QGraphicsLineItem(175,glob_Height/2,175,self.parentView.currentItem.graphicalPmtList[-1].pos().y()+glob_Height/2,self.parentView.currentItem)
                self.parentView.currentItem.childrenLine.setPen(QtGui.QPen(QtCore.Qt.DashLine))
            
            
            #Notify view that scene Rect changed(QGraphicsView doesn't adjust scroll bars when items that are not visible in viewport are translated outside of the last set sceneRect)
            self.parentView.updateSceneRect(self.parentView.sceneRect())
            #Collect info for eventual redos
            self.newDom = self.parentView.primitive._writeDom(self.parentView.dom.ownerDocument())
            self.newCrossState = [item.activated for item in self.parentView.scene().items() if isinstance(item,MedTreeCross)]
            self.firstFlag = False
            
        else:
            #Real redo
            self.parentView.scene().clear()
            #Model Load
            self.parentView.primitive = treeEditorPmtModel(None, None,self.parentView, self.newDom)
            treeHeight, mainGroup = self.parentView._loadTree(self.parentView.primitive,0,0,0)
            self.parentView.scene().addItem(mainGroup)
            newCrosses = [items for items in self.parentView.scene().items() if isinstance(items,MedTreeCross)]
            for crosses in newCrosses :
                crosses.fakePress(self.newCrossState[newCrosses.index(crosses)])
            self.parentView.currentItem = None
            self.parentView.generalUpdate()
        
    def undo(self):
        '''
        Undo add child operation
        '''
        self.parentView.scene().clear()
        #Model Load
        self.parentView.primitive = treeEditorPmtModel(None, None,self.parentView, self.currentDom)
        treeHeight, mainGroup = self.parentView._loadTree(self.parentView.primitive,0,0,0)
        self.parentView.scene().addItem(mainGroup)
        newCrosses = [items for items in self.parentView.scene().items() if isinstance(items,MedTreeCross)]
        for crosses in newCrosses :
            crosses.fakePress(self.oldCrossState[newCrosses.index(crosses)])
        self.parentView.currentItem = None
        self.parentView.generalUpdate()
            
class CommandAddMC(QtGui.QUndoCommand):
    '''
    Class embedding the addChild function, hence allowing the undo/redo functionalities
    '''
    def __init__(self, parentView,numChild,description="Paste"):
        QtGui.QUndoCommand.__init__(self,description)
        self.parentView = parentView
        self.numChild = numChild
        #Redo flag
        self.firstFlag = True
        #Undo info
        self.currentDom = self.parentView.primitive._writeDom(self.parentView.dom.ownerDocument())
        self.oldCrossState = [item.activated for item in self.parentView.scene().items() if isinstance(item,MedTreeCross)]
        
    def redo(self):
        '''
        @summary Add numChild child to the current primitive 
        Reason : in switch(switch bins etc), adding numerous child can be useful
        '''
        if self.firstFlag:
            while self.numChild:
                #Create a CommandAdd function and call its redo function
                #CommandAdd object will not interfere with stack since it hasn't been push on it, but we have to manually call the redo
                #so it is performed the first time
                tmpCommandAdd = CommandAddChild(self.parentView)
                tmpCommandAdd.redo()
                self.numChild = self.numChild-1
            #Collect info for eventual redos
            self.newDom = self.parentView.primitive._writeDom(self.parentView.dom.ownerDocument())
            self.newCrossState = [item.activated for item in self.parentView.scene().items() if isinstance(item,MedTreeCross)]
            self.firstFlag = False
            
        else:
            #Real redo
            self.parentView.scene().clear()
            #Model Load
            self.parentView.primitive = treeEditorPmtModel(None, None,self.parentView, self.newDom)
            treeHeight, mainGroup = self.parentView._loadTree(self.parentView.primitive,0,0,0)
            self.parentView.scene().addItem(mainGroup)
            newCrosses = [items for items in self.parentView.scene().items() if isinstance(items,MedTreeCross)]
            for crosses in newCrosses :
                crosses.fakePress(self.newCrossState[newCrosses.index(crosses)])
            self.parentView.currentItem = None
            self.parentView.generalUpdate()
            
    def undo(self):
        '''
        Undo add child operation
        '''
        self.parentView.scene().clear()
        #Model Load
        self.parentView.primitive = treeEditorPmtModel(None, None,self.parentView, self.currentDom)
        treeHeight, mainGroup = self.parentView._loadTree(self.parentView.primitive,0,0,0)
        self.parentView.scene().addItem(mainGroup)
        newCrosses = [items for items in self.parentView.scene().items() if isinstance(items,MedTreeCross)]
        for crosses in newCrosses :
            crosses.fakePress(self.oldCrossState[newCrosses.index(crosses)])
        self.parentView.currentItem = None
        self.parentView.generalUpdate()
        
class CommandAddSA(QtGui.QUndoCommand):
    '''
    Class embedding the addSiblingAfter function, hence allowing the undo/redo functionalities
    '''
    def __init__(self, parentView,description="Paste"):
        QtGui.QUndoCommand.__init__(self,description)
        self.parentView = parentView
        #Redo flag
        self.firstFlag = True
        #Undo info
        self.currentDom = self.parentView.primitive._writeDom(self.parentView.dom.ownerDocument())
        self.oldCrossState = [item.activated for item in self.parentView.scene().items() if isinstance(item,MedTreeCross)]
        
    def redo(self):
        '''
        @summary Adds a child after the currently selected graphical representation of a primitive, hence adding it into the model
        '''
        if self.firstFlag:
            parentPmt = self.parentView.currentItem.getPrimitive().getParentPrimitive()
            pmtPos = self.parentView.currentItem.getPrimitive().getParentPrimitive().guiGetChildPos(self.parentView.currentItem.getPrimitive())
            parentPmt.guiAddChild("Control_Nothing", pmtPos)
            childOffset = 0
            if self.parentView.currentItem.cross:
                if self.parentView.currentItem.cross.activated:
                    #Child located above has a subTree, compute height of this subTree
                    childOffset = self.parentView.currentItem.cross._calculateAmountOfSpace()
            treeHeight, newGraphicalPmt = self.parentView._loadTree(parentPmt.guiGetChild(pmtPos+1),self.parentView.currentItem.getRow()+childOffset/glob_ColDist+1,self.parentView.currentItem.getColumn(),self.parentView.currentItem.parentItem().getRow())
            
            #Translate items located below
            yPos = self.parentView.currentItem.scenePos().y()+childOffset+glob_Height
            for item in self.parentView.scene().items(QtCore.QRectF(0,yPos,self.parentView.scene().sceneRect().width(),self.parentView.scene().sceneRect().height()-yPos)):
                if item.parentItem().scenePos().y() < yPos and isinstance(item,MedTreeItem):
                        item.moveBy(0,glob_ColDist)
            
            #Add to scene
            newGraphicalPmt.setParentItem(self.parentView.currentItem.parentItem(),False)
            newGraphicalPmt.parentItem().graphicalPmtList.insert(newGraphicalPmt.parentItem().graphicalPmtList.index(self.parentView.currentItem)+1,newGraphicalPmt)
            #Adjust z value of siblings
            for item in self.parentView.currentItem.parentItem().graphicalPmtList[0:pmtPos+1]:
                item.setZValue(item.zValue()+1)
            newGraphicalPmt.setZValue(self.parentView.currentItem.zValue()-1)
            #Look for branch tag
            newGraphicalPmt.manageBranchTag()
            self.parentView.currentItem.parentItem().lookForLineModif()
            if len(self.parentView.currentItem.parentItem().graphicalPmtList)==2:
                #A second child was added to the current item, create vertical line
                self.parentView.currentItem.parentItem().childrenLine = QtGui.QGraphicsLineItem(175,glob_Height/2,175,self.parentView.currentItem.parentItem().graphicalPmtList[-1].pos().y()+glob_Height/2,self.parentView.currentItem.parentItem())
                self.parentView.currentItem.parentItem().childrenLine.setPen(QtGui.QPen(QtCore.Qt.DashLine))
            
            #Notify view that scene Rect changed(QGraphicsView doesn't adjust scroll bars when items that are not visible in viewport are translated outside of the last set sceneRect)
            self.parentView.updateSceneRect(self.parentView.sceneRect())
            #Collect info for eventual redos
            self.newDom = self.parentView.primitive._writeDom(self.parentView.dom.ownerDocument())
            self.newCrossState = [item.activated for item in self.parentView.scene().items() if isinstance(item,MedTreeCross)]
            self.firstFlag = False
            
        else:
            #Real redo
            self.parentView.scene().clear()
            #Model Load
            self.parentView.primitive = treeEditorPmtModel(None, None,self.parentView, self.newDom)
            treeHeight, mainGroup = self.parentView._loadTree(self.parentView.primitive,0,0,0)
            self.parentView.scene().addItem(mainGroup)
            newCrosses = [items for items in self.parentView.scene().items() if isinstance(items,MedTreeCross)]
            for crosses in newCrosses :
                crosses.fakePress(self.newCrossState[newCrosses.index(crosses)])
            self.parentView.currentItem = None
            self.parentView.generalUpdate()
          
    def undo(self):
        '''
        Undo add child operation
        '''
        self.parentView.scene().clear()
        #Model Load
        self.parentView.primitive = treeEditorPmtModel(None, None,self.parentView, self.currentDom)
        treeHeight, mainGroup = self.parentView._loadTree(self.parentView.primitive,0,0,0)
        self.parentView.scene().addItem(mainGroup)
        newCrosses = [items for items in self.parentView.scene().items() if isinstance(items,MedTreeCross)]
        for crosses in newCrosses :
            crosses.fakePress(self.oldCrossState[newCrosses.index(crosses)])
        self.parentView.currentItem = None
        self.parentView.generalUpdate()
        
class CommandAddSB(QtGui.QUndoCommand):
    '''
    Class embedding the addSiblingBefore function, hence allowing the undo/redo functionalities
    '''
    def __init__(self, parentView,description="Paste"):
        QtGui.QUndoCommand.__init__(self,description)
        self.parentView = parentView
        #Redo flag
        self.firstFlag = True
        #Undo info
        self.currentDom = self.parentView.primitive._writeDom(self.parentView.dom.ownerDocument())
        self.oldCrossState = [item.activated for item in self.parentView.scene().items() if isinstance(item,MedTreeCross)]
        
    def redo(self):
        '''
        @summary Adds a child before the currently selected graphical representation of a primitive, hence adding it into the model
        '''
        if self.firstFlag:
            parentPmt = self.parentView.currentItem.getPrimitive().getParentPrimitive()
            pmtPos = self.parentView.currentItem.getPrimitive().getParentPrimitive().guiGetChildPos(self.parentView.currentItem.getPrimitive())
            parentPmt.guiAddChild("Control_Nothing", pmtPos,"shift")
            #Create graphical primitive 
            treeHeight, newGraphicalPmt = self.parentView._loadTree(parentPmt.guiGetChild(pmtPos),self.parentView.currentItem.getRow(),self.parentView.currentItem.getColumn(),self.parentView.currentItem.parentItem().getRow())
            #Translate items located below currentItem's subTree
            yPos = self.parentView.currentItem.scenePos().y()+glob_Height
            if self.parentView.currentItem.cross:
                if self.parentView.currentItem.cross.activated:
                    yPos += self.parentView.currentItem.cross._calculateAmountOfSpace()
            
            for item in self.parentView.scene().items(QtCore.QRectF(0,yPos,self.parentView.scene().sceneRect().width(),self.parentView.scene().sceneRect().height()-yPos)):
                if item.parentItem().scenePos().y() < yPos and isinstance(item,MedTreeItem):
                        item.moveBy(0,glob_ColDist)
            
            if self.parentView.currentItem.parentItem().graphicalPmtList.index(self.parentView.currentItem) == 0:
                #Current Item was first child, take car of its line
                self.parentView.currentItem.parentLine.setLine(-(glob_RowDist-(glob_Width))/2,glob_Height/2,0,glob_Height/2)
            self.parentView.currentItem.moveBy(0,glob_ColDist)
            #Add to scene
            newGraphicalPmt.setParentItem(self.parentView.currentItem.parentItem(),False)
            newGraphicalPmt.parentItem().graphicalPmtList.insert(pmtPos,newGraphicalPmt)
            #Adjust z value of siblings
            newGraphicalPmt.setZValue(self.parentView.currentItem.zValue()+1)
            for item in self.parentView.currentItem.parentItem().graphicalPmtList[0:pmtPos]:
                item.setZValue(item.zValue()+1)
            #Look for add/remove of branch tags
            newGraphicalPmt.manageBranchTag()
            self.parentView.currentItem.manageBranchTag()
            self.parentView.currentItem.parentItem().lookForLineModif()
            if len(self.parentView.currentItem.parentItem().graphicalPmtList)==2:
                #A second child was added to the current item, create vertical line
                self.parentView.currentItem.parentItem().childrenLine = QtGui.QGraphicsLineItem(175,glob_Height/2,175,self.parentView.currentItem.parentItem().graphicalPmtList[-1].pos().y()+glob_Height/2,self.parentView.currentItem.parentItem())
                self.parentView.currentItem.parentItem().childrenLine.setPen(QtGui.QPen(QtCore.Qt.DashLine))
            
            #Notify view that scene Rect changed(QGraphicsView doesn't adjust scroll bars when items that are not visible in viewport are translated outside of the last set sceneRect)
            self.parentView.updateSceneRect(self.parentView.sceneRect())
            #Collect info for eventual redos
            self.newDom = self.parentView.primitive._writeDom(self.parentView.dom.ownerDocument())
            self.newCrossState = [item.activated for item in self.parentView.scene().items() if isinstance(item,MedTreeCross)]
            self.firstFlag = False
        else:
            #Real redo
            self.parentView.scene().clear()
            #Model Load
            self.parentView.primitive = treeEditorPmtModel(None, None,self.parentView, self.newDom)
            treeHeight, mainGroup = self.parentView._loadTree(self.parentView.primitive,0,0,0)
            self.parentView.scene().addItem(mainGroup)
            newCrosses = [items for items in self.parentView.scene().items() if isinstance(items,MedTreeCross)]
            for crosses in newCrosses :
                crosses.fakePress(self.newCrossState[newCrosses.index(crosses)])
            self.parentView.currentItem = None
            self.parentView.generalUpdate()
        
    def undo(self):
        '''
        Undo add child operation
        '''
        self.parentView.scene().clear()
        #Model Load
        self.parentView.primitive = treeEditorPmtModel(None, None,self.parentView, self.currentDom)
        treeHeight, mainGroup = self.parentView._loadTree(self.parentView.primitive,0,0,0)
        self.parentView.scene().addItem(mainGroup)
        newCrosses = [items for items in self.parentView.scene().items() if isinstance(items,MedTreeCross)]
        for crosses in newCrosses :
            crosses.fakePress(self.oldCrossState[newCrosses.index(crosses)])
        self.parentView.currentItem = None
        self.parentView.generalUpdate()
        
class CommandCut(QtGui.QUndoCommand):
    '''
    Class embedding the cut function, hence allowing the undo/redo functionalities
    '''
    def __init__(self, parentView,description="Cut"):
        QtGui.QUndoCommand.__init__(self,description)
        self.parentView = parentView
        #Redo flag
        self.firstFlag = True
        #Undo info
        self.currentDom = self.parentView.primitive._writeDom(self.parentView.dom.ownerDocument())
        self.oldCrossState = [item.activated for item in self.parentView.scene().items() if isinstance(item,MedTreeCross)]
        
    def redo(self):
        '''
        Remove item and paste it to clipboard
        '''
        if self.firstFlag:
            #Test if it is root Node
            if not self.parentView.currentItem.getPrimitive().isRootPmt:
                if self.parentView.currentItem.getPrimitive().getParentPrimitive().guiCanDeleteChild():
                    #Delete child
                    self.parentView.mainWindow.clipboard = self.parentView.currentItem.getPrimitive()._writeDom(self.parentView.dom.ownerDocument())
                    self.parentView.currentItem.getPrimitive().getParentPrimitive().guiDeleteChild(self.parentView.currentItem.getPrimitive())
                    self.parentView.currentItem.collapseSubTree(True)
                    
                    yPos = self.parentView.currentItem.scenePos().y()+glob_Height
                    
                    if len(self.parentView.currentItem.parentItem().graphicalPmtList) > 1 and self.parentView.currentItem.parentItem().graphicalPmtList[0] == self.parentView.currentItem:
                        #Adjust parent line if child located at position 1 becomes first child
                        self.parentView.currentItem.parentItem().graphicalPmtList[1].parentLine.setLine(-(glob_RowDist-(glob_Width)),glob_Height/2,0,glob_Height/2)
                        if self.parentView.currentItem.parentItem().graphicalPmtList[1].branchTagEditor:
                            self.parentView.scene().removeItem(self.parentView.currentItem.parentItem().graphicalPmtList[1].branchTagEditor)
                            self.parentView.currentItem.parentItem().graphicalPmtList[1].branchTagEditor = None
                                
                    self.parentView.currentItem.parentItem().graphicalPmtList.remove(self.parentView.currentItem)
                    #Keep reference on parent
                    parentItem = self.parentView.currentItem.parentItem()
                    #Remove Item
                    self.parentView.scene().removeItem(self.parentView.currentItem)
                    
                    #Translate items located below, if necessary
                    translationList = []
                    if parentItem.graphicalPmtList:
                        for item in self.parentView.scene().items(QtCore.QRectF(0,yPos,self.parentView.scene().sceneRect().width(),self.parentView.scene().sceneRect().height()-yPos)):
                            if item.parentItem().scenePos().y() < yPos and isinstance(item,MedTreeItem):
                                translationList.append(item)
                        #Here's The reason we stock items in a list before moving them:
                        #Presume and item is located at yPos and its parent at yPos-something
                        #This item is moved -glob_ColDist
                        #Presume this item has a child
                        #Its parent is now located at yPos-glob_ColDist, so this item his moved too, hence ending in an extra translation
                        for item in translationList:
                            item.moveBy(0,-glob_ColDist)
                        #One child left, delete parentLine
                        if len(parentItem.graphicalPmtList) == 1:
                            self.parentView.scene().removeItem(parentItem.childrenLine)
                        else:
                            #In case the deleted child is the last child, look for needed modifications in children line
                            parentItem.lookForLineModif()
                    else:
                        #No more children, delete cross
                        self.parentView.scene().removeItem(parentItem.cross)
                        parentItem.cross = None
                    
                else:
                    #Replace model Item by Nothing
                    self.parentView.mainWindow.clipboard = self.parentView.currentItem.getPrimitive()._writeDom(self.parentView.dom.ownerDocument())
                    pmtPos = self.parentView.currentItem.parentItem().getPrimitive().guiGetChildPos(self.parentView.currentItem.getPrimitive())
                    self.parentView.currentItem.getPrimitive().getParentPrimitive().guiSetModelData("Control_Nothing",pmtPos)
                    self.parentView.currentItem.collapseSubTree(True)
                    #Add New Nothing node
                    treeHeight, newSubTree = self.parentView._loadTree(self.parentView.currentItem.parentItem().getPrimitive().guiGetChild(pmtPos), self.parentView.currentItem.getRow(), self.parentView.currentItem.getColumn(), self.parentView.currentItem.parentItem().getRow())
                    newSubTree.setParentItem(self.parentView.currentItem.parentItem(),False)
                    newSubTree.manageBranchTag()
                    #Adjust Z values
                    self.parentView.currentItem.parentItem().graphicalPmtList[self.parentView.currentItem.parentItem().graphicalPmtList.index(self.parentView.currentItem)] = newSubTree
                    newSubTree.setZValue(self.parentView.currentItem.zValue())
                    #Remove old Item
                    self.parentView.scene().removeItem(self.parentView.currentItem)
                    
            else:
                #root Primitive, clear whole tree
                self.parentView.mainWindow.clipboard = self.parentView.currentItem.getPrimitive()._writeDom(self.parentView.dom.ownerDocument())
                self.parentView.primitive = treeEditorPmtModel(None, None,self.parentView, self.parentView.dom.ownerDocument().createElement("Control_Nothing"))
                self.parentView.scene().clear()
                treeHeight, mainGroup = self.parentView._loadTree(self.parentView.primitive,0,0,0)
                self.parentView.scene().addItem(mainGroup)
    
            self.parentView.currentItem = None
            self.parentView.generalUpdate()
            #Collect info for eventual redos
            self.newDom = self.parentView.primitive._writeDom(self.parentView.dom.ownerDocument())
            self.newCrossState = [item.activated for item in self.parentView.scene().items() if isinstance(item,MedTreeCross)]
            self.firstFlag = False
        
        else:
            #Real redo
            self.parentView.scene().clear()
            #Model Load
            self.parentView.primitive = treeEditorPmtModel(None, None,self.parentView, self.newDom)
            treeHeight, mainGroup = self.parentView._loadTree(self.parentView.primitive,0,0,0)
            self.parentView.scene().addItem(mainGroup)
            newCrosses = [items for items in self.parentView.scene().items() if isinstance(items,MedTreeCross)]
            for crosses in newCrosses :
                crosses.fakePress(self.newCrossState[newCrosses.index(crosses)])
            self.parentView.currentItem = None
            self.parentView.generalUpdate()
            
    def undo(self):
        '''
        Undo cut operation
        '''
        self.parentView.scene().clear()
        #Model Load
        self.parentView.primitive = treeEditorPmtModel(None, None,self.parentView, self.currentDom)
        treeHeight, mainGroup = self.parentView._loadTree(self.parentView.primitive,0,0,0)
        self.parentView.scene().addItem(mainGroup)
        newCrosses = [items for items in self.parentView.scene().items() if isinstance(items,MedTreeCross)]
        for crosses in newCrosses :
            crosses.fakePress(self.oldCrossState[newCrosses.index(crosses)])
        self.parentView.currentItem = None
        self.parentView.generalUpdate()

class CommandDropChild(QtGui.QUndoCommand):
    '''
    Class embedding the dropChild function, hence allowing the undo/redo functionalities
    If first ever call to redo, use current tree information to make modifications
    Else, just reload the tree using a dom as done in the undo function
    '''
    def __init__(self, parentView,itemModified,newPrimitiveName, description="Replace child"):
        QtGui.QUndoCommand.__init__(self,description)
        self.parentView = parentView
        #First redo info
        self.itemModified = itemModified
        self.newPmtName = newPrimitiveName
        #Redo flag
        self.firstFlag = True
        #Undo info
        self.currentDom = self.parentView.primitive._writeDom(self.parentView.dom.ownerDocument())
        self.oldCrossState = [item.activated for item in self.parentView.scene().items() if isinstance(item,MedTreeCross)]
        
    def redo(self):
        '''
        @summary Replace child primitive by the one being dropped on it
        '''
        if self.firstFlag:
            #Redo automatically called at class creation
            #Test if it is root Node
            if not self.itemModified.pmt.isRootPmt:
                #Replace model Item by child
                pmtPos = self.itemModified.parentItem().getPrimitive().guiGetChildPos(self.itemModified.getPrimitive())
                self.itemModified.getPrimitive().getParentPrimitive().guiSetModelData(self.newPmtName,pmtPos)
                #Update Tree
                newItem = self.parentView._updateTree(self.itemModified,self.itemModified.getPrimitive().getParentPrimitive().guiGetChild(pmtPos))
                self.parentView.currentItem = newItem
            else:
                #Item replaced is root primitive
                self.parentView.primitive = treeEditorPmtModel(None, None,self.parentView, self.parentView.dom.ownerDocument().createElement(self.newPmtName))
                self.parentView.scene().clear()
                treeHeight, mainGroup = self.parentView._loadTree(self.parentView.primitive,0,0,0)
                self.parentView.scene().addItem(mainGroup)
                self.parentView.currentItem = mainGroup
                
            self.parentView.generalUpdate()
            
            #Notify view that scene Rect changed(QGraphicsView doesn't adjust scroll bars when items that are not visible in viewport are translated outside of the last set sceneRect)
            self.parentView.updateSceneRect(self.parentView.sceneRect())
            #Collect info for eventual redos
            self.newDom = self.parentView.primitive._writeDom(self.parentView.dom.ownerDocument())
            self.newCrossState = [item.activated for item in self.parentView.scene().items() if isinstance(item,MedTreeCross)]
            self.firstFlag = False
        else:
            #Real redo
            self.parentView.scene().clear()
            #Model Load
            self.parentView.primitive = treeEditorPmtModel(None, None,self.parentView, self.newDom)
            treeHeight, mainGroup = self.parentView._loadTree(self.parentView.primitive,0,0,0)
            self.parentView.scene().addItem(mainGroup)
            newCrosses = [items for items in self.parentView.scene().items() if isinstance(items,MedTreeCross)]
            for crosses in newCrosses :
                crosses.fakePress(self.newCrossState[newCrosses.index(crosses)])
            self.parentView.currentItem = None
            self.parentView.generalUpdate()
        
    def undo(self):
        '''
        Undo replace child operation
        '''
        self.parentView.scene().clear()
        #Model Load
        self.parentView.primitive = treeEditorPmtModel(None, None,self.parentView, self.currentDom)
        treeHeight, mainGroup = self.parentView._loadTree(self.parentView.primitive,0,0,0)
        self.parentView.scene().addItem(mainGroup)
        newCrosses = [items for items in self.parentView.scene().items() if isinstance(items,MedTreeCross)]
        for crosses in newCrosses :
            crosses.fakePress(self.oldCrossState[newCrosses.index(crosses)])
        self.parentView.currentItem = None
        self.parentView.generalUpdate()
        
class CommandPaste(QtGui.QUndoCommand):
    '''
    Class embedding the paste function, hence allowing the undo/redo functionalities
    '''
    def __init__(self, parentView,description="Paste"):
        QtGui.QUndoCommand.__init__(self,description)
        self.parentView = parentView
        #Redo flag
        self.firstFlag = True
        #Undo info
        self.currentDom = self.parentView.primitive._writeDom(self.parentView.dom.ownerDocument())
        self.oldCrossState = [item.activated for item in self.parentView.scene().items() if isinstance(item,MedTreeCross)]
        
    def redo(self):
        '''
        @summary Paste function
        Looks if a MedTreeItem is currently selected and pastes MainEditorWindow's clipboard content, if there is one, onto currently selected MedTreeItem
        '''
        if self.firstFlag:
            if not self.parentView.currentItem.getPrimitive().isRootPmt:
                pmtPos = self.parentView.currentItem.parentItem().getPrimitive().guiGetChildPos(self.parentView.currentItem.getPrimitive())
                self.parentView.currentItem.getPrimitive().getParentPrimitive().guiReplaceModelData(pmtPos,self.parentView.mainWindow.clipboard)
                #Update Tree
                self.parentView.currentItem = self.parentView._updateTree(self.parentView.currentItem,self.parentView.currentItem.getPrimitive().getParentPrimitive().guiGetChild(pmtPos))
            else:
                self.parentView.primitive = treeEditorPmtModel(None, None,self.parentView, self.parentView.mainWindow.clipboard)
                self.parentView.scene().clear()
                treeHeight, mainGroup = self.parentView._loadTree(self.parentView.primitive,0,0,0)
                self.parentView.scene().addItem(mainGroup)
                self.parentView.currentItem = mainGroup
        
            self.parentView.generalUpdate()
            
            #Notify view that scene Rect changed(QGraphicsView doesn't adjust scroll bars when items that are not visible in viewport are translated outside of the last set sceneRect)
            self.parentView.updateSceneRect(self.parentView.sceneRect())
            #Collect info for eventual redos
            self.newDom = self.parentView.primitive._writeDom(self.parentView.dom.ownerDocument())
            self.newCrossState = [item.activated for item in self.parentView.scene().items() if isinstance(item,MedTreeCross)]
            self.firstFlag = False
        else:
            #Real redo
            self.parentView.scene().clear()
            #Model Load
            self.parentView.primitive = treeEditorPmtModel(None, None,self.parentView, self.newDom)
            treeHeight, mainGroup = self.parentView._loadTree(self.parentView.primitive,0,0,0)
            self.parentView.scene().addItem(mainGroup)
            newCrosses = [items for items in self.parentView.scene().items() if isinstance(items,MedTreeCross)]
            for crosses in newCrosses :
                crosses.fakePress(self.newCrossState[newCrosses.index(crosses)])
            self.parentView.currentItem = None
            self.parentView.generalUpdate()
            
    def undo(self):
        '''
        Undo paste operation
        '''
        self.parentView.scene().clear()
        #Model Load
        self.parentView.primitive = treeEditorPmtModel(None, None,self.parentView, self.currentDom)
        treeHeight, mainGroup = self.parentView._loadTree(self.parentView.primitive,0,0,0)
        self.parentView.scene().addItem(mainGroup)
        newCrosses = [items for items in self.parentView.scene().items() if isinstance(items,MedTreeCross)]
        for crosses in newCrosses :
            crosses.fakePress(self.oldCrossState[newCrosses.index(crosses)])
        self.parentView.currentItem = None
        self.parentView.generalUpdate()
        
class MedTreeItem(QtGui.QGraphicsWidget):
    '''
    This class is a graphical representation of a xml node in a QGraphicsView
    Most of it is reimplemented from QGraphicsWidget
    '''
    def __init__(self,position,dimension,parent = None):
        '''
        @summary Constructor
        @param position : position relative to parent's graphical object
        @param dimension : size of the object
        @param parent : QGraphicsView in which this object is going to be shown
        '''
        QtGui.QGraphicsWidget.__init__(self)
        #Initialize Variables
        self.dim = dimension
        self.parentView = parent
        self.pmt = None
        self.setPos(position)
        self.branchTagEditor = None
        self.graphicalPmtList = []
        self.cross = None
        self.childrenLine = None
        self.info = None
        #Initialize flags
        self.setAcceptDrops(True)
        self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable|QtGui.QGraphicsItem.ItemStacksBehindParent)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def setParentItem(self,parentItem,appendToEndOfList=True):
        '''
        @summary Reimplementation of QGraphicsWidget.setParentItem(self,parentItem)
        Parent primitive keeps a list of its  MedTreeItem children
        @param parentItem : parent MedTreeItem
        @param appendToEndOfList : if set to False, user will have to correctly manage the graphicalPmtList
        '''
        if appendToEndOfList:
            parentItem.graphicalPmtList.append(self)
        QtGui.QGraphicsWidget.setParentItem(self,parentItem)
        self.connect(self,QtCore.SIGNAL("yChanged()"),parentItem.lookForLineModif)
        
    def boundingRect(self):
        '''
        @summary Reimplementation of QGraphicsWidget.boundingRect(self) virtual function
        Required to correctly paint the graphic item
        The boundingRect coordinates must be in item's coordinate, hence the (0,0) position 
        '''
        return QtCore.QRectF(0,0,self.dim.x(),self.dim.y())

    def paintHook(self):
        '''
        @summary If an error is found in the model this function is called
        Hence, the item is repainted and changes colour, keeping the tree view and the model synced 
        '''
        self.update(self.boundingRect())
        
    def paint(self, painter, option, widget = None):
        '''
        @summary Overloaded function(QGraphicsWidget) : painting is done in item coordinate
        @params : see QGraphicsWidget's doc for details
        ''' 
        
        painter.setRenderHints(QtGui.QPainter.Antialiasing)
        if self.getPrimitive().guiIsHighlighted():
            painter.setBrush(QtGui.QColor(255,204,255))
        else:
            painter.setBrush(QtCore.Qt.white)
        
        #if pressed, paint thick blue border line
        if self == self.parentView.currentItem:
            painter.setPen(QtGui.QPen(QtGui.QBrush(QtCore.Qt.blue),4))
            painter.drawRoundedRect(self.boundingRect(),4,4)
            painter.setPen(QtGui.QPen(QtGui.QBrush(QtCore.Qt.black),2))
            fontMetrics = QtGui.QFontMetrics(painter.font())
            if fontMetrics.width(self.getPrimitive().guiGetName()) > 140:
                    modifiedFont = painter.font()
                    modifiedFont.setPointSizeF(modifiedFont.pointSizeF()*140/fontMetrics.width(self.getPrimitive().guiGetName()))
                    painter.setFont(modifiedFont)
            painter.drawText(self.boundingRect(), QtCore.Qt.AlignCenter, self.getPrimitive().guiGetName())
        
        else:
            
            #Paint in color if errors, else in black
            colorDict = {"Unknown" : QtCore.Qt.black,
                     "Valid" : QtCore.Qt.black,
                     "Warning" : QtGui.QColor(255,215,0),
                     "Error":QtCore.Qt.red}
            
            painter.setPen(QtGui.QPen(QtGui.QBrush(colorDict[self.getPrimitive().getValidityState()]),2))
            painter.drawRoundedRect(self.boundingRect(),10,10)
            display = self.getPrimitive().guiGetAttrDisplay()
            
            if display:
                painter.setPen(QtGui.QPen(QtGui.QBrush(QtCore.Qt.black),2))
                fontMetrics = QtGui.QFontMetrics(painter.font())
                if fontMetrics.width(self.getPrimitive().guiGetName()) > 140:
                    modifiedFont = painter.font()
                    modifiedFont.setPointSizeF(modifiedFont.pointSizeF()*140/fontMetrics.width(self.getPrimitive().guiGetName()))
                    painter.setFont(modifiedFont)
                painter.drawText(self.boundingRect(), QtCore.Qt.AlignCenter, self.getPrimitive().guiGetName())
                painter.setPen(QtGui.QPen(QtGui.QBrush(QtCore.Qt.gray),1))
                painter.setFont(QtGui.QFont("DejaVu [Serif]",8))
                fontMetrics = QtGui.QFontMetrics(QtGui.QFont("DejaVu [Serif]",8))
                textWidth = fontMetrics.width(display[0]) if fontMetrics.width(display[0]) < 140 else 140
                
                alignmentFlags = {"br":QtCore.Qt.AlignRight|QtCore.Qt.AlignBottom,
                                      "bl":QtCore.Qt.AlignBottom,
                                      "tr":QtCore.Qt.AlignRight|QtCore.Qt.AlignTop,
                                      "tl":QtCore.Qt.AlignTop}
                
                
                if textWidth == 140:
                    dotAlignment = QtCore.Qt.AlignRight|QtCore.Qt.AlignBottom
                    if display[1][0] == "t":
                        dotAlignment = QtCore.Qt.AlignRight|QtCore.Qt.AlignTop
                    if display[1][1] == "l":
                        painter.drawText(QtCore.QRectF(135,0,10,self.boundingRect().height()),dotAlignment,"...")
                        painter.drawText(QtCore.QRectF(5,0,textWidth-10,self.boundingRect().height()),alignmentFlags[display[1]],display[0])
                    else:
                        painter.drawText(QtCore.QRectF(5,0,10,self.boundingRect().height()),dotAlignment,"...")
                        painter.drawText(QtCore.QRectF(15,0,textWidth-10,self.boundingRect().height()),alignmentFlags[display[1]],display[0])
                else:
                    rect = self.boundingRect()
                    rect.setWidth(140)
                    rect.setX(5)
                    painter.drawText(rect,alignmentFlags[display[1]],display[0])
            else:
                
                painter.setPen(QtGui.QPen(QtGui.QBrush(QtCore.Qt.black),2))
                fontMetrics = QtGui.QFontMetrics(painter.font())
                if fontMetrics.width(self.getPrimitive().guiGetName()) > 140:
                    modifiedFont = painter.font()
                    modifiedFont.setPointSizeF(modifiedFont.pointSizeF()*140/fontMetrics.width(self.getPrimitive().guiGetName()))
                    painter.setFont(modifiedFont)
                painter.drawText(self.boundingRect(), QtCore.Qt.AlignCenter, self.getPrimitive().guiGetName())

    def manageBranchTag(self):
        '''
        @summary Adds a branch tag to subtree or update one if already present
        '''
        if self.branchTagEditor:
            self.branchTagEditor.updateBranchTag()
        else:
            if self.getPrimitive().getParentPrimitive().guiCanHaveBranchTag(self.getPrimitive()) and not self.getRow() == 0:  
                self.branchTagEditor = MedTreeEditableBranchTag(self)
                self.branchTagEditor.updateBranchTag()
                
    def manageAsterisk(self):
        '''
        @summary Manage asterisk that indicates whether or not primitive has a user comment
        '''
        if self.sender().document().toPlainText():
            if not hasattr(self,"asterisk"):
                newAsteriskItem = QtGui.QGraphicsTextItem("*",self)
                newAsteriskItem.setPos(QtCore.QPointF(135,-22))
                newAsteriskItem.setDefaultTextColor(QtCore.Qt.white)
                newAsteriskItem.setFont(QtGui.QFont("DejaVu [Serif]",18))
                self.asterisk = newAsteriskItem
        else:
            if hasattr(self,"asterisk"):
                self.scene().removeItem(self.asterisk)
                delattr(self,"asterisk")
                
    def dumpModelInfos(self):
        '''
        @summary debug function
        Print self.primitive information in the console
        '''
        self.getPrimitive().guiDumpModelInfos()
        
    def getPrimitive(self):
        '''
        @summary Return basePmtModel's primitive instance associated with this graphical object
        '''
        return self.pmt
    
    def setPrimitive(self,primitive):
        '''
        @summary Set basePmtModel's primitive instance associated with this graphical object
        @param primitive : basePmtModel's primitive instance
        '''
        self.pmt = primitive
        self.connect(primitive,QtCore.SIGNAL("updateBranchTag()"), self.manageBranchTag)
        
    def shape(self):
        '''
        @summary Reimplementation of QGraphicsView.boundingRect(self) virtual function
        Allows the correct propagation of mouse event
        '''
        path=QtGui.QPainterPath()
        path.addRect(self.boundingRect())
        return path
     
    def getRow(self):
        '''
        @summary This function returns self's relative row
        '''
        return (self.pos().y())/glob_ColDist
    
    def getColumn(self):
        '''
        @summary This function returns self's relative column
        '''
        return (self.pos().x())/glob_RowDist
    
    def collapseSubTree(self,updateLayout=False):
        '''
        @summary This functions prepares the folding of a branch
        First, it looks for the MedTreeCross associated with the branch
        Once found, it sets its activation state to False
        Afterward, It calls it's _expOrCollapse function that will allow the propagation of the activation status
        Finally, if needed, it will call a layoutUpdate on the MedTreeCross
        @param updateLayout : For some particular reason, we want to perform this action without updating the general layout of the Tree
        For example, when we add a new SubTree to a Primitive, we will first collapse the subTree. Since this new subTree isn't yet
        part of the Tree, we don't want the general Layout to be updated, hence the utility of the updateLayout boolean. 
        '''
        for item in self.childItems():
            if isinstance(item,MedTreeCross):
                item.activated = False
                item._expOrCollapse(False)
                if updateLayout:
                    item._layout_update(-1)
                return item._calculateAmountOfSpace()
            
    def expandSubTree(self,updateLayout=False):
        '''
        @summary This functions prepares the expand of a branch
        First, it looks for the MedTreeCross associated with the branch
        Once found, it sets its activation state to True
        Afterward, it will call a layoutUpdate on the MedTreeCross
        Finally, It calls it's _expOrCollapse function that will allow the propagation of the activation status
        Note: _expOrCOllapse, if compared to the collapseSubTree function, is called after the update : since the layoutUpdate function
        calls the _calculateAmoutOfSpace function which itself relies on the visible status to calculate the amount of space used or released by a
        collapse/expand action, we first have to calculate the amount of space that will be used by the "invisible subTree" before setting the branch and all of its subTree visible
        '''
        for item in self.childItems():
            if isinstance(item,MedTreeCross):
                item.activated = True
                if updateLayout:
                    item._layout_update(1)
                item._expOrCollapse(True)

                return
        
    def lookForLineModif(self):
        '''
        @summary Function allowing a MedTreeItem with multiple line objects to update its vertical line
        '''
        if self.childrenLine:
            self.childrenLine.setLine(175,glob_Height/2,175,self.graphicalPmtList[-1].pos().y()+glob_Height/2)
        
    def moveBy(self,dx,dy):
        '''
        @summary : Reimplementation of QGraphicsWidget.moveBy(self, dx, dy) virtual function
        Function calls parent's class moveBy implementation
        '''
        super(MedTreeItem, self).moveBy(dx,dy)
    
    def reInitialize(self,primitive):
        '''
        @summary Method called by the undo function
        Allows a tree with invalid primitive pointer to correctly re-initialize
        @param primitive, new primitive
        '''
        self.pmt = primitive
        for child in self.graphicalPmtList:
            child.reInitialize(self.pmt.guiGetChild(self.graphicalPmtList.index(child)))
            
    def _cloneNode(self,parentView):
        '''
        @summary : Manually clone node, since Qt doesn't support such operation
        Recursively call function on child nodes 
        '''
        clone = MedTreeItem(self.pos(),QtCore.QPointF(glob_Width,glob_Height),parentView)
        clone.setVisible(self.isVisible())
        for graphicalChild in self.graphicalPmtList:
            cloneChild = graphicalChild._cloneNode(parentView)
            cloneChild.setParentItem(clone)
        
        clone.setZValue(self.zValue())
        if hasattr(self,"parentLine"):
            #Tests if parentLine attribute exists since root object doesn't have any
            clone.parentLine = QtGui.QGraphicsLineItem(self.parentLine.line(),clone)
            clone.parentLine.setPen(QtGui.QPen(QtCore.Qt.DashLine))
       # if hasattr(self,"choiceList"):
            #Tests if choiceList attribute exists since root object doesn't have any
          #  clone.choiceList = MedTreeArrow(QtCore.QPointF(125,38),clone) 
        if self.cross:
            #Self has cross
            clone.cross = MedTreeCross(QtCore.QPointF(glob_RowDist-31,3),QtCore.QPointF(12,12),parentView)
            clone.cross.activated = self.cross.activated
            clone.cross.setParentItem(clone)
            #Since self has cross, self might have children line
            if self.childrenLine:
                clone.childrenLine = QtGui.QGraphicsLineItem(self.childrenLine.line(),clone)
                clone.childrenLine.setVisible(self.childrenLine.isVisible())
                clone.childrenLine.setPen(QtGui.QPen(QtCore.Qt.DashLine))
        if self.branchTagEditor:
            #self has Edtior
            clone.branchTagEditor = MedTreeEditableBranchTag(clone,self.branchTagEditor.toPlainText())
        if self.info:
            #Self has branch info
            clone.info = QtGui.QGraphicsTextItem(self.info.toPlainText(),clone)
            clone.info.setFont(QtGui.QFont("Helvetica",9))          
            clone.info.setTextWidth(150)
            clone.info.setPos(QtCore.QPointF(0,-clone.info.boundingRect().height()))
            clone.info.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        if hasattr(self,"asterisk"):
            newAsteriskItem = QtGui.QGraphicsTextItem("*",clone)
            newAsteriskItem.setPos(QtCore.QPointF(135,-22))
            newAsteriskItem.setDefaultTextColor(QtCore.Qt.white)
            newAsteriskItem.setFont(QtGui.QFont("DejaVu [Serif]",18))
            clone.asterisk = newAsteriskItem
        
        return clone
    
class MedTreeCross(QtGui.QGraphicsWidget):
    '''
    This class is a graphical representation of a cross/minus sign
    Most of it is reimplemented from QGraphicsWidget
    It is used as a graphical way for the user to fold/unfold parts of the tree
    '''
    def __init__(self,position,dimension, parent = None):
        '''
        @summary Constructor
        @param position : position relative to parent's graphical object
        @param dimension : size of the object
        @param parent : QGraphicsView in which this object is going to be shown
        '''
        QtGui.QGraphicsWidget.__init__(self)
        self.dim = dimension
        self.parentView = parent
        self.activated = True
        self.setPos(position)
        
    def paint(self, painter, option, widget = None):
        '''
        @summary Overloaded function(QGraphicsWidget) : painting is done in item coordinate
        @params : see QGraphicsWidget's doc for details
        ''' 
        
        painter.setBrush(QtGui.QBrush(QtCore.Qt.white))
        if self.activated:
            #Paint a "-"s operator
            painter.setPen(QtGui.QPen(QtGui.QBrush(QtCore.Qt.black),2))
            painter.drawLine(self.boundingRect().x()+1, self.boundingRect().y()+self.boundingRect().height()/2,self.boundingRect().x()+self.boundingRect().width()-1,self.boundingRect().y()+self.boundingRect().height()/2)
           
        else:
            colorDict = {"Unknown" : QtCore.Qt.black,
                     "Valid" : QtCore.Qt.green,
                     "Warning" : QtCore.Qt.yellow,
                     "Error":QtCore.Qt.red}
            #Paint a "+" operator
            #Draw Cross the color of the subtree
            eventColor = self.parentItem().getPrimitive()._findWorstEvent()
            painter.setPen(QtGui.QPen(QtGui.QBrush(colorDict[eventColor]),2))
            painter.drawLine(self.boundingRect().x()+1, self.boundingRect().y()+self.boundingRect().height()/2,self.boundingRect().x()+self.boundingRect().width()-1,self.boundingRect().y()+self.boundingRect().height()/2)
            painter.drawLine(self.boundingRect().x()+self.boundingRect().width()/2, self.boundingRect().y()+1,self.boundingRect().x()+self.boundingRect().width()/2,self.boundingRect().y()+self.boundingRect().height()-1)
          
    def boundingRect(self):
        '''
        @summary Reimplementation of QGraphicsView.boundingRect(self) virtual function
        Required to correctly paint the graphic item
        The boundingRect coordinates must be in item's coordinate, hence the (0,0) position 
        '''
        return QtCore.QRectF(0,0,self.dim.x(),self.dim.y())
    
    def shape(self):
        '''
        @summary Reimplementation of QGraphicsView.boundingRect(self) virtual function
        Allows the correct propagation of mouse event
        '''
        path=QtGui.QPainterPath()
        path.addRect(self.boundingRect())
        return path
    
    def mousePressEvent(self,event):
        '''
        @summary Function changes activation status and forwards it to its parent children
        It also allows the appropriate geometry change(updating the position) of the Tree
        @param event: see QGraphicsWidget's documentation for more information
        '''
        if event.button() == QtCore.Qt.LeftButton:
            if self.activated:
                self.activated = False
                self._expOrCollapse(self.activated)
                self.update()
                self._layout_update(-1)
            else:
                self.activated = True
                self.update()
                self._layout_update(1)
                self._expOrCollapse(self.activated)
                
        QtGui.QGraphicsWidget.mousePressEvent(self,event)
            
    def fakePress(self,state):
        '''
        @summary Function changes activation status, adjust layout if not hidden yet
        Called by the redo/undo system, to adjuste a newly created tree to a previous/posterior state
        '''
        if self.isVisible():
            if not state:
                self.activated = False
                self._expOrCollapse(self.activated)
                self.update()
                self._layout_update(-1)
                
        else:
            self.activated = state
        
    def _expOrCollapse(self,activationStatus):
        '''
        @summary This function loops through all children and change their visible state(if child is a MedTreeItem)
        Qt forwards invisible state to children
        Visible state is also forwarded unless the child has explicitly been set invisible(Qt behavior)
        @param activationStatus is a boolean to modify visible state
        '''
        for item in self.parentItem().graphicalPmtList:
            #If item in graphicsGroup is a MedTreeItem
            item.setVisible(activationStatus)
            if self.parentItem().childrenLine:
                self.parentItem().childrenLine.setVisible(activationStatus)
                
    def _layout_update(self,negFactor):
        '''
        @summary This function loops through all items located under the cross after a collapse or expand action
        and finds the items with a parent located higher in the tree
        @param negFactor is the multiplication factor(-1 or 1) to apply
        '''
        for item in self.scene().items(QtCore.QRectF(0,self.scenePos().y()+35,self.scene().sceneRect().width(),self.scene().sceneRect().height()-self.scenePos().y())):
            #if item isn't visible, then it's part of the branch we collapsed or that we are going to expand
            if item.isVisible():
                if isinstance(item,MedTreeItem):
                    #Test if MedTreeItem is a child item of a MedTreeItem higher in the tree(smaller y in scene coordinate)
                    #If so, start propagating the geometry change from this item
                    if item.parentItem().scenePos().y()<self.scenePos().y()+35:
                        item.moveBy(0,negFactor*self._calculateAmountOfSpace())
                
    def _calculateAmountOfSpace(self):
        '''
        @summary  This function calculates the amount of space released or used by an expand or collapse action   
        '''
        lastTreeElement = self.parentItem().graphicalPmtList[-1]
        
        while True:
            #Look if current element has a cross and if it is activated
            if lastTreeElement.cross:
                if lastTreeElement.cross.activated:
                    lastTreeElement = lastTreeElement.graphicalPmtList[-1]
                    continue
            return lastTreeElement.scenePos().y()-self.parentItem().scenePos().y()
              
class MedTreeEditableBranchTag(QtGui.QGraphicsTextItem):
    '''
    This class is a graphical representation of a switch value for primitives Switch, SwitchBins and DynnamicBranch
    When such primitives have switch values, those values are located left to the MedTreeItem, aligned with the horizontal branch line  
    Most of it is reimplemented from QGraphicsTextItem
    '''
    def __init__(self, parent, text=""):
        '''
        @summary Constructor
        @param position : parent is the line located right to the EditableBranchTag
        @param parent : text is the switch value
        '''
        QtGui.QGraphicsTextItem.__init__(self,parent)
        self.setPlainText(text)
        self.calculateTextWidth()
        
    def calculateTextWidth(self):
        '''
        @summary Calculates the width taken by the switch value and adjusts position 
        '''
        fontMetrics = QtGui.QFontMetrics(self.font())
        self.setPos(QtCore.QPointF(-fontMetrics.width(self.toPlainText())-35,0))
        
    def updateBranchTag(self):
        '''
        @summary This slot is called when a primitive switch values have been modified
        '''
        if self.parentItem().getPrimitive().guiGetBranchTag():
            self.setPlainText(self.parentItem().getPrimitive().guiGetBranchTag()[2])
            self.calculateTextWidth()   
    
    def focusOutEvent(self,event):
        '''
        @summary Reimplementation of QGraphicsTextItem.focusOutEvent(self,event) virtual function
        Leave Edit Mode and update
        @param event : see QGraphicsTextItem documentation for more information
        '''
        if self.textInteractionFlags() == QtCore.Qt.TextEditorInteraction:
            #Update primitive and size/position
            self.parentItem().getPrimitive().guiSetBranchTag(self.toPlainText())
            self.calculateTextWidth()
        
        QtGui.QGraphicsTextItem.focusOutEvent(self,event)
    
    def mousePressEvent(self,event):
        '''
        @summary Reimplementation of QGraphicsTextItem.mousePressEvent(self,event) virtual function
        Enter Edit Mode if branch tag doesn't refer to a reference attribute
        @param event : see QGraphicsTextItem documentation for more information
        ''' 
        if self.parentItem().getPrimitive().guiGetBranchTag()[1]:
            self.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        else:
            self.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
            
        QtGui.QGraphicsTextItem.mousePressEvent(self,event)
        
    def paint(self, painter, option, widget = None):
        '''
        @summary Overloaded function(QGraphicsTextItem) : painting is done in item coordinate
        @params : see QGraphicsTextItem's doc for details
        '''
        painter.setPen(QtGui.QPen(QtGui.QBrush(QtCore.Qt.red),4))
        painter.setBrush(QtGui.QBrush(QtGui.QColor(QtCore.Qt.red)))
        
        if not self.document().toPlainText() and not self.hasFocus():
            self.setDefaultTextColor(QtGui.QColor(QtCore.Qt.red))
            painter.drawText(self.boundingRect(),QtCore.Qt.AlignCenter,"!")
        elif self.document().toPlainText() == "!":
            self.setDefaultTextColor(QtGui.QColor(QtCore.Qt.red))
        else:
            self.setDefaultTextColor(QtGui.QColor(QtCore.Qt.black))
        
        QtGui.QGraphicsTextItem.paint(self,painter, option, widget)

    def keyPressEvent(self,event):
        '''
        @summary Overloaded function(QGraphicsTextItem) : readjust size when text is edited
        @param event : see QGraphicsTextItem's doc for details
        ''' 
        QtGui.QGraphicsTextItem.keyPressEvent(self,event)
        self.calculateTextWidth()
        
class MedTreeArrow(QtGui.QGraphicsWidget):
    '''
    This class is a graphical representation of an arrow
    Most of it is reimplemented from QGraphicsWidget
    It is used as a graphical way for the user to unfold a list of primitive that can replace its associated node
    '''
    def __init__(self,position, parent = None):
        '''
        @summary Constructor
        @param position : position relative to parent's graphical object
        @param dimension : size of the object
        @param parent : QGraphicsView in which this object is going to be shown
        '''
        QtGui.QGraphicsWidget.__init__(self)
        self.setParentItem(parent)
        self.setPos(position)
        self.setFlags(QtGui.QGraphicsItem.ItemIsFocusable)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def paint(self, painter, option, widget = None):
        '''
        @summary Overloaded function(QGraphicsWidget) : painting is done in item coordinate
        @params : see QGraphicsWidget's doc for details
        ''' 
        painter.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
        painter.setPen(QtGui.QPen(QtCore.Qt.gray))
        painter.drawConvexPolygon(QtCore.QPointF(0,0),QtCore.QPointF(20,0),QtCore.QPointF(10,10))
            
    def boundingRect(self):
        '''
        @summary Reimplementation of QGraphicsWidget.boundingRect(self) virtual function
        Required to correctly paint the graphic item
        The boundingRect coordinates must be in item's coordinate, hence the (0,0) position 
        '''
        return QtCore.QRectF(0,0,20,10)
    
    def shape(self):
        '''
        @summary Reimplementation of QGraphicsWidget.boundingRect(self) virtual function
        Allows the correct propagation of mouse event
        '''
        path=QtGui.QPainterPath()
        path.addPolygon(QtGui.QPolygonF([QtCore.QPointF(0,0),QtCore.QPointF(20,0),QtCore.QPointF(10,10)]))
        return path
    
    def mousePressEvent(self,event):
        '''
        @summary Reimplementation of QGraphicsWidget.mousePressEvent(self,event)
        Handles a mouseClick on the item
        Reimplementation is needed of we want the release to be later called on this item
        @param event : see Qt's documentation for more details
        '''
        QtGui.QGraphicsWidget.mousePressEvent(self,event)
        event.accept()
        
    def mouseReleaseEvent(self,event):
        '''
        @summary Reimplementation of QGraphicsWidget.mouseReleaseEvent(self,event)
        Handles a mouseRelease on the item
        This will trigger the rendering of a MedtreeChoicesList, hence showing the value(primitives) this node can take
        @param event : see Qt's documentation for more details
        '''
        self.medChoices = QtGui.QGraphicsProxyWidget(self)
        self.medChoices.setGeometry(QtCore.QRectF(-125,0,150,35))
        self.medChoices.setWidget(MedTreeComboBox(self.medChoices))
        self.medChoices.widget().setModel(ChoiceComboBoxModel(self.parentItem().getPrimitive()))
        self.medChoices.widget().showPopup()       
        
class MedTreeComboBox(QtGui.QComboBox):
    '''
    This class is a comboBox embed in a ProxyWidget
    Most of its is reimplemented from QtGui.QGraphicsProxyWidget
    It is used as a graphical way for the user to present a list of primitive that can replace its associated node
    '''
    def __init__(self,parent):
        '''
        @summary Constructor
        @param choices : list of possible replacing primitives
        @param parent : proxyWidget this item is embed in
        '''
        QtGui.QComboBox.__init__(self)
        self.proxyParent = parent
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.connect(self,QtCore.SIGNAL("activated(QString)"),self.proxyParent.parentItem().parentItem().parentView._updateTreeHook)
    
