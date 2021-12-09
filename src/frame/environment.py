"""
.. module:: demoFileEditor

.. codeauthor:: Majid Malis

:Created on: 2009-10-15

"""

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'environment.ui'
#
# Created: Thu Oct 15 22:35:16 2009
#      by: PyQt4 UI code generator 4.5.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore
from PyQt4 import QtGui

class Ui_environment(object):
    '''
    This class is an automatically generated python file using the pyuic4 program and .ui file generated by Qt_Designer.
    This class is the mainWindow's tab containing the environment information of the simulation.
    '''
    def __init__(self, parent):
        '''
        Constructor.
        
        :param parent: Application's mainWindow
        :type parent: :class:`~LSD_inputGUI.src.frame.MainWindow`
        '''
        self.parent = parent
        
    def setupUi(self, environment):
        """
        Creates the widgets that will be displayed on the frame.
        
        :param environment: Representation of the environment tab
        :type environment: :class:`~LSD_inputGUI.src.frame.MainFrame.MyWidgetTabEnvironment`
        """
        environment.setObjectName("environment")
        #Creating Layouts
        #Creating Layout for the Add and Delete Buttons
        self.layoutControls = QtGui.QHBoxLayout()
        #Creating layout that will hold all the other layouts
        self.mainLayout = QtGui.QVBoxLayout()
        #Label at top of the widget
        self.tableLabel = QtGui.QLabel()
        
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(75)
        font.setBold(True)
        self.tableLabel.setFont(font)
        self.tableLabel.setObjectName("tableLabel")
        
        #Creating TableView
        self.tableView = ArrowsAwareTableView()
        self.tableView.setObjectName("tableView")
        
        # My preferences
        self.tableView.setDragEnabled(True)
        self.tableView.setAcceptDrops(True)
        self.tableView.setDropIndicatorShown(True)
        self.tableView.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.tableView.setDefaultDropAction(QtCore.Qt.DropAction(QtCore.Qt.MoveAction))
        self.tableView.setDragDropOverwriteMode(False)
        self.tableView.horizontalHeader().setSortIndicatorShown(True)
        self.tableView.setSortingEnabled(True)
        
        #Adding child widgets/layouts to the main layout
        self.mainLayout.addWidget(self.tableLabel)
        self.mainLayout.addWidget(self.tableView)
        self.mainLayout.addLayout(self.layoutControls)
        
        #Buttons Add and Delete
        self.add = QtGui.QPushButton()
        self.add.setFixedSize(QtCore.QSize(77,25))
        self.add.setObjectName("add")
        self.delete = QtGui.QPushButton()
        self.delete.setFixedSize(QtCore.QSize(77,25))
        self.delete.setObjectName("delete")
        #Adding these widgets to their layout 
        self.layoutControls.addWidget(self.add)
        self.layoutControls.addWidget(self.delete)  
        self.layoutControls.addItem(QtGui.QSpacerItem(100, 30, QtGui.QSizePolicy.Expanding))
        
        #Setting the spacings
        self.layoutControls.setSpacing(10)
        #Setting the margins
        self.mainLayout.setMargin(50)
        
        #Setting MainLayout to environment
        environment.setLayout(self.mainLayout)
        
        #Pyuic4 auto-generated code and connections
        self.retranslateUi(environment)
        QtCore.QMetaObject.connectSlotsByName(environment)
        
        self.connect(self.add, QtCore.SIGNAL("clicked()"), self.addRow)
        self.connect(self.delete, QtCore.SIGNAL("clicked()"), self.deleteRow)
        self.connect(self.tableView, QtCore.SIGNAL("deleteVariable()"), self.deleteRow)
        
    def retranslateUi(self, environment):
        """
        Translate the labels on the frame.
        
        :param environment: Representation of the environment tab
        :type environment: :class:`~LSD_inputGUI.src.frame.MainFrame.MyWidgetTabEnvironment`
        """
        environment.setWindowTitle(QtGui.QApplication.translate("environment", "Population", None, QtGui.QApplication.UnicodeUTF8))
        self.tableLabel.setText(QtGui.QApplication.translate("environment", "Environment variables :", None, QtGui.QApplication.UnicodeUTF8))
        self.add.setText(QtGui.QApplication.translate("environment", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.delete.setText(QtGui.QApplication.translate("environment", "Delete", None, QtGui.QApplication.UnicodeUTF8))
        
    def deleteRow(self):
        '''
        Removes 1 or many variables from the model
        '''
        if len(self.tableView.selectedIndexes()) > 1:
            self.tableView.model().specialRemove([index.row() for index in self.tableView.selectedIndexes()])
            self.tableView.clearSelection()
        
        elif len(self.tableView.selectedIndexes()):
            index = self.tableView.selectedIndexes()[0]
            self.tableView.model().removeRow(self.tableView.rootIndex(),index.row())
            self.tableView.clearSelection()
            
    def addRow(self):
        '''
        Add variable in model
        '''
        if self.tableView.selectedIndexes() and len(self.tableView.selectedIndexes()) == 1:
            self.tableView.model().insertRow(self.tableView.selectedIndexes()[0].row()+1, self.tableView.rootIndex())
            return
        
        self.tableView.model().insertRow(self.tableView.model().rowCount(), self.tableView.rootIndex())

class ArrowsAwareTableView(QtGui.QTableView):
    '''
    This class slightly modify Qt's QTableView class.
    Navigating the TableView with arrows will generate the same signal as if the user was using the mouse buttons.
    This way, previews will be generated like the user had clicked in the table view.
    '''
    def __init__(self):
        '''
        Constructor 
        '''
        QtGui.QTableView.__init__(self)
        
    def keyPressEvent(self,event):
        '''
        Reimplementation of QTableView's keyPressEvent function.
        
        :param event: See QTableView's documentation for more information
        '''
        super(ArrowsAwareTableView, self).keyPressEvent(event)
        if event.key() == QtCore.Qt.Key_Delete and not self.state() == QtGui.QAbstractItemView.EditingState:
            self.emit(QtCore.SIGNAL("deleteVariable()"))