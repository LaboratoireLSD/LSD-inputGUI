'''
Created on 2011-06-01

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
    This class is an independent dialog used to search primitives with known attribute values
    It searches the primitive using xquery, open the processes in tree editor and higlights the primitives in pink
    '''
    def __init__(self, parent):
        '''
        @summary Constructor
        @param parent : application's main window
        @param loadFileAtStartup : Create or open a file at startup
        '''
        QtGui.QDialog.__init__(self,None,QtCore.Qt.Window)
        self.parent = parent
        self.setupUi()
        self.setWindowTitle("Search tool")
        
    def setupUi(self):
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
        for dictFilePath in pmtDictRef.getDictList().keys():
            name = pmtDictRef.getDictNameFromFilePath(dictFilePath)
            if name != "":
                newMedList = MedListView(pmtDictRef.getDictList()[dictFilePath])
                self.tabWidget.addTab(newMedList, name)
                self.connect(newMedList,QtCore.SIGNAL("itemClicked(QListWidgetItem*)"),self.updateProperties)
        


        #Layout look and feel
        self.mainLayout.setMargin(50)
        
        
        self.setLayout(self.mainLayout)
        
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.search)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
    
    def updateProperties(self,itemClicked=None):
        '''
        @summary Create and show a widget that contains the currently selected primitive attributes 
        '''
        #Clear the current tab widget containing the properties of the last selected item
        #Need to create a fake dom document, how shitty
        if itemClicked:
            domDocument =QDomDocument()
            newTmpDomElement = domDocument.createElement(itemClicked.doc.name)
            self.primitive = Primitive(None, None,self, newTmpDomElement)
        self.rightLayout.removeWidget(self.attributeWidget)
        self.attributeWidget.deleteLater()
        self.attributeWidget = QtGui.QWidget()
        self.attributeWidget.setLayout(self.primitive.guiGetAttrLayout())
        self.rightLayout.addWidget(self.attributeWidget)
        
    def search(self):
        '''
        Search for elements in dom corresponding to primitive searched by user 
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
