"""
.. module:: PrimitiveModel

.. codeauthor:: Marc-André Gardner

:Created on: 2009-01-27

"""
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
import Definitions

class PrimitiveValidityEvent():
    '''
    This class represents an error (or at least a notice) in the Primitive Tree.
    '''
    
    def __init__(self, primitiveRef, eventType, eventArgs):
        '''
        Constructor.
        
        :param primitiveRef: Associated primitive instance.
        :param eventType: Event type (see DocPrimitiveEvent).
        :param eventArgs: Event arguments (see DocPrimitiveEvent).
        '''
        self.eventRef = primitiveRef.xsdInfos.getSpecificEventInfo(eventType)
        self.eArgs = eventArgs

        if self.eventRef.isNull:
            print("Warning : unknown event", eventType, "for primitive", primitiveRef.name)
    
    def isValid(self):
        '''
        Return's if event is valid
        '''
        return not self.eventRef.isNull

    def generateEventMsg(self):
        '''
        Generate message  associated with this event
        '''
        if self.eventRef.isNull:
            print("Could not generate error Message!")
            return "Error : This primitive seems to be unknown"
        return self.eventRef.generateErrorMsg(self.eArgs)

class PrimitiveAttribute(QtCore.QObject):
    '''
    This class represents the attribute of a Primitive.
    '''  
    def __init__(self, name, value, parentPrimitive):
        '''
        Constructor.
        
        :param name: Attribute's name.
        :param value: Attribute's value.
        :param parentPrimitive: Attribute's primitive.
        :type name: String
        :type value: String
        :type parentPrimitive: :class:`.Primitive`.
        '''
        QtCore.QObject.__init__(self)
        self.pmtParent = parentPrimitive
        self.name = name
        #  #print value
        self.value = str(value)
        # print self.value
        self.editor = None
        self.layout = None
        self.choiceMenu = None
        self.typeDir = {'@':'indVar','#':'envVar','$':'param','%':'locVar'}
        if self.type == "value":
            if self.pmtParent.xsdInfos.getAttribute(self.name).pairedAttr:
                if not self.pmtParent.hasAttribute(self.pmtParent.xsdInfos.getAttribute(self.name).pairedAttr):
                    #Paired attribute found in xsd but not in parent attributes
                    #Maybe it has not been created yet, maybe it is not in xml
                    #Hence, we're not going to take any chances and create it already
                    #At worst its going to be overridden
                    self.pmtParent.addAttributeByName(self.pmtParent.xsdInfos.getAttribute(self.name).pairedAttr) 
    
    def getMappedName(self):
        '''
        Return's attribute mapped Name or attribute's name if mapped Name doesn't exist.
        
        :return: String.
        '''
        return self.pmtParent.xsdInfos.getAttribute(self.name).getMappedName() if self.pmtParent.xsdInfos.getAttribute(self.name).getMappedName() else self.name
    
    @property    
    def type(self):
        '''
        Returns where this attribute comes from.
        Possible values : indVar, envVar, param, locVar and value.
        
        :return: String
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
        Return attribute's value
        '''
        if self.type == "value":
            return self.value
        return self.value[1:]
    
    def getLayout(self):
        '''
        Creates and returns layout.
        
        :return: QtGui.QHboxLayout.
        '''
        self.layout = QtGui.QHBoxLayout()
        self.layout.setAlignment(QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.guiCreatePropertyLabel())
        self.checkSetChoice()
        self.layout.addWidget(self.guiCreateEditor())    
        if not self.pmtParent.xsdInfos.isPaired(self.name) and not self.pmtParent.xsdInfos.getAttribute(self.name).required:
            pushButtonRemove = QtGui.QPushButton("-")
            pushButtonRemove.setFixedWidth(25)
            pushButtonRemove.setFixedHeight(27)
            self.layout.addWidget(pushButtonRemove)
            self.connect(pushButtonRemove,QtCore.SIGNAL("pressed()"),self.remove)
        return self.layout
    
    def guiCreateEditor(self):
        '''
        Creates an editor (a QLineEdit or QComboBox)
        
        :return: QLineEdit | QComboBox
        '''
        typeDir = {'indVar':'indVariables','envVar':'envVariables','param':'allParameters','locVar':'locVariables','cusVal':'customValue'}
        
        if self.pmtParent.xsdInfos.getAttribute(self.name).behavior.list:
            if len(self.pmtParent.xsdInfos.getAttribute(self.name).behavior.list) <= 1:
                varType = self.pmtParent.xsdInfos.getAttribute(self.name).behavior.list[0]["type"]    
            else:
                #Multiple list for the attribute
                if not self.value or self.type.lower() == "value":
                    if self.pmtParent.xsdInfos.getAttribute(self.name).pairedAttr and self.pmtParent.name == "Data_Value":
                        #Might be a boolean attribute
                        pairedAttr = self.pmtParent.xsdInfos.getAttribute(self.name).pairedAttr
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
                    varType = typeDir[self.type]
                    
            self.editor = QtGui.QComboBox()    
            self.guiSetEditorData(self.editor, True, varType)
            self.guiUpdateWidgetGeometryComboBox(self.editor.currentText())
            self.connect(self.editor,QtCore.SIGNAL("currentIndexChanged(QString)"),self.guiSetModelData)
            self.connect(self.editor,QtCore.SIGNAL("currentIndexChanged(QString)"),self.guiUpdateWidgetGeometryComboBox)
            
        elif self.pmtParent.xsdInfos.getAttribute(self.name).possibleValues:
            self.editor = QtGui.QComboBox()
            self.guiSetEditorData(self.editor,True)
            self.guiUpdateWidgetGeometryComboBox(self.editor.currentText())
            self.connect(self.editor,QtCore.SIGNAL("currentIndexChanged(QString)"),self.guiSetModelData)
            self.connect(self.editor,QtCore.SIGNAL("currentIndexChanged(QString)"),self.guiUpdateWidgetGeometryComboBox)
        elif self.pmtParent.xsdInfos.getAttribute(self.name).type == "boolean":
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
    
    def guiSetEditorData(self, editorWidget, isComboBox=False, reference=None):
        '''
        Sets an editor data (QLineEdit or QComboBox).
        
        :param editorWidget: The widget itself which is a QLineEdit or QComboBox.
        :param Boolean isComboBox: Tells if the widget is a comboBox.
        :param String reference: Tells if the attribute's value is a reference to a parameter.
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
            variables.extend(envModel.modelMapper)
            editorWidget.addItems(sorted(variables,key=str.lower))
        elif reference == "envVariables":
            envModel = BaseEnvModel()
            editorWidget.addItems(sorted(envModel.modelMapper,key=str.lower))
        elif reference == "indVariables":
            varModel = GeneratorBaseModel()
            variables = [var for values in varModel.modelMapper.values() for var in values]
            editorWidget.addItems(sorted(variables,key=str.lower))
        elif reference == "locVariables":
            locVarModel = BaseLocalVariablesModel()
            indexNode = self.pmtParent.pmtRoot.pmtDomTree.parentNode()
            editorWidget.addItems(sorted(locVarModel.getLocVarsList(indexNode),key=str.lower))
        elif reference == "allTypes":
            items = map(Definitions.typeToDefinition, Definitions.baseTypes)
            editorWidget.addItems(sorted(items,key=str.lower))
        elif reference == "atomTypes":
            items = map(Definitions.typeToDefinition, Definitions.baseTypes)
            editorWidget.addItems(sorted(items,key=str.lower))
        elif reference == "numericTypes":
            items = map(Definitions.typeToDefinition, Definitions.numberTypes)
            editorWidget.addItems(sorted(items,key=str.lower))
        elif reference =="allParameters":
            paramModel = BaseParametersModel()
            parameters = paramModel.getTruncatedRefList()
            editorWidget.addItems(sorted(parameters,key=str.lower))
            for parameter in sorted(parameters,key=str.lower):
                editorWidget.setItemData(sorted(parameters,key=str.lower).index(parameter), str(paramModel.getValue("ref."+parameter)), QtCore.Qt.ToolTipRole)
            editorWidget.addItem("Add new parameter")
            self.connect(self.editor, QtCore.SIGNAL("activated(int)"), self.addNewParam)
            editorWidget.setCurrentIndex(editorWidget.findText(self.getValue()[4:]))
            editorWidget.view().setMinimumWidth(self.calculateListWidth())
            return
        else:
            #Reference is None, get value in possible Values
            editorWidget.addItems(sorted(self.pmtParent.xsdInfos.getAttribute(self.name).possibleValues,key=str.lower))
        
        editorWidget.setCurrentIndex(editorWidget.findText(Definitions.typeToDefinition(self.getValue())))
        editorWidget.view().setMinimumWidth(self.calculateListWidth())
        
    def guiSetModelData(self, text):
        '''
        Updates data when this attribute's editor data is modified.
        
        :param text: New value as string.
        '''
        text = Definitions.convertType(text)
        prefixDir = {'Environment variables':'#','Individual variables':'@','Local Variables':'%','Parameters':'$','Value':''}
        if self.choiceMenu:
            if self.type == "param":
                if text == "Add new parameter":
                    return
                
                self.value = prefixDir[self.choiceMenu.checkedAction().text()] + "ref." + text
            else:
                self.value = prefixDir[self.choiceMenu.checkedAction().text()] + text
        else:
            self.value = text
            
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
        Creates attribute name's label.
        
        :return: QLabel.
        '''
        propertyLabel = QtGui.QLabel()
        propertyLabel.setText(self.getMappedName())
        propertyLabel.setFixedWidth(self.calculateTextWidth(propertyLabel.text(), propertyLabel.font()))
        if self.pmtParent.xsdInfos.getAttribute(self.name).getAttributeInfo():
            propertyLabel.setToolTip(self.pmtParent.xsdInfos.getAttribute(self.name).getAttributeInfo())
        return propertyLabel
    
    def guiUpdateWidgetGeometry(self, newText):
        '''
        Updates self.editor geometry.
        
        :param newText: Text found in editor.
        :type newText: String
        '''
        self.editor.setMinimumWidth(1)
        self.editor.setMaximumWidth(self.calculateTextWidth(newText, self.editor.font())+15)
        
    def guiUpdateWidgetGeometryComboBox(self, newText):
        '''
        Like :meth:`.guiUpdateWidgetGeometry` but for a comboBox.
        
        :param newText: Text found in editor.
        :type newText: String
        '''
        self.editor.setMinimumWidth(1)
        self.editor.setMaximumWidth(self.calculateTextWidth(newText, self.editor.font())+30)
    
    def calculateListWidth(self):
        '''
        Calculates pixel width of largest item in drop-down list.
        
        :return: Int.
        '''
        fm = QtGui.QFontMetrics(self.editor.view().font())
        minimumWidth = 0
        for i in range(self.editor.count()):
            if fm.width(self.editor.itemText(i)) > minimumWidth:
                minimumWidth = fm.width(self.editor.itemText(i))
        return minimumWidth + 10
    
    def calculateTextWidth(self, text, font):
        '''
        Computes and returns the pixel width used by a given string.
        
        :param text: String we want the width of.
        :param font: Text's font.
        :type text: String
        :type font: QFont | QFontMetrics
        :return: Int
        '''
        fontMetrics = QtGui.QFontMetrics(font)
        return fontMetrics.width(text)
    
    def addNewParam(self, index):
        '''
        Adds a parameter on the fly when in a comboBox listing parameters.
        
        :param index: Index of the clicked item.
        :type index: Int
        '''
        if index == self.editor.count() - 1:
            reponse,valid = QtGui.QInputDialog.getText(self.pmtParent.topWObject, "Enter New Parameter Name", "Param Name : ")
            if valid:
                baseParamModel = BaseParametersModel()
                baseParamModel.addRef("ref."+reponse, "Double")
                self.value = "$ref." + reponse
                insertIndex = sorted(baseParamModel.getTruncatedRefList()).index(reponse)
                self.editor.insertItem(insertIndex, reponse)
            self.editor.setCurrentIndex(self.editor.findText(self.getValue()[4:]))
        
    def modifyEditor(self):
        '''
        Slot called when a Token type attribute is modified.
        Allows this attribute to correctly update its editor.
        '''
        widgetToGetRidOf = self.layout.takeAt(self.layout.count()-1)
        self.disconnect(self.pmtParent.getAttributeByName("type").editor,QtCore.SIGNAL("currentIndexChanged(QString)"), self.modifyEditor)
        self.editor = None
        self.layout.addWidget(self.guiCreateEditor())
        widgetToGetRidOf.widget().deleteLater()
    
    def modifyList(self, checkStatus):
        '''
        Slot called when an attribute's source changes.
        
        :param checkStatus:
        :type checkStatus: Not used
        '''
        sources = {"Environment variables": "#",
                   "Individual variables": "@",
                   "Local Variables": "%",
                   "Parameters": "$"}    
        if self.sender().text() == "Value":
            self.value = ""
            if self.pmtParent.xsdInfos.getAttribute(self.name).pairedAttr:
                #Paired attribute found, show it
                self.pmtParent.addAttributeByName(self.pmtParent.xsdInfos.getAttribute(self.name).pairedAttr)  
        else:
            self.value =  sources[self.sender().text()]
            if self.pmtParent.xsdInfos.getAttribute(self.name).pairedAttr:
                #Paired attribute found in xsd
                if self.pmtParent.hasAttribute(self.pmtParent.xsdInfos.getAttribute(self.name).pairedAttr):
                    #Paired attribute found, delete it
                    self.pmtParent.deleteAttribute(self.pmtParent.xsdInfos.getAttribute(self.name).pairedAttr)
                
        self.pmtParent.topWObject.updateProperties()
    
    def remove(self):
        '''
        Slot called when an unpaired optional attribute is removed from the GUI by user.
        '''
        self.pmtParent.deleteAttribute(self.name)
        self.pmtParent.topWObject.updateProperties()
        
    def checkSetChoice(self):
        '''
        Looks and sets (if needed) choice ComboBox.
        '''
        guiTypes = {"envVar": "Environment variables",
                    "indVar": "Individual variables",
                    "locVar": "Local Variables",
                    "param": "Parameters",
                    "value": ""}
        labels = {"envVariables": "Environment variables",
                  "indVariables": "Individual variables",
                  "locVariables": "Local Variables",
                  "allParameters": "Parameters",
                  "customValue": "Value"}
        if len(self.pmtParent.xsdInfos.getAttribute(self.name).behavior.list) > 1:
            pushButtonChoice = QtGui.QPushButton()
            pushButtonMenu = QtGui.QMenu()
            pushButtonActionGroup = QtGui.QActionGroup(pushButtonMenu) #to be sure checkable buttons are mutually exclusive
            for source in sorted([labels[sources["type"]] for sources in self.pmtParent.xsdInfos.getAttribute(self.name).behavior.list]):
                if source != "Value":
                    newAction = pushButtonMenu.addAction(source)
                    newAction.setCheckable(True)
                    self.connect(newAction,QtCore.SIGNAL("triggered(bool)"), self.modifyList)
                    pushButtonActionGroup.addAction(newAction)
                    if guiTypes[self.type] == source:
                        newAction.setChecked(True)
                else:
                    newAction = pushButtonMenu.addAction(source)
                    newAction.setCheckable(True)
                    self.connect(newAction,QtCore.SIGNAL("triggered(bool)"), self.modifyList)
                    pushButtonActionGroup.addAction(newAction)
                    if self.type == "value":
                        newAction.setChecked(True)    
            pushButtonChoice.setFixedWidth(20)
            pushButtonChoice.setMenu(pushButtonMenu)
            self.layout.addWidget(pushButtonChoice)
            self.choiceMenu = pushButtonActionGroup
            if not self.choiceMenu.checkedAction():
                #No action has not been set, probably a new attribute without the value option
                #Check first available option and set value consequently
                self.choiceMenu.actions()[0].setChecked(True)
                self.value = [key for key, value in self.typeDir.items() if value == [k for k, v in guiTypes.items() if v == self.choiceMenu.checkedAction().text()][0]][0]
        else:
            self.choiceMenu = None
            
    def _check(self):
        '''
        Looks for errors in attribute.
        
        :return: Boolean. True = error. False = everything is fine.
        '''
        attrInfos = self.pmtParent.xsdInfos.getAttribute(self.name)
        if not self.getValue():
            self.pmtParent.addValidityEvent( PrimitiveValidityEvent(self.pmtParent, "EmptyAttributeValue", [self.getMappedName()]))
            return True
        if attrInfos.isNull:
            self.pmtParent.addValidityEvent( PrimitiveValidityEvent(self.pmtParent, "BadAttribute", [self.getMappedName(), self.getValue()]))
            return True
        
        #Get expected type from XSD
        attrType = attrInfos.type
        
        #First, check if attribute has a defined GUI type
        if attrInfos.guiType:
            if self.type == "envVar":
                envModel = BaseEnvModel()
                if not envModel.variableExists(self.getValue()):
                    self.pmtParent.validityEventsList.append(PrimitiveValidityEvent(self.pmtParent,"UnknownVariable", [self.getValue(), self.pmtParent.name]))
                    return True
                if not self.pmtParent._matchType(attrInfos.guiType, envModel.getVarType(self.getValue())):
                    self.pmtParent.addValidityEvent( PrimitiveValidityEvent(self.pmtParent, "BadAttributeValue", [attrInfos.guiType, envModel.getVarType(self.getValue()), self.getMappedName()]))
                    return True
                return False
            elif self.type == "indVar":
                varModel = GeneratorBaseModel()
                if not varModel.variableExistsIgnoringSupPop(self.getValue()):
                    self.pmtParent.validityEventsList.append(PrimitiveValidityEvent(self.pmtParent,"UnknownVariable", [self.getValue(), self.pmtParent.name]))
                    return True
                if not self.pmtParent._matchType(attrInfos.guiType, varModel.getVarTypeIgnoringSubPop(self.getValue())):
                    self.pmtParent.addValidityEvent( PrimitiveValidityEvent(self.pmtParent, "BadAttributeValue", [attrInfos.guiType, varModel.getVarTypeIgnoringSubPop(self.getValue()), self.getMappedName()]))
                    return True
                return False
            elif self.type == "param":
                paramModel = BaseParametersModel()
                if not self.getValue() in paramModel.refVars.keys():
                    self.pmtParent.validityEventsList.append(PrimitiveValidityEvent(self.pmtParent,"UnknownParameter", [self.getValue()[4:], self.pmtParent.name]))
                    return True
                if not self.pmtParent._matchType(attrInfos.guiType, paramModel.refVars[self.getValue()]["type"]):
                    self.pmtParent.addValidityEvent( PrimitiveValidityEvent(self.pmtParent, "BadAttributeValue", [attrInfos.guiType, paramModel.refVars[self.getValue()]["type"], self.getMappedName()]))
                    return True
                return False
            elif self.type == "locVar":
                locVarModel = BaseLocalVariablesModel()
                indexNode = self.pmtParent.pmtRoot.pmtDomTree.parentNode()
                if self.getValue() not in locVarModel.getLocVarsList(indexNode):
                    self.pmtParent.validityEventsList.append(PrimitiveValidityEvent(self.pmtParent,"UnknownVariable", [self.getValue(), self.pmtParent.name]))
                    return True
                if not self.pmtParent._matchType(attrInfos.guiType, locVarModel.getLocalVarType(indexNode, self.getValue())):
                    self.pmtParent.addValidityEvent( PrimitiveValidityEvent(self.pmtParent, "BadAttributeValue", [attrInfos.guiType, locVarModel.getLocalVarType(indexNode, self.getValue()), self.getMappedName()]))
                    return True
                return False
            elif self.type == "value":
                #Attribute is in a line edit
                #Convert type and check as xsd type
                attrType = Definitions.typeToName(attrInfos.guiType)
        
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
            if not self.value.lower() in ["false","true"]:
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
                int(self.value)
            except ValueError:
                self.pmtParent.addValidityEvent( PrimitiveValidityEvent(self.pmtParent, "BadAttributeValue", [attrType, str(self.value), self.getMappedName()]))
                return True

        elif attrType == "unsignedLong":
            try:
                int(self.value)
            except ValueError:
                self.pmtParent.addValidityEvent( PrimitiveValidityEvent(self.pmtParent, "BadAttributeValue", [attrType, str(self.value), self.getMappedName()]))
                return True
            if int(self.value) < 0:
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
            if self.type == "indVar":
                varModel = GeneratorBaseModel()
                if not varModel.variableExistsIgnoringSupPop(self.getValue()):
                    self.pmtParent.validityEventsList.append(PrimitiveValidityEvent(self.pmtParent,"UnknownVariable", [self.getValue(), self.pmtParent.name]))
                    return True
            if self.type == "locVar":
                locVarModel = BaseLocalVariablesModel()
                indexNode = self.pmtParent.pmtRoot.pmtDomTree.parentNode()
                if self.getValue() not in locVarModel.getLocVarsList(indexNode):
                    self.pmtParent.validityEventsList.append(PrimitiveValidityEvent(self.pmtParent,"UnknownVariable", [self.getValue(), self.pmtParent.name]))
                    return True
            if self.type == "value":
                #Might be processes being listed
                if self.pmtParent.xsdInfos.getAttribute(self.name).behavior.list:
                    if len(self.pmtParent.xsdInfos.getAttribute(self.name).behavior.list) <= 1:
                        if "processes" == self.pmtParent.xsdInfos.getAttribute(self.name).behavior.list[0]["type"]:
                            #Make sure process exists
                            baseModelTr = BaseTreatmentsModel()
                            if self.getValue() not in baseModelTr.getTreatmentsDict().keys():
                                self.pmtParent.validityEventsList.append(PrimitiveValidityEvent(self.pmtParent,"UnknownProcess", [self.getValue(), self.pmtParent.guiname]))
                                return True
        return False
   
