"""
.. module:: demoFileEditor

.. codeauthor::  Mathieu Gagnon <mathieu.gagnon.10@ulaval.ca>

:Created on: 2010-09-01

"""

from PyQt4 import QtCore, QtGui
from PyQt4.QtXml import QDomDocument
from model.PopModel import SimplePopModel
from model.baseVarModel import SimpleBaseVarModel
from controller.VarDelegate import SimpleVarDelegate
from util.opener import Opener


class demoFileEditor(QtGui.QDialog):
    '''
    This class is an independent dialog used to create and edit demography files.
    '''
    def __init__(self, parent,loadFileAtStartup = True ):
        '''
        Constructor.
        
        :param parent: Application's main window
        :param loadFileAtStartup: Create or open a file at startup
        :type parent: :class:`~LSD_inputGUI.src.frame.MainWindow`
        :type loadFileAtStartup: Boolean
        '''
        QtGui.QDialog.__init__(self,None,QtCore.Qt.Window)
        self.parent = parent
        self.setupUi()
        self.setWindowTitle("Demography File Editor")
        self.demoFile = None
        self.domDocument = None
        if not loadFileAtStartup:
            self.domDocument = QDomDocument()
            newDemoElement = self.domDocument.createElement("Demography")
            self.domDocument.appendChild(newDemoElement)
            demoPopModel = SimplePopModel(SimpleBaseVarModel(self.parent,self.domDocument.firstChild()),self.parent)
            self.tableView.setModel(demoPopModel)
            self.tableView.setItemDelegate(SimpleVarDelegate(self.tableView,self.parent))
        else:
            self.open()
        
    def setupUi(self):
        """
        Creates the widgets that are displayed on the frame
        """
        self.setObjectName("Form")
        #Dialog buttons
        self.buttonBox = QtGui.QDialogButtonBox()
        self.buttonBox.setFixedWidth(200)
        self.buttonBox.setFixedHeight(30)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok )
        self.buttonBox.setObjectName("buttonBox")
        
        #Creating and setting the layouts
        self.mainLayout = QtGui.QVBoxLayout()
        self.layoutLabel = QtGui.QHBoxLayout()
        self.layoutButtons = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(self.layoutLabel)
        
        self.tableView = QtGui.QTableView()
        self.mainLayout.addWidget(self.tableView)
        self.mainLayout.addLayout(self.layoutButtons)
        self.mainLayout.addSpacing(50)
        self.mainLayout.addWidget(self.buttonBox)
        self.mainLayout.setAlignment(self.buttonBox, QtCore.Qt.AlignRight)
        #Now that main layout is all set up, populate horizontal layouts
        self.label = QtGui.QLabel()
        self.label.setObjectName("label")
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setText("Demography From File : ")
        
        self.label2 = QtGui.QLabel()
        self.label2.setObjectName("label2")
        self.label2.setFont(font)
        self.label2.setText("")

        self.pushButton_Load= QtGui.QPushButton("Load Demography")
        self.pushButton_Load.setFixedHeight(26)
        self.pushButton_Load.setFixedWidth(150)
        self.layoutLabel.addWidget(self.label)
        self.layoutLabel.addWidget(self.label2)
        self.layoutLabel.addWidget(self.pushButton_Load)
        self.layoutLabel.addItem(QtGui.QSpacerItem(100, 30, QtGui.QSizePolicy.Expanding))
        self.pushButton_Add= QtGui.QPushButton("Add variable")
        self.pushButton_Add.setFixedHeight(26)
        self.pushButton_Add.setFixedWidth(150)
        
        self.pushButton_Delete= QtGui.QPushButton("Delete variable")
        self.pushButton_Delete.setFixedHeight(26)
        self.pushButton_Delete.setFixedWidth(150)

        self.layoutButtons.addWidget(self.pushButton_Add)
        self.layoutButtons.addWidget(self.pushButton_Delete)
        self.layoutButtons.addItem(QtGui.QSpacerItem(100, 30, QtGui.QSizePolicy.Expanding))

        #Layout look and feel
        self.mainLayout.setMargin(50)
        self.layoutLabel.setSpacing(10)
        self.layoutButtons.setSpacing(10)
        
        self.setLayout(self.mainLayout)
        
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.lookForAccept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QObject.connect(self.pushButton_Load, QtCore.SIGNAL("clicked()"), self.load)
        QtCore.QObject.connect(self.pushButton_Add, QtCore.SIGNAL("clicked()"), self.addVar)
        QtCore.QObject.connect(self.pushButton_Delete, QtCore.SIGNAL("clicked()"), self.deleteVar)
    
    def load(self):
        '''
        Load a demography file.
        Save before loading if needed.
        '''
        reply = QtGui.QMessageBox.warning(self,"Loading Demography", "Save changes made to the previously loaded file?",QtGui.QMessageBox.Yes|QtGui.QMessageBox.No|QtGui.QMessageBox.Cancel)
        if reply == QtGui.QMessageBox.Cancel:
            return
        elif reply == QtGui.QMessageBox.Yes:
            if not self.demoFile:
                if not self.saveAs():
                    return
            else:
                self.save()
               
        self.open()
            
    def lookForAccept(self):
        '''
        Save and quit.
        '''
        mBoxSave = QtGui.QMessageBox( QtGui.QMessageBox.Warning, "Leaving demography file editor", "Save changes made to demography file?",QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel|QtGui.QMessageBox.Save)
        mBoxSave.button(QtGui.QMessageBox.Save).setText("Save as")
        reply = mBoxSave.exec_()
        if reply == QtGui.QMessageBox.Cancel:
            return
        elif reply == QtGui.QMessageBox.Ok:
            if not self.demoFile:
                if self.saveAs():
                    self.accept()
            else:
                self.save()
                self.accept()
        elif reply == QtGui.QMessageBox.Save:
            if self.saveAs():
                self.accept()
        
    def open(self):
        '''
        Open an existing demography file.
        '''
        demoPath = QtGui.QFileDialog.getOpenFileName(self, self.tr("Choose a demography to edit"),
                                              "./database", self.tr("XML files (*.xml);;All files (*);;"))
        if not demoPath:
            #User pressed cancel
            #If at startup and no model has been created yet
            if not self.tableView.model():
                self.domDocument = QDomDocument()
                newDemoElement = self.domDocument.createElement("Demography")
                self.domDocument.appendChild(newDemoElement)
                demoPopModel = SimplePopModel(SimpleBaseVarModel(self.parent,self.domDocument.firstChild()),self.parent)
                self.tableView.setModel(demoPopModel)
                self.tableView.setItemDelegate(SimpleVarDelegate(self.tableView,self.parent))
            return
        
        if demoPath.split(".")[-1] != "xml":
            #Non XMl-File edition is not allowed for the moment
            QtGui.QMessageBox.Warning(self,"Open File", "Non-Xml Files cannot be open for the moment",QtGui.QMessageBox.Ok)
            return
        
        else:
            f = Opener(demoPath)
            self.domDocument = f.getDomDocument()
            root_node = f.getRootNode()
            if root_node.nodeName() != "Demography":
                QtGui.QMessageBox.Warning(self,"Open File", "File "+demoPath+" is not a demography file!", QtGui.QMessageBox.Ok)
                return
            else:
                self.demoFile = demoPath
                demoPopModel = SimplePopModel(SimpleBaseVarModel(self.parent,root_node),self.parent)
                self.tableView.setModel(demoPopModel)
                self.tableView.setItemDelegate(SimpleVarDelegate(self.tableView,self.parent))
                self.label2.setText(self.demoFile.rsplit("/")[-1])
                
    def save(self):
        '''
        Save a demography file.
        '''
        tmpTextStream = QtCore.QTextStream()
        fileP = QtCore.QFile(self.demoFile)
        if fileP.open(QtCore.QIODevice.ReadWrite| QtCore.QIODevice.Truncate):
            tmpTextStream.setDevice(fileP)
            self.domDocument.save(tmpTextStream, 5)
        else:
            print("Could not open file :", self.demoFile)
            print("Error code :", fileP.error())
        fileP.close()
        
    def saveAs(self):
        '''
        Save as a new demography file. Returns a boolean telling if the save was made correctly or not.
        
        :return: Boolean
        '''
        self.demoFile = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save demography file"),
                                                        "./database", self.tr("XML files (*.xml);;All files (*);;"))
        if self.demoFile:
            if self.demoFile[-4:] != ".xml":
                self.demoFile += ".xml"
            self.save()
            return True
        
        return False
        
    def addVar(self):
        '''
        Adds a variable to the demography.
        '''
        if self.tableView.model():
            index = self.tableView.currentIndex()
        
            if index.isValid():
                self.tableView.model().insertRow(index.row())
            else:
                self.tableView.model().insertRow(self.tableView.model().rowCount())
        
    def deleteVar(self):
        '''
        Removes a variable from the demography.
        '''
        if self.tableView.model():
            index = self.tableView.currentIndex()
            if index.isValid():
                self.tableView.model().removeRow(index.row())
                
        
                
