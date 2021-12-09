"""
.. module:: SearchTool

.. codeauthor::  Mathieu Gagnon <mathieu.gagnon.10@ulaval.ca>

:Created on: 2011-06-01

"""

from editor.MedList import MedListView
from PyQt4 import QtCore, QtGui
from PyQt4.QtXml import QDomDocument
from PyQt4.QtXmlPatterns import QXmlQuery
from util.DocPrimitive import PrimitiveDict
from model.PrimitiveModel import Primitive
from model.baseTreatmentsModel import BaseTreatmentsModel
from editor.mainEditorFrame import MainEditorWindow
from editor.AdvancedTreeEditor import MedTreeView

class searchDialog(QtGui.QDialog):
    '''
    This class is an independent dialog used to search primitives with known attribute values.
    It searches the primitive using xquery, open the processes in tree editor and highlights the primitives in pink.
    '''
    def __init__(self, parent):
        '''
        Constructor.
        
        :param parent: Application's main window
        :param loadFileAtStartup: Create or open a file at startup
        '''
        QtGui.QDialog.__init__(self,None,QtCore.Qt.Window)
        self.parent = parent
        self.setupUi()
        self.setWindowTitle("Search tool")
        
    def setupUi(self):
        """
        Creates the widgets that will be displayed on the frame.
        """
        self.setObjectName("Form")
        self.resize(800,600)
        #Dialog buttons
        self.buttonBox = QtGui.QDialogButtonBox()
        self.buttonBox.setFixedWidth(200)
        self.buttonBox.setFixedHeight(30)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok )
        self.buttonBox.setObjectName("buttonBox")
        
        #Creating and setting the layouts
        self.mainLayout = QtGui.QVBoxLayout()
        self.splitter = QtGui.QSplitter()
        self.mainLayout.addWidget(self.splitter)
        self.mainLayout.addWidget(self.buttonBox)
        self.mainLayout.setAlignment(self.buttonBox, QtCore.Qt.AlignRight)
        
        #Left Layout
        self.leftLayout = QtGui.QVBoxLayout()
        self.leftWidget = QtGui.QWidget()
        self.leftWidget.setLayout(self.leftLayout)
        self.leftLabel = QtGui.QLabel("Available primitives:")
        self.leftLabel.setFixedHeight(30)
        self.tabWidget = QtGui.QTabWidget()
        self.leftLayout.addWidget(self.leftLabel)
        self.leftLayout.addWidget(self.tabWidget)    
        self.splitter.addWidget(self.leftWidget)
        
        #Right Layout
        self.rightLayout = QtGui.QVBoxLayout()
        self.rightWidget = QtGui.QWidget()
        self.rightWidget.setLayout(self.rightLayout)
        self.rightLabel = QtGui.QLabel("Available attributes :")
        self.rightLabel.setFixedHeight(30)
        self.rightLayout.addWidget(self.rightLabel)
        self.attributeWidget = QtGui.QWidget()
        self.rightLayout.addWidget(self.attributeWidget)
        self.splitter.addWidget(self.rightWidget)
        
        #Creating MedList
        pmtDictRef = PrimitiveDict()
        #Create libraries and add them to their tab Widget
        for dictFilePath in pmtDictRef.dictPrimitives.keys():
            name = pmtDictRef.getDictNameFromFilePath(dictFilePath)
            if name != "":
                newMedList = MedListView(pmtDictRef.dictPrimitives[dictFilePath])
                self.tabWidget.addTab(newMedList, name)
                self.connect(newMedList,QtCore.SIGNAL("itemClicked(QListWidgetItem*)"),self.updateProperties)
        


        #Layout look and feel
        self.mainLayout.setMargin(50)
        
        
        self.setLayout(self.mainLayout)
        
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.search)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
    
    def updateProperties(self,itemClicked=None):
        '''
        Creates and shows a widget that contains the currently selected primitive attributes.
        
        :param itemClicked: Optional
        :type itemClicked: QListWidgetItem
        '''
        #Clear the current tab widget containing the properties of the last selected item
        #Need to create a fake dom document, how shitty
        if itemClicked:
            domDocument = QDomDocument()
            newTmpDomElement = domDocument.createElement(itemClicked.doc.name)
            self.primitive = Primitive(None, None,self, newTmpDomElement)
        self.rightLayout.removeWidget(self.attributeWidget)
        self.attributeWidget.deleteLater()
        self.attributeWidget = QtGui.QWidget()
        self.attributeWidget.setLayout(self.primitive.guiGetAttrLayout())
        self.rightLayout.addWidget(self.attributeWidget)
        
    def search(self):
        '''
        Searches for elements in dom corresponding to primitive searched by user .
        '''
        if not hasattr(self,"primitive"):
            QtGui.QMessageBox.warning(self, "Nothing to search for", "Select a primitive first before pressing ok.")
            return
        predicateList = ""
        for attribute in self.primitive.nextAttribute():
            if attribute.getValue():
                #Add Predicate
                predicateList = predicateList+("[@"+attribute.name+"='"+str(attribute.value)+"']")
        
        #buildx path of the query
        xpath = "//"+self.primitive.name+predicateList
        
        #Once predicate is built
        #Make XQuery
        dependencyQuery = QXmlQuery()
        #Parent is top object, asks for its node
        #Proceded XQuery
        queryBuffer = QtCore.QBuffer()
        queryBuffer.setData(self.parent.domDocs["main"].toString())
        queryBuffer.open(QtCore.QIODevice.ReadOnly)
        dependencyQuery.bindVariable("varSerializedXML", queryBuffer)
        query= "for $x in doc($varSerializedXML)"+xpath+"/ancestor::Process[@label]/@label return string(data($x))"
        dependencyQuery.setQuery(query)
        dependencies = []
        dependencyQuery.evaluateTo(dependencies)
        if not len(dependencies):
            QtGui.QMessageBox.warning(self, "Primitive not found", "Couldn't find a match for selected criterion")
            return
        treatmentModel = BaseTreatmentsModel()
        processList = list(set(dependencies))
        for process in processList:
            if not processList.index(process):
                #First Process gotta create tree editor
                tree = treatmentModel.getTreatmentsDict()[process]
                editor = MainEditorWindow(tree.toElement().elementsByTagName("PrimitiveTree").item(0).firstChild(),self.parent,process)
                editor.setWindowModality(QtCore.Qt.WindowModal)
                editor.tabWidget_2.currentWidget().primitive.propagateHighlighting(self.primitive)
                continue
            tree = treatmentModel.getTreatmentsDict()[process]
            newTreeView = MedTreeView(tree.toElement().elementsByTagName("PrimitiveTree").item(0).firstChild(),editor)
            editor.tabWidget_2.addTab(newTreeView,process)
            newTreeView.primitive.propagateHighlighting(self.primitive)
        
        editor.exec_()
            
    def updateDirtyState(self):
        '''
        @Function called by primitive in tree editor
        We don't need this function here, so we just pass
        '''
        pass
