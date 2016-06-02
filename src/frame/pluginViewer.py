"""
.. module:: pluginViewer

.. codeauthor::  Mathieu Gagnon <mathieu.gagnon.10@ulaval.ca>

:Created on: 2009-01-18

"""

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'wizstart2.ui'
#
# Created: Mon Jan 18 10:46:39 2010
#      by: PyQt4 UI code generator 4.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from util.DocPrimitive import PrimitiveDict
import os

class PluginViewer(QtGui.QDialog):
    '''
    This class was automatically generated using a qtdesigner .ui file and qt's pyuic4 program.
    It is a dialog allowing a user to see available libraries(.xsd files) and select them for the current project.
    '''
    def __init__(self):
        QtGui.QDialog.__init__(self)
        #Creating the layouts
        self.mainLayout = QtGui.QVBoxLayout()
        self.layoutLists = QtGui.QHBoxLayout()
        self.layoutArrows = QtGui.QVBoxLayout()
        self.layoutButtons = QtGui.QHBoxLayout()
        self.layoutLeftList = QtGui.QVBoxLayout()
        self.layoutRightList = QtGui.QVBoxLayout()
        self.layoutAddDict = QtGui.QHBoxLayout()
        self.layoutCentral = QtGui.QVBoxLayout()
        
        #Creating list labels
        self.label = QtGui.QLabel()
        self.label.setObjectName("label")
        self.label_2 = QtGui.QLabel()
        self.label_2.setObjectName("label_2")
        #Creating lists
        self.listWidget = QtGui.QListWidget()
        self.listWidget.setObjectName("listWidget")
        self.listWidget.setDragEnabled(True)
        self.listWidget_2 = QtGui.QListWidget()
        self.listWidget_2.setObjectName("listWidget_2")
        self.listWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.listWidget_2.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        #Creating ArrowButtons
        self.pushButton_up = QtGui.QPushButton()
        self.pushButton_down = QtGui.QPushButton()
        self.pushButton_up.setIcon(QtGui.QIcon("../img/actions/go-previous.png"))
        self.pushButton_down.setIcon(QtGui.QIcon("../img/actions/go-next.png"))
        
        #Setting size policies
        self.listWidget.setMaximumSize(300, 500)
        self.listWidget_2.setMaximumSize(300, 500)
        self.label.setFixedSize(150,20)
        self.label_2.setFixedSize(150,20)
        self.listWidget.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        self.listWidget_2.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        self.pushButton_down.setFixedSize(30,30)
        self.pushButton_up.setFixedSize(30,30)
        #Atom layouts
        self.layoutLeftList.addWidget(self.label)
        self.layoutLeftList.addWidget(self.listWidget)
        self.layoutRightList.addWidget(self.label_2)
        self.layoutRightList.addWidget(self.listWidget_2)
        self.layoutArrows.addWidget(self.pushButton_up)
        self.layoutArrows.addWidget(self.pushButton_down)
        self.layoutArrows.setAlignment(QtCore.Qt.AlignVCenter)
       
        
        #Layout Add Dictionary
        self.label_3 = QtGui.QLabel()
        self.label_3.setObjectName("label_3")
        self.label_3.setFixedSize(200,20)
        self.pushButton_3 = QtGui.QPushButton()
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.setFixedSize(75,25)
        
        self.layoutAddDict.addWidget(self.label_3)
        self.layoutAddDict.addWidget(self.pushButton_3)
        self.layoutAddDict.setAlignment(QtCore.Qt.AlignHCenter)
        #Central part
        self.layoutLists.addLayout(self.layoutLeftList)
        self.layoutLists.addLayout(self.layoutArrows)
        self.layoutLists.addLayout(self.layoutRightList)
        self.layoutCentral.addLayout(self.layoutLists,)
        self.layoutCentral.addLayout(self.layoutAddDict)
        self.layoutCentral.setAlignment(QtCore.Qt.AlignCenter)
        
        #Buttons 
        self.buttonBox = QtGui.QDialogButtonBox()
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        
        #Main layout
        self.mainLayout.setMargin(50)
        self.mainLayout.addLayout(self.layoutCentral)
        self.mainLayout.addWidget(self.buttonBox) 
        self.setLayout(self.mainLayout)
        self.retranslateUi()
        
        #Initialize page
        self.initialize()
              
        self.connect(self.pushButton_3,QtCore.SIGNAL("clicked()"),self.openDialog)
        self.connect(self.pushButton_down,QtCore.SIGNAL("clicked()"),self.addNewItem)
        self.connect(self.pushButton_up,QtCore.SIGNAL("clicked()"),self.removeItem)
        self.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        self.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
               
    def retranslateUi(self):
        '''
        Function allowing naming of the different labels regardless of app's language.
        '''
        self.setWindowTitle(QtGui.QApplication.translate("PluginViewer", "LSD - Plugin Manager", None, QtGui.QApplication.UnicodeUTF8))
        self.listWidget.setSortingEnabled(True)
        self.listWidget_2.setSortingEnabled(True)
        self.label.setText(QtGui.QApplication.translate("PluginViewer", "Available libraries :", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("PluginViewer", "Used libraries :", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("PluginViewer", "Add library from file system :", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_3.setText(QtGui.QApplication.translate("PluginViewer", "Browse", None, QtGui.QApplication.UnicodeUTF8))
    

    def initialize(self):
        '''
        Called before Dialog is shown to populate list Widgets
        '''
        pluginDict = PrimitiveDict()
        #Not clean but does the job for the moment
        self.pluginNode = pluginDict.topObject.domDocs["main"].firstChildElement("System").firstChildElement("Plugins")
        
        for dictionaries in pluginDict.dictPrimitives:
            if not pluginDict.getDictNameFromFilePath(dictionaries) == "":
                newListWidgetItem = QtGui.QListWidgetItem(pluginDict.getDictNameFromFilePath(dictionaries))
                newListWidgetItem.setData(QtCore.Qt.UserRole, dictionaries)
                self.listWidget_2.addItem(newListWidgetItem)
                
        for files in os.listdir("util/XSD"):
            if os.path.splitext(files)[1] == ".xsd":
                newListWidgetItem = QtGui.QListWidgetItem(os.path.splitext(files)[0])
                newListWidgetItem.setData(QtCore.Qt.UserRole, "util/XSD/"+files)
                #If it's a definition library, do not show
                if os.path.splitext(files)[0] in ["PMT","GUI","BaseTypes"]:
                    continue
                if files.split("/")[-1] in [dictPath.split("/")[-1] for dictPath in pluginDict.dictPrimitives.keys()]:
                    continue
                else:
                    self.listWidget.addItem(newListWidgetItem)

    def openDialog(self):
        '''
        Opens a dialog so the user can add libraries that weren't found by the initialize function.
        '''
        xmlPath = ""
        pluginDict = PrimitiveDict()
        filePath = QtGui.QFileDialog.getOpenFileName(self, self.tr("Open XML parameters file"),
                                                                  xmlPath, self.tr("XSD files (*.xsd);;All files (*);;"))
        
        if filePath.rsplit(".")[-1] == "xsd":
            if filePath.split("/")[-1] in [dictPath.split("/")[-1] for dictPath in pluginDict.dictPrimitives.keys()]:
                return
            pluginDict.addFromXSD(filePath)
            newListWidgetItem = QtGui.QListWidgetItem(pluginDict.getDictNameFromFilePath(filePath))
            newListWidgetItem.setData(QtCore.Qt.UserRole, filePath)
            self.listWidget_2.addItem(newListWidgetItem)

    def addNewItem(self):
        '''
        Adds a library to the selected libraries list.
        '''
        pluginDict = PrimitiveDict()
        if self.listWidget.selectedItems():            
            for i in self.listWidget.selectedItems():
                dictAdded = self.listWidget.takeItem(self.listWidget.row(i))
                self.listWidget_2.addItem(dictAdded)
                pluginDict.addFromXSD(dictAdded.data(QtCore.Qt.UserRole))
                newPluginNode = self.pluginNode.ownerDocument().createElement("Plugin")
                newPluginNode.toElement().setAttribute("xsdfile","XSD/"+dictAdded.data(QtCore.Qt.UserRole).split("/")[-1])
                newPluginNode.toElement().setAttribute("source","lib"+dictAdded.data(QtCore.Qt.UserRole).lower().split("/")[-1][0:-3]+"so")
                self.pluginNode.appendChild(newPluginNode)
        self.listWidget.clearSelection()
        
                
    def removeItem(self):
        '''
        Removes a library from the selected libraries list.
        '''
        pluginDict = PrimitiveDict()
        if self.listWidget_2.selectedItems():
            for i in self.listWidget_2.selectedItems():
                dictRemoved = self.listWidget_2.takeItem(self.listWidget_2.row(i))
                self.listWidget.addItem(dictRemoved)
                pluginDict.removeDictFromFilePath(dictRemoved.data(QtCore.Qt.UserRole))
                childPlugins = self.pluginNode.elementsByTagName("Plugin")
                for pluginIndex in range (0,childPlugins.count()):
                    if childPlugins.item(pluginIndex).toElement().attribute("xsdfile") in dictRemoved.data(QtCore.Qt.UserRole):
                        self.pluginNode.removeChild(childPlugins.item(pluginIndex))
                        break
        self.listWidget_2.clearSelection()
                
