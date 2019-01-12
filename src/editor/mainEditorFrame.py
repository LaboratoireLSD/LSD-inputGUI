'''

Created on 2010-12-18

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
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Drag_And_Drop_2.0.ui'
#
# Created: Fri Dec 18 15:29:18 2009
#      by: PyQt4 UI code generator 4.6
#
# WARNING! All changes made in this file will be lost!

import platform
from PyQt4 import QtCore, QtGui, QtXml
from editor.MedList import MedListView
from editor.AdvancedTreeEditor import MedTreeView
from editor.openDialog import Ui_OpenDialog as TreeOpener
from util.DocPrimitive import PrimitiveDict
from model.baseVarModel import GeneratorBaseModel
from model.baseTreatmentsModel import BaseTreatmentsModel
from frame.pluginViewer import PluginViewer
from model.LocalVariableModel import LocVarsModel, BaseLocalVariablesModel
from controller.LocVarDelegate import LocVarsDelegate

class MainEditorWindow(QtGui.QDialog):
    '''
    This class is an automatically generated python file using the pyuic4 program and .ui file generated by Qt_Designer
    However, it has been largely modified by the author
    This class is derived from mainWindow so it can have its own menu
    The window itself contains multiple tab
    Principal tab holds instances of MedTreeView a user-interactive graphical representation of a xml tree
    Some Other tabs contain information also located in the xml file, like xml node attributes, comments
    Finally, remaining tabs contain application specific features
    
    '''
    def __init__(self, domNode = QtXml.QDomNode(),parent=None,docName=""):
        '''
        @summary Constructor
        @param domNode: xml node of the first MedTreeView to be shown
        @param parent :  application's main window
        @param docName : tab Name of the first MedTreeView to be shown
        '''
        QtGui.QDialog.__init__(self,parent)
        self.resize(QtCore.QSize(1500,1000))
        self.setModal(True)
        self.setWindowFlags(QtCore.Qt.Window or QtCore.Qt.WindowMaximizeButtonHint)
        #self.setWindowFlags(QtCore.Qt.Dialog|QtCore.Qt.WindowMaximizeButtonHint|QtCore.Qt.WindowCloseButtonHint)
        # self.setModal(True)
        self.clipboard = None
        #Vertical Layout is the main layout
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.verticalLayout.setObjectName("verticalLayout")

        #This is the application main widget, containing the 4 tabs(MedList,MedTreeView,Property tab and comment/definition tab)
        self.splitter_2 = QtGui.QSplitter(self)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName("splitter_2")
        #Make sure splitter 2 takes as much space as possible
        self.splitter_2.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        #Left splitter(containing Primitive list tab widget and local variable tableView
        self.splitter_3 = QtGui.QSplitter(self.splitter_2)
        self.splitter_3.setOrientation(QtCore.Qt.Vertical)
        #Primitive list tab widget
        self.tabWidget = QtGui.QTabWidget(self.splitter_3)
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.setMovable(True)
        #Local variable table view
        self.locVarWidget = QtGui.QWidget(self.splitter_3)
        self.locVarLayout = QtGui.QVBoxLayout()
        self.locVarLayout.setMargin(0)
        self.locVarLabel = QtGui.QLabel("Local variables :")
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(75)
        font.setBold(True)
        self.locVarLabel.setFont(font)
        self.locVarLayout.addWidget(self.locVarLabel)
        self.locVarTblView = QtGui.QTableView()
        self.locVarLayout.addWidget(self.locVarTblView)
        self.buttonLayout = QtGui.QHBoxLayout()
        self.addLocVarButton = QtGui.QPushButton("Add")
        self.delLocVarButton = QtGui.QPushButton("Delete")
        self.addLocVarButton.setFixedSize(QtCore.QSize(77,25))
        self.delLocVarButton.setFixedSize(QtCore.QSize(77,25))
        self.buttonLayout.addWidget(self.addLocVarButton)
        self.buttonLayout.addWidget(self.delLocVarButton)
        self.buttonLayout.setAlignment(QtCore.Qt.AlignRight)
        self.locVarLayout.addLayout(self.buttonLayout)
        self.locVarWidget.setLayout(self.locVarLayout)
        #Central Widget
        self.tabWidget_2 = QtGui.QTabWidget(self.splitter_2)
        self.tabWidget_2.setTabsClosable(True)
        self.tabWidget_2.setMovable(True)
        self.tabWidget_2.setObjectName("tabWidget_2")
        #Right Widget
        self.splitter = QtGui.QSplitter(self.splitter_2)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        #Property Tab
        self.tabWidget_3 = QtGui.QTabWidget(self.splitter)
        self.tabWidget_3.setObjectName("tabWidget_3")
        #Definition widget
        self.tab_Widget_4 = QtGui.QTabWidget(self.splitter)
        #Comment Tab
        textBrowser = QtGui.QTextEdit(self)
        textBrowser.setObjectName("textBrowser")
        textBrowser.setText("Welcome to The LSD tree Editor.")
        self.tab_Widget_4.addTab(textBrowser, "Welcome")
        self.verticalLayout.addWidget(self.splitter_2)
        self.verticalLayout.addSpacing(20)
        #Bottom of the main window
        #We don't use a QDialogButtonBox to fool Qt(read QDialog for more details)
        #Setting up layout for the zoom buttons


        self.horizontalLayoutButtons = QtGui.QHBoxLayout()
        self.toolButton = QtGui.QPushButton(QtGui.QIcon("../img/actions/Zoom-Out-icon.png"),"",self)
        self.toolButton.setObjectName("toolButton")
        self.horizontalLayoutButtons.addWidget(self.toolButton)
        self.toolButton_2 = QtGui.QPushButton(QtGui.QIcon("../img/actions/Zoom-icon.png"),"",self)
        self.toolButton_2.setObjectName("toolButton_2")
        self.horizontalLayoutButtons.addWidget(self.toolButton_2)
        self.toolButton_3 = QtGui.QPushButton(QtGui.QIcon("../img/actions/Zoom-In-icon.png"),"",self)      
        self.toolButton_3.setObjectName("toolButton_3")
        self.horizontalLayoutButtons.addWidget(self.toolButton_3)

        self.buttonOk = QtGui.QPushButton("&OK")
        self.buttonCancel = QtGui.QPushButton("&Cancel")
        self.horizontalLayoutButtons.addWidget(self.buttonCancel)
        self.horizontalLayoutButtons.addWidget(self.buttonOk)
        self.horizontalLayoutButtons.setAlignment(QtCore.Qt.AlignRight)
        self.verticalLayout.addLayout(self.horizontalLayoutButtons)
        
        #Finishing the main layout with a status bar
        self.statusBar = QtGui.QStatusBar(self)
        self.verticalLayout.addWidget(self.statusBar)
        #Creating TreeView
        initTreeView = MedTreeView(domNode,self)
        initTreeView.setObjectName("treeView")
        self.tabWidget_2.addTab(initTreeView, docName)
        #Creating Normal Status Bar label
        self.statusBarLabel = QtGui.QLabel("Currently editing : "+docName)
        self.statusBar.addPermanentWidget(self.statusBarLabel)
        #self.statusBar.showMessage("Validity Status : "+str(initTreeView.primitive.worstEvent))
        
        #Creating MedList
        pmtDictRef = PrimitiveDict()
        #Create libraries and add them to their tab Widget
        for dictFilePath in pmtDictRef.getDictList().keys():
            name = pmtDictRef.getDictNameFromFilePath(dictFilePath)
            if name != "":
                newMedList = MedListView(pmtDictRef.getDictList()[dictFilePath])
                self.tabWidget.addTab(newMedList, name)
        
        #Add Tab that will hold properties
        self.tab_property = QtGui.QWidget()
        self.tab_property.setObjectName("tab_property")
        self.tabWidget_3.addTab(self.tab_property, "")
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_property), "Properties")
        #Splitter configuration. Allows good looking proportions when widget is created
        self.splitter.setSizes((500,100))
        self.splitter_3.setSizes((500,100))
        self.splitter_2.setSizes((150,750,150))
        #Connections
        QtCore.QObject.connect(self.buttonCancel, QtCore.SIGNAL("clicked()"), self.reject)
        QtCore.QObject.connect(self.buttonOk, QtCore.SIGNAL("clicked()"),self.saveAndQuit)
        QtCore.QObject.connect(self.toolButton, QtCore.SIGNAL("clicked()"), self.fzoomOut)
        QtCore.QObject.connect(self.toolButton_2, QtCore.SIGNAL("clicked()"), self.fzoomInit)
        QtCore.QObject.connect(self.toolButton_3, QtCore.SIGNAL("clicked()"), self.fzoomIn)
        QtCore.QObject.connect(self.tabWidget_2, QtCore.SIGNAL("tabCloseRequested(int)"),self.closeTab)
        QtCore.QObject.connect(self.tabWidget_2,QtCore.SIGNAL("currentChanged(int)"),self.updateStatusBar)
        QtCore.QObject.connect(self.tabWidget_2,QtCore.SIGNAL("currentChanged(int)"),self.updateProperties)
        QtCore.QObject.connect(self.tabWidget_2,QtCore.SIGNAL("currentChanged(int)"),self.updateLocals)
        QtCore.QObject.connect(self.addLocVarButton,QtCore.SIGNAL("pressed()"),self.addLocal)
        QtCore.QObject.connect(self.delLocVarButton,QtCore.SIGNAL("pressed()"),self.removeLocal)
        QtCore.QObject.connect(self,QtCore.SIGNAL("rejected()"),self.cleanLocals)
        
        self.setLayout(self.verticalLayout)
        self.createMenu()
        self.setWindowTitle("%s" % self.tabWidget_2.tabText(self.tabWidget_2.currentIndex()))
        self.setWindowIcon(QtGui.QIcon("../img/emblems/emblem-mushroom.png"))
        self.setWindowIconText("LSD Tree Editor")
        #Finally, setting up the tab widget
        #Initializing local variable table
        self.updateLocals(self.tabWidget_2.currentIndex())
        #Hide local variable table if it holds nothing
        #if not self.locVarWidget.isEnabled():
            #self.splitter_3.setSizes((600,0))
        #elif not self.locVarTblView.model().rowCount():
            #self.splitter_3.setSizes((600,0))
        
    def fzoomIn(self):
        '''
        @summary Zoom In
        '''
        self.tabWidget_2.currentWidget().scale(1.2, 1.2)
        
    def fzoomOut(self):
        '''
        @summary Zoom Out
        '''
        self.tabWidget_2.currentWidget().scale(0.9, 0.9)
        
    def fzoomInit(self):
        '''
        @summary Reset default zoom
        '''
        self.tabWidget_2.currentWidget().resetMatrix()
      
    def printSVGFile(self):
        '''
        @summary Ask the current MedTreeView tab to print and save a .svg file
        '''
        self.tabWidget_2.currentWidget().printSVGFile()
    
    def openTab(self,processName=None):
        '''
        @summary Opens a new tab
        @param processName : name of the process to open
        '''
        if not processName:
            #Give choice to user
            openDlg = TreeOpener(self)
            openDlg.exec_()
            if openDlg.result():
                newTreeView = MedTreeView(openDlg.chosenNode.toElement().elementsByTagName("PrimitiveTree").item(0).firstChild(),self)
                self.tabWidget_2.addTab(newTreeView,openDlg.comboBox.currentText())
                self.tabWidget_2.setCurrentWidget(newTreeView)
            
        else:
            #If process name is given, tab was opened via a double click on an other MedTreeView(tab)
            #Hence, it has to be a process
            baseTrModel = BaseTreatmentsModel()
            processNode =  baseTrModel.getTreatmentTree(processName)
            newTreeView = MedTreeView(processNode.toElement().elementsByTagName("PrimitiveTree").item(0).firstChild(),self)
            self.tabWidget_2.addTab(newTreeView,processName)
            self.tabWidget_2.setCurrentWidget(newTreeView)
    
    
    def saveAndQuit(self):
        '''
        @summary Save all tabs and quit
        '''
        for i in range(0,self.tabWidget_2.count()):
            if not self.tabWidget_2.widget(i).primitive._checkForSimilarDoms(self.tabWidget_2.widget(i).dom):
                self.parent().dirty = True
                self.tabWidget_2.widget(i).save()
            else:
                #Make sure local variable model is saved even if no changes appear in dom
                self.tabWidget_2.widget(i).saveLocals()
        self.accept()
        
    def save(self):
        '''
        @summary Save current tab
        '''
        if not self.tabWidget_2.currentWidget().primitive._checkForSimilarDoms(self.tabWidget_2.currentWidget().dom):
            self.parent().dirty = True
            self.tabWidget_2.currentWidget().save()
        else:
            #Make sure local variable model is saved even if no changes appear in dom
            self.tabWidget_2.currentWidget().saveLocals()
    
    def closeTab(self, tabIndex):
        '''
        @summary Close a Tab, ask save questions before closing
        @summary This function will not clause the tab itself, but rather return a boolean telling if the tab can be closes or not
        @param tabIndex: tab number
        '''
        treeName = str(self.tabWidget_2.tabText(tabIndex))
        currentTab = self.tabWidget_2.widget(tabIndex)
        #Look for modifications
        baseLocVarModel = BaseLocalVariablesModel()
        if currentTab.primitive._checkForSimilarDoms(currentTab.dom) and baseLocVarModel.checkForSimilarLocals(currentTab.dom.parentNode()):
            self.tabWidget_2.removeTab(tabIndex)
            return True
        #Ask for save
        reply = QtGui.QMessageBox.question(self, "%s" % QtGui.QApplication.applicationName() + " - Unsaved Changes", "Do you want to save the modifications made to "+treeName+"'s tree?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)
        if reply == QtGui.QMessageBox.Yes :
            currentTab.save()
            self.parent().dirty = True
            baseTrModel = BaseTreatmentsModel()
            #Look if current tab holds a process/scenario so model can update its validation state
            if not baseTrModel.updateValidationState(treeName, currentTab.primitive):
                baseVarModel = GeneratorBaseModel()
                #If not, Look if current tab holds a variable
                if not baseVarModel.updateValidationState(treeName, currentTab.primitive):
                    print("Modified a tree unknown to current model")
        
        #Keep Tab is user pressed cancel
        elif reply == QtGui.QMessageBox.Cancel :
            return False
        
        #else delete tab
        self.tabWidget_2.removeTab(tabIndex)
        if self.locVarTblView.model():
            #Request reload of tree's local variables
            self.locVarTblView.model().getBaseModel().parseLocVars(self.locVarTblView.model().node)
            
        return True

    def updateStatusBar(self,tabIndex):
        '''
        @summary Updates the name of the currently edited file in the status bar
        '''
        if not tabIndex == -1:
            self.statusBarLabel.setText("Currently editing : "+str(self.tabWidget_2.tabText(tabIndex)))
            self.statusBar.clearMessage()
            self.statusBar.showMessage("Validity Status : "+str(self.tabWidget_2.currentWidget().primitive.worstEvent))
    
    def updateProperties(self,tabIndex):
        '''
        @summary Updates the error, properties, comment and definition tabs with view's currentItem info, if any
        @param tabIndex : index of the tab has just been raised 
        '''
        if not tabIndex == -1:
            self.tabWidget_2.widget(tabIndex).generalUpdate()
    
    def checkAndUpdateProperties(self):
        '''
        @summary Updates the error, properties, comment and definition tabs with view's currentItem info, if any
        Check for errors in current Primitive if needed
        @param tabIndex : index of the tab has just been raised 
        '''
        currTab = self.tabWidget_2.currentIndex()
        if not currTab == -1:
            #Local variable modified can be anywhere in the tree, so we need to check it all
            self.tabWidget_2.widget(currTab).primitive._check(True)
            self.tabWidget_2.widget(currTab).generalUpdate()
            
    def cleanLocals(self):
        '''
        @summary Ask local variable model to reload itself so unsaved modifications are cleared from the model for next execution
        This function is called right before destruction
        '''
        baseLocVarModel = BaseLocalVariablesModel()
        baseLocVarModel.reload()
        
    def updateLocals(self,tabIndex):
        '''
        @summary Updates the error, properties, comment and definition tabs with view's currentItem info, if any
        @param tabIndex : index of the tab has just been raised 
        '''
        self.locVarTblView.setModel(None)
        self.locVarTblView.setItemDelegate(None)
        self.locVarWidget.setEnabled(False)
        if self.tabWidget_2.tabText(tabIndex) == "Clock" or self.tabWidget_2.tabText(tabIndex) == "AcceptFunction":
            return
        elif not tabIndex == -1:
            self.locVarTblView.setModel(self.tabWidget_2.widget(tabIndex).getLocVarModel())
            self.locVarTblView.setItemDelegate(LocVarsDelegate(self.locVarTblView,self)) 
            self.locVarWidget.setEnabled(True)
            self.connect(self.locVarTblView.itemDelegate(),QtCore.SIGNAL("closeEditor(QWidget*)"),self.checkAndUpdateProperties)
    
    def askForSave(self):
        '''
        @summary loop through tabs and "close" them
        '''
        for i in range(0,self.tabWidget_2.count()):
            if not self.closeTab(0):
                return False
        return True
           
    def closeEvent(self, event):
        '''
        @summary If askForSave succeeds, close window
        '''
        
        if self.askForSave():
            self.close()
        else:
            event.ignore()
            
    def createMenu(self):
        '''
        @summary Creates Menus for the main window
        '''
        self.menuBar = QtGui.QMenuBar()
        self.verticalLayout.setMenuBar(self.menuBar)
        ''' File menu '''
        self.fileMenu = self.menuBar.addMenu(self.tr("&File"))
        fileOpenAction = self.createAction("&Open...", self.openTab, "Ctrl+O", "document-open", "Open File")
        fileSaveAction = self.createAction("&Save", self.save, "Ctrl+S", "document-save", "Save File")
        fileExitAction = self.createAction("E&xit", self.reject, "Ctrl+Q", "system-log-out", "Exit")
        fileSaveTreePictureAction = self.createAction("Save Tree Picture", self.printSVGFile, None, None, None)
        fileSaveTreePictureAction.setIcon(QtGui.QIcon("../img/mimetypes/image-x-generic.png"))
        fileSaveTreePictureAction.setIconVisibleInMenu(True)
        fileOpenPrimitiveDict = self.createAction("Open &Plugin", self.addPlugin, "Ctrl+Shift+O", "plugin-add", "Open XSD Primitive Information File")
        self.fileMenu.addAction(fileOpenAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(fileSaveAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(fileOpenPrimitiveDict)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(fileSaveTreePictureAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(fileExitAction)
        
        ''' Edit menu '''
        self.editMenu = self.menuBar.addMenu(self.tr("&Edit"))
        editCutAction = self.createAction("Cu&t",self.cut, QtGui.QKeySequence.Cut, "edit-cut", "Cut")
        editCopyAction = self.createAction("&Copy",  self.copy, QtGui.QKeySequence.Copy, "edit-copy", "Copy")
        editPasteAction = self.createAction("&Paste",  self.paste, QtGui.QKeySequence.Paste, "edit-paste", "Paste")
        editRedoAction = self.createAction("&Redo",  self.redo, QtGui.QKeySequence.Redo, "edit-redo", "Redo")
        editUndoAction = self.createAction("&Undo",  self.undo,QtGui.QKeySequence.Undo, "edit-undo", "Undo")
        editTakeScreenshotAction = self.createAction("&Take Screenshot", self.takeScreenshot, QtGui.QKeySequence.AddTab, "camera-photo", "Screenshot")
        self.editMenu.addAction(editCutAction)
        self.editMenu.addAction(editCopyAction)
        self.editMenu.addAction(editPasteAction)
        self.editMenu.addSeparator()
        self.editMenu.addAction(editRedoAction)
        self.editMenu.addAction(editUndoAction)
        self.editMenu.addSeparator()
        self.editMenu.addAction(editTakeScreenshotAction)
        
        ''' Node Menu '''
        self.nodeMenu = self.menuBar.addMenu(self.tr("&Node"))
        nodeAddChildAction = self.createAction("&Add child", self.addChild, "Ctrl+A", "insert-child", None)
        nodeAddAttributeAction = self.createAction("&Add multiple children", self.multipleAdd, "Ctrl+Shift+A", "insert-multiple", None)
        nodeInsertBeforeAction = self.createAction("Insert &before selected node", self.insertBefore, "Ctrl+Up",  "insert-before", None)
        nodeInsertAfterAction = self.createAction("Insert &after selected node", self.insertAfter, "Ctrl+Down",  "insert-after",None)
        self.nodeMenu.addAction(nodeAddChildAction)
        self.nodeMenu.addAction(nodeAddAttributeAction)
        self.nodeMenu.addAction(nodeInsertBeforeAction)
        self.nodeMenu.addAction(nodeInsertAfterAction)
        
        ''' Help menu '''
        self.helpMenu = self.menuBar.addMenu(self.tr("&Help"))
        helpAboutAction = self.createAction("&About", self.helpAbout, None, None, "Help")
        helpAboutAction.setIcon(QtGui.QIcon("../img/apps/help-browser.png"))
        helpAboutAction.setIconVisibleInMenu(True)
        self.helpMenu.addAction(helpAboutAction)
        
    def createAction(self, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False, signal="triggered()"):
        '''
        @Summary Creates the choices that will be be shown in the different menus(ex : Save Or Save as in the file menu)
        @param text : Text shown in the menu bar
        @param slot : QtGui.QMainWindow function that will be called when the item is going to be clicked in the menu
        @param shortcut : keyboard shortcut that will trigger the action(ex : ctrl+v for action paste)
        @param icon : An icon or picture that will be seen left to the text in the menu
        @param tip : a tooltip shown when the user will hover the mouse over an action
        @param checkable : Sets if a checkbox is visible left to the text in the menu
        @signal : default signal that will trigger the action(triggered, checked, etc...)
        '''
        action = QtGui.QAction(text, self)
        if icon is not None:
            action.setIcon(QtGui.QIcon("../img/actions/%s.png" % icon))
            action.setIconVisibleInMenu(True)
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, QtCore.SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action
    
    def multipleAdd(self):
        '''
        @summary Calls current tab's multiple add function
        '''
        numChildToAdd, modif =  QtGui.QInputDialog.getInteger( self, "Add Multiple Children",
                                                        """<p>How many child do you want to add?
                                                        <p>Warning : If a node isn't selected,
                                                         nothing will happen""", 0,0, 200, 1)

        if modif:
            self.tabWidget_2.currentWidget().addMultipleChildren(numChildToAdd)
            
    def takeScreenshot(self):
        '''
        @summary Takes a screenshot of the window
        '''
        #-20 is to grab the window frame(the title bar)
        screenshot = QtGui.QPixmap.grabWindow(self.winId(),0,-22)
        fileName = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save screenshot"),
                                                        "", self.tr("PNG files (*.png);;All files (*);;"))
        if fileName:
            screenshot.save(fileName,QtCore.QString("png").toAscii())
    
    def addPlugin(self):
        '''
        @Add plugin to project by calling Main Window's open plugin function and create MedListView of the new dictionary
        '''
        pv = PluginViewer()
        pv.exec_()
        #Recreate MedLists
        pmtDictRef = PrimitiveDict()
        self.tabWidget.clear()
        #Create libraries and add them to their tab Widget
        for dictFilePath in pmtDictRef.getDictList().keys():
            name = pmtDictRef.getDictNameFromFilePath(dictFilePath)
            if name != "":
                newMedList = MedListView(pmtDictRef.getDictList()[dictFilePath])
                self.tabWidget.addTab(newMedList, name) 
    
    def addLocal(self):        
        '''
        @summary Add local variable to currently edited tree
        '''
        widgetAddLocal = Widget_AddLocalVar(self)
        widgetAddLocal.exec_()
        #If user cancelled the operation, do nothing
        if not widgetAddLocal.result() :
            return
        #Else user entered parameter information, so create new parameter
        newVarName = widgetAddLocal.lineEditName.text()
        newType = widgetAddLocal.comboBoxType.currentText()
        if widgetAddLocal.radioButtonScalar.isChecked():
            newValue = widgetAddLocal.lineEditScalar.text()
        else:
            newValue = [ str(item.text()) for item in [widgetAddLocal.listWidgetVector.item(i) for i in range(0,widgetAddLocal.listWidgetVector.count())]]
        
        self.locVarTblView.model().insertRow(self.locVarTblView.model().rowCount(),self.locVarTblView.rootIndex(),newVarName,newType, newValue)
       
        #Since user might have a property tab with a combobox holding local variables, we want the new
        #local variable to appear in the dropdown list, we have to update the properties tab
        self.tabWidget_2.currentWidget().updateProperties()
        
    def removeLocal(self):
        '''
        @Summary Remove currently selected local variable to the currently edited tree
        '''
        if self.locVarTblView.selectedIndexes():
            self.locVarTblView.model().removeRow(self.locVarTblView.selectedIndexes()[0].row())
            #Might have introduced errors in the current tab, check and reload properties tab
            self.tabWidget_2.currentWidget().primitive._check()
            self.tabWidget_2.currentWidget().updateProperties()
            
    def copy(self):
        '''
        @summary Simple copy function
        '''
        self.tabWidget_2.currentWidget().copy()
        
    def paste(self):
        '''
        @summary Simple paste function
        '''
        self.tabWidget_2.currentWidget().paste()
        
    def cut(self):
        '''
        @summary Simple cut function
        '''
        self.tabWidget_2.currentWidget().cut()
    
    def redo(self):
        '''
        @summary Simple redo function
        '''
        self.tabWidget_2.currentWidget().undoStack.redo()
    
    def undo(self):
        '''
        @summary Simple undo function
        '''
        self.tabWidget_2.currentWidget().undoStack.undo()
        
    def addChild(self):
        '''
        @summary Calls current tab's addChild function
        '''
        self.tabWidget_2.currentWidget().addChild()
        
    def insertAfter(self):
        '''
        @summary Calls current tab's insertAfter function
        '''
        self.tabWidget_2.currentWidget().addSiblingAfter()
         
    def insertBefore(self):
        '''
        @summary Calls current tab's insertBefore function
        '''
        self.tabWidget_2.currentWidget().addSiblingBefore()
    
    def helpAbout(self):
        '''
        @summary Show help information
        '''
        QtGui.QMessageBox.about(self, "About LSD Tree Editor",
                                """<b>LSD Tree Editor</b> v %s
                          <p>Copyright &copy; 2009 L.S.D.
                          All rights reserved.
                          <p>This is the simulator tree Editor application.
                          <p>Python %s - Qt %s - PyQt %s on %s""" 
                                % ("2.0", platform.python_version(), QtCore.QT_VERSION_STR, QtCore.PYQT_VERSION_STR, platform.system()))
        
    def popNodeMenu(self,pos):
        '''
        @summary Popup Node menu
        @param pos : global position for the pop up menu to pop
        '''
        self.nodeMenu.popup(pos)

class Widget_AddLocalVar(QtGui.QDialog):
    '''
    Dialog allowing the user to create a new Parameter
    '''
    def __init__(self,parent):
        '''
        @summary: Constructor
        @param parent: parameters Tab
        '''
        QtGui.QDialog.__init__(self,parent)
        self.resize(450,340)
        self.setObjectName("paramManager")
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(10, 300, 430, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        
        self.labelName = QtGui.QLabel("Name : ",self)
        self.labelName.setGeometry(QtCore.QRect(20,20,100,22))
        
        self.lineEditName = QtGui.QLineEdit(self)
        self.lineEditName.setGeometry(QtCore.QRect(150,20,150,22))
        
        self.labelType = QtGui.QLabel("Type : ",self)
        self.labelType.setGeometry(QtCore.QRect(20,50,100,22))
        
        self.comboBoxType = QtGui.QComboBox(self)
        self.comboBoxType.setGeometry(QtCore.QRect(150,50,150,22))
        self.comboBoxType.addItems(["Bool","Double","Float","Int","Long","String","ULong","UInt"])
        self.radioButtonScalar = QtGui.QRadioButton("Scalar",self)
        self.radioButtonScalar.setGeometry(QtCore.QRect(20,80,100,22))
        
        self.radioButtonVector = QtGui.QRadioButton("Vector",self)
        self.radioButtonVector.setGeometry(QtCore.QRect(150,80,100,22))
        
        self.lineEditScalar = QtGui.QLineEdit(self)
        self.lineEditScalar.setGeometry(QtCore.QRect(30,130,100,22))
        
        self.listWidgetVector = QtGui.QListWidget(self)
        self.listWidgetVector.setGeometry(QtCore.QRect(160,130,140,100))
        
        self.pushButtonAdd = QtGui.QPushButton("Add", self)
        self.pushButtonAdd.setGeometry(QtCore.QRect(320,150,100,25))
        
        self.pushButtonDelete = QtGui.QPushButton("Delete", self)
        self.pushButtonDelete.setGeometry(QtCore.QRect(320,185,100,25))
        
        self.connect(self.radioButtonScalar,QtCore.SIGNAL("toggled(bool)"),self.rbManager)
        self.connect(self.pushButtonAdd,QtCore.SIGNAL("clicked()"),self.addData)
        self.connect(self.pushButtonDelete,QtCore.SIGNAL("clicked()"),self.removeData)
        self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.commitParameter)
        self.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        
        self.radioButtonScalar.setChecked(True)
        self.setWindowTitle(QtGui.QApplication.translate("paramManager", "Add parameter", None, QtGui.QApplication.UnicodeUTF8))

    def rbManager(self,state):
        '''
        @summary Enable or disable widgets depending of the currently selected radio Button
        '''
        self.lineEditScalar.setEnabled(state)
        self.listWidgetVector.setDisabled(state)
        self.pushButtonAdd.setDisabled(state)
        self.pushButtonDelete.setDisabled(state)
        
    def addData(self):
        '''
        @summary Asks the user to enter a value if we are in vector mode
        '''
        result, status = QtGui.QInputDialog.getText(self, "Enter Data", "Value : ")
        if not status:
            return
        else:
            self.listWidgetVector.addItem(result)
    
    def removeData(self):
        '''
        @summary Removes a value from the list if we are in vector mode
        '''
        self.listWidgetVector.takeItem(self.listWidgetVector.currentRow())
        
    def commitParameter(self):
        '''
        Check if all fields were entered before closing dialog
        '''
        if self.lineEditName.text().isEmpty():
            QtGui.QMessageBox.warning(self,"Empty Name!", "Cannot add a parameter with an empty name!")
            return
        if self.radioButtonScalar.isChecked():
            if self.lineEditScalar.text().isEmpty():
                QtGui.QMessageBox.warning(self,"Empty Value!", "Cannot add a parameter with an empty value!")
                return
        elif not self.listWidgetVector.count():
            QtGui.QMessageBox.warning(self,"Empty Value!", "Cannot add a vector parameter with no value")
            return
        
        self.accept()