class Primitive(QtCore.QObject):
    '''
    This class represents a primitive.
    A primitive may contain primitive children and attributes.
    This class is just a wrapper over the simulator XML code, and is used to make a bridge between the xml code and the user's perspective of a tree node.
    '''
    
    def __init__(self, parentPrimitive, rootPrimitive, topWindowObject, XMLTree, autoMissingItemsFill=True, displayComments=True, name="Control_Nothing"): 
        """
        Constructor.
        
        :param parentPrimitive: The primitive parent of this primitive (null primitive if there's none).
        :param rootPrimitive: The primitive root of the tree this primitive belongs to (null primitive if this is the root).
        :param topWindowObject: MainFrame pointer.
        :param XMLTree: A QDomNode() representing this primitive.
        :param autoMissingItemsFill: Optional - If set to true, Primitive object will try to fill missing required children or attributes.
        :param displayComments: Optional - If set to true, Primitive object will parse XML comments and give users access to them.
        :param name: Optional - Name of the primitive.
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
        if self.xsdInfos.isNull:
            print("Warning : no information about primitive", self.name)
            self.autoMissingItemsFill = False   # We cannot display missing childs if we don't know the childs...
        
        self.childrenList = [] #Primitive children list
        self.attrList = {} #Primitive Attribute List
        self.userComment = "" #Xml node's first argument
        self.defaultComment = "" #Xml node's next sibling argument
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
        Returns child at given position as seen in GUI.
        
        :param childPos: Child's position in GUI.
        :type childPos: Int
        :return: :class:`.Primitive`.
        '''
        assert childPos < self.countChildren(), "Error in PrimitiveBaseModel::guiGetChild() : invalid childPos " + str(childPos) + ", length of childs list is " + str(self.guicountChildren())

        return self.childrenList[childPos]
    
    @property
    def guiname(self):
        '''
        Returns primitive's name as seen in GUI.
        
        :return: String
        '''
        if self.xsdInfos.isNull:
            return self.name
        else:
            if not self.xsdInfos.getMappedName():
                return self.name
            else:
                return self.xsdInfos.getMappedName()
    
    def guiCanDeleteChild(self):
        '''
        Tells if this primitive has enough children to see one being deleted.
        
        :return: Boolean.
        '''
        return self.countChildren() > self.xsdInfos.getMinimumNumChilds()
    
    def guiGetAttrDisplay(self):
        '''
        Returns Attribute information that is going to be displayed in the tree.
        
        :return: String.
        '''
        for attribute in self.nextAttribute():
            success,behavior = self.xsdInfos.getAttribute(attribute.name).behavior.getBehavior("displayValue")
            if success:
                if behavior and behavior["showAttr"]:
                    return attribute.getValue() + " " + behavior["delimiter"] + " " + self.getAttributeByName(behavior["showAttr"]).getValue(), behavior["position"]
                value = attribute.getValue()
                if attribute.type == "param":
                    value = attribute.getValue()[4:]    
                return value,behavior["position"]
    
    def guiGetBranchInfo(self):
        '''
        Returns a primitive's branch information.
        
        :return: String.
        '''
        if not self.pmtParent.xsdInfos.isNull and not self.pmtParent.xsdInfos.getSimpleOrderedChild(self.pmtParent.getChildPos(self)).isNull:   
            return self.pmtParent.xsdInfos.getSimpleOrderedChild(self.pmtParent.getChildPos(self)).toChoice().branchTag["en"]
                
    def guiGetBranchTag(self):
        '''
        Returns a primitive's branch tag.
        
        :return: Object list
        '''
        if "branchTag" in self.guiInfos.keys():
            return self.guiInfos["branchTag"]
        return []
    
    def guiSetBranchTag(self, newValue):
        '''
        Sets primitive's attribute value associated with branchTag.
        
        :param newValue: Primitive's new value as an object.
        '''
        if "branchTag" not in self.guiInfos.keys():
            self.guiInfos["branchTag"] = [True,True,0]
        self.guiInfos["branchTag"][2] = newValue
        self.pmtParent._updateAttribute(self.pmtParent.guiInfos["attrBranchMapped"])
                
    def guiDeleteChild(self, childPmt):
        '''
        Deletes a child.
        
        :param childPmt: Child's Primitive instance.
        :type childPmt: Int
        '''
        self.detachChild(self.getChildPos(childPmt))
        
    def guiGetChildPos(self, childPmt):
        '''
        Returns a child position in GUI.
        
        :param childPmt: Child's Primitive instance.
        :type childPmt: :class:`.Primitive`
        '''
        if childPmt in self.childrenList:
            return self.childrenList.index(childPmt)
        print("Warning: in Primitive::guiGetChildPos, childPmt not in childrenList")
    
    def guiCanHaveBranchTag(self, pmtChild):
        '''
        Tells if child can have a branch tag.
        
        :param pmtChild: Child's Primitive instance.
        :type pmtChild: Int
        :return: Boolean.
        '''
        for attrib in self.xsdInfos.getNextAttribute():
            if self.hasAttribute(attrib.name):
                success, branchBehavior = attrib.behavior.getBehavior("mapToBranches")
                if success:
                    childPos = self.guiGetChildPos(pmtChild)
                    if branchBehavior["startIndex"] <=  childPos:
                        if branchBehavior["endIndex"] >= childPos or branchBehavior["endIndex"] == -1:
                            return True

        return False

    def guiCreateEditor(self, parentObject):
        '''
        Creates the tab of the UserComment, and the tab of the definition if definition isn't empty.
        
        :param parentObject: Widget where the information is going to be shown.
        :type parentObject: PyQt4.QtGui.QTabWidget
        :return: QtGui.QTextBrowser
        '''
        userCommentWidget = QtGui.QTextBrowser()
        userCommentWidget.setReadOnly(False)
        self.guiSetEditorData(userCommentWidget, "Comment")
        parentObject.addTab(userCommentWidget, "User Comment")
        self.connect(userCommentWidget,QtCore.SIGNAL("textChanged()"), self.guiSetComment)
        if self.xsdInfos.getDocStr():
            definitionWidget = QtGui.QTextBrowser()
            definitionWidget.setReadOnly(True)
            self.guiSetEditorData(definitionWidget, "Definition")
            parentObject.addTab(definitionWidget, "Definition")
        
        return userCommentWidget
    
    def guiSetEditorData(self, editorWidget, option):
        '''
        Populates created editor.
        
        :param editorWidget: The editor.
        :param option: Definition or Comment.
        :type editorWidget: PyQt4.QtGui.QTextBrowser
        :type option: String
        '''
        if option == "Comment":
            editorWidget.setPlainText(self.userComment)
        elif option == "Definition":
            editorWidget.setPlainText(self.xsdInfos.getDocStr())
    
    def guiSetModelData(self, newPmtName, guiPosition):
        '''
        Replaces a child in model based on primitive name.
        
        :param newPmtName: Name of the newly added Primitive.
        :param guiPosition: Position of the replaced child in gui.
        :type newPmtName: String
        :type guiPosition: Int
        '''
        self.replaceChild(newPmtName, guiPosition)
    
    def guiReplaceModelData(self, guiPosition, xmlNode=QtXml.QDomNode()):
        '''
        Replaces a child in model based on a primitive xml node.
        
        :param guiPosition: Position of the replaced child in gui.
        :param xmlNode: Optional - Primitive's xml node.
        :type guiPosition: Int
        :type xmlNode: QtXml.QDomNode
        '''
        newPmt = Primitive(self, self.pmtRoot, self.topWObject, xmlNode,False)
        self.childrenList[guiPosition] = newPmt
        self._lookForBranchTag(newPmt)
        self._check(False)
        
    def guiAddChild(self, newPmtName, guiPosition, behaviorWanted="skip"):
        '''
        Adds a child to model.
        
        :param newPmtName: Child's primitive name.
        :param guiPosition: Position in gui.
        :param behaviorWanted: Optional - Behavior of the add function.
        :type newPmtName: String
        :type guiPosition: Int
        :type behaviorWanted: String
        '''
        if guiPosition >= len(self.childrenList):
            self.addChild(newPmtName, self.countChildren(), behaviorWanted)        
        else:
            self.addChild(newPmtName, guiPosition, behaviorWanted)
    
    def guiGetAttrLayout(self):
        '''
        Constructs the layout that is going to be used by the tree editor to display attribute information.
        
        :return: QtGui.QVBoxLayout. Layout to be used in tree editor.
        '''
        layout = QtGui.QVBoxLayout()
        self.optAttrComboBox = QtGui.QComboBox()
        for attribute in self.nextAttribute():
            layout.addLayout(attribute.getLayout())
        
        for attrib in self.xsdInfos.getNextAttribute():
            if not self.hasAttribute(attrib.name) and not attrib.required and not self.xsdInfos.isPaired(attrib.name):
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
        Creates the layout for optional attributes, like it is done in the attribute class.
        
        :return: QtGui.QHBoxLayout. Layout to be used in tree editor
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
        for i in range(self.optAttrComboBox.count()):
            if fm.width(self.optAttrComboBox.itemText(i)) > minimumWidth:
                minimumWidth = fm.width(self.optAttrComboBox.itemText(i))
        self.optAttrComboBox.view().setMinimumWidth(minimumWidth)
        #Calculate width for the combobox itself
        self.optAttrComboBox.setMinimumWidth(1)
        fontMetrics = QtGui.QFontMetrics(self.optAttrComboBox.font())
        self.optAttrComboBox.setMaximumWidth(fontMetrics.width(self.optAttrComboBox.currentText())+30)
        self.connect(addButton,QtCore.SIGNAL("pressed()"), self.addAttributeByWidget)
        
        return optAttrLayout
    
    def guiSetComment(self):
        '''
        Modifies user's comments.
        '''
        newComment = self.sender().document().toPlainText()
        self.userComment = newComment

    def guiDumpModelInfos(self):
        '''
        Useful debug function.
        '''
        print("Dumping Info for primitive named", self.name)
        print("Primtives's error list :", self.validityEventsList)
        print("Primitive's return Type is", self._getReturnType())
        print("Will dump info for children")
        for child in self.childrenList:
            childXSDInfo = self.xsdInfos.getSimpleOrderedChild(self.getChildPos(child)).toChoice()
            print("\t\t Was expecting a return Value of Type "+childXSDInfo.getAcceptedType()[0]+" defined by "+childXSDInfo.getAcceptedType()[1])
            print("\tChild "+child.name+" has a return Type of "+child._getReturnType())
        print ("Attributes are :", self.attrList.keys())
        print("Supposed Attributes are :")
        for child in self.xsdInfos.getNextAttribute():
            print(child.name)
        print("Branch Tag Info:")
        if "branchTag" in self.guiInfos:
            print(self.guiInfos["branchTag"])
        
    def guiDoubleClickBehavior(self):
        '''
        Tells if primitive has special behaviors triggered by a double click.
        
        :return: Boolean.
        '''
        return self.xsdInfos.getPrimitiveBehavior().hasBehavior("openOnDoubleClick")
    
    def guiIsHighlighted(self):
        '''
        Tells if primitive has to be highlighted, for whatever reason.
        
        :return: Boolean.
        '''
        return self.guiInfos["Highlighted"]
    
    def guiSetHighlighted(self, highlight):
        '''
        Sets Highlight status.
        
        :param highlight: New highlight status.
        :type highlight: Boolean.
        '''
        self.guiInfos["Highlighted"] = highlight
    
    '''
    /Section: Gui
    '''
    
    def getTreeSize(self):
        '''
        Returns tree's depth.
        '''
        currentCount = 1    #we have to count this primitive
        for child in self.childrenList:
            currentCount += child.getTreeSize()    
        return currentCount
    
    def addAttribute(self, newAttr, eraseIfPresent = True):
        '''
        Adds as attribute.
        
        :param newAttr: PrimitiveAttribute to add.
        :param eraseIfPresent: Optional - Delete primitive or not if present.
        '''
        if not newAttr.name in self.attrList.keys() or eraseIfPresent:
            self.attrList[newAttr.name] = newAttr
        else:
            print("Warning : unable to insert new attribute", newAttr.getAttrName(), ": already present")

    def addAttributeByName(self, newAttrName, newAttrValue="", eraseIfPresent=True):
        '''
        Adds an attribute.
        
        :param newAttrName: Attribute's name.
        :param newAttrValue: Optional - Attribute's value.
        :param eraseIfPresent: Optional - Delete primitive or not if present.
        :type newAttrName: String
        :type newAttrValue: String
        :type eraseIfPresent: Boolean
        '''
        self.addAttribute(PrimitiveAttribute(newAttrName, newAttrValue, self), eraseIfPresent)

    def addAttributeByWidget(self):
        '''
        Called when a button is pressed in the GUI.
        Tells the model to add an attribute. Attribute's mapped name can be found in optional attribute combobox.
        '''
        for attrib in self.xsdInfos.getNextAttribute():
            if attrib.getMappedName() == self.optAttrComboBox.currentText():
                self.addAttributeByName(attrib.name)
        self.topWObject.updateProperties()
    
    def deleteAttribute(self, attrName):
        '''
        Removes an attribute from attribute list.
        
        :param attrName: Attribute's name.
        :type attrName: String
        '''
        if not self.xsdInfos.getAttribute(attrName).required:
            self.attrList.pop(attrName)
        else:
            print("Error : Primitive::deleteAttribute, cannot delete required attribute named", attrName)
        
    def getAttributeByName(self, attrName):
        '''
        Returns an attribute.
        
        :param attrName: Attribute's name.
        :type attrName: String
        :return: :class:`.PrimitiveAttribute`.
        '''
        if attrName in self.attrList.keys():
            return self.attrList[attrName]
    
    def hasAttribute(self, attrName):
        '''
        Tells if this primitive has a given attribute.
        
        :param attrName: Name of the attribute we are looking for.
        :type attrName: String
        :return: Boolean.
        '''
        return attrName in self.attrList.keys()
    
    def nextAttribute(self):
        '''
        Primitive's attribute generator
        '''
        for attr in sorted(self.attrList.keys()):
            yield self.attrList[attr]
    
    def addChild(self, childName, childPos, behaviorIfPosAlreadyUsed="skip"): # shift, erase, skip
        '''
        Adds a child.
        
        :param childName: Child's name.
        :param childPos: Child's position.
        :param behaviorIfPosAlreadyUsed: Possible values are : shift, erase or skip.
        :type childName: String
        :type childPos: Int
        :type behaviorIfPosAlreadyUsed: String
        '''
        if childPos > len(self.childrenList):
            print("Warning in Primitive::addChild() : try to add a child at position", childPos, "on a primitive with", len(self.childrenList), "childs. Primitive will be added as last child.")
            childPos = len(self.childrenList)
        if behaviorIfPosAlreadyUsed == "skip" and childPos == len(self.childrenList):
            childPos -= 1
            
        #Construct new Child
        newChildNode = QtXml.QDomNode()
        newPmt = Primitive(self, self.pmtRoot, self.topWObject, newChildNode , True, self.displayComments,childName)
        
        if behaviorIfPosAlreadyUsed == "shift": 
            self.childrenList.insert(childPos, newPmt)
        elif behaviorIfPosAlreadyUsed == "erase":
            self.childrenList[childPos] = newPmt    
        elif behaviorIfPosAlreadyUsed == "skip":
            self.childrenList.insert(childPos+1, newPmt)
        else:
            print("Warning : unexpected behavior", behaviorIfPosAlreadyUsed, "in Primitive::addChild(), possible values are 'shift', 'skip' and 'erase'")

        for primitiveData in self.childrenList[self.getChildPos(newPmt):]:
            self._lookForBranchTag(primitiveData)

        if newPmt.autoMissingItemsFill:
            newPmt._lookForMissingChildren()
        
        self._check(False)
    
    def countChildren(self):
        '''
        Returns the number of child.
        
        :return: Int.
        '''
        return len(self.childrenList)
    
    def detachChild(self, childPos):
        '''
        Removes a child from the tree.
        
        :param childPos: Child's position in tree.
        :type childPos: Int
        '''
        if childPos >= len(self.childrenList):
            print("Warning : calling detachChild at position", childPos, "without any child already present")
        else:
            self.childrenList.pop(childPos)                
            for primitiveData in self.childrenList:
                self._lookForBranchTag(primitiveData)
    
    def getChild(self, childPos):
        '''
        Returns the child at given position.
        
        :param childPos: Child's position.
        :type childPos: Int
        :return: :class:`.PrimitiveAttribute`.
        '''
        return self.childrenList[childPos]
    
    def getChildPos(self, childPmt):
        '''
        Returns a child's position.
        
        :param childPmt: Child's primitive.
        :type childPmt: :class:`.PrimitiveAttribute`
        :return: Int.
        '''
        if childPmt in self.childrenList:
            return self.childrenList.index(childPmt)
            
        print("Warning: in Primitive::getChildPos, childPmt not in childrenList")  
    
    def replaceChild(self, childName, childPos):
        '''
        Replaces an already existing child by a new one.
        
        :param childName: New child name.
        :param childPos: New child position.
        '''
        if childPos >= len(self.childrenList):
            print("Warning : calling replaceChild at position", childPos, "without any child already present")
        else:
            self.addChild(childName, childPos, "erase")
    
    def addValidityEvent(self, eventObject):
        '''
        Adds a new event for this primitive.
        
        :param eventObject:
        :type eventObject: :class:`.PrimitiveValidityEvent`
        '''
        self.validityEventsList.append(eventObject)

    def getValidityList(self):
        '''
        Returns the simplified list of event for primitive.
        
        :return: String list.
        '''
        eventList = [events.eventRef.gravity for events in self.validityEventsList if events.isValid()]
        return eventList if len(eventList) != 0 else ["Valid"]
    
    def getValidityState(self):
        '''
        Returns the worst event this primitive hold.
        
        :return: String.
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
    
    def propagateHighlighting(self, similarPrimitive):
        '''
        Looks if given primitive is similar and set highlight status to True if it is.
        Propagate comparison to child primitives.
        Two primitive are similar if comparison primitive have the same name, attributes and attribute values for attributes whose values are defined.
        
        :param similarPrimitive: Primitive to compare.
        :type similarPrimitive: :class:`.PrimitiveAttribute`
        '''
        if similarPrimitive.name == self.name:
            self.guiSetHighlighted(True)
            for attribute in similarPrimitive.nextAttribute():
                if self.hasAttribute(attribute.name):
                    if attribute.value:
                        if attribute.value == self.getAttributeByName(attribute.name).value:
                            continue
                        else:
                            self.guiSetHighlighted(False)
                else:
                    self.guiSetHighlighted(False)
                    
        for childPmt in self.childrenList:
            childPmt.propagateHighlighting(similarPrimitive)
                
    def _check(self, childRecursiveCheck=True):
        '''
        Looks for errors in this tree.
        
        :param childRecursiveCheck: Optional - If True, check children too.
        '''
        
        prevListLength = len(self.validityEventsList)
        # If new event is True, then something new happened
        #If its false, make sure we check previousListLength to see if an event disappeared
        #If something happened, emit a signal to the view
        self.validityEventsList = []
        newEvent = False
        if self.xsdInfos.isNull:
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
        if typeDefBy == "parameterValue":
            baseModelRef = BaseParametersModel()
            refName = self.getAttributeByName(returnType).getValue()
            if not refName in baseModelRef.refVars.keys():
                self.validityEventsList.append(PrimitiveValidityEvent(self, "UnknownParameter", [refName, self.name]))
                newEvent = True
        
        #If defined by variable, make sure variable exists
        elif typeDefBy == "variableValue":
            baseModelVar = GeneratorBaseModel()
            baseModelEnv = BaseEnvModel()
            varName = self.getAttributeByName(returnType).getValue()

            if baseModelVar.variableExistsIgnoringSupPop(varName):
                pass
            elif baseModelEnv.variableExists(varName):
                pass
            else:
                self.validityEventsList.append(PrimitiveValidityEvent(self, "UnknownVariable", [varName, self.name]))
                newEvent = True
                
        #Attributes verification
        if True in [attribute._check() for attribute in self.nextAttribute()]:
            newEvent = True
        #Branch Tag verification
        for attribute in self.nextAttribute():
            success, branchBehavior = self.xsdInfos.getAttribute(attribute.name).behavior.getBehavior("mapToBranches")
            if attribute.type == "value" and attribute.name.endswith("_Type") and attribute.value in list(Definitions.typesToDefinitions.values()):
                #Make sure the type of an attribute is a base type
                attribute.value = Definitions.definitionToType(attribute.value)
                attribute.pmtParent.pmtDomTree.toElement().setAttribute(attribute.name, attribute.value)
            elif attribute.type == "value" and attribute.name.endswith("_Type") and attribute.value in Definitions.oldTypes:
                #The value must not be an old type
                attribute.value = Definitions.convertType(attribute.value)
                attribute.pmtParent.pmtDomTree.toElement().setAttribute(attribute.name, attribute.value)
            if success:
                #look for sum behavior
                if branchBehavior["sum"] != "0":
                    for child in self.childrenList:
                        #Make sure childList is up to date
                        self._lookForBranchTag(child)
                    currentSum = Decimal("0")
                    for child in self.childrenList:
                        if "branchTag" in child.guiInfos.keys():
                            if child.guiInfos["branchTag"][2]:
                                try:
                                    currentSum += Decimal(str(child.guiInfos["branchTag"][2]))
                                except ValueError:
                                    newEvent = PrimitiveValidityEvent(self, "BadBranchTag", [child.guiname, str(self.guiGetChildPos(child)), child.guiInfos["branchTag"][2]])
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
            
            if child.hasAttribute("inValue_Type") and child.getAttributeByName("inValue_Type").getValue() in Definitions.oldTypes:
                child.addAttributeByName("inValue_Type", Definitions.convertType(child.getAttributeByName("inValue_Type").getValue()))

            if childInfo.isNull:
                #No info found, there shouldn't even be a child at currentPos
                newEvent = PrimitiveValidityEvent(self, "BadChildPosition", [self.name, child.guiname, str(self.xsdInfos.getMaximumChilds()), str(currentPos)])
                self.validityEventsList.append(newEvent)
                newEvent = True
                
            elif childInfo.isChoice():
                #If this child can be a choice between multiple primitives
                #Look for that child is a valid choice
                if not childInfo.toChoice().isValidChoice(child.name):
                    newEvent = PrimitiveValidityEvent(self, "BadChild", [self.getChildPos(child), child.guiname, self.guiname])
                    self.validityEventsList.append(newEvent)
                    newEvent = True

            elif childInfo.isElement():
                #This child cannot be a choice, look if name found in info correspond to this child's name
                if childInfo.toElement().name != child.name:
                    newEvent = PrimitiveValidityEvent(self, "BadChild", [child.guiname, childInfo.toElement().name])
                    self.validityEventsList.append(newEvent)
                    newEvent = True
                
            else:
                #Something happened, we aren't supposed to get there
                print("Warning : unable to check for a choice or an element in xsd child list for child", currentPos)
            
            #Look that child has the right return type
            accType = "Any"
            obtainedType = child._getReturnType()
            accTypeDefBy, accTypeRef = childInfo.toChoice().getAcceptedType()
            if accTypeDefBy == "staticType":
                accType = accTypeRef
            elif accTypeDefBy == "argument":
                accType = self.childrenList[int(accTypeRef)-1]._getReturnType()
            elif accTypeDefBy == "variableValue":
                if self.getAttributeByName(accTypeRef).type == "indVar":
                    varModel = GeneratorBaseModel()
                    if not varModel.variableExistsIgnoringSupPop(self.getAttributeByName(accTypeRef).getValue()):
                        accType = "Any"
                    else:
                        accType = varModel.getVarTypeIgnoringSubPop(self.getAttributeByName(accTypeRef).getValue())
                elif self.getAttributeByName(accTypeRef).type == "locVar":
                    locVarModel = BaseLocalVariablesModel()
                    if not self.getAttributeByName(accTypeRef).getValue() in locVarModel.getLocVarsList(self.pmtRoot.pmtDomTree.parentNode()):
                        accType = "Any"
                    else:
                        accType = locVarModel.getLocalVarType(self.pmtRoot.pmtDomTree.parentNode(), self.getAttributeByName(accTypeRef).getValue())
                else:
                    accType = "Any"

            if not self._matchType(accType, obtainedType):
                newEvent = PrimitiveValidityEvent(self, "BadChildReturnValue", [str(currentPos), Definitions.typeToDefinition(accType), Definitions.typeToDefinition(obtainedType)])
                self.validityEventsList.append(newEvent)
                newEvent = True
            
            if childRecursiveCheck:
                #Child checks itself
                child._check()
                
            #Increment position and pass to next child
            currentPos += 1
        
        #Verification of the primitive "Set variable value"
        if self.name == "Data_SetVariable":
            outVariable = self.attrList["outVariable"]
            value = self.attrList["inValue"]
            
            #Getting the type of the output variable
            if outVariable.type == "envVar":
                envModel = BaseEnvModel()
                outVariableType = envModel.getVarType(outVariable.getValue())
            elif outVariable.type == "indVar":
                varModel = GeneratorBaseModel()
                outVariableType = varModel.getVarTypeIgnoringSubPop(outVariable.getValue())
            elif outVariable.type == "param":
                paramModel = BaseParametersModel()
                outVariableType = paramModel.refVars[outVariable.getValue()]["type"]
            elif outVariable.type == "locVar":
                locVarModel = BaseLocalVariablesModel()
                indexNode = outVariable.pmtParent.pmtRoot.pmtDomTree.parentNode()
                outVariableType = locVarModel.getLocalVarType(indexNode, outVariable.getValue())
            else:
                outVariableType = "Unknown"
                
            #Getting the type of the value
            if "inValue_Type" in self.attrList:
                valueType = self.attrList["inValue_Type"].value
            else:
                if value.type == "envVar":
                    envModel = BaseEnvModel()
                    valueType = envModel.getVarType(value.getValue())
                elif value.type == "indVar":
                    varModel = GeneratorBaseModel()
                    valueType = varModel.getVarTypeIgnoringSubPop(value.getValue())
                elif value.type == "param":
                    paramModel = BaseParametersModel()
                    valueType = paramModel.refVars[value.getValue()]["type"]
                elif value.type == "locVar":
                    locVarModel = BaseLocalVariablesModel()
                    indexNode = value.pmtParent.pmtRoot.pmtDomTree.parentNode()
                    valueType = locVarModel.getLocalVarType(indexNode, value.getValue())
                elif value.pmtParent.xsdInfos.getAttribute(value.name).guiType:
                    valueType = value.pmtParent.xsdInfos.getAttribute(value.name).guiType
                else:
                    valueType = "Unknown"
                    
            outVariableType = Definitions.typeToDefinition(outVariableType)
            valueType = Definitions.typeToDefinition(valueType)
            
            if outVariableType != valueType and outVariableType != "Unknown" and valueType:
                newEvent = PrimitiveValidityEvent(self, "BadAttributeValue", [outVariableType, valueType, value.getMappedName()])
                self.validityEventsList.append(newEvent)
                newEvent = True
            
        #Verification of the primitive if it's "Result to variable" or a comparison
        if not self.childrenList and self.attrList.keys():
            if set(["inArgLeft", "inArgRight"]) <= set(self.attrList.keys()):
                #We are in a case where all the attributes above exist in the primitive
                leftArg = self.attrList["inArgLeft"]
                rightArg = self.attrList["inArgRight"]
                
                
                #Getting the type of the right argument
                if "inArgRight_Type" in self.attrList.keys():
                    #Right number is a "value"
                    rightTypeArg = self.attrList["inArgRight_Type"].value
                else:
                    if rightArg.type == "envVar":
                        envModel = BaseEnvModel()
                        rightTypeArg = envModel.getVarType(rightArg.getValue())
                    elif rightArg.type == "indVar":
                        varModel = GeneratorBaseModel()
                        rightTypeArg = varModel.getVarTypeIgnoringSubPop(rightArg.getValue())
                    elif rightArg.type == "param":
                        paramModel = BaseParametersModel()
                        rightTypeArg = paramModel.refVars[rightArg.getValue()]["type"]
                    elif rightArg.type == "locVar":
                        locVarModel = BaseLocalVariablesModel()
                        indexNode = rightArg.pmtParent.pmtRoot.pmtDomTree.parentNode()
                        rightTypeArg = locVarModel.getLocalVarType(indexNode, rightArg.getValue())
                    elif rightArg.pmtParent.xsdInfos.getAttribute(rightArg.name).guiType:
                        rightTypeArg = rightArg.pmtParent.xsdInfos.getAttribute(rightArg.name).guiType
                    else:
                        rightTypeArg = "Unknown"
                rightTypeArg = Definitions.typeToDefinition(rightTypeArg)
                
                #Getting the type of the left argument
                if "inArgLeft_Type" in self.attrList.keys():
                    #Right number is a "value"
                    leftArgType = self.attrList["inArgLeft_Type"].value
                else:
                    if leftArg.type == "envVar" and leftArg.getValue():
                        envModel = BaseEnvModel()
                        leftArgType = envModel.getVarType(leftArg.getValue())
                    elif leftArg.type == "indVar" and leftArg.getValue():
                        varModel = GeneratorBaseModel()
                        leftArgType = varModel.getVarTypeIgnoringSubPop(leftArg.getValue())
                    elif leftArg.type == "param" and leftArg.getValue():
                        paramModel = BaseParametersModel()
                        leftArgType = paramModel.refVars[leftArg.getValue()]["type"]
                    elif leftArg.type == "locVar" and leftArg.getValue():
                        locVarModel = BaseLocalVariablesModel()
                        indexNode = leftArg.pmtParent.pmtRoot.pmtDomTree.parentNode()
                        leftArgType = locVarModel.getLocalVarType(indexNode, leftArg.getValue())
                    else:
                        leftArgType = "Unknown"
                leftArgType = Definitions.typeToDefinition(leftArgType)
                    
                if "outResult" in self.attrList.keys():
                    outVariable = self.attrList["outResult"]
                    #Getting the type of the output variable
                    if outVariable.type == "envVar":
                        envModel = BaseEnvModel()
                        outVariableType = envModel.getVarType(outVariable.getValue())
                    elif outVariable.type == "indVar":
                        varModel = GeneratorBaseModel()
                        outVariableType = varModel.getVarTypeIgnoringSubPop(outVariable.getValue())
                    elif outVariable.type == "param":
                        paramModel = BaseParametersModel()
                        outVariableType = paramModel.refVars[outVariable.getValue()]["type"]
                    elif outVariable.type == "locVar":
                        locVarModel = BaseLocalVariablesModel()
                        indexNode = outVariable.pmtParent.pmtRoot.pmtDomTree.parentNode()
                        outVariableType = locVarModel.getLocalVarType(indexNode, outVariable.getValue())
                    else:
                        outVariableType = "Unknown"
                    outVariableType = Definitions.typeToDefinition(outVariableType)
                else:
                    outVariableType = "Unknown"
                    
                #Checking if there is an "inValue" attribute
                if "inValue" in self.attrList.keys():
                    if "inValue_Type" in self.attrList.keys():
                        inValueType = self.attrList["inValue_Type"].value
                    else:
                        inValue = self.attrList["inValue"]
                        #Getting the type of the output variable
                        if inValue.type == "envVar":
                            envModel = BaseEnvModel()
                            inValueType = envModel.getVarType(inValue.getValue())
                        elif inValue.type == "indVar":
                            varModel = GeneratorBaseModel()
                            inValueType = varModel.getVarTypeIgnoringSubPop(inValue.getValue())
                        elif inValue.type == "param":
                            paramModel = BaseParametersModel()
                            inValueType = paramModel.refVars[inValue.getValue()]["type"]
                        elif inValue.type == "locVar":
                            locVarModel = BaseLocalVariablesModel()
                            indexNode = inValue.pmtParent.pmtRoot.pmtDomTree.parentNode()
                            inValueType = locVarModel.getLocalVarType(indexNode, inValue.getValue())
                        else:
                            inValueType = "Unknown"
                else:
                    inValueType = "Unknown"
                inValueType = Definitions.typeToDefinition(inValueType)
                
                #Case where there is an ouput result and a right argument
                if outVariableType != rightTypeArg and outVariableType != "Unknown" and rightTypeArg:
                    newEvent = PrimitiveValidityEvent(self, "BadAttributeValue", [outVariableType, rightTypeArg, rightArg.getMappedName()])
                    self.validityEventsList.append(newEvent)
                    newEvent = True
                #Case where there is an ouput result and a left argument
                if outVariableType != leftArgType and outVariableType != "Unknown" and leftArgType:
                    newEvent = PrimitiveValidityEvent(self, "BadAttributeValue", [outVariableType, leftArgType, leftArg.getMappedName()])
                    self.validityEventsList.append(newEvent)
                    newEvent = True
                #Case where there isn't an output result and neither an inValue. So only checking the type of left and right arguments
                if not "outResult" in self.attrList.keys() and not "inValue" in self.attrList.keys():
                    if rightTypeArg != leftArgType:
                        newEvent = PrimitiveValidityEvent(self, "BadAttributeValue", [leftArgType, rightTypeArg, rightArg.getMappedName()])
                        self.validityEventsList.append(newEvent)
                        newEvent = True
                elif not "outResult" in self.attrList.keys():
                    if rightTypeArg != inValueType:
                        newEvent = PrimitiveValidityEvent(self, "BadAttributeValue", [inValueType, rightTypeArg, rightArg.getMappedName()])
                        self.validityEventsList.append(newEvent)
                        newEvent = True
                    elif leftArgType != inValueType:
                        newEvent = PrimitiveValidityEvent(self, "BadAttributeValue", [inValueType, leftArgType, rightArg.getMappedName()])
                        self.validityEventsList.append(newEvent)
                        newEvent = True
                elif not "inValue" in self.attrList.keys():
                    if rightTypeArg != outVariableType:
                        newEvent = PrimitiveValidityEvent(self, "BadAttributeValue", [outVariableType, rightTypeArg, rightArg.getMappedName()])
                        self.validityEventsList.append(newEvent)
                        newEvent = True
                    elif leftArgType != outVariableType:
                        newEvent = PrimitiveValidityEvent(self, "BadAttributeValue", [outVariableType, leftArgType, rightArg.getMappedName()])
                        self.validityEventsList.append(newEvent)
                        newEvent = True
            
        self._findWorstEvent()
        if len(self.validityEventsList) < prevListLength or newEvent:
            #An error was corrected, emit signal and tell parent if parent has errors
            #We tell parent because parent's error might be coming from self's own error
            self.emit(QtCore.SIGNAL("ErrorFound()"))
            if not self.isRootPmt:
                if self.pmtParent.getValidityList() != ["Valid"]:
                    self.pmtParent._check(False)
                    
    def _findWorstEvent(self, includeSelf=False):
        '''
        Finds the primitive's worst event.
        
        :param includeSelf: Optional - Whether or not check itself.
        :return: String.
        '''
        eventDict = {"Unknown" : 0,
                     "Valid" : 1,
                     "Warning" : 2,
                     "Error" : 3}
        
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
        Gets returned tree's returned type for this primitive.
        
        :return: String.
        '''
        typeDefBy, returnType = self.xsdInfos.getReturnType()
        #If type is defined by argument, which means by the return type of one of its children
        if typeDefBy == "argument":
            if int(returnType) == -1:
                dataReturnPos = -1
            else:
                dataReturnPos = int(returnType) - 1
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
            if trName in baseModelTr.processesModelMapper:
                processDict = baseModelTr.getTreatmentsDict()
            else:
                return "Any"
            tmpPrimitive = PrimitiveSimplified(None, None, self.topWObject, processDict[str(trName)].firstChildElement("PrimitiveTree").firstChild())
            return tmpPrimitive._getReturnType()
        
        elif typeDefBy == "staticType":
            #If type is static, return
            return Definitions.definitionToType(returnType)
        
        elif typeDefBy == "attributeValue":
            #If type is defined by the value of an attribute
            if self.getAttributeByName(returnType):
                return Definitions.definitionToType(self.getAttributeByName(returnType).getValue())
            else:
                #try to see if returnType matches *_Type
                try : 
                    mainAttr = self.getAttributeByName(returnType[:-5])
                    if mainAttr:
                        attrType = mainAttr.type 
                        if attrType == "value":
                            print("Warning : In PrimitiveBaseModel::_getReturnType, value attribute doesn't have its optional counterpart, returning Any")
                            return "Any"
                        elif attrType == "param":
                            paramModel = BaseParametersModel()
                            return paramModel.refVars[mainAttr.getValue()]["type"]
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
            if refName in baseModelRef.refVars.keys():
                return baseModelRef.refVars[refName]["type"]
            else:
                return "Any"
        
        elif typeDefBy == "commonType":
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
                  
            LCAFinder = LCA(Definitions.treeTypes)
            currentCommonType = typeList[0]
            for currentTestedType in typeList[1:-1]:
                currentCommonType = LCAFinder(currentCommonType,currentTestedType)
                
            return currentCommonType
        
        else:
            print("Warning : Bad return type definition '"+ typeDefBy + "', will accept Any return value")
            return "Any"
   
    def _matchType(self, acceptedType, obtainedType):
        '''
        Tells if the type obtained in the corresponds the one required by DocPrimitive.
        
        :param acceptedType: DocPrimitive's requirement.
        :param obtainedType: Type obtained in tree.
        :type acceptedType: String
        :type obtainedType: String
        :return: Boolean.
        '''
        if acceptedType.lower() == obtainedType.lower():
            return True

        if acceptedType.lower() == "any":
            return True
        elif acceptedType.lower() == "integer":
            return obtainedType in Definitions.integerTypes
        elif acceptedType.lower() == "number":
            return obtainedType in Definitions.numberTypes
        elif acceptedType.lower() == "atom":
            return obtainedType in Definitions.atomTypes
        elif acceptedType.lower() == "float":
            return obtainedType in Definitions.floatTypes

        return False
          
    def _lookForMissingChildren(self):
        '''
        Looks for children that are supposed to be in the tree but aren't.
        '''
        if  len(self.childrenList) < self.xsdInfos.getMinimumNumChilds():
            #Loop (i missing children) time
            for _ in range(self.xsdInfos.getMinimumNumChilds()-len(self.childrenList)):
                #Create child and execute common function
                newPmt = Primitive(self, self.pmtRoot, self.topWObject, QtXml.QDomNode(), True, self.displayComments)
                self.childrenList.append(newPmt)
                self._lookForBranchTag(newPmt)
                    
    def _lookForMissingAttribute(self):
        '''
        Looks for attributes that are supposed to be in the tree but aren't.
        '''
        if len(self.attrList) < self.xsdInfos.howManyAttributes():
            for attrib in self.xsdInfos.getNextAttribute():
                #if attrib.name not in self.attrList and attrib.required:
                if attrib.name not in self.attrList and attrib.required:
                    self.addAttribute(PrimitiveAttribute(attrib.name, attrib.defValue, self))

    def _lookForBranchTag(self, newChild):
        '''
        Looks in attribute list and find if child has a branch tag.
        
        :param newChild: Child to eventually add a branch tag to.
        :type newChild: :class:`.Primitive`
        '''
        self.guiInfos["attrBranchMapped"] = None
        for attrib in self.nextAttribute():
            attrXSDInfos = self.xsdInfos.getAttribute(attrib.name)
            success, branchBehavior = attrXSDInfos.behavior.getBehavior("mapToBranches")
            if success:
                self.guiInfos["attrBranchMapped"] = self.getAttributeByName(attrib.name)
                break

        #After loop, look in guiInfos if an attribute has to be branch Mapped
        if self.guiInfos["attrBranchMapped"]:
            if self.guiInfos["attrBranchMapped"].type == "value":
                editable = branchBehavior["editable"]
                #Split attribute using regexp and create a list with values that can be mapped to child according to position
                if branchBehavior["regexp"]:
                    valueList = self.guiInfos["attrBranchMapped"].getValue().split(branchBehavior["regexp"])
                elif not branchBehavior["editable"] and branchBehavior["sum"] != '0':
                    #Branch isn't a normal branch, sum dictates how branch is supposed to behave
                    if int(branchBehavior["startIndex"]) == self.guiGetChildPos(newChild) and int(branchBehavior["endIndex"]) == self.guiGetChildPos(newChild):
                        try:
                            value = str(Decimal(branchBehavior["sum"]) - Decimal(self.guiInfos["attrBranchMapped"].getValue()))
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
                            value = Decimal(self.guiInfos["attrBranchMapped"].getValue())
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
                success, branchBehavior = self.xsdInfos.getAttribute(self.guiInfos["attrBranchMapped"].name).behavior.getBehavior("mapToBranches")
                valueList = []
                if self.guiInfos["attrBranchMapped"].type == "envVar":
                    #Warning : Will only tell if sum is good at the beginning of the simulation
                    envModel = BaseEnvModel()
                    if envModel.variableExists(self.guiInfos["attrBranchMapped"].getValue()):
                        valueList = envModel.getVarValue(self.guiInfos["attrBranchMapped"].getValue())
                elif self.guiInfos["attrBranchMapped"].type == "indVar":
                    #Cannot actually find a way to tell if branching sums to 1
                    pass
                elif self.guiInfos["attrBranchMapped"].type == "param":
                    paramModel = BaseParametersModel()
                    if paramModel.referenceExists(self.guiInfos["attrBranchMapped"].getValue()[4:]):
                        valueList = paramModel.getValue(self.guiInfos["attrBranchMapped"].getValue())
                elif self.guiInfos["attrBranchMapped"].type == "locVar":
                    locVarModel = BaseLocalVariablesModel()
                    if self.guiInfos["attrBranchMapped"].getValue() in locVarModel.getLocVarsList(self.pmtRoot.pmtDomTree.parentNode()):
                        valueList = locVarModel.getLocalVarValue(self.pmtRoot.pmtDomTree.parentNode(), self.guiInfos["attrBranchMapped"].getValue())
                
                if valueList and not branchBehavior["regexp"]:
                    #Branch isn't a normal branch, sum dictates how branch is supposed to behave
                    if int(branchBehavior["startIndex"]) == self.guiGetChildPos(newChild) and int(branchBehavior["endIndex"]) == self.guiGetChildPos(newChild):
                        try:
                            value = str(Decimal(branchBehavior["sum"]) - Decimal(valueList[0]))
                        except ValueError:
                            #If attribute's value is empty or not castable
                            value = ""
                        newChild.guiInfos["branchTag"] = [branchBehavior["displayAttribute"], editable,value]
                        newChild.emit(QtCore.SIGNAL("updateBranchTag()"))
                        return
                    elif self.guiGetChildPos(newChild) == 0:
                        #Since we only have the 2 branches Branching primitive defined yet
                        #First child has to be the attribute's value
                        try:
                            value = Decimal(valueList[0])
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
                    newChild.guiInfos["branchTag"] = [branchBehavior["displayAttribute"], editable, value]
                else:
                    #Since list is not long enough for this child's position, add an exclamation mark to tell user this branch tag has to be filled
                    newChild.guiInfos["branchTag"] = [branchBehavior["displayAttribute"], editable, ""]
            
            newChild.emit(QtCore.SIGNAL("updateBranchTag()"))
        
    def _updateAttribute(self, attribute):
        '''
        This function is a slot called when a user modifies a branch tag via a MedTreeEditableBranchTag.
        This way, the attribute's value is updated.
        
        :param attribute: The attribute associated to the branch tag.
        '''
        assert attribute.name in self.attrList.keys(), "In Primitive::_updateAttribute, unknown attribute : " + attribute.name
        #Call DocPrimitive and get mapToBranches behavior
        _,behaviorInfo = self.xsdInfos.getAttribute(attribute.name).behavior.getBehavior("mapToBranches")
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
        if not attribute.editor is None:
            attribute.guiSetEditorData(attribute.editor)
            attribute.guiUpdateWidgetGeometry(attribute.value)
        
        self._check()

    def _parseName(self):
        '''
        Parses primitive's name.
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
        
        for i in range(self.attrCount):
            lCurrentAttribute = lQAttributes.item(i).toAttr()
            trimmed_value = "".join(lCurrentAttribute.value().split())
            appendedAttr = PrimitiveAttribute(lCurrentAttribute.name(), trimmed_value, self)
            self.attrList[lCurrentAttribute.name()] = appendedAttr
        
        if self.autoMissingItemsFill:
            self._lookForMissingAttribute()
    
    def _checkForSimilarDoms(self, comparedDom):
        '''
        Since no function exists to check if two DOM instances are similar,
        this function loops through child, comments and attributes and test if elements are equals.
        
        :param comparedDom: The dom node to compare with this node.
        :type comparedDom: PyQt4.QtXml.QDomNode
        :return: Boolean.
        '''
        selfDom = self._writeDom(comparedDom.ownerDocument())
        #Attributes check
        if not selfDom.toElement().attributes().count() == comparedDom.toElement().attributes().count():
            return False
        for i in range(selfDom.toElement().attributes().count()):
            attrName = selfDom.toElement().attributes().item(i).toAttr().name()
            if not comparedDom.toElement().hasAttribute(attrName):
                return False
            if not comparedDom.toElement().attribute(attrName) == selfDom.toElement().attribute(attrName):
                return False
        
        #Comments and child list check
        if not selfDom.childNodes().count() == comparedDom.childNodes().count():
            return False
        commentCompteur = 0
        for i in range(selfDom.childNodes().count()):
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
        Creates complete DOM of this primitive and returns it as a string.
        
        :param tmpDoc:
        :type tmpDoc: PyQt4.QtXml.QDomDocument
        :return: PyQt4.QtXml.QDomElement
        '''
        domNode = tmpDoc.createElement(self.name)
        if self.userComment:
            newUserCommentNode = tmpDoc.createComment(self.userComment)
            domNode.appendChild(newUserCommentNode)
        for children in self.childrenList:
            domNode.appendChild(children._writeDom(tmpDoc))
            if children.defaultComment != "":
                newDefaultCommentNode = tmpDoc.createComment(children.defaultComment)
                domNode.appendChild(newDefaultCommentNode)
    
        for attributes in self.attrList.keys():
            domNode.toElement().setAttribute(attributes, self.attrList[attributes].value)
        return domNode

class PrimitiveAttributeSimplified(QtCore.QObject):
    '''
    This class represents the attribute of a Primitive, in a simplified way so the validator is more efficient(memory and CPU).
    '''
    __slots__ = ('pmtParent','name','value')
    def __init__(self, name, value, parentPrimitive):
        '''
        Constructor.
        
        :param name: Attribute's name.
        :param value: Attribute's value.
        :param parentPrimitive: Attribute's primitive.
        :param mappedFromPrimitive: Tells if this attribute is mapped from a primitive.
        :param mappedPmtField: Mapped pmt field.
        :param mappedPmt: Mapped pmt.
        '''
        QtCore.QObject.__init__(self)
        self.pmtParent =  parentPrimitive
        self.name = name
        self.value = str(value)
  
    
    def getValue(self):
        '''
        Returns as attribute's value, without wildcard.
        
        :return: String.
        '''
        if not self.value:
            return self.value
        if not self.value[0] in "#@$%":
            return self.value
        return self.value[1:]
    
    @property    
    def type(self):
        '''
        Returns where this attribute comes from
        Possible values : indVar, envVar, param, locVar and value.
        
        :return: String.
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
    This class represents a primitive.
    A primitive may contain primitive children and attributes.
    This class is just a wrapper over the simulator XML code, and is used to make a bridge between the xml code and the user's perspective of a tree node.
    It is only used to speed up the validation of trees, because this class is much smaller than the one above.
    '''
    __slots__ = ('pmtRoot', 'topWObject', 'pmtDomTree','autoMissingItemsFill','childrenList','pmtParent','name','xsdInfos','attrList','isRootPmt','worstEvent') 
    def __init__(self, parentPrimitive, rootPrimitive, topWindowObject, XMLTree, autoMissingItemsFill=True, name="Control_Nothing"): 
        """
        Constructor.
        
        :param parentPrimitive: The primitive parent of this primitive (null primitive if there's none).
        :param rootPrimitive: The primitive root of the tree this primitive belongs to (null primitive if this is the root).
        :param topWindowObject: MainFrame pointer.
        :param XMLTree: A QDomNode() representing this primitive.
        :param autoMissingItemsFill: Optional - If set to true, Primitive object will try to fill missing required children or attributes.
        :param displayComments: Optional - If set to true, Primitive object will parse XML comments and give access to them to the user.
        :param name: Optional - Name of the primitive.
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
        if self.xsdInfos.isNull:
            print("Warning : no information about primitive", self.name)
            self.autoMissingItemsFill = False   # We cannot display missing childs if we don't know the childs...
        
        self.childrenList = [] #Primitive children list
        self.attrList = {} #Primitive Attribute List
        if self.pmtParent is None:
            self.isRootPmt = True
            self.pmtRoot = self
            self.worstEvent = "Unknown"
        else:
            self.isRootPmt = False
       
    def countChildren(self):
        '''
        Returns the number of child.
        
        :return: Int.
        '''
        return len(self.childrenList)
    
    def getAttributeByName(self, attrName):
        '''
        Returns an attribute.
        
        :param attrName: Attribute's name.
        :return: :class:`.PrimitiveAttributeSimplified`.
        '''
        if attrName in self.attrList.keys():
            return self.attrList[attrName]

    def getChild(self, childPos):
        '''
        Return child at given position
        @param childPos : child's position
        '''
        return self.childrenList[childPos]
    
    def _lookForMissingChildren(self):
        '''
        Looks for children that are supposed to be in the tree but aren't
        '''
        if  len(self.childrenList) < self.xsdInfos.getMinimumNumChilds():
            #Loop (all missing children) time
            for _ in range(self.xsdInfos.getMinimumNumChilds()-len(self.childrenList)):
                #Create child and execute common function
                newPmt = PrimitiveSimplified(self, self.pmtRoot, self.topWObject, QtXml.QDomNode(), True)
                self.childrenList.append(newPmt)
                    
    def _lookForMissingAttribute(self):
        '''
        Looks for attributes that are supposed to be in the tree but aren't
        '''
        if len(self.attrList) < self.xsdInfos.howManyAttributes():
            for attrib in self.xsdInfos.getNextAttribute():
                #if attrib.name not in self.attrList and attrib.required:
                if attrib.name not in self.attrList and attrib.required:
                    self.attrList[attrib.name] = PrimitiveAttributeSimplified(attrib.name, attrib.defValue, self)

    def _getReturnType(self):
        '''
        Get returned tree's returned type for this primitive
        '''
        typeDefBy, returnType = self.xsdInfos.getReturnType()
        #If type is defined by argument, which means by the return type of one of its children
        if typeDefBy == "argument":
            if int(returnType) == -1:
                dataReturnPos = -1
            else:
                dataReturnPos = int(returnType) - 1
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
            if trName in baseModelTr.processesModelMapper:
                processDict = baseModelTr.getTreatmentsDict()
            else:
                return "Any"
            
            tmpPrimitive = PrimitiveSimplified(None, None, self.topWObject, processDict[trName].firstChildElement("PrimitiveTree").firstChild())
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
                        attrType = mainAttr.type 
                        if attrType == "value":
                            return "Any"
                        elif attrType == "param":
                            paramModel = BaseParametersModel()
                            return paramModel.refVars[mainAttr.getValue()]["type"]
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
            if refName in baseModelRef.refVars.keys():
                return baseModelRef.refVars[refName]["type"]
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
            LCAFinder = LCA(Definitions.treeTypes)
            currentCommonType = typeList[0]
            for currentTestedType in typeList[1:-1]:
                currentCommonType = LCAFinder(currentCommonType,currentTestedType)
                
            return currentCommonType
        
        else:
            print("Warning : Bad return type definition '"+ typeDefBy + "', will accept Any return value")
            return "Any"

    def _parseName(self):
        '''
        Parse primitive's name
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
        
        for i in range(self.attrCount):
            lCurrentAttribute = lQAttributes.item(i).toAttr()
            trimmed_value = "".join(lCurrentAttribute.value().split())
            appendedAttr = PrimitiveAttributeSimplified(lCurrentAttribute.name(), trimmed_value, self)
            self.attrList[lCurrentAttribute.name()] = appendedAttr
        
        if self.autoMissingItemsFill:
            self._lookForMissingAttribute()
    
