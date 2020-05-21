'''
Created on 2009-01-27

@author:  Marc Andre Gardner
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

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import QtXml
from decimal import Decimal
from util.DocPrimitive import PrimitiveDict
from util.LCA import LCA
from model.baseEnvModel import BaseEnvModel
from model.baseTreatmentsModel import BaseTreatmentsModel
from model.baseVarModel import GeneratorBaseModel
from model.BaseParametersModel import BaseParametersModel
from model.LocalVariableModel import BaseLocalVariablesModel

class PrimitiveValidityEvent():
    '''
    This class represent an error (or at least a notice) in the Primitive Tree.
    '''
    
    def __init__(self, primitiveRef, eventType, eventArgs):
        '''
        @summary Constructor
        @param primitiveRef : associated primitive instance
        @param eventType : event type (see DocPrimitiveEvent)
        @param eventArgs : event arguments (see DocPrimitiveEvent)
        '''
        self.eventRef = primitiveRef.xsdInfos.getSpecificEventInfo(str(eventType))
        self.eArgs = eventArgs
        self.pmtRef = primitiveRef

        if self.eventRef.isObjectNull():
            print("Warning : unknown event " + str(eventType) + " for primitive " + primitiveRef.name)
            return

    def getGravity(self):
        '''
        @summary Return's event gravity
        '''
        return self.eventRef.getGravity()

    def isMoreSevereThan(self, referenceStr):
        '''
        @summary Return's if event is more important than other event
        '''
        return self.eventRef.isMoreSevereThan(referenceStr)

    def haveToForceCorrection(self):
        '''
        @summary Return's if user has to correct before continuing
        '''
        return self.eventRef.haveToForceCorrection()

    def haveToWarnUser(self):
        '''
        @summary Return's if user has to be warned
        '''
        return self.eventRef.haveToWarnUser()
    
    def isValid(self):
        '''
        @summary Return's if event is valid
        '''
        return not self.eventRef.isObjectNull()
    
    def haveToAddComment(self):
        '''
        @summary Return if comment has to be added
        '''
        return self.eventRef.haveToAddComment()

    def generateEventMsg(self):
        '''
        @summary Generate message  associated with this event
        '''
        if self.eventRef.isNull:
            print("Could not generate error Message!")
            return "Error : This primitive seems to be unknown"
        return self.eventRef.generateErrorMsg(self.eArgs)

class PrimitiveAttribute(QtCore.QObject):
    '''
    This class represents the attribute of a Primitive
    '''  
    def __init__(self, name, value, parentPrimitive):
        '''
        @summary Constructor
        @param name : attribute's name
        @param value : attribute's value
        @param parentPrimitive : attribute's primitive
        '''
        QtCore.QObject.__init__(self)
        self.pmtParent =  parentPrimitive
        self.name = str(name)
      #  #print value
        self.value = str(value)
       # print self.value
        self.editor = None
        self.layout = None
        self.choiceMenu = None
        self.typeDir = {'@':'indVar','#':'envVar','$':'param','%':'locVar'}
        if self.getType() == "value":
            if self.pmtParent.xsdInfos.getAttribute(self.name).getPairedAttr():
                if not self.pmtParent.hasAttribute(self.pmtParent.xsdInfos.getAttribute(self.name).getPairedAttr()):
                    #Paired attribute found in xsd but not in parent attributes
                    #Maybe it has not been created yet, maybe it is not in xml
                    #Hence, we're not going to take any chances and create it already
                    #At worst its going to be overridden
                    self.pmtParent.addAttributeByName(self.pmtParent.xsdInfos.getAttribute(self.name).getPairedAttr()) 
        
    def getName(self):
        '''
        @summary Return attribute's name
        '''
        return self.name
    
    def getMappedName(self):
        '''
        @summary Return's attribute mapped Name or attribute's name if mapped NAme doesn't exist
        '''
        return self.pmtParent.xsdInfos.getAttribute(self.name).getMappedName() if self.pmtParent.xsdInfos.getAttribute(self.name).getMappedName() else self.name
        
    def getType(self):
        '''
        @Summary Return where this attribute comes from
        Possible values : indVar, envVar, param, locVar and value
        '''
        if not self.value:
            return "value"
        else:
            try:
                return self.typeDir[self.value[0]]
            except KeyError:
                return "value"
    
    def getValue(self):
        '''
        @summary Return attribute's value
        '''
        if self.getType() == "value":
            return self.value
        return self.value[1:]
    
    def getLayout(self):
        '''
        @summary Create and return layout
        '''
        self.layout = QtGui.QHBoxLayout()
        self.layout.setAlignment(QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.guiCreatePropertyLabel())
        self.checkSetChoice()
        self.layout.addWidget(self.guiCreateEditor())    
        if not self.pmtParent.xsdInfos.isPaired(self.getName()) and self.pmtParent.xsdInfos.getAttribute(self.getName()).isOptionnal():
            pushButtonRemove = QtGui.QPushButton("-")
            pushButtonRemove.setFixedWidth(25)
            pushButtonRemove.setFixedHeight(27)
            self.layout.addWidget(pushButtonRemove)
            self.connect(pushButtonRemove,QtCore.SIGNAL("pressed()"),self.remove)
        return self.layout
    
    def guiCreateEditor(self):
        '''
        @summary Created an editor( a QLineEdit or QComboBox)
        '''
        typeDir = {'indVar':'indVariables','envVar':'envVariables','param':'allParameters','locVar':'locVariables'}
        
        if self.pmtParent.xsdInfos.getAttribute(self.name).getBehavior().getList():
            if len(self.pmtParent.xsdInfos.getAttribute(self.name).getBehavior().getList()) <= 1:
                type = self.pmtParent.xsdInfos.getAttribute(self.name).getBehavior().getList()[0]["type"]    
            else:
                #Multiple list for the attribute
                if not self.value or self.getType() == "value":
                    if self.pmtParent.xsdInfos.getAttribute(self.getName()).getPairedAttr() and self.pmtParent.name == "Data_Value":
                        #Might be a boolean attribute
                        pairedAttr = self.pmtParent.xsdInfos.getAttribute(self.getName()).getPairedAttr()
                        if self.pmtParent.hasAttribute(pairedAttr):
                            #Attribute exists
                            if self.pmtParent.getAttributeByName(pairedAttr).getValue() == "Bool":
                                #Value attribute with boolean type, list possible values
                                self.editor = QtGui.QComboBox()
                                self.editor.addItems(["true","false"])
                                self.editor.setCurrentIndex(self.editor.findText(self.getValue()))
                                self.guiUpdateWidgetGeometryComboBox(self.editor.currentText())
                                self.connect(self.editor,QtCore.SIGNAL("currentIndexChanged(QString)"),self.guiSetModelData)
                                self.connect(self.editor,QtCore.SIGNAL("currentIndexChanged(QString)"),self.guiUpdateWidgetGeometryComboBox)
                                return self.editor
                    #Value is a line edit value
                    self.editor = QtGui.QLineEdit()
                    self.guiSetEditorData(self.editor)
                    self.guiUpdateWidgetGeometry(self.editor.text())
                    self.connect(self.editor,QtCore.SIGNAL("textEdited(QString)"),self.guiSetModelData)
                    self.connect(self.editor,QtCore.SIGNAL("textChanged(QString)"),self.guiUpdateWidgetGeometry)
                    return self.editor
                else:
                    #Currently referring to a variable or parameters
                    type = typeDir[self.getType()]
                    
            self.editor = QtGui.QComboBox()    
            self.guiSetEditorData(self.editor,True,type)
            self.guiUpdateWidgetGeometryComboBox(self.editor.currentText())
            self.connect(self.editor,QtCore.SIGNAL("currentIndexChanged(QString)"),self.guiSetModelData)
            self.connect(self.editor,QtCore.SIGNAL("currentIndexChanged(QString)"),self.guiUpdateWidgetGeometryComboBox)
            
        elif self.pmtParent.xsdInfos.getAttribute(self.name).getPossibleValues():
            self.editor = QtGui.QComboBox()
            self.guiSetEditorData(self.editor,True)
            self.guiUpdateWidgetGeometryComboBox(self.editor.currentText())
            self.connect(self.editor,QtCore.SIGNAL("currentIndexChanged(QString)"),self.guiSetModelData)
            self.connect(self.editor,QtCore.SIGNAL("currentIndexChanged(QString)"),self.guiUpdateWidgetGeometryComboBox)
        elif self.pmtParent.xsdInfos.getAttribute(self.name).getType() == "boolean":
            self.editor = QtGui.QComboBox()
            self.editor.addItems(["true","false"])
            self.guiSetEditorData(self.editor,True)
            self.guiUpdateWidgetGeometryComboBox(self.editor.currentText())
            self.connect(self.editor,QtCore.SIGNAL("currentIndexChanged(QString)"),self.guiSetModelData)
            self.connect(self.editor,QtCore.SIGNAL("currentIndexChanged(QString)"),self.guiUpdateWidgetGeometryComboBox)
        else:
            self.editor = QtGui.QLineEdit()
            self.guiSetEditorData(self.editor)
            self.guiUpdateWidgetGeometry(self.editor.text())
            self.connect(self.editor,QtCore.SIGNAL("textEdited(QString)"),self.guiSetModelData)
            self.connect(self.editor,QtCore.SIGNAL("textChanged(QString)"),self.guiUpdateWidgetGeometry)
            
                
        return self.editor
    
    def guiSetEditorData(self,editorWidget,isComboBox = False,reference = None):
        '''
        @summary Sets an editor data(QLineEdit or QComboBox)
        @param editorWidget : the widget itself
        @param isComboBox : tells if the widget is a comboBox
        @param reference : tells if the attribute's value is a reference to a parameter
        '''
        if not isComboBox:
            editorWidget.setText(self.getValue())
            editorWidget.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("[^@#$%].+"),editorWidget))
            return
        if reference == "processes":
            procModel= BaseTreatmentsModel()
            treatments = list(procModel.getTreatmentsDict().keys())
            editorWidget.addItems(sorted(treatments,key=str.lower))
        elif reference == "allVariables":
            varModel = GeneratorBaseModel()
            envModel = BaseEnvModel()
            variables = varModel.getAllPossibleVars()
            variables.extend(envModel.getVars())
            editorWidget.addItems(sorted(variables,key=str.lower))
        elif reference == "envVariables":
            envModel = BaseEnvModel()
            editorWidget.addItems(sorted(envModel.getVars(),key=str.lower))
        elif reference == "indVariables":
            varModel = GeneratorBaseModel()
            variables = varModel.getAllPossibleVars()
            editorWidget.addItems(sorted(variables,key=str.lower))
        elif reference == "locVariables":
            locVarModel = BaseLocalVariablesModel()
            indexNode = self.pmtParent.pmtRoot.pmtDomTree.parentNode()
            editorWidget.addItems(sorted(locVarModel.getLocVarsList(indexNode),key=str.lower))
        elif reference == "allTypes":
            editorWidget.addItems(sorted(self.pmtParent.xsdInfos.getAttribute(self.name).getPossibleValues(),key=str.lower))
        elif reference == "atomTypes":
            editorWidget.addItems(sorted(self.pmtParent.xsdInfos.getAttribute(self.name).getPossibleValues(),key=str.lower))
        elif reference == "numericTypes":
            editorWidget.addItems(sorted(self.pmtParent.xsdInfos.getAttribute(self.name).getPossibleValues(),key=str.lower))
        elif reference =="allParameters":
            paramModel = BaseParametersModel()
            parameters = paramModel.getTruncatedRefList()
            editorWidget.addItems(sorted(parameters,key=str.lower))
            for parameter in sorted(parameters,key=str.lower):
                editorWidget.setItemData(sorted(parameters,key=str.lower).index(parameter), QtCore.QVariant(QtCore.QString(str(paramModel.getValue("ref."+parameter)))),QtCore.Qt.ToolTipRole)
            editorWidget.addItem("Add new parameter")
            self.connect(self.editor,QtCore.SIGNAL("activated(int)"),self.addNewParam)
            editorWidget.setCurrentIndex(editorWidget.findText(self.getValue()[4:]))
            editorWidget.view().setMinimumWidth(self.calculateListWidth())
            return
        else:
            #Reference is None, get value in possible Values
            editorWidget.addItems(sorted(self.pmtParent.xsdInfos.getAttribute(self.name).getPossibleValues(),key=str.lower))
        
        editorWidget.setCurrentIndex(editorWidget.findText(self.getValue()))
        editorWidget.view().setMinimumWidth(self.calculateListWidth())
        
    def guiSetModelData(self,text):
        '''
        @summary Update data when this attribute's editor data is modified
        @param text : new value
        '''
        prefixDir = {'Environment variables':'#','Individual variables':'@','Local Variables':'%','Parameters':'$','Value':''}
        if self.choiceMenu:
            if self.getType() == "param":
                if str(text) == "Add new parameter":
                    return
                
                self.value=prefixDir[str(self.choiceMenu.checkedAction().text())]+"ref."+str(text)
            else:
                self.value=prefixDir[str(self.choiceMenu.checkedAction().text())]+str(text)
        else:
            self.value = str(text)
            
        for child in self.pmtParent.childrenList:
            self.pmtParent._lookForBranchTag(child)
        
        self.pmtParent._check(False)
        if self.pmtParent.pmtParent:
            #Changing an attribute might cause parent of parent primitive to change status
            self.pmtParent.pmtParent._check(False)
            
        self.pmtParent.topWObject.updateDirtyState()
        if self.pmtParent.xsdInfos.isPaired(self.name) and self.pmtParent.name == "Data_Value":
            #Might have became a bool or was a bool and became something else, reload just to make sure
            self.pmtParent.topWObject.updateProperties()       
        
    def guiCreatePropertyLabel(self):
        '''
        @summary Create attribute name's label
        '''
        propertyLabel = QtGui.QLabel()
        propertyLabel.setText(self.getMappedName())
        propertyLabel.setFixedWidth(self.calculateTextWidth(propertyLabel.text(), propertyLabel.font()))
        if self.pmtParent.xsdInfos.getAttribute(self.name).getAttributeInfo():
            propertyLabel.setToolTip(self.pmtParent.xsdInfos.getAttribute(self.name).getAttributeInfo())
        return propertyLabel
    
    def guiUpdateWidgetGeometry(self,newText):
        '''
        @summary Update self.editor geometry
        @param newText : text found in editor
        '''
        self.editor.setMinimumWidth(1)
        self.editor.setMaximumWidth(self.calculateTextWidth(newText, self.editor.font())+15)
        
    def guiUpdateWidgetGeometryComboBox(self,newText):
        '''
        @summary Like guiUpdateWidgetGeometry but for a combo box
        '''
        self.editor.setMinimumWidth(1)
        self.editor.setMaximumWidth(self.calculateTextWidth(newText, self.editor.font())+30)
    
    def calculateListWidth(self):
        '''
        @summary Calculate pixel width of largest item in drop-down list 
        '''
        fm = QtGui.QFontMetrics(self.editor.view().font())
        minimumWidth = 0
        for i in range(0,self.editor.count()):
            if fm.width(self.editor.itemText(i)) > minimumWidth:
                minimumWidth = fm.width(self.editor.itemText(i))
        return minimumWidth+10
    
    def calculateTextWidth(self,text,font):
        '''
        @summary Compute and return the pixel width used by a given string
        @param text : string we want the width of
        @param font : text's font
        '''
        fontMetrics = QtGui.QFontMetrics(font)
        return fontMetrics.width(text)
    
    def addNewParam(self,index):
        '''
        @summary Add parameter on the fly when in a comboBox listing parameters
        @param index : index of the clicked item
        '''
        if index == self.editor.count()-1:
            reponse,valid = QtGui.QInputDialog.getText(self.pmtParent.topWObject, "Enter New Parameter Name", "Param Name : ")
            if valid:
                baseParamModel = BaseParametersModel()
                baseParamModel.addRef("ref."+str(reponse), "Double")
                self.value = str('$ref.'+reponse)
                insertIndex = sorted(baseParamModel.getTruncatedRefList()).index(str(reponse))
                self.editor.insertItem(insertIndex,reponse)
            self.editor.setCurrentIndex(self.editor.findText(self.getValue()[4:]))
        
    def modifyEditor(self):
        '''
        @summary Slot called when a Token type attribute is modified
        Allows this attribute to correctly update its editor
        '''
        widgetToGetRidOf = self.layout.takeAt(self.layout.count()-1)
        self.disconnect(self.pmtParent.getAttributeByName("type").editor,QtCore.SIGNAL("currentIndexChanged(QString)"),self.modifyEditor)
        self.editor = None
        self.layout.addWidget(self.guiCreateEditor())
        widgetToGetRidOf.widget().deleteLater()
    
    def modifyList(self,checkStatus):
        '''
        @summary Slot called when an attribute's source changes
        @param checkStatus : unused
        '''
        sources = {'Environment variables':'#','Individual variables':'@','Local Variables':'%','Parameters':'$'}    
        if str(self.sender().text()) == 'Value':
            self.value = ""
            if self.pmtParent.xsdInfos.getAttribute(self.name).getPairedAttr():
                #Paired attribute found, show it
                self.pmtParent.addAttributeByName(self.pmtParent.xsdInfos.getAttribute(self.name).getPairedAttr())  
        else:
            self.value =  sources[str(self.sender().text())]
            if self.pmtParent.xsdInfos.getAttribute(self.name).getPairedAttr():
                #Paired attribute found in xsd
                if self.pmtParent.hasAttribute(self.pmtParent.xsdInfos.getAttribute(self.name).getPairedAttr()):
                    #Paired attribute found, delete it
                    self.pmtParent.deleteAttribute(self.pmtParent.xsdInfos.getAttribute(self.name).getPairedAttr())
                
        self.pmtParent.topWObject.updateProperties()
    
    def remove(self):
        '''
        @summary Slot called when an unpaired optional attribute is removed from the GUI by user
        '''
        self.pmtParent.deleteAttribute(self.getName())
        self.pmtParent.topWObject.updateProperties()
        
    def checkSetChoice(self):
        '''
        @summary Look and set(if needed) choice ComboBox 
        '''
        guiTypes = {'envVar':'Environment variables','indVar':'Individual variables','locVar':'Local Variables','param':'Parameters','value':''}
        labels = {'envVariables':'Environment variables','indVariables':'Individual variables','locVariables':'Local Variables','allParameters':'Parameters'}
        if len(self.pmtParent.xsdInfos.getAttribute(self.name).getBehavior().getList()) > 1:
            pushButtonChoice = QtGui.QPushButton()
            pushButtonMenu = QtGui.QMenu()
            pushButtonActionGroup = QtGui.QActionGroup(pushButtonMenu) #to be sure checkable buttons are mutually exclusive
            for source in sorted([labels[sources["type"]] for sources in self.pmtParent.xsdInfos.getAttribute(self.name).getBehavior().getList()]):  
                newAction = pushButtonMenu.addAction(source)
                newAction.setCheckable(True)
                self.connect(newAction,QtCore.SIGNAL("triggered(bool)"),self.modifyList)
                pushButtonActionGroup.addAction(newAction)
                if guiTypes[self.getType()] == source:
                    newAction.setChecked(True) 
            if len(self.pmtParent.xsdInfos.getAttribute(self.name).getBehavior().getList()) == 4:
                #for the moment, if 4 items are found in the list, then attribute can be a value 
                newAction = pushButtonMenu.addAction("Value")
                newAction.setCheckable(True)
                self.connect(newAction,QtCore.SIGNAL("triggered(bool)"),self.modifyList)
                pushButtonActionGroup.addAction(newAction)
                if self.getType() == "value":
                    newAction.setChecked(True)    
            pushButtonChoice.setFixedWidth(20)
            pushButtonChoice.setMenu(pushButtonMenu)
            self.layout.addWidget(pushButtonChoice)
            self.choiceMenu = pushButtonActionGroup
            if not self.choiceMenu.checkedAction():
                #No action has not been set, probably a new attribute without the value option
                #Check first available option and set value consequently
                self.choiceMenu.actions()[0].setChecked(True)
                self.value = [key for key,value in self.typeDir.iteritems() if value == [k for k,v in guiTypes.iteritems() if v== str(self.choiceMenu.checkedAction().text())][0]][0]
        else:
            self.choiceMenu = None
            
    def _check(self):
        '''
        @summary : look for errors in attribute
        '''
        attrInfos = self.pmtParent.xsdInfos.getAttribute(self.name)
        if not self.getValue():
            self.pmtParent.addValidityEvent( PrimitiveValidityEvent(self.pmtParent, "EmptyAttributeValue", [self.getMappedName()]))
            return True
        if attrInfos.isObjectNull():
            self.pmtParent.addValidityEvent( PrimitiveValidityEvent(self.pmtParent, "BadAttribute", [self.getMappedName(), self.getValue()]))
            return True
        
        #Get expected type from XSD
        attrType = attrInfos.getType()
        
        #First, check if attribute has a defined GUI type
        if attrInfos.getGuiType():
                if self.getType() == "envVar":
                    envModel = BaseEnvModel()
                    if not envModel.variableExists(self.getValue()):
                        self.pmtParent.validityEventsList.append(PrimitiveValidityEvent(self.pmtParent,"UnknownVariable",[self.getValue(),self.pmtParent.name]))
                        return True
                    if not envModel.getVarType(self.getValue()) == attrInfos.getGuiType():
                        self.pmtParent.addValidityEvent( PrimitiveValidityEvent(self.pmtParent, "BadAttributeValue", [attrInfos.getGuiType(), envModel.getVarType(self.getValue()), self.getMappedName()]))
                        return True
                    return False
                elif self.getType() == "indVar":
                    varModel = GeneratorBaseModel()
                    if not varModel.variableExistsIgnoringSupPop(self.getValue()):
                        self.pmtParent.validityEventsList.append(PrimitiveValidityEvent(self.pmtParent,"UnknownVariable",[self.getValue(),self.pmtParent.name]))
                        return True
                    if not varModel.getVarTypeIgnoringSubPop(self.getValue()) == attrInfos.getGuiType():
                        self.pmtParent.addValidityEvent( PrimitiveValidityEvent(self.pmtParent, "BadAttributeValue", [attrInfos.getGuiType(), varModel.getVarTypeIgnoringSubPop(self.getValue()), self.getMappedName()]))
                        return True
                    return False
                elif self.getType() == "param":
                    paramModel = BaseParametersModel()
                    if not self.getValue() in paramModel.getRefList():
                        self.pmtParent.validityEventsList.append(PrimitiveValidityEvent(self.pmtParent,"UnknownParameter",[self.getValue()[4:],self.pmtParent.name]))
                        return True
                    if not paramModel.getRefType(self.getValue()) == attrInfos.getGuiType():
                        self.pmtParent.addValidityEvent( PrimitiveValidityEvent(self.pmtParent, "BadAttributeValue", [attrInfos.getGuiType(), paramModel.getRefType(self.getValue()), self.getMappedName()]))
                        return True
                    return False
                elif self.getType() == "locVar":
                    locVarModel = BaseLocalVariablesModel()
                    indexNode = self.pmtParent.pmtRoot.pmtDomTree.parentNode()
                    if self.getValue() not in locVarModel.getLocVarsList(indexNode):
                        self.pmtParent.validityEventsList.append(PrimitiveValidityEvent(self.pmtParent,"UnknownVariable",[self.getValue(),self.pmtParent.name]))
                        return True
                    if not locVarModel.getLocalVarType(indexNode, self.getValue()) == attrInfos.getGuiType():
                        self.pmtParent.addValidityEvent( PrimitiveValidityEvent(self.pmtParent, "BadAttributeValue", [attrInfos.getGuiType(), locVarModel.getLocalVarType(indexNode, self.getValue()), self.getMappedName()]))
                        return True
                    return False
                elif self.getType() == "value":
                    #Attribute is in a line edit
                    #Convert type and check as xsd type 
                    convTable = {"Double":"double","Float":"float","Int":"integer","Long":"long","ULong":"unsignedLong","UInt":"unsignedInt","Bool":"boolean","String":"string"}
                    attrType = convTable[attrInfos.getGuiType()]
        
        #if self.getType() == "value":
        if attrType == "double" or attrType == "float":
            try:
                float(self.value)
            except ValueError:
                self.pmtParent.addValidityEvent( PrimitiveValidityEvent(self.pmtParent, "BadAttributeValue", [attrType, str(self.value), self.getMappedName()]))
                return True

        elif attrType == "integer":
            try:
                int(self.value)
            except ValueError:
                self.pmtParent.addValidityEvent( PrimitiveValidityEvent(self.pmtParent, "BadAttributeValue", [attrType, str(self.value), self.getMappedName()]))
                return True
            if int(self.value) > 2147483647 or int(self.value) < -2147483648:
                self.pmtParent.addValidityEvent( PrimitiveValidityEvent(self.pmtParent, "OutOfBoundAttributeValue", [attrType, str(self.value), self.getMappedName()]))
                return True

        elif attrType == "boolean":
            if not self.value in ["True","False","false","true","TRUE","FALSE"]:
                self.pmtParent.addValidityEvent( PrimitiveValidityEvent(self.pmtParent, "BadAttributeValue", [attrType, str(self.value), self.getMappedName()]))
                return True

        elif attrType == "unsignedInt":
            try:
                int(self.value)
            except ValueError:
                self.pmtParent.addValidityEvent( PrimitiveValidityEvent(self.pmtParent, "BadAttributeValue", [attrType, str(self.value), self.getMappedName()]))
                return True
            if int(self.value) > 4294967295 or int(self.value) < 0 :
                self.pmtParent.addValidityEvent( PrimitiveValidityEvent(self.pmtParent, "OutOfBoundAttributeValue", [attrType, str(self.value), self.getMappedName()]))
                return True

        elif attrType == "long":
            try:
                long(self.value)
            except ValueError:
                self.pmtParent.addValidityEvent( PrimitiveValidityEvent(self.pmtParent, "BadAttributeValue", [attrType, str(self.value), self.getMappedName()]))
                return True

        elif attrType == "unsignedLong":
            try:
                long(self.value)
            except ValueError:
                self.pmtParent.addValidityEvent( PrimitiveValidityEvent(self.pmtParent, "BadAttributeValue", [attrType, str(self.value), self.getMappedName()]))
                return True
            if long(self.value) < 0:
                self.pmtParent.addValidityEvent(PrimitiveValidityEvent(self.pmtParent, "OutOfBoundAttributeValue", [attrType, str(self.value), self.getMappedName()]))
                return True

        elif attrType != "string":
            #Unknown attribute type
            self.pmtParent.addValidityEvent( PrimitiveValidityEvent(self.pmtParent, "BadAttributeType", [self.getMappedName(), attrType]))
            return True
        
        else:
            #Clearly defined by xsd:string
            #It might be a listing property with either local variables or individual variables
            #If so make sure the variables exist
            if self.getType() == "indVar":
                varModel = GeneratorBaseModel()
                if not varModel.variableExistsIgnoringSupPop(self.getValue()):
                    self.pmtParent.validityEventsList.append(PrimitiveValidityEvent(self.pmtParent,"UnknownVariable",[self.getValue(),self.pmtParent.name]))
                    return True
            if self.getType() == "locVar":
                locVarModel = BaseLocalVariablesModel()
                indexNode = self.pmtParent.pmtRoot.pmtDomTree.parentNode()
                if self.getValue() not in locVarModel.getLocVarsList(indexNode):
                    self.pmtParent.validityEventsList.append(PrimitiveValidityEvent(self.pmtParent,"UnknownVariable",[self.getValue(),self.pmtParent.name]))
                    return True
            if self.getType() == "value":
                #Might be processes being listed
                if self.pmtParent.xsdInfos.getAttribute(self.name).getBehavior().getList():
                    if len(self.pmtParent.xsdInfos.getAttribute(self.name).getBehavior().getList()) <= 1:
                        if "processes" == self.pmtParent.xsdInfos.getAttribute(self.name).getBehavior().getList()[0]["type"]:
                            #Make sure process exists
                            baseModelTr = BaseTreatmentsModel()
                            if self.getValue() not in baseModelTr.getTreatmentsDict().keys():
                                self.pmtParent.validityEventsList.append(PrimitiveValidityEvent(self.pmtParent,"UnknownProcess",[self.getValue(),self.pmtParent.guiGetName()]))
                                return True
        return False
   
class Primitive(QtCore.QObject):
    '''
    This class represents a primitive
    A primitive may contain primitive children and attributes
    This class is just a wrapper over the simulator XML code, and is used to make a bridge between the xml code and the user's perspective of a tree node
    '''
    
    def __init__(self, parentPrimitive, rootPrimitive, topWindowObject, XMLTree, autoMissingItemsFill=True, displayComments = True,name = "Control_Nothing"): 
        """
        summary Constructor
        @param parentPrimitive : the primitive parent of this primitive (null primitive if there's none)
        @param rootPrimitive : the primitive root of the tree this primitive belongs to (null primitive if this is the root)
        @param topWindowObject : MainFrame pointer
        @param primitivePos : the position of this primitive in its parent's children list
        @param XMLTree : a QDomNode() representing this primitive
        @param autoMissingItemsFill : boolean. If set to true, Primitive object will try to fill missing required children or attributes
        @param displayComments : boolean. If set to true, Primitive object will parse XML comments and give users access to them
        """
        QtCore.QObject.__init__(self)
        
        self.pmtRoot = rootPrimitive
        self.topWObject = topWindowObject
        self.pmtDomTree = XMLTree
        self.autoMissingItemsFill = autoMissingItemsFill
        self.displayComments = displayComments
        
        self.assocDict = PrimitiveDict()
        self.pmtParent = parentPrimitive
        self.name = name

        self.validityEventsList = []

        if not XMLTree.isNull():
            self._parseName()
       
        self.xsdInfos = self.assocDict.getPrimitiveInfo(self.name)
        if self.xsdInfos.isObjectNull():
            print("Warning : no information about primitive '" + str(self.name) + "'")
            self.autoMissingItemsFill = False   # We cannot display missing childs if we don't know the childs...
        
        self.childrenList = [] #Primitive children list
        self.attrList = {} #Primitive Attribute List
        self.userComment = QtCore.QString() #Xml node's first argument
        self.defaultComment = QtCore.QString() #Xml node's next sibling argument
        self.guiInfos = {}
        self.guiInfos["Highlighted"] = False
        
        if self.pmtParent == None:
            self.isRootPmt = True
            self.pmtRoot = self
        else:
            self.isRootPmt = False
        
        self.worstEvent = "Unknown"
        self.isNull = False
        
        
        self._parseAttributes()
        self._parseChilds()
        self._check(False)
    
    '''
    Section : GUI
    Purpose : to respect modularity, all information requested by the treeEditor must call a gui"Function"
    '''
    
    def guiGetChild(self, childPos):
        '''
        @summary Return child at given position as seen in GUI
        @param childPos : child's position in GUI
        '''
        assert childPos < self.countChildren(), "Error in PrimitiveBaseModel::guiGetChild() : invalid childPos " + str(childPos) + ", length of childs list is " + str(self.guicountChildren())

        return self.childrenList[childPos]
    
    def guiGetName(self):
        '''
        @summary Return primitive's name as seen in GUI
        '''
        if self.xsdInfos.isObjectNull():
            return self.name
        else:
            if self.xsdInfos.getMappedName() == "":
                return self.name
            else:
                return self.xsdInfos.getMappedName()
      
    def guiGetDefinition(self):
        '''
        @summary Return primitive's definition
        '''
        return self.xsdInfos.getDocStr()
    
    def guiCanDeleteChild(self):
        '''
        @summary Return if this primitive has enough children to see one being deleted
        '''
        return self.countChildren() > self.xsdInfos.getMinimumNumChilds()
    
    def guiGetAttrDisplay(self):
        '''
        @summary Return Attribute information that is going to be displayed in the tree
        '''
        for attribute in self.nextAttribute():
            success,behavior = self.xsdInfos.getAttribute(attribute.getName()).getBehavior().getBehavior("displayValue")
            if success:
                if behavior:
                    if behavior["showAttr"]:
                        return attribute.getValue()+" "+behavior["delimiter"]+" "+self.getAttributeByName(behavior["showAttr"]).getValue(), behavior["position"]
                value = attribute.getValue()
                if attribute.getType() == "param":
                    value = attribute.getValue()[4:]    
                return value,behavior["position"]
        return ""
    
    def guiGetBranchInfo(self):
        '''
        @summary Return primitive's branch information
        '''
        if not self.getParentPrimitive().xsdInfos.isNull and not self.getParentPrimitive().xsdInfos.getSimpleOrderedChild(self.getParentPrimitive().getChildPos(self)).isNull:   
            return QtCore.QString(self.getParentPrimitive().xsdInfos.getSimpleOrderedChild(self.getParentPrimitive().getChildPos(self)).toChoice().getItemBranchTag())
            
        return QtCore.QString()
    
    def guiGetBranchTag(self):
        '''
        @summary Return primitive's branch tag
        '''
        if "branchTag" in self.guiInfos.keys():
            return self.guiInfos["branchTag"]
        return []
    
    def guiSetBranchTag(self,newValue):
        '''
        @summary Sets primitive's attribute value associated with branchTag
        @param newValue : primitive's new value
        '''
        if "branchTag" not in self.guiInfos.keys():
            self.guiInfos["branchTag"] = [True,True,0]
        self.guiInfos["branchTag"][2]=newValue
        self.getParentPrimitive()._updateAttribute(self.getParentPrimitive().guiInfos["attrBranchMapped"])
        return
    
    def guiGetChoicesList(self,childPos):
        '''
        @summary Get Valid Primitives for a child
        @param childPos : child's position
        '''
        childInfo = self.xsdInfos.getSimpleOrderedChild(childPos)
        return childInfo.toChoice().getChoicesNamesList()
                
    def guiDeleteChild(self,childPmt):
        '''
        @summary Delete child
        @param childPmt : child's Primitive instance
        '''
        self.detachChild(self.getChildPos(childPmt))
        
    def guiGetChildPos(self,childPmt):
        '''
        Return child position in GUI
        @param childPmt : child's Primitive instance
        '''
        if childPmt in self.childrenList:
                return self.childrenList.index(childPmt)
        print("Warning: in Primitive::guiGetChildPos, childPmt not in childrenList")
    
    def guiCanHaveBranchTag(self,pmtChild):
        '''
        @summary Return if child can have a branch tag
        @param pmtChild : child's Primitive instance
        '''
        for attrib in self.xsdInfos.getNextAttribute():
            if self.hasAttribute(attrib.getName()):
                success, branchBehavior = attrib.getBehavior().getBehavior("mapToBranches")
                if success:
                    childPos = self.guiGetChildPos(pmtChild)
                    if branchBehavior["startIndex"] <=  childPos:
                        if branchBehavior["endIndex"] >= childPos or branchBehavior["endIndex"] == -1:
                            return True

        return False

    def guiCreateEditor(self, parentObject):
        '''
        @summary creates the tab of the UserComment, and the tab of the definition if definition isn't empty
        @param parentObject : widget where the information is going to be shown
        '''
        userCommentWidget = QtGui.QTextBrowser()
        userCommentWidget.setReadOnly(False)
        self.guiSetEditorData(userCommentWidget,"Comment")
        parentObject.addTab(userCommentWidget,QtCore.QString("User Comment"))
        self.connect(userCommentWidget,QtCore.SIGNAL("textChanged()"),self.guiSetComment)
        if not QtCore.QString(self.xsdInfos.getDocStr()).isEmpty():
            definitionWidget = QtGui.QTextBrowser()
            definitionWidget.setReadOnly(True)
            self.guiSetEditorData(definitionWidget,"Definition")
            parentObject.addTab(definitionWidget,"Definition")
        
        return userCommentWidget
    
    def guiSetEditorData(self, editorWidget,option):
        '''
        @summary Populate create editor
        @param editorWidget : the editor
        @param option : Definition or Comment
        '''
        if option == "Comment":
            editorWidget.setPlainText(self.userComment)
        elif option == "Definition":
            editorWidget.setPlainText(self.xsdInfos.getDocStr())
        return
    
    def guiSetModelData(self,newPmtName,guiPosition):
        '''
        Replace a child in model based on primitive name
        @param newPmtName : name of the newly added Primitive
        @param guiPosition : position of the replaced child in gui
        '''
        self.replaceChild(newPmtName, guiPosition)
        return
    
    def guiReplaceModelData(self,guiPosition,xmlNode = QtXml.QDomNode()):
        '''
        Replace a child in model based on a primitive xml node
        @param guiPosition : position of the replaced child in gui
        @param xmlNode : primitive's xml node
        '''
        newPmt = Primitive(self, self.pmtRoot, self.topWObject, xmlNode,False)
        self.childrenList[guiPosition] = newPmt
        self._lookForBranchTag(newPmt)
        self._check(False)
        
    def guiAddChild(self,newPmtName,guiPosition,behaviorWanted = "skip"):
        '''
        @summary Adds a child to model
        @param newPmtName : child's primitive name
        @param guiPosition : position in gui
        @param behaviorWanted : behavior of the add function
        '''
        if guiPosition >= len(self.childrenList):
            self.addChild(newPmtName,self.countChildren(),behaviorWanted)        
        else:
            self.addChild(newPmtName,guiPosition,behaviorWanted)
    
    def guiGetAttrLayout(self):
        '''
        @summary Construct Layout that is going to be used by the tree editor to display attribute information
        @return QtGui.QVBoxLayout : layout to be used in tree editor
        '''
        layout = QtGui.QVBoxLayout()
        self.optAttrComboBox = QtGui.QComboBox()
        for attribute in self.nextAttribute():
            layout.addLayout(attribute.getLayout())
        
        for attrib in self.xsdInfos.getNextAttribute():
            if not self.hasAttribute(attrib.getName()) and attrib.isOptionnal() and not self.xsdInfos.isPaired(attrib.getName()):
                #Attribute is unpaired and optional, give user's possibility to add this attribute
                self.optAttrComboBox.addItem(attrib.getMappedName())
        #Assign layout
        layout.setAlignment(QtCore.Qt.AlignTop)
        self.layout = layout
        #Look if optional attribute were added in combobox. If so, add comboBox to layout
        if self.optAttrComboBox.count():
            optAttrLayout = self.getOptAttrLayout()
            self.layout.addStretch()
            self.layout.addLayout(optAttrLayout)
           
        return self.layout
    
    def getOptAttrLayout(self):
        '''
        @summary Create layout for optional attributes, like it is done in the attribute class
        @return QtGui.QHBoxLayout, layout to be used in tree editor
        '''
        #Create Layout
        optAttrLayout = QtGui.QHBoxLayout()
        optAttrLayout.setAlignment(QtCore.Qt.AlignLeft)
        #Create Label
        optAttrLabel = QtGui.QLabel("Optional attributes :")
        optAttrLayout.addWidget(QtGui.QLabel("Optional attributes :"))
        #Calculate pixel size of text
        fontMetrics = QtGui.QFontMetrics(optAttrLabel.font())
        optAttrLabel.setFixedWidth(fontMetrics.width(optAttrLabel.text()))
        #Add ComboBox 
        optAttrLayout.addWidget(self.optAttrComboBox)
        #Create push button to add optional attributes
        addButton = QtGui.QPushButton("+")
        addButton.setFixedWidth(25)
        optAttrLayout.addWidget(addButton)
        #Calculate list width for the combobox, required by Windows to correctly display drop-down list
        fm = QtGui.QFontMetrics(self.optAttrComboBox.view().font())
        minimumWidth = 0
        for i in range(0,self.optAttrComboBox.count()):
            if fm.width(self.optAttrComboBox.itemText(i)) > minimumWidth:
                minimumWidth = fm.width(self.optAttrComboBox.itemText(i))
        self.optAttrComboBox.view().setMinimumWidth(minimumWidth)
        #Calculate width for the combobox itself
        self.optAttrComboBox.setMinimumWidth(1)
        fontMetrics = QtGui.QFontMetrics(self.optAttrComboBox.font())
        self.optAttrComboBox.setMaximumWidth(fontMetrics.width(self.optAttrComboBox.currentText())+30)
        self.connect(addButton,QtCore.SIGNAL("pressed()"),self.addAttributeByWidget)
        
        return optAttrLayout
    
    def guiGetComment(self):
        '''
        @summary Return user comment
        '''
        return self.userComment 
    
    def guiSetComment(self):
        '''
        @summary Modify user comment
        '''
        newComment = self.sender().document().toPlainText()
        self.userComment = newComment

    def guiDumpModelInfos(self):
        '''
        @summary Useful debug function
        '''
        print("Dumping Info for primitive named "+self.name)
        print("Primtives's error list : " + str(self.guiGetEvents()))
        print("Primitive's return Type is "+self._getReturnType())
        print("Will dump info for children")
        for child in self.childrenList:
            childXSDInfo = self.xsdInfos.getSimpleOrderedChild(self.getChildPos(child)).toChoice()
            print("\t\t Was expecting a return Value of Type "+childXSDInfo.getAcceptedType()[0]+" defined by "+childXSDInfo.getAcceptedType()[1])
            print("\tChild "+child.name+" has a return Type of "+child._getReturnType())
        print ("Attributes are : "+str(self.attrList.keys()))
        print("Supposed Attributes are :")
        for child in self.xsdInfos.getNextAttribute():
            print(child.name)
        print("Branch Tag Info:")
        if "branchTag" in self.guiInfos:
            print(self.guiInfos["branchTag"])
        
    def guiGetEvents(self):
        '''
        @summary Return list of event for primitive
        '''
        return self.validityEventsList
        
    def guiDoubleClickBehavior(self):
        '''
        @summary Return if primitive has special behavior triggered by a double click
        '''
        return self.xsdInfos.getPrimitiveBehavior().hasBehavior("openOnDoubleClick")
    
    def guiIsHighlighted(self):
        '''
        @summary Return if primitive has to be highlighted, for whatever reason
        '''
        return self.guiInfos["Highlighted"]
    
    def guiSetHighlighted(self,highlight):
        '''
        @summary Set Highlight status
        @param highlight : boolean, new highlight status
        '''
        self.guiInfos["Highlighted"] = highlight
    
    '''
    /Section: Gui
    '''
    
    def getParentPrimitive(self):
        '''
        @summary return parent primitive
        '''
        return self.pmtParent
    
    def isNull(self):
        '''
        @summary Return if primitive isn't yet defined
        '''
        return self.isNull   
    
    def getTreeSize(self):
        '''
        @summary return tree's depth
        '''
        currentCount = 1    #we have to count this primitive
        for child in self.childrenList:
            currentCount += child.getTreeSize()    
        return currentCount
    
    def addAttribute(self, newAttr, eraseIfPresent = True):
        '''
        @summary Add attribute
        @param newAttr : PrimitiveAttribute to add
        @param eraseIfPresent : delete primitive or not if present
        '''
        if not str(newAttr.getName()) in self.attrList.keys() or eraseIfPresent:
            self.attrList[newAttr.getName()] = newAttr
        else:
            print("Warning : unable to insert new attribute " + str(newAttr.getAttrName()) + " : already present")

    def addAttributeByName(self, newAttrName, newAttrValue="", eraseIfPresent = True):
        '''
        @summary Add attribute
        @param newAttrName : Attribute's name
        @param newAttrValue : Attribute's value
        @param eraseIfPresent : delete primitive or not if present
        '''
        self.addAttribute(PrimitiveAttribute(newAttrName, newAttrValue, self), eraseIfPresent)

    def addAttributeByWidget(self):
        '''
        @summary Function called when a button is pressed in the GUI
        Tells the model to add an attribute. Attribute's mapped name can be found in optional attribute combobox 
        '''
        for attrib in self.xsdInfos.getNextAttribute():
            if attrib.getMappedName() == str(self.optAttrComboBox.currentText()):
                self.addAttributeByName(attrib.getName())
        self.topWObject.updateProperties()
        
    def countAttributes(self):
        '''
        @summary Return number of attributes
        '''
        return len(self.attrList)
    
    def deleteAttribute(self,attrName):
        '''
        @summary Remove Attribute from attribute list
        @param attrName : attribute's name
        '''
        if self.xsdInfos.getAttribute(attrName).isOptionnal():
            self.attrList.pop(attrName)
        else:
            print("Error : Primitive::deleteAttribute, cannot delete required attribute named "+attrName)
    
    def getAttributeByPos(self,pos):
        '''
        @summary Return attribute at given position
        @attrName attribute's position
        '''
        if pos >= len(self.attrList):
            print("Warning : no such attribute at position " + str(pos)+" for primitive "+str(self.name))
            return PrimitiveAttribute()
        else:
            return self.attrList[[key for key in self.attrList.keys()][pos]]
        
    def getAttributeByName(self,attrName):
        '''
        @summary Return attribute
        @attrName attribute's name
        '''
        if attrName in self.attrList.keys():
            return self.attrList[attrName]
        
        return None
    
    def getOptionalAttributes(self):
        '''
        @summary Return a list of optional attributes not currently part of this primitive
        '''
        optionalAttrList = []
        for attrib in self.xsdInfos.getNextAttribute():
            #if attrib.getName() not in self.attrList and not attrib.isOptionnal():
            if attrib.getName() not in self.attrList and attrib.isOptionnal():
                optionalAttrList.append(attrib.getName())
        return optionalAttrList
    
    def hasAttribute(self,attrName):
        '''
        @summary Return is this primitive has a given attribute
        @summary attrName : name of the attribute we are looking for
        '''
        return True if attrName in self.attrList.keys() else False
    
    def nextAttribute(self):
        '''
        @summary Primitive's attribute generator
        '''
        for attr in sorted(self.attrList.keys()):
            yield self.attrList[attr]

    def getComment(self):
        '''
        @summary Return default comment
        '''
        return self.defaultComment
    
    def getUserComment(self):
        '''
        @summary Return user comment
        '''
        return self.userComment
    
    def hasDefaultComment(self):
        '''
        @summary Return is this primitive has a default comment
        '''
        return not self.defaultComment.isEmpty()
    
    def hasUserComment(self):
        '''
        @summary Return is this primitive has a user comment
        '''
        return not self.userComment.isEmpty()
    
    def addChild(self, childName, childPos,behaviorIfPosAlreadyUsed = "skip"): # shift, erase, skip
        '''
        @summary Adds a child
        @param childName : child's name
        @param childPos : child's position
        @param behaviorIfPosAlreadyUsed : shift, erase or skip
        '''
        if childPos > len(self.childrenList):
            print("Warning in Primitive::addChild() : try to add a child at position " + str(childPos) + " on a primitive with " + str(len(self.childrenList)) + " childs. Primitive will be added as last child.")
            childPos = len(self.childrenList)
        if behaviorIfPosAlreadyUsed == "skip" and childPos == len(self.childrenList):
            childPos-=1
            
        #Construct new Child
        newChildNode = QtXml.QDomNode()
        newPmt = Primitive(self, self.pmtRoot, self.topWObject, newChildNode , True, self.displayComments,childName)
        
        if str(behaviorIfPosAlreadyUsed) == "shift": 
            self.childrenList.insert(childPos,newPmt)
        elif str(behaviorIfPosAlreadyUsed) == "erase":
            self.childrenList[childPos] = newPmt    
        elif str(behaviorIfPosAlreadyUsed) == "skip":
            self.childrenList.insert(childPos+1,newPmt)
        else:
            print("Warning : unexpected behavior '"+str(behaviorIfPosAlreadyUsed)+"' in Primitive::addChild(), possible values are 'shift', 'skip' and 'erase'")

        for primitiveData in self.childrenList[self.getChildPos(newPmt):]:
                self._lookForBranchTag(primitiveData)


        if newPmt.autoMissingItemsFill:
            newPmt._lookForMissingChildren()
        
        
        self._check(False)
    
    def canThisChildBeAdded(self, childName, childPos):
        '''
        @summary Ask if a child is a valid primitive before adding it
        @param childName : eventual child name
        @param childPos : eventual child position
        '''
        if self.xsdInfos.isObjectNull():
            print("Warning : cannot determine if '"+str(childName)+"' can be added as child of '"+self.name+"' : no information about this primitive")
            return True
        else:
            if childName in self.xsdInfos.getChildsInfos():
                return True
            return False 
    
    def countChildren(self):
        '''
        @summary Return number of child
        '''
        return len(self.childrenList)
    
    def detachChild(self, childPos):
        '''
        @summary Remove a child from the tree
        @param childPos : child's position in tree
        '''
        if childPos >= len(self.childrenList):
            print("Warning : calling detachChild at position " + str(childPos) + " without any child already present")
            return
        else:
            item = self.childrenList.pop(childPos)                
            for primitiveData in self.childrenList:
                self._lookForBranchTag(primitiveData)
    
    def getChild(self,childPos):
        '''
        @summary Return child at given position
        @param childPos : child's position
        '''
        return self.childrenList[childPos]
    
    def getChildPos(self,childPmt):
        '''
        @summary Return child position
        @param childPmt : child's primitive
        '''
        if childPmt in self.childrenList:
            return self.childrenList.index(childPmt)
            
        print("Warning: in Primitive::getChildPos, childPmt not in childrenList")  
    
    def replaceChild(self, childName, childPos):
        '''
        @summary Replace an already existing child by a new one
        @param childName : new child name
        @param childPos : new child position
        '''
        if childPos >= len(self.childrenList):
            print("Warning : calling replaceChild at position " + str(childPos) + " without any child already present")
        else:
            self.addChild(childName, childPos, "erase")
    
    def addValidityEvent(self, eventObject):
        '''
        @summary Adds a new event for this primitive
        '''
        self.validityEventsList.append(eventObject)
        return

    def getValidityList(self):
        '''
        @summary Return simplified list of event for primitive
        '''
        eventList = [events.getGravity() for events in self.validityEventsList if events.isValid()]
        return eventList if len(eventList) != 0 else ["Valid"]
    
    def getValidityState(self):
        '''
        @summary Return worst event this primitive hold
        '''
        eventDict = {"Unknown" : 0,
                     "Valid" : 1,
                     "Warning" : 2,
                     "Error":3}
        
        currentWorstEvent = "Unknown"
        for event in self.getValidityList():
            if eventDict[event] > eventDict[currentWorstEvent]:
                currentWorstEvent = event
     
        return currentWorstEvent
    
    def propagateHighlighting(self,similarPrimitive):
        '''
        @summary Look if given primitive is similar and set highlight status to True if it is
        Propagate comparison to child primitives
        Two primitive are similar if comparison primitive have the same name, attributes and attribute values for attributes whose values are defined
        '''
        if similarPrimitive.name == self.name:
            self.guiSetHighlighted(True)
            for attribute in similarPrimitive.nextAttribute():
                if self.hasAttribute(attribute.getName()):
                    if attribute.value:
                        if attribute.value == self.getAttributeByName(attribute.getName()).value:
                            continue
                        else:
                            self.guiSetHighlighted(False)
                else:
                    self.guiSetHighlighted(False)
                    
        for childPmt in self.childrenList:
            childPmt.propagateHighlighting(similarPrimitive)
                
    def _check(self, childRecursiveCheck = True):
        '''
        @summary look for errors in this tree
        @param childsRecursiveCheck : check children too
        '''
#        if self.isRootPmt:
#            progress = QtGui.QProgressDialog("Validating", "Abort Validation", 0, 20, self.topWObject)
#            progress.setWindowModality(QtCore.Qt.WindowModal)
#            progress.show()
        prevListLength = len(self.validityEventsList)
        # If new event is True, then something new happened
        #If its false, make sure we check previousListLength to see if an event disappeared
        #If something happened, emit a signal to the view
        self.validityEventsList = []
        newEvent = False
        if self.xsdInfos.isObjectNull():
            #This primitive doesn't even exist
            newEvent = PrimitiveValidityEvent(self, "UnknownPrimitive", [])
            self.validityEventsList.append(newEvent)
            self.emit(QtCore.SIGNAL("ErrorFound()"))
            newEvent = True
            return
        
        #Self verification
        #Return Value verification
        
        #If defined by parameter, make sure parameter exists
        typeDefBy, returnType = self.xsdInfos.getReturnType()
        if typeDefBy=="parameterValue":
            baseModelRef = BaseParametersModel()
            refName = self.getAttributeByName(returnType).getValue()
            if not refName in baseModelRef.getRefList():
                self.validityEventsList.append(PrimitiveValidityEvent(self,"UnknownParameter",[refName,self.name]))
                newEvent = True
        
        #If defined by variable, make sure variable exists
        elif typeDefBy=="variableValue":
            baseModelVar = GeneratorBaseModel()
            baseModelEnv = BaseEnvModel()
            varName = self.getAttributeByName(returnType).getValue()

            if baseModelVar.variableExistsIgnoringSupPop(varName):
                pass
            elif baseModelEnv.variableExists(varName):
                pass
            else:
                self.validityEventsList.append(PrimitiveValidityEvent(self,"UnknownVariable",[varName,self.name]))
                newEvent = True
                
        #If defined by process, make sure process exists
#        elif typeDefBy=="processReturnValue":
#            baseModelTr = BaseTreatmentsModel()
#            processName = self.getAttributeByName(returnType).getValue()
#            if processName in baseModelTr.getTreatmentsDict().keys():
#                pass
#            else:
#                #Normally
#                self.validityEventsList.append(PrimitiveValidityEvent(self,"UnknownProcess",[processName,self.name]))
#                newEvent = True
                
        #Attributes verification
        if True in [attribute._check() for attribute in self.nextAttribute()]:
            newEvent = True
        #Branch Tag verification
        for attribute in self.nextAttribute():
            success, branchBehavior = self.xsdInfos.getAttribute(attribute.getName()).getBehavior().getBehavior("mapToBranches")
            if success:
                #look for sum behavior
                if branchBehavior["sum"] != '0':
                    for child in self.childrenList:
                        #Make sure childList is up to date
                        self._lookForBranchTag(child)
                    currentSum = Decimal('0')
                    for child in self.childrenList:
                        if "branchTag" in child.guiInfos.keys():
                            if child.guiInfos["branchTag"][2]:
                                try:
                                    currentSum+=Decimal(str(child.guiInfos["branchTag"][2]))
                                except ValueError:
                                    newEvent = PrimitiveValidityEvent(self, "BadBranchTag", [str(child.guiGetName()), str(self.guiGetChildPos(child)),child.guiInfos["branchTag"][2]])
                                    self.validityEventsList.append(newEvent)
                                    newEvent = True
                                    break
                    if currentSum != Decimal(branchBehavior["sum"]):
                        newEvent = PrimitiveValidityEvent(self, "BadBranchSum", [branchBehavior["sum"], str(currentSum)])
                        self.validityEventsList.append(newEvent)
                        newEvent = True
                    break
        #Children verification
        currentPos = 0
        for child in self.childrenList:
            #Get DocPrimitive info about child at position currentPos
            childInfo = self.xsdInfos.getSimpleOrderedChild(currentPos)

            if childInfo.isObjectNull():
                #No info found, there shouldn't even be a child at currentPos
                newEvent = PrimitiveValidityEvent(self, "BadChildPosition", [self.name,str(child.guiGetName()), str(self.xsdInfos.getMaximumChilds()),str(currentPos)])
                self.validityEventsList.append(newEvent)
                newEvent = True
                
            elif childInfo.isChoice():
            
#               #If this child can be a choice between multiple primitives
                #Look for that child is a valid choice
                if not childInfo.toChoice().isValidChoice(child.name):
                    newEvent = PrimitiveValidityEvent(self, "BadChild", [self.getChildPos(child),str(child.guiGetName()), str(self.guiGetName())])
                    self.validityEventsList.append(newEvent)
                    newEvent = True

            elif childInfo.isElement():
                #This child cannot be a choice, look if name found in info correspond to this child's name
                if childInfo.toElement().getName() != child.name:
                    newEvent = PrimitiveValidityEvent(self, "BadChild", [str(child.guiGetName()), childInfo.toElement().getName()])
                    self.validityEventsList.append(newEvent)
                    newEvent = True
                
            else:
                #Something happened, we aren't supposed to get there
                print("Warning : unable to check for a choice or an element in xsd child list for child " + str(currentPos))
            
            #Look that child has the right return type
            accType = "Any"
            obtainedType = child._getReturnType()
            accTypeDefBy, accTypeRef = childInfo.toChoice().getAcceptedType()
            if accTypeDefBy == "staticType":
                accType = accTypeRef
            elif accTypeDefBy == "argument":
                accType = self.childrenList[int(accTypeRef)-1]._getReturnType()
            elif accTypeDefBy == "variableValue":
                if self.getAttributeByName(accTypeRef).getType() =="indVar":
                    varModel = GeneratorBaseModel()
                    if not varModel.variableExistsIgnoringSupPop(self.getAttributeByName(accTypeRef).getValue()):
                        accType = "Any"
                    else:
                        accType = varModel.getVarTypeIgnoringSubPop(self.getAttributeByName(accTypeRef).getValue())
                elif self.getAttributeByName(accTypeRef).getType() =="locVar":
                    locVarModel = BaseLocalVariablesModel()
                    if not self.getAttributeByName(accTypeRef).getValue() in locVarModel.getLocVarsList(self.pmtRoot.pmtDomTree.parentNode()):
                        accType = "Any"
                    else:
                        accType = locVarModel.getLocalVarType(self.pmtRoot.pmtDomTree.parentNode(), self.getAttributeByName(accTypeRef).getValue())
                else:
                    accType = "Any"

            if not self._matchType(accType, obtainedType):
                newEvent = PrimitiveValidityEvent(self, "BadChildReturnValue", [str(currentPos), accType, obtainedType])
                self.validityEventsList.append(newEvent)
                newEvent = True
            
            if childRecursiveCheck:
                #Child checks itself
                child._check()
                
            #Increment position and pass to next child
            currentPos += 1
            
        
        self._findWorstEvent()
        if len(self.validityEventsList) < prevListLength or newEvent:
            #An error was corrected, emit signal and tell parent if parent has errors
            #We tell parent because parent's error might be coming from self's own error
            self.emit(QtCore.SIGNAL("ErrorFound()"))
            if not self.isRootPmt:
                if self.pmtParent.getValidityList() != ["Valid"]:
                    self.pmtParent._check(False)
                    
    def _findWorstEvent(self,includeSelf = False):
        '''
        @summary Find primitive's worst event
        '''
        eventDict = {"Unknown" : 0,
                     "Valid" : 1,
                     "Warning" : 2,
                     "Error":3}
        
        self.worstEvent = "Unknown"
        
        if self.childrenList:
            for child in self.childrenList:
                childWorstEvent = child._findWorstEvent(True)
                if eventDict[childWorstEvent] > eventDict[self.worstEvent]:
                    self.worstEvent = childWorstEvent
                    
        if includeSelf:
            worstEvent = self.worstEvent
            if eventDict[self.getValidityState()] > eventDict[worstEvent]:
                    worstEvent = self.getValidityState()
        
    
        return worstEvent if includeSelf else self.worstEvent

    def _getReturnType(self):
        '''
        @summary Get returned tree's returned type for this primitive
        '''
        typeDefBy, returnType = self.xsdInfos.getReturnType()
        #If type is defined by argument, which means by the return type of one of its children
        if typeDefBy == "argument":
            if int(returnType) == -1:
                dataReturnPos = -1
            else:
                dataReturnPos = int(returnType)-1
            return self.getChild(dataReturnPos)._getReturnType()
        
        elif typeDefBy == "variableValue":
            #If type is defined by the type of a variable
            baseModelVar = GeneratorBaseModel()
            baseModelEnv = BaseEnvModel()
            varName = self.getAttributeByName(returnType).getValue()

            if baseModelVar.variableExistsIgnoringSupPop(varName):
                return baseModelVar.getVarTypeIgnoringSubPop(varName)
                
            elif baseModelEnv.variableExists(varName):
                return baseModelEnv.getVarType(varName)
            else:
                print("Warning : In PrimitiveBaseModel::_getReturnType, variable not found in model, returning Any")
                return "Any"
        
        elif typeDefBy == "processReturnValue":
            #If type is defined by the return value of a process(CallProcess)
            baseModelTr = BaseTreatmentsModel()
            trName = self.getAttributeByName(returnType).getValue()
            if trName in baseModelTr.getViewTreatmentsDict():
                processDict = baseModelTr.getTreatmentsDict()
            else:
                return "Any"
            tmpPrimitive = PrimitiveSimplified(None, None, self.topWObject, processDict[str(trName)].firstChildElement("PrimitiveTree").firstChild())
            return tmpPrimitive._getReturnType()
        
        elif typeDefBy == "staticType":
            #If type is static, return
            return returnType
        
        elif typeDefBy == "attributeValue":
            #If type is defined by the value of an attribute
            if self.getAttributeByName(returnType):
                return self.getAttributeByName(returnType).getValue()
            else:
                #try to see if returnType matches *_Type
                try : 
                    mainAttr = self.getAttributeByName(returnType[:-5])
                    if mainAttr:
                        attrType = mainAttr.getType() 
                        if attrType == "value":
                            print("Warning : In PrimitiveBaseModel::_getReturnType, value attribute doesn't have its optional counterpart, returning Any")
                            return "Any"
                        elif attrType == "param":
                            paramModel = BaseParametersModel()
                            return paramModel.getRefType(mainAttr.getValue())
                        elif attrType == "indVar":
                            varModel = GeneratorBaseModel()
                            return varModel.getVarTypeIgnoringSubPop(mainAttr.getValue())
                        elif attrType =="envVar":
                            envModel = BaseEnvModel()
                            return envModel.getVarType(mainAttr.getValue())
                        elif attrType == "locVar":
                            locVarModel = BaseLocalVariablesModel()
                            return locVarModel.getLocalVarType(self.pmtRoot.pmtDomTree.parentNode(), mainAttr.getValue())
                    else:
                        print("Warning : In PrimitiveBaseModel::_getReturnType, attribute not found in model, returning Any")
                        return "Any"
                except IndexError:
                    print("Warning : In PrimitiveBaseModel::_getReturnType, attribute not found in model, returning Any")
                    return "Any"
                except KeyError:
                    print("Warning : In PrimitiveBaseModel::_getReturnType, attribute not found in model, returning Any")
                    return "Any"
                
        elif typeDefBy == "parameterValue":
            #If type is defined by the type a parameter
            baseModelRef = BaseParametersModel()
            refName = self.getAttributeByName(returnType).getValue()
            if refName in baseModelRef.getRefList():
                return baseModelRef.getRefType(refName)
            else:
                return "Any"
        
        elif typeDefBy== "commonType":
            #Type is defined by most common "ancestor" of children return Types
            #We have to parse returnType to find the indexes of the children defining the common type
            indexList = returnType.split(",")
            typeList = []
            for index in indexList:
                if ":" in index:
                    #index list contains a sequence
                    sequence = index.split(":")
                    endOfList = int(sequence[1])
                    if "-1" in sequence:
                        #sequence starts at a number and ends at last child
                        endOfList = self.countChildren() 
                    for i in range(int(sequence[0]),endOfList):
                        typeList.append(self.getChild(i)._getReturnType())
                else:
                    if index == "-1":
                        index = str(self.countChildren()-1)
                    typeList.append(self.getChild(int(index))._getReturnType())
            #Now we have our list of types, let's determine most common
            #First, lets build our type tree(we might want to automate this in the future)
            typeTree={'Atom':'Any','Void':'Any','Number':'Atom','Bool':'Atom','String':'Atom','Char':'Atom','FPoint':'Number','Integer':'Number','UInt':'Integer','Int':'Integer','ULong':'Integer','Long':'Integer','Float':'FPoint','Double':'FPoint'}      
            LCAFinder = LCA(typeTree)
            currentCommonType = typeList[0]
            for currentTestedType in typeList[1:-1]:
                currentCommonType = LCAFinder(currentCommonType,currentTestedType)
                
            return currentCommonType
        
        else:
            print("Warning : Bad return type definition '"+ typeDefBy + "', will accept Any return value")
            return "Any"
   
    def _matchType(self, acceptedType, obtainedType):
        '''
        @summary See if the type obtained in the corresponds the one required by DocPrimitive
        @param acceptedType : DocPrimitive's requirement
        @param obtainedType : type obtained in tree
        '''
        if str(acceptedType).lower() == str(obtainedType).lower():
            return True

        if acceptedType == "Any":
            return True
        elif acceptedType == "Integer":
            if obtainedType in ["Int", "Long", "UInt", "ULong"]:
                return True
        elif acceptedType == "Number":
            if obtainedType in ["Int", "Double", "Float", "Long", "UInt", "ULong","Integer"]:
                return True
        elif acceptedType == "Atom":
            if obtainedType in ["Int", "Double", "Float", "Long", "UInt", "ULong", "Number","Integer", "String", "Char", "Bool"]:
                return True
        elif acceptedType == "Float":
            if obtainedType in ["Double", "Float"]:
                return True

        return False
          
    def _lookForMissingChildren(self):
        '''
        @summary Looks for children that are supposed to be in the tree but aren't
        '''
        if  len(self.childrenList) < self.xsdInfos.getMinimumNumChilds():
            #Loop (i missing children) time
            for i in range(0,self.xsdInfos.getMinimumNumChilds()-len(self.childrenList)):
                #Create child and execute common function
                newPmt = Primitive(self, self.pmtRoot, self.topWObject, QtXml.QDomNode(), True, self.displayComments)
                self.childrenList.append(newPmt)
                self._lookForBranchTag(newPmt)
                    
    def _lookForMissingAttribute(self):
        '''
        @summary Looks for attributes that are supposed to be in the tree but aren't
        '''
        if len(self.attrList) < self.xsdInfos.howManyAttributes():
            for attrib in self.xsdInfos.getNextAttribute():
                #if attrib.getName() not in self.attrList and not attrib.isOptionnal():
                if attrib.getName() not in self.attrList and not attrib.isOptionnal():
                    self.addAttribute(PrimitiveAttribute(attrib.getName(), attrib.getDefaultValue(), self))

    def _lookForBranchTag(self , newChild):
        '''
        @summary Looks in attribute list and find if child has a branch tag
        @param newChild : child to eventually add a branch tag to
        '''
        self.guiInfos["attrBranchMapped"] = None
        for attrib in self.nextAttribute():
            attrXSDInfos = self.xsdInfos.getAttribute(attrib.getName())
            success, branchBehavior = attrXSDInfos.getBehavior().getBehavior("mapToBranches")
            if success:
                self.guiInfos["attrBranchMapped"] = self.getAttributeByName(attrib.getName())
                break

        #After loop, look look in guiInfos if an attribute has to be branch Mapped
        if self.guiInfos["attrBranchMapped"]:
            if self.guiInfos["attrBranchMapped"].getType() == "value":
                editable = branchBehavior["editable"]
                #Split attribute using regexp and create a list with values that can be mapped to child according to position
                if branchBehavior["regexp"]:
                    valueList = self.guiInfos["attrBranchMapped"].getValue().split(branchBehavior["regexp"])
                elif not branchBehavior["editable"] and branchBehavior["sum"] != '0':
                    #Branch isn't a normal branch, sum dictates how branch is supposed to behave
                    if int(branchBehavior["startIndex"]) == self.guiGetChildPos(newChild) and int(branchBehavior["endIndex"]) == self.guiGetChildPos(newChild):
                        try:
                            value = str(float(branchBehavior["sum"]) - float(self.guiInfos["attrBranchMapped"].getValue()))
                        except ValueError:
                            #If attribute's value is empty or not castable
                            value =""
                        newChild.guiInfos["branchTag"]= [branchBehavior["displayAttribute"],editable,value]
                        newChild.emit(QtCore.SIGNAL("updateBranchTag()"))
                        return
                    elif self.guiGetChildPos(newChild) == 0:
                        #Since we only have the 2 branches Branching primitive defined yet
                        #First child has to be the attribute's value
                        try:
                            value = float(self.guiInfos["attrBranchMapped"].getValue())
                        except ValueError:
                            #If attribute's value is empty or not castable
                            value =""
                        newChild.guiInfos["branchTag"]= [branchBehavior["displayAttribute"],editable,value]
                        newChild.emit(QtCore.SIGNAL("updateBranchTag()"))
                        return
                    else:
                        #Case not defined yet
                        return
                else:
                    return
            
            else:
                #Take branch tag in one parameters or variables
                editable = False
                success, branchBehavior = self.xsdInfos.getAttribute(self.guiInfos["attrBranchMapped"].getName()).getBehavior().getBehavior("mapToBranches")
                valueList = []
                if self.guiInfos["attrBranchMapped"].getType() == "envVar":
                    #Warning : Will only tell if sum is good at the beginning of the simulation
                    envModel = BaseEnvModel()
                    if envModel.variableExists(self.guiInfos["attrBranchMapped"].getValue()):
                        valueList = envModel.getVarValue(self.guiInfos["attrBranchMapped"].getValue())
                elif self.guiInfos["attrBranchMapped"].getType() == "indVar":
                    #Cannot actually find a way to tell if branching sums to 1
                    pass
                elif self.guiInfos["attrBranchMapped"].getType() == "param":
                    paramModel = BaseParametersModel()
                    if paramModel.referenceExists(self.guiInfos["attrBranchMapped"].getValue()[4:]):
                        valueList = paramModel.getValue(self.guiInfos["attrBranchMapped"].getValue())
                elif self.guiInfos["attrBranchMapped"].getType() == "locVar":
                    locVarModel = BaseLocalVariablesModel()
                    if self.guiInfos["attrBranchMapped"].getValue() in locVarModel.getLocVarsList(self.pmtRoot.pmtDomTree.parentNode()):
                        valueList = locVarModel.getLocalVarValue(self.pmtRoot.pmtDomTree.parentNode(), self.guiInfos["attrBranchMapped"].getValue())
                else:
                    #case undefined
                    pass
                
                if valueList and not branchBehavior["regexp"]:
                    #Branch isn't a normal branch, sum dictates how branch is supposed to behave
                    if int(branchBehavior["startIndex"]) == self.guiGetChildPos(newChild) and int(branchBehavior["endIndex"]) == self.guiGetChildPos(newChild):
                        try:
                            value = str(float(branchBehavior["sum"]) - float(valueList[0]))
                        except ValueError:
                            #If attribute's value is empty or not castable
                            value =""
                        newChild.guiInfos["branchTag"]= [branchBehavior["displayAttribute"],editable,value]
                        newChild.emit(QtCore.SIGNAL("updateBranchTag()"))
                        return
                    elif self.guiGetChildPos(newChild) == 0:
                        #Since we only have the 2 branches Branching primitive defined yet
                        #First child has to be the attribute's value
                        try:
                            value = float(valueList[0])
                        except ValueError:
                            #If attribute's value is empty or not castable
                            value =""
                        newChild.guiInfos["branchTag"]= [branchBehavior["displayAttribute"],editable,value]
                        newChild.emit(QtCore.SIGNAL("updateBranchTag()"))
                        return
                    else:
                        #Case not defined yet
                        return
                
            if self.guiGetChildPos(newChild) >= int(branchBehavior["startIndex"]) and (int(branchBehavior["endIndex"]) == -1 or self.guiGetChildPos(newChild) <= int(branchBehavior["endIndex"])):
                #Child is inside indexes that can have a branch tag
                #little formating will be done
                if self.guiGetChildPos(newChild)-int(branchBehavior["startIndex"]) < len(valueList):
                    #Value found in list, so set child's branch tag
                    value = valueList[self.guiGetChildPos(newChild)-int(branchBehavior["startIndex"])]
                    value = (str(value).rstrip()).lstrip()
                    newChild.guiInfos["branchTag"]= [branchBehavior["displayAttribute"],editable,value]
                else:
                    #Since list is not long enough for this child's position, add an exclamation mark to tell user this branch tag has to be filled
                    newChild.guiInfos["branchTag"]= [branchBehavior["displayAttribute"],editable,""]
            
            newChild.emit(QtCore.SIGNAL("updateBranchTag()"))
        
    def _updateAttribute(self,attribute):
        '''
        @summary This function is a slot called when a user modifies a branch tag via a MedTreeEditableBranchTag
        This way, the attribute's value is updated
        @param attribute : the attribute associated to the branch tag
        '''
        assert attribute.name in self.attrList.keys(), "In Primitive::_updateAttribute, unknown attribute : "+str(attribute.name)
        #Call DocPrimitive and get mapToBranches behavior
        success,behaviorInfo = self.xsdInfos.getAttribute(attribute.name).getBehavior().getBehavior("mapToBranches")
        #Clear attribute's value
        attribute.value = ""
        #-1 value means the endIndex is the last child
        if int(behaviorInfo["endIndex"]) == -1:
            endIndex = len(self.childrenList)-1
        else:
            endIndex = int(behaviorInfo["endIndex"])
        #For all child primitive between start index and end index
        for primitiveData in self.childrenList[int(behaviorInfo["startIndex"]):endIndex+1]:
            if "branchTag" in primitiveData.guiInfos:
                #if child has a branch tag, update attribute with value and put delimiter
                attribute.value = attribute.value+primitiveData.guiInfos["branchTag"][2]+behaviorInfo["regexp"]
            else:
                #if child doesn't have a branch tag yet, put delimiter only
                attribute.value = attribute.value+behaviorInfo["regexp"]
        #If attribute currently have an editor, update editor
        if attribute.editor != None:
            attribute.guiSetEditorData(attribute.editor)
            attribute.guiUpdateWidgetGeometry(attribute.value)
        
        self._check()

    def _parseName(self):
        '''
        @summary Parse primitive's name
        '''
        self.name = self.pmtDomTree.nodeName()

    def _parseChilds(self):
        '''
        Function used to parse children of a Primitive
        '''
        
        self.childrenList = []
        currentChild = self.pmtDomTree.firstChildElement()

        #Check if first Child is a comment:
        if self.pmtDomTree.firstChild().isComment():
            self.userComment = self.pmtDomTree.firstChild().nodeValue()
               
        while not currentChild.isNull():
            # For each QDomElement
            newPmt = Primitive(self, self.pmtRoot, self.topWObject, currentChild, True, self.displayComments)
            self.childrenList.append(newPmt)


            #Check for branch Tag    
            self._lookForBranchTag(newPmt)
              
            #Check for comment in child List
            #Recent versions aren't supposed to have comments in children unless it's the first child Node
            #Next lines are for backward compatibility
            if currentChild.nextSibling().isComment():
                newPmt.defaultComment = currentChild.nextSibling().nodeValue()

            currentChild = currentChild.nextSiblingElement()
            
        if self.autoMissingItemsFill:   
            self._lookForMissingChildren()
            
    def _parseAttributes(self):
        '''
        Function used to parse attributes of a Primitive
        '''
        lQAttributes = self.pmtDomTree.attributes()
        self.attrCount = lQAttributes.count()
        self.attrList = {}
        
        for i in range(0, self.attrCount):
            lCurrentAttribute = lQAttributes.item(i).toAttr()
            appendedAttr = PrimitiveAttribute(lCurrentAttribute.name(), lCurrentAttribute.value().simplified(), self)
            self.attrList[str(lCurrentAttribute.name())] = appendedAttr
        
        if self.autoMissingItemsFill:
            self._lookForMissingAttribute()
    
    def _checkForSimilarDoms(self,comparedDom):
        '''
        @summary Since no function exists to check if two DOM instances are similar, this function loops through child, comments and attributes and test if elements are equals
        @param comparedDom : the dom node to compare with this node
        '''
        
        selfDom = self._writeDom(comparedDom.ownerDocument())
        #Attributes check
        if not selfDom.toElement().attributes().count() == comparedDom.toElement().attributes().count():
            return False
        for i in range(0,selfDom.toElement().attributes().count()):
            attrName = selfDom.toElement().attributes().item(i).toAttr().name()
            if not comparedDom.toElement().hasAttribute(attrName):
                return False
            if not comparedDom.toElement().attribute(attrName) == selfDom.toElement().attribute(attrName):
                return False
        
        #Comments and child list check
        if not selfDom.childNodes().count() == comparedDom.childNodes().count():
            return False
        commentCompteur = 0
        for i in range(0,selfDom.childNodes().count()):
            currentSelfChild = selfDom.childNodes().item(i)
            currentComparedChild = comparedDom.childNodes().item(i)
            if currentSelfChild.isComment():
                commentCompteur += 1
                if not currentComparedChild.isComment():
                    return False
                if not currentSelfChild.nodeValue() == currentComparedChild.nodeValue():
                    return False
            else:
                if not self.childrenList[i-commentCompteur]._checkForSimilarDoms(currentComparedChild):
                    return False
        
        return True

    def _writeDom(self, tmpDoc):
        '''
        @summary Create complete DOM of this primitive and return it as a string
        '''
        domNode = tmpDoc.createElement(self.name)
        if self.hasUserComment():
            newUserCommentNode = tmpDoc.createComment(self.userComment)
            domNode.appendChild(newUserCommentNode)
        for children in self.childrenList:
            domNode.appendChild(children._writeDom(tmpDoc))
            if children.hasDefaultComment():
                newDefaultCommentNode = tmpDoc.createComment(children.defaultComment)
                domNode.appendChild(newDefaultCommentNode)
    
        for attributes in self.attrList.keys():
            domNode.toElement().setAttribute(attributes,QtCore.QString.fromUtf8(self.attrList[attributes].value))
        return domNode

class PrimitiveAttributeSimplified(QtCore.QObject):
    '''
    This class represents the attribute of a Primitive, in a simplified way so the validator is more efficient(memory and CPU)
    '''
    __slots__ = ('pmtParent','name','value')
    def __init__(self, name, value, parentPrimitive):
        '''
        @summary Constructor
        @param name : attribute's name
        @param value : attribute's value
        @param parentPrimitive : attribute's primitive
        @param mappedFromPrimitive : tells if this attribute is mapped from a primitive
        @param mappedPmtField : mapped pmt field
        @param mappedPmt : mapped pmt
        '''
        QtCore.QObject.__init__(self)
        self.pmtParent =  parentPrimitive
        self.name = str(name)
        self.value = str(value)
  
    def getValue(self):
        '''
        @summary return attribute's value, without widlcard
        '''
        if not self.value:
            return self.value
        if not self.value[0] in "#@$%":
            return self.value
        return self.value[1:]
        
    def getType(self):
        '''
        @Summary Return where this attribute comes from
        Possible values : indVar, envVar, param, locVar and value
        '''
        if not self.value:
            return "value"
        elif self.value[0] == "@":
            return "indVar"
        elif self.value[0] == "#":
            return "envVar"
        elif self.value[0] == "$":
            return "param"
        elif self.value[0] == "%":
            return "locVar"
        return "value"
            
class PrimitiveSimplified(QtCore.QObject):
    '''
    This class represents a primitive
    A primitive may contain primitive children and attributes
    This class is just a wrapper over the simulator XML code, and is used to make a bridge between the xml code and the user's perspective of a tree node
    '''
    __slots__ = ('pmtRoot', 'topWObject', 'pmtDomTree','autoMissingItemsFill','childrenList','pmtParent','name','xsdInfos','attrList','isRootPmt','worstEvent') 
    def __init__(self, parentPrimitive, rootPrimitive, topWindowObject, XMLTree, autoMissingItemsFill=True, name = "Control_Nothing"): 
        """
        summary Constructor
        @param parentPrimitive : the primitive parent of this primitive (null primitive if there's none)
        @param rootPrimitive : the primitive root of the tree this primitive belongs to (null primitive if this is the root)
        @param topWindowObject : MainFrame pointer
        @param primitivePos : the position of this primitive in its parent's children list
        @param XMLTree : a QDomNode() representing this primitive
        @param autoMissingItemsFill : boolean. If set to true, Primitive object will try to fill missing required children or attributes
        @param displayComments : boolean. If set to true, Primitive object will parse XML comments and give access to them to the user
        """
        QtCore.QObject.__init__(self)
        
        self.pmtRoot = rootPrimitive
        self.topWObject = topWindowObject
        self.pmtDomTree = XMLTree
        self.autoMissingItemsFill = autoMissingItemsFill
        
        
        self.pmtParent = parentPrimitive
        self.name = name

        self.validityEventsList = []

        if not XMLTree.isNull():
            self._parseName()
       
        assocDict = PrimitiveDict()
        self.xsdInfos = assocDict.getPrimitiveInfo(self.name)
        if self.xsdInfos.isObjectNull():
            print("Warning : no information about primitive '" + str(self.name) + "'")
            self.autoMissingItemsFill = False   # We cannot display missing childs if we don't know the childs...
        
        self.childrenList = [] #Primitive children list
        self.attrList = {} #Primitive Attribute List
        if self.pmtParent == None:
            self.isRootPmt = True
            self.pmtRoot = self
            self.worstEvent = "Unknown"
        else:
            self.isRootPmt = False
       
    def countChildren(self):
        '''
        @summary Return number of child
        '''
        return len(self.childrenList)
    
    def getAttributeByName(self,attrName):
        '''
        @summary Return attribute
        @attrName attribute's name
        '''
        if attrName in self.attrList.keys():
            return self.attrList[attrName]

    def getChild(self,childPos):
        '''
        @summary Return child at given position
        @param childPos : child's position
        '''
        return self.childrenList[childPos]
    
    def _lookForMissingChildren(self):
        '''
        @summary Looks for children that are supposed to be in the tree but aren't
        '''
        if  len(self.childrenList) < self.xsdInfos.getMinimumNumChilds():
            #Loop (i missing children) time
            for i in range(0,self.xsdInfos.getMinimumNumChilds()-len(self.childrenList)):
                #Create child and execute common function
                newPmt = PrimitiveSimplified(self, self.pmtRoot, self.topWObject, QtXml.QDomNode(), True)
                self.childrenList.append(newPmt)
                    
    def _lookForMissingAttribute(self):
        '''
        @summary Looks for attributes that are supposed to be in the tree but aren't
        '''
        if len(self.attrList) < self.xsdInfos.howManyAttributes():
            for attrib in self.xsdInfos.getNextAttribute():
                #if attrib.getName() not in self.attrList and not attrib.isOptionnal():
                if attrib.getName() not in self.attrList and not attrib.isOptionnal():
                    self.attrList[attrib.getName()] = PrimitiveAttributeSimplified(attrib.getName(), attrib.getDefaultValue(), self)

    def _getReturnType(self):
        '''
        @summary Get returned tree's returned type for this primitive
        '''
        typeDefBy, returnType = self.xsdInfos.getReturnType()
        #If type is defined by argument, which means by the return type of one of its children
        if typeDefBy == "argument":
            if int(returnType) == -1:
                dataReturnPos = -1
            else:
                dataReturnPos = int(returnType)-1
            
            self._parseChilds()
            
            return self.getChild(dataReturnPos)._getReturnType()
        
        
        elif typeDefBy == "variableValue":
            #If type is defined by the type of a variable(example is TokenVariable or TokenEnvironment)
            self._parseAttributes()
            baseModelVar = GeneratorBaseModel()
            baseModelEnv = BaseEnvModel()
            varName = self.getAttributeByName(returnType).getValue()

            if baseModelVar.variableExistsIgnoringSupPop(varName):
                return baseModelVar.getVarTypeIgnoringSubPop(varName)
                
            elif baseModelEnv.variableExists(varName):
                return baseModelEnv.getVarType(varName)
            else:
                print("Warning : In PrimitiveBaseModel::_getReturnType, variable not found in model, returning Any")
                return "Any"
        
        elif typeDefBy == "processReturnValue":
            #If type is defined by the return value of a process(TokenCallProcess)
            self._parseAttributes()
            baseModelTr = BaseTreatmentsModel()
            trName = self.getAttributeByName(returnType).getValue()
            if trName in baseModelTr.getViewTreatmentsDict():
                processDict = baseModelTr.getTreatmentsDict()
            else:
                return "Any"
            
            tmpPrimitive = PrimitiveSimplified(None, None, self.topWObject, processDict[str(trName)].firstChildElement("PrimitiveTree").firstChild())
            return tmpPrimitive._getReturnType()
        
        elif typeDefBy == "staticType":
            #If type is static, return
            return returnType
        
        elif typeDefBy == "attributeValue":
            #If type is defined by the value of an attribute
            self._parseAttributes()
            if self.getAttributeByName(returnType):
                return self.getAttributeByName(returnType).getValue()
            else:
                #try to see if returnType matches *_Type
                try : 
                    mainAttr = self.getAttributeByName(returnType[:-5])
                    if mainAttr:
                        attrType = mainAttr.getType() 
                        if attrType == "value":
                            return "Any"
                        elif attrType == "param":
                            paramModel = BaseParametersModel()
                            return paramModel.getRefType(mainAttr.getValue())
                        elif attrType == "indVar":
                            varModel = GeneratorBaseModel()
                            return varModel.getVarTypeIgnoringSubPop(mainAttr.getValue())
                        elif attrType =="envVar":
                            envModel = BaseEnvModel()
                            return envModel.getVarType(self.getAttributeByName(mainAttr).getValue())
                        elif attrType == "locVar":
                            #Not implemented yet
                            locVarModel = BaseLocalVariablesModel()
                            return locVarModel.getLocalVarType(self.pmtRoot.pmtDomTree.parentNode(), mainAttr.getValue())
                    else:
                        return "Any"
                except:
                    return "Any"
        
        elif typeDefBy == "parameterValue":
            #If type is defined by the type a parameter
            self._parseAttributes()
            baseModelRef = BaseParametersModel()
            refName = self.getAttributeByName(returnType).getValue()
            if refName in baseModelRef.getRefList():
                return baseModelRef.getRefType(refName)
            else:
                return "Any"
            
        elif typeDefBy== "commonType":
            #Type is defined by most common "ancestor" of children return Types
            #We have to parse returnType to find the indexes of the children defining the common type
            indexList = returnType.split(",")
            typeList = []
            self._parseChilds()
            for index in indexList:
                if ":" in index:
                    #index list contains a sequence
                    sequence = index.split(":")
                    endOfList = int(sequence[1])
                    if "-1" in sequence:
                        #sequence starts at a number and ends at last child
                        endOfList = self.countChildren() 
                    for i in range(int(sequence[0]),endOfList):
                        typeList.append(self.getChild(i)._getReturnType())
                else:
                    if index == "-1":
                        index = str(self.countChildren()-1)
                    typeList.append(self.getChild(int(index))._getReturnType())
            #Now we have our list of types, let's determine most common
            #First, lets build our type tree(we might want to automate this in the future)
            typeTree={'Atom':'Any','Void':'Any','Number':'Atom','Bool':'Atom','String':'Atom','Char':'Atom','FPoint':'Number','Integer':'Number','UInt':'Integer','Int':'Integer','ULong':'Integer','Long':'Integer','Float':'FPoint','Double':'FPoint'}      
            LCAFinder = LCA(typeTree)
            currentCommonType = typeList[0]
            for currentTestedType in typeList[1:-1]:
                currentCommonType = LCAFinder(currentCommonType,currentTestedType)
                
            return currentCommonType
        
        else:
            print("Warning : Bad return type definition '"+ typeDefBy + "', will accept Any return value")
            return "Any"

    def _parseName(self):
        '''
        @summary Parse primitive's name
        '''
        self.name = self.pmtDomTree.nodeName()

    def _parseChilds(self):
        '''
        Function used to parse children of a Primitive
        '''
        
        self.childrenList = []
        currentChild = self.pmtDomTree.firstChildElement()
               
        while not currentChild.isNull():
            # For each QDomElement
            newPmt = PrimitiveSimplified(self, self.pmtRoot, self.topWObject, currentChild, True)
            self.childrenList.append(newPmt)
              
            #Check for comment in child List
            #Recent versions aren't supposed to have comments in children unless it's the first child Node
            #Next lines are for backward compatibility
            currentChild = currentChild.nextSiblingElement()
            
        if self.autoMissingItemsFill:   
            self._lookForMissingChildren()
            
    def _parseAttributes(self):
        '''
        Function used to parse attributes of a Primitive
        '''
        lQAttributes = self.pmtDomTree.attributes()
        self.attrCount = lQAttributes.count()
        self.attrList = {}
        
        for i in range(0, self.attrCount):
            lCurrentAttribute = lQAttributes.item(i).toAttr()
            appendedAttr = PrimitiveAttributeSimplified(lCurrentAttribute.name(), lCurrentAttribute.value().simplified(), self)
            self.attrList[str(lCurrentAttribute.name())] = appendedAttr
        
        if self.autoMissingItemsFill:
            self._lookForMissingAttribute()
    