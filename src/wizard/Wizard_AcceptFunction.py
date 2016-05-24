'''
Created on 2009-05-26

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

# Form implementation generated from reading ui file 'Wizard_AcceptFunction.ui'
#
# Created: Wed May 26 12:33:48 2010
#      by: PyQt4 UI code generator 4.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from model.baseVarModel import GeneratorBaseModel

class Ui_WizardPage(object):
    '''
    This class was automatically generated using a qtdesigner .ui file and qt's pyuic4 program.
    It is a dialog allowing a user to modify the accept function of a population
    '''
    def setupUi(self, WizardPage):
        WizardPage.setObjectName("WizardPage")
        WizardPage.resize(640, 480)
        self.parent = WizardPage.parent()
        self.scrollArea = QtGui.QScrollArea(WizardPage)
        self.scrollArea.setGeometry(QtCore.QRect(120, 110, 600, 250))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtGui.QWidget(self.scrollArea)
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.label = QtGui.QLabel(WizardPage)
        self.label.setGeometry(QtCore.QRect(120, 90, 121, 17))
        self.label.setObjectName("label")
        self.checkBox = QtGui.QCheckBox("Accept all individuals",WizardPage)
        self.checkBox.setGeometry(QtCore.QRect(421,380,170,28))
        self.checkBox.setChecked(False)
        
        self.retranslateUi(WizardPage)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)
        self.connect(self.checkBox,QtCore.SIGNAL("stateChanged(int)"),self.restrict)
        
    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setTitle(QtGui.QApplication.translate("WizardPage", "Profile - Step 2", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setSubTitle(QtGui.QApplication.translate("WizardPage", "Choose which individuals you want to keep for your population based on the available variables.", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("WizardPage", "Accept function :", None, QtGui.QApplication.UnicodeUTF8))

    def initializePage(self):
        '''
        @summary Reimplemented from QWizardPage.initializePage(self)
        Called automatically when the page is shown
        '''
        baseVarModel = GeneratorBaseModel()
        if not self.scrollAreaWidgetContents.layout():
            profileName = self.parent.topWObject.popTab.comboBox.itemData(self.field("currProfile")[0])
            self.gridLayout = EvalFunctionWidget(baseVarModel,profileName,self)
            self.gridLayout.parseEntry(self.gridLayout.baseModel.getAcceptFunctionNode(profileName))
                                                                                  
            self.scrollAreaWidgetContents.setLayout(self.gridLayout)
        
    def restrict(self,checkState):
        '''
        @summary Enable/Disable Accept Function Scroll Area
        @param checkState : boolean state
        '''
        if checkState == QtCore.Qt.Checked:
            self.scrollArea.setDisabled(True) 
        else:
            self.scrollArea.setDisabled(False)
    
    def parseResults(self):
        '''
        @summary Parse grid layout's widgets and create appropriate DOM tree
        '''
        if self.checkBox.isChecked():
            domNode = self.createDomNode("Token","type","Bool","value","True")
            self.gridLayout.acceptFunctionPmtTree.replaceChild(domNode,self.gridLayout.acceptFunctionPmtTree.firstChild())
            return
        domNode = self.createDomNode("And")
        i = 0
        while i < self.gridLayout.rowCount():
            if not self.gridLayout.itemAtPosition(i,0):
                i+=1
                continue
            currVar = self.gridLayout.itemAtPosition(i,0).widget()
            domNodeDict = []
            while(True):
                condition = self.gridLayout.itemAtPosition(i,1).widget().currentText()
                if condition:
                    domNodeDict.append(self.writeXmlRestriction(condition, [currVar,self.gridLayout.itemAtPosition(i,2).widget(),self.gridLayout.itemAtPosition(i,3).widget()]))
                if not self.gridLayout.itemAtPosition(i+1,0) and  self.gridLayout.itemAtPosition(i+1,1):
                    i+=1
                else:
                    if domNodeDict:
                        newOrNode = domNode.appendChild(self.createDomNode("Or"))
                        for item in domNodeDict:
                            newOrNode.appendChild(item)
                    i+=1
                    break
        self.gridLayout.acceptFunctionPmtTree.replaceChild(domNode,self.gridLayout.acceptFunctionPmtTree.firstChild())
            
    def writeXmlRestriction(self,widgetCondition,widgetList):
        '''
        @summary creates the xml subtree corresponding to one line(restriction)
        @params widgetCondition, widgetList : line condition and widgets used to create xml tree
        '''
        varName = widgetList[0].text()
        varValue = widgetList[1].text()
        baseModel = GeneratorBaseModel()
        profileName = self.parent.topWObject.popTab.comboBox.itemData(self.field("currProfile").toInt()[0])
        if widgetCondition == "equals":
            domVar = self.createDomNode("TokenVariable","label",varName)
            domToken = self.createDomNode("Token","type",baseModel.getVarType(profileName,varName),"value",varValue)
            domEquals = self.createDomNode("IsEqual")
            domEquals.appendChild(domVar)
            domEquals.appendChild(domToken)
            return domEquals
        elif widgetCondition == "<=":
            domVar = self.createDomNode("TokenVariable","label",varName)
            domToken = self.createDomNode("Token","type",baseModel.getVarType(profileName,varName),"value",varValue)
            domEquals = self.createDomNode("IsLessOrEqual")
            domEquals.appendChild(domVar)
            domEquals.appendChild(domToken)
            return domEquals
        elif widgetCondition == ">=":
            domVar = self.createDomNode("TokenVariable","label",varName)
            domToken = self.createDomNode("Token","type",baseModel.getVarType(profileName,varName),"value",varValue)
            domEquals = self.createDomNode("IsGreaterOrEqual")
            domEquals.appendChild(domVar)
            domEquals.appendChild(domToken)
            return domEquals    
        else:
            #case between
            varValue2 = widgetList[2].text()
            domVar = self.createDomNode("TokenVariable","label",varName)
            domToken = self.createDomNode("Token","type",baseModel.getVarType(profileName,varName),"value",varValue)
            domToken2 = self.createDomNode("Token","type",baseModel.getVarType(profileName,varName),"value",varValue2)
            domBetween = self.createDomNode("Between")
            domBetween.appendChild(domVar)
            domBetween.appendChild(domToken)
            domBetween.appendChild(domToken2)
            return domBetween
           
    
    def createDomNode(self, nodeName, arg1="", arg1Value="", arg2="", arg2Value=""):
        '''
        @summary Creates an xml node
        '''
        domNode = self.gridLayout.acceptFuncDom.ownerDocument().createElement(nodeName)
        if arg1:
            domNode.toElement().setAttribute(arg1,arg1Value)
        if arg2:
            domNode.toElement().setAttribute(arg2,arg2Value)
        return domNode
    
    def validatePage(self):
        '''
        @summary Reimplemented from QWizardPage.validatePage(self)
        Called automatically when the page is about to be changed
        '''
        self.parseResults()
        return True
         
class EvalFunctionWidget(QtGui.QGridLayout):
    '''
    Reimplemented from QtGui.QGridLayout()
    Restrictions are listed in this class as widgets
    '''
    def __init__(self,baseModel, profileName, mainPage):
        '''
        @summary Constructor
        @param baseModel : BaseVarModel
        @param profileName : currently selected profile
        @param mainPage : wizard page associated with this widget
        '''
        QtGui.QGridLayout.__init__(self)
        self.setSizeConstraint(QtGui.QLayout.SetMinAndMaxSize)
        self.setColumnMinimumWidth(2, 120)
        self.setColumnMinimumWidth(3, 120)
        self.setColumnStretch(0, 1)
        self.baseModel = baseModel
        self.profileName = profileName
        self.page = mainPage
        
    def parseEntry(self, funcNode):
        '''
        @summary Parse funcNode and create widgets until an unknown xml node is encountered or until the node is completely parsed
        @param funcNode : the xml node to be parsed
        '''
        self.acceptFuncDom = funcNode
        funcDict={"IsLessEqual":self.parseRegular,
                  "IsGreaterEqual":self.parseRegular,
                  "IsEqual":self.parseRegular,
                  "Between":self.parseBetween}
        indexDict ={"IsLessEqual":2,
                  "IsGreaterEqual":3,
                  "IsEqual":1,
                  "Between":4}

        self.acceptFunctionPmtTree = funcNode.firstChildElement("PrimitiveTree")
        acceptFunctionNode = self.acceptFunctionPmtTree.firstChild()
        #First Node has to be And
        if acceptFunctionNode.nodeName() == "And":
            lAndChildList = acceptFunctionNode.childNodes()
            for i in range(lAndChildList.count()):
                lCurrentChildNode = lAndChildList.item(i)
                if lCurrentChildNode.nodeName() == "Or":
                    sameVariable, varName = self.checkIfSameVariable(lCurrentChildNode)
                    if sameVariable:
                        lOrChildList = lCurrentChildNode.childNodes()
                        for orChilds in range(lOrChildList.count()):
                            lCurrentOrChild = lOrChildList.item(orChilds)             
                            if lCurrentOrChild.nodeName() in funcDict.keys():
                                if funcDict[lCurrentOrChild.nodeName()](lCurrentOrChild, varName, indexDict[lCurrentOrChild.nodeName()]):
                                    continue               
                            self.parent().setEnabled(False)
                        continue
                self.parent().setEnabled(False)
               
        #Or a Token Bool = True (accept all individuals)
        elif acceptFunctionNode.nodeName() == "Token":
            
            if acceptFunctionNode.toElement().attribute("type") == "Bool":
                
                self.page.checkBox.setChecked(True)
                self.page.scrollArea.setEnabled(False)
            else:
                self.page.scrollAreaWidgetContents.setEnabled(False)
        #Else set disabled, accept function has to be edited via Tree Editor
        else:
            self.parent().setEnabled(False)
        #Don'T forget to add the variables that weren't found in the accept Function Node
        for var in self.baseModel.getDemoVarsList(self.profileName):
            if var not in self.varList():
                numRows = self.rowCount()
                self.createWidgets(numRows)
                self.addWidget(QtGui.QLabel(var), numRows, 0)
                self.addWidget(QtGui.QPushButton("+"), numRows, 5)
                self.itemAtPosition(numRows, 5).widget().setFixedWidth(30)
                self.itemAtPosition(numRows, 4).widget().setDisabled(True)
                self.connect(self.itemAtPosition(numRows, 5).widget(), QtCore.SIGNAL("clicked()"), self.addRestriction)
    
    def parseRegular(self, domNode, varName, indexVal):
        '''
        @summary Parse the xml node of a regular expression
        @param dmoNode : the domNode to parse
        @param varName : the variable name of the parsed node
        @param indexVal : an int corresponding to the type of condition(IsEqual, IsGreater, etc...)
        '''
        if domNode.childNodes().count() == 2:
            firstChild = domNode.childNodes().item(0)
            secondChild = domNode.childNodes().item(1)
            if firstChild.nodeName() == "TokenVariable" and secondChild.nodeName() == "Token" :
                numRows = self.rowCount()
                self.createWidgets(numRows)
                self.itemAtPosition(numRows, 1).widget().setCurrentIndex(indexVal)
                self.itemAtPosition(numRows, 2).widget().setText(secondChild.toElement().attribute("value", ""))
                if not varName in self.varList():
                    self.addWidget(QtGui.QLabel(varName),numRows, 0)
                    self.addWidget(QtGui.QPushButton("+"), numRows, 5)
                    self.itemAtPosition(numRows, 5).widget().setFixedWidth(30)
                    self.itemAtPosition(numRows, 4).widget().setDisabled(True)
                    self.connect(self.itemAtPosition(numRows, 5).widget(), QtCore.SIGNAL("clicked()"), self.addRestriction)
                else:
                    self.addWidget(self.itemAtPosition(numRows-1, 5).widget(), numRows, 5)
                    self.itemAtPosition(numRows-1, 4).widget().setEnabled(True)
               
                return True
            
        return False
    
    def parseBetween(self, domNode, varName, indexVal):
        '''
        @summary Parse the xml node of a between expression
        @param dmoNode : the domNode to parse
        @param varName : the variable name of the parsed node
        @param indexVal : an int corresponding to the type of condition(IsEqual, IsGreater, etc...)
        '''
        if domNode.childNodes().count() == 3:
            firstChild = domNode.childNodes().item(0)
            secondChild = domNode.childNodes().item(1)
            thirdChild = domNode.childNodes().item(2)
            if firstChild.nodeName() == "TokenVariable" and secondChild.nodeName() == "Token" and thirdChild.nodeName() == "Token" :
                numRows = self.rowCount()
                self.createWidgets(numRows)
                self.itemAtPosition(numRows, 1).widget().setCurrentIndex(indexVal)
                self.itemAtPosition(numRows, 2).widget().setText(secondChild.toElement().attribute("value", ""))
                self.itemAtPosition(numRows, 3).widget().setEnabled(True)
                self.itemAtPosition(numRows, 3).widget().setText(thirdChild.toElement().attribute("value", ""))
                if not varName in self.varList():
                    self.addWidget(QtGui.QLabel(varName),numRows, 0)
                    self.addWidget(QtGui.QPushButton("+"), numRows, 5)
                    self.itemAtPosition(numRows, 5).widget().setFixedWidth(30)
                    self.itemAtPosition(numRows, 4).widget().setDisabled(True)
                    self.connect(self.itemAtPosition(numRows, 5).widget(), QtCore.SIGNAL("clicked()"), self.addRestriction)
                else:
                    self.addWidget(self.itemAtPosition(numRows-1, 5).widget(), numRows, 5)
                    self.itemAtPosition(numRows-1, 4).widget().setEnabled(True)
                    
                return True
            
        return False
    
    def varList(self):
        '''
        @summary return the variables present in the grid
        '''
        variables = []
        rows = self.rowCount()
        for i in range(rows):
            if self.itemAtPosition(i, 0):
                variables.append(self.itemAtPosition(i, 0).widget().text())
        return variables
    
    def checkIfSameVariable(self, domNode):
        '''
        @summary Security function
        @Make sure there is only one variable listed in a Or 
        '''
        tokenVariableList = domNode.toElement().elementsByTagName("TokenVariable")
        varName = []
        for i in range(tokenVariableList.count()):
            varName.append(tokenVariableList.item(i).toElement().attribute("label", ""))
        if len(set(varName)) == 1:
            if varName[0]: 
                return True, varName[0]
        return False, None
    
    def createWidgets(self, numRows):
        '''
        @summary Creates the widget before they are customized by parse function
        @param numRows : row of the widget to create
        '''
        self.addWidget(QtGui.QComboBox(), numRows, 1)
        self.itemAtPosition(numRows, 1).widget().addItems(["", "equals", "<=", ">=", "between"])
        self.addWidget(QtGui.QLineEdit(), numRows, 2)
        self.addWidget(QtGui.QLineEdit(), numRows, 3)
        self.itemAtPosition(numRows, 3).widget().setDisabled(True)
        self.addWidget(QtGui.QPushButton("-"), numRows, 4)
        self.itemAtPosition(numRows, 4).widget().setFixedWidth(30)
        self.connect(self.itemAtPosition(numRows, 4).widget(), QtCore.SIGNAL("clicked()"), self.removeRestriction)
        self.connect(self.itemAtPosition(numRows, 1).widget(), QtCore.SIGNAL("currentIndexChanged(QString)"), self.enableLineEdit)
        
    def enableLineEdit(self, text):
        cellSizes = self.getItemPosition(self.indexOf(self.sender()))
        row = cellSizes[0]
        if text == "between":
            self.itemAtPosition(row, 3).widget().setEnabled(True)
            return
        self.itemAtPosition(row, 3).widget().setEnabled(False)
    
    def addRestriction(self):
        '''
        @summary Adds a line after the line where the pushButton was pressed
        '''
        #get row of the pushButton that sent the request
        cellSizes = self.getItemPosition(self.indexOf(self.sender()))
        row = cellSizes[0]
        newComboBox = QtGui.QComboBox()
        newComboBox.addItems(["", "equals", "<=", ">=", "between"])
        self.updateLayout(row)
        self.addWidget(newComboBox, row+1,1)
        self.addWidget(QtGui.QLineEdit(), row+1,2)
        self.addWidget(QtGui.QLineEdit(), row+1,3)
        self.itemAtPosition(row+1, 3).widget().setDisabled(True)
        self.addWidget(QtGui.QPushButton("-"), row+1, 4)
        self.itemAtPosition(row+1, 4).widget().setFixedWidth(30)
        #First remove pushButton and then add it. Adding it without removing it first gives an unexpected behavior
        self.removeWidget(self.sender())
        #self.sender().sender().setParent(None)
        self.addWidget(self.sender(), row+1, 5)
        self.connect(newComboBox, QtCore.SIGNAL("currentIndexChanged(QString)"), self.enableLineEdit)
        self.connect(self.itemAtPosition(row+1, 4).widget(), QtCore.SIGNAL("clicked()"), self.removeRestriction)
        #Set PushButton_remove("-") of the precedent item. Will ensure that if item was disabled because it was the only condition of the variable, it will now be available for discard
        self.itemAtPosition(row, 4).widget().setEnabled(True)
        
    def removeRestriction(self):
        '''
        @summary Removes the line where a "-" psuhButton was pressed
        '''
        #get row of the psuhButton that sent the request
        cellSizes = self.getItemPosition(self.indexOf(self.sender()))
        row = cellSizes[0]
        self.updateLayout(row, False)
        #Look if disabling the PushButton "-" is necessary
        for i in range(self.rowCount()):
            if self.itemAtPosition(i, 0) :
                if self.itemAtPosition(i+1, 0) or not self.itemAtPosition(i+1, 1):
                    self.itemAtPosition(i, 4).widget().setEnabled(False)
                    
    def updateLayout(self, rowFrom, rowAdded=True):
        '''
        @summary QGridLayout only provides methods to replace a widget at a certain position
        This function, although not quite efficient, allows the insertion of a row in the model, "pushing" 1 row further
        @param rowAdded: if false, allows the removal of a row in the model
        @rowFrom : row where the updateLAyout comes from
        '''
        if rowAdded:
            rowCount = self.rowCount()
            while rowCount > rowFrom + 1:
                for i in range(6):
                    if self.itemAtPosition(rowCount-1, i):
                        self.addWidget(self.itemAtPosition(rowCount-1, i).widget(), rowCount, i)
                rowCount += -1
        else:
            #Quite complex conditions to check, so they are going to be described
            rowCount =  self.rowCount()
            #As long as there are rows located higher(higher is lower on the screen) than the one being deleted
            while rowFrom < rowCount:
                #for all 6 columns available(label,comboBoxCondition. 2 lines Edits, + and - push Buttons)
                for i in range(6):
                    #look if there is an item on the line higher
                    if self.itemAtPosition(rowFrom+1, i):
                        #Look if there is an item on the row currently being transformed
                        if self.itemAtPosition(rowFrom, i):
                            #if it's a pushButton +, send it on the line before
                            if i == 5:
                                self.addWidget(self.itemAtPosition(rowFrom, i).widget(), rowFrom-1, i)
                            #else delete this item(important)
                            else:
                                item = self.itemAtPosition(rowFrom, i)
                                self.removeItem(item)
                                item.widget().deleteLater()
                        #now u can safely take the line over the one  being transformed and transfer its widgets
                        self.addWidget(self.itemAtPosition(rowFrom+1, i).widget(), rowFrom, i)
                        
                    #if there is no object on the line above, multiple possibilities
                    else:
                        #look if there is an item on the row currently being transformed
                        if self.itemAtPosition(rowFrom, i):
                            #if so and we're on line 5, there is QPushButton + to move below
                            if i == 5:
                                self.addWidget(self.itemAtPosition(rowFrom, i).widget(), rowFrom-1, i)
                            #if there is a label, leave it there
                            elif i == 0:
                                continue
                            #else, delete objects
                            else:
                                item = self.itemAtPosition(rowFrom, i)
                                self.removeItem(item)
                                item.widget().deleteLater()
                        
                rowFrom += 1
        #Note : other conditions are implicit: ex : since a QpushButton "-" is disabled when his line is the only condition of the variable, we don'T have to check for this case(this function will never get called)
