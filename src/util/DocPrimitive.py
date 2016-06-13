"""
.. module:: DocPrimitive

.. codeauthor:: Marc-André Gardner

:Created on: 2009-09-18

"""
from PyQt4.QtXml import QDomNode
from PyQt4 import QtCore
from PyQt4.QtGui import QColor
from util.opener import Opener
from functools import wraps

def fakeSingleton(PrimitiveDict):
    '''
    Python Decorator, emulates a singleton behavior.
    It emulates the behavior because if the user passes arguments to the constructor, we implicitly consider he wants a new instance of PrimitiveDcit
    Else, its acts as a singleton
    '''
    instance_container = []
    '''
    Wrapper function
    '''
    @wraps(PrimitiveDict)
    def wrapper(*args):
        if not len(instance_container):
            #Create PrimitiveDict if it doesn't exist
            instance_container.append(PrimitiveDict(*args))
        elif len(args):
            #If it exists and arguments are passed through the constructor, create new instance
            instance_container[0] = PrimitiveDict(*args)
        #return singleton or new instance
        return instance_container[0]
    return wrapper

@fakeSingleton
class PrimitiveDict():
    '''
    Container for the xsd files loaded in a simulation and their corresponding Doc* objects.
    '''
    def __init__(self, topObject, xsdFilesList=[]):
        '''
        Constructor.
        
        :param topObject : Application's main window
        :param xsdFilesList : Optional - List of .xsd file names
        :type topObject: :class:`.MainFrame`
        :type xsdFilesList: String list
        '''
        self.dictPrimitives = {}
        self.dictAbstractPrimitives = {}
        self.dictComplexTypes = {}
        self.dictListInfos = {}
        self.topObject = topObject

        if len(xsdFilesList) != 0:
            for xsdFile in xsdFilesList:
                self.addFromXSD(xsdFile)

    def addFromXSD(self, xsdFile, reopenIfAlreadyLoaded=False):
        '''
        Adds primitives from .xsd file.
        
        :param xsdFile : .xsd primitive dictionary file name.
        :param reopenIfAlreadyLoaded : Optional - Load or not if .xsd file is already loaded.
        :type xsdFile: String
        :type reopenIfAlreadyLoaded: Boolean
        '''
        if xsdFile in self.dictPrimitives.keys():
            if not reopenIfAlreadyLoaded:
                print("Tentative to reload", xsdFile, "aborted : already opened.")
                return
            else:
                print("Notice : reloading xsd file named :", xsdFile)

        if xsdFile:
            self.dictPrimitives[xsdFile] = {}
            self.dictAbstractPrimitives[xsdFile] = {}
            self.dictComplexTypes[xsdFile] = {}
            tmpInfos = {}
            
            f = Opener(xsdFile)
            xsdTree = f.getRootNode()
            #Dictionary information
            if xsdTree.firstChildElement().nodeName() == "xsd:annotation":
                listInfoNode = xsdTree.firstChildElement().childNodes()
                for nodeIndex in range(listInfoNode.length()):
                    currentNode = listInfoNode.item(nodeIndex)
                    if currentNode.nodeName() == "xsd:appinfo":

                        for infoDictNodeIndex in range(currentNode.childNodes().length()):
                            currentInfo = currentNode.childNodes().item(infoDictNodeIndex).toElement()
                            if currentInfo.hasAttribute("dictName"):
                                tmpInfos["name"] = currentInfo.attribute("dictName")
                            elif currentInfo.hasAttribute("dictPriority"):
                                tmpInfos["priority"] = int(currentInfo.attribute("dictPriority"))
                            elif currentInfo.hasAttribute("dictRequires"):
                                tmpInfos["requirements"] = currentInfo.attribute("dictRequires")
                            elif currentInfo.hasAttribute("shortDescription"):
                                tmpInfos["shortDesc"] = currentInfo.attribute("shortDescription")
                    elif currentNode.nodeName() == "xsd:documentation":
                        tmpInfos["longDesc"] = currentNode.firstChild().nodeValue()
                        break
                    elif nodeIndex > 2:
                        break

            self.dictListInfos[str(xsdFile)] = tmpInfos

            # Listing of all primitives and types
            xsdNodeList = xsdTree.childNodes()
            for nodeIndex in range(xsdNodeList.length()):
                currentNode = xsdNodeList.item(nodeIndex)
                if str(currentNode.nodeName()) == "xsd:element":
                    infoCurrentPmt = DocPrimitive(currentNode, self)
                    if currentNode.toElement().attribute("ignore", "false") == "true":
                        pass
                    elif currentNode.toElement().attribute("abstract", "false") == "true":
                        self.dictAbstractPrimitives[xsdFile][infoCurrentPmt.name] = infoCurrentPmt
                    else:
                        self.dictPrimitives[xsdFile][infoCurrentPmt.name] = infoCurrentPmt
                elif str(currentNode.nodeName()) == "xsd:complexType":
                    infosCurrentType = DocPrimitiveComplexType(currentNode, self)
                    self.dictComplexTypes[xsdFile][infosCurrentType.typeName] = infosCurrentType
                elif str(currentNode.nodeName()) == "xsd:include":
                    #MAke sure to append XSD so opener finds the shema
                    self.addFromXSD(self.topObject.folderPath+"XSD/"+currentNode.toElement().attribute("schemaLocation"))
            
    
    def getDictNameFromFilePath(self, filePath):
        '''
        Returns a primitives dictionary name.
        
        :param filePath: File path of the .xsd file.
        :type filePath: String
        :return: String.
        '''
        if "name" in self.dictListInfos[filePath].keys():
            return self.dictListInfos[filePath]["name"]
    
    def removeDictFromFilePath(self, filePath):
        '''
        Removes a primitives dictionary from dictionary list.
        
        :param filePath: File path of the .xsd file.
        :type filePath: String
        '''
        if str(filePath) in self.dictPrimitives.keys():
            self.dictPrimitives.pop(filePath)
            self.dictListInfos.pop(filePath)
            self.dictAbstractPrimitives.pop(filePath)
            self.dictComplexTypes.pop(filePath)
        else:
            print("Warning : In PrimitiveDict::removeDictFromFilePath, xsd file at", filePath, "has not been loaded has a dictionary")
    
    def getPrimitiveInfo(self, primitiveName, lookInAbstract=False):
        '''
        Returns the information related to a primitive.
        
        :param primitiveName: Name of the DocPrimitive's primitive.
        :param lookInAbstract: Optional - Look or not in abstract primitives.
        :type primitiveName: String
        :type lookInAbstract: Boolean
        :return: :class:`.DocPrimitive`.
        '''
        for dictPath in self.dictPrimitives.keys():
            if primitiveName in self.dictPrimitives[dictPath].keys():
                return self.dictPrimitives[dictPath][primitiveName]

        if lookInAbstract == True:
            return self.getAbstractPrimitive(primitiveName)
        else:
            return DocPrimitive()

    def getAbstractPrimitive(self, abstractPmtName):
        '''
        Returns an abstract primitive.
        
        :param abstractPmtName: Name of the DocPrimitive's abstract primitive.
        :type abstractPmtName: String
        :return :class:`.DocPrimitive`.
        '''
        for dictPath in self.dictAbstractPrimitives.keys():
            if abstractPmtName in self.dictAbstractPrimitives[dictPath].keys():
                return self.dictAbstractPrimitives[dictPath][abstractPmtName]

        return DocPrimitive()

    def getComplexType(self, typeName):
        '''
        Returns a complex primitive type from its name.
        
        :param typeName: Name of the wanted type.
        :type typeName: String
        :return: :class:`.DocPrimitiveComplexType`.
        '''
        for dictPath in self.dictComplexTypes.keys():
            if typeName in self.dictComplexTypes[dictPath].keys():
                return self.dictComplexTypes[dictPath][typeName]

        return DocPrimitiveComplexType()

    def _getPossibleSubstitutions(self, pmtName, returnEventIfAbstract=False):
        '''
        Gets all primitives a primitive inherits/descends from.
        
        :param pmtName: Primitive's name.
        :param returnEventIfAbstract: Optional - Return or not abstract primitives.
        :type pmtName: String
        :type returnEventIfAbstract: Boolean
        :return: :class:`.DocPrimitive`.
        '''
        returnList = []
        for dictPath in self.dictPrimitives.keys():
            for currentPmt in self.dictPrimitives[dictPath].keys():
                if self.dictPrimitives[dictPath][currentPmt].canSubsituteTo == pmtName:
                    returnList.append(self.dictPrimitives[dictPath][currentPmt])
                    returnList.extend(self._getPossibleSubstitutions(self.dictPrimitives[dictPath][currentPmt].name))
            
            for currentPmt in self.dictAbstractPrimitives[dictPath].keys():
                if self.dictAbstractPrimitives[dictPath][currentPmt].canSubsituteTo == pmtName:
                    if returnEventIfAbstract:
                        returnList.append(self.dictAbstractPrimitives[dictPath][currentPmt])

                    returnList.extend(self._getPossibleSubstitutions(self.dictAbstractPrimitives[dictPath][currentPmt].name))

        return returnList

    def _DEBUG_PRINT_PMT_LIST(self):
        '''
        Useful debug function
        '''
        print("##############################################################\nXSD LISTING")
        print("Standards :")
        for dictPath in self.dictPrimitives.keys():
            print("\n>> BEGIN : " + dictPath)
            for pmt in self.dictPrimitives[dictPath].keys():
                print("\t" + pmt)
            print("\n>> END : " + dictPath + "\n")

        print("Abstracts :")
        for dictPath in self.dictAbstractPrimitives.keys():
            print("\n>> BEGIN : " + dictPath)
            for pmt in self.dictAbstractPrimitives[dictPath].keys():
                print("\t" + pmt)
            print("\n>> END : " + dictPath + "\n")

        print("Complex types :")
        for dictPath in self.dictComplexTypes.keys():
            print("\n>> BEGIN : " + dictPath)
            for pmt in self.dictComplexTypes[dictPath].keys():
                print("\t" + pmt)
            print("\n>> END : " + dictPath + "\n")
        print("##############################################################")

class ParsedXSDObject():
    '''
    Base class for all XSD object definitions.
    '''

    def __init__(self, constructionObject=None, dictRef=None):
        '''
        Constructor.
        
        :param constructionObject: Optional - Typically a xsd node, but can be a ParsedXSDObject(copy constructor) .
        :param dictRef: Optional - Dictionary this object belongs to.
        '''
        if dictRef == None:
            self.isNull = True
            self.docStr = None
        elif isinstance(constructionObject, ParsedXSDObject):
            #Copy Constructor
            self.dictRef = dictRef
            if constructionObject.isNull:
                self.isNull = True
                self.docStr = None
            else:
                self.isNull = False
                self.docStr = constructionObject.docStr
        else:
            if not isinstance(constructionObject, QDomNode):
                print("Error in XSD parser : construction object is not a ParsedXSDObject() nor a QDomNode!")
            self.xsdTree = constructionObject
            self.dictRef = dictRef
            self.docStr = {"en" : ""}
            if self.xsdTree.isNull():
                self.isNull = True
            else:
                if not isinstance(constructionObject, QDomNode):
                    print("Error in XSD parser : construction object is not a ParsedXSDObject() nor a QDomNode!")
                self.xsdTree = constructionObject
                self.dictRef = dictRef
                self.docStr = {"en" : ""}
                if self.xsdTree.isNull():
                    self.isNull = True
                else:
                    self.isNull = False

    def getDocStr(self, lang="en"):
        '''
        Returns the documentation string of the current element.
        
        :param lang: Optional - Language wanted.
        :type lang: String
        :return: String
        '''
        if self.docStr == None:
            return ""
        if lang not in self.docStr.keys():
            return self.docStr["en"]
        else:
            return self.docStr[str(lang)]

    def _childsListGenerator(self, pnode, jumpComments=True, fromChild=0, upToChild=-1):
        '''
        Generator object for a xsd tree.
        
        :param pnode: xsd node.
        :param jumpComments: Optional - Ignore or not xsd comments.
        :param fromChild: Optional - start at child fromChild.
        :param upToChild: Optional - End at child upToChild.
        :type pnode: PyQt4.QtXml.QDomNode
        :type jumpComments: Boolean
        :type fromChild: Int
        :type upToChild: Int
        '''
        childsList = pnode.childNodes()
        if upToChild < 0:
            upToChild = childsList.length()

        for nodeIndex in range(fromChild, upToChild):
            if jumpComments and childsList.item(nodeIndex).isComment():
                continue
            else:
                yield childsList.item(nodeIndex)

    def _parseXSDthrowchild(self, pnode):
        '''
        Calls appropriate function depending of pnode's tag name.
        
        :param pnode: xsd node.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        nodeName = pnode.nodeName()
        if pnode.isComment():
            return

        funcDict = {"xsd:annotation": self._parseXSDannotation,
            "xsd:appinfo" : self._parseXSDappinfo,
            "xsd:complexType": self._parseXSDcomplexType,
            "xsd:complexContent": self._parseXSDcomplexContent,
            "xsd:attribute": self._parseXSDattribute,
            "xsd:sequence": self._parseXSDsequence,
            "xsd:choice": self._parseXSDchoice,
            "xsd:simpleType": self._parseXSDsimpleType,
            "xsd:simpleContent": self._parseXSDsimpleContent,
            "xsd:extension": self._parseXSDextension,
            "xsd:restriction": self._parseXSDrestriction,
            "xsd:any": self._parseXSDany,
            "xsd:element": self._parseXSDelement,
            "xsd:enumeration": self._parseXSDenumeration,
            "pmt:info" : self._parsePMTinfo,
            "pmt:mappedName" : self._parsePMTmappedName,
            "pmt:returnType" : self._parsePMTreturnType,
            "pmt:childBranchTag" : self._parsePMTchildBranchTag,
            "pmt:childType" : self._parsePMTchildType,
            "pmt:attributeInfo" : self._parsePMTattributeInfo,
            "pmt:attributeMappedName" : self._parsePMTattributeMappedName,
            "pmt:attributeType" : self._parsePMTattributeType,
            "pmt:eventHandler" : self._parsePMTeventHandler,
            "pmt:event" : self._parsePMTevent,
            "pmt:eventArg" : self._parsePMTeventArg,
            "gui:style" : self._parseGUIstyle,
            "gui:behavior" : self._parseGUIbehavior,
            "gui:deleteUselessChilds" : self._parseGUIdeleteUselessChilds,
            "gui:readOnly" : self._parseGUIreadOnly,
            "gui:attributeBehavior" : self._parseGUIattributeBehavior,
            "gui:mapToBranches" : self._parseGUImapToBranches,
            "gui:list" : self._parseGUIlist,
            "gui:openOnDoubleClick": self._parseGUIopenOnDoubleClick,
            "gui:displayValue":self._parseGUIdisplayValue,
            "gui:individualType": self._parseGUIindividualType,
            "gui:sum":self._parseGUIsum}
        if nodeName in funcDict:
            funcDict[nodeName](pnode)
        else:
            print("Warning in ParsedXSDObject::_parseXSDthrowchild() : unknow element", nodeName, "will not be parsed")

    '''
    Next function are defined so an ParsedXSDObject inherited class prints a warning if the function isn't defined
    These function will not be commented since they have the same shape/goal
    '''
    def _parseXSDannotation(self, pnode):
        assert pnode.toElement().tagName() == "xsd:annotation", "PmtXSDParser::_parseXSDannotation() receive a node named " + pnode.toElement().tagName() + " instead of xsd:annotation."
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())

    def _parseXSDappinfo(self, pnode):
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())

    def _parseXSDcomplexType(self, pnode):
        assert pnode.toElement().tagName() == "xsd:complexType", "PmtXSDParser::_parseXSDcomplexType() receive a node named " + pnode.toElement().tagName() + " instead of xsd:complexType."
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())

    def _parseXSDcomplexContent(self, pnode):
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())

    def _parseXSDsimpleType(self, pnode):
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())

    def _parseXSDsimpleContent(self, pnode):
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())

    def _parseXSDextension(self, pnode):
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())

    def _parseXSDrestriction(self, pnode):
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())

    def _parseXSDany(self, pnode):
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())

    def _parseXSDattribute(self, pnode):
        assert pnode.toElement().tagName() == "xsd:attribute", "PmtXSDParser::_parseXSDattribute() receive a node named " + pnode.toElement().tagName() + " instead of xsd:attribute."
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())

    def _parseXSDsequence(self, pnode):
        assert pnode.toElement().tagName() == "xsd:sequence", "PmtXSDParser::_parseXSDsequence() receive a node named " + pnode.toElement().tagName() + " instead of xsd:sequence."
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())

    def _parseXSDchoice(self, pnode):
        assert pnode.toElement().tagName() == "xsd:choice", "PmtXSDParser::_parseXSDchoice() receive a node named " + pnode.toElement().tagName() + " instead of xsd:choice."
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())

    def _parseXSDelement(self, pnode):
        assert pnode.toElement().tagName() == "xsd:element", "PmtXSDParser::_parseXSDelement() receive a node named " + pnode.toElement().tagName() + " instead of xsd:element."
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())
    
    def _parseXSDenumeration(self, pnode):
        assert pnode.toElement().tagName() == "xsd:enumeration", "PmtXSDParser::_parseXSDenumeration() receive a node named " + pnode.toElement().tagName() + " instead of xsd:enumeration."
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())
    
    def _parsePMTinfo(self, pnode):
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())

    def _parsePMTmappedName(self, pnode):
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())

    def _parsePMTreturnType(self, pnode):
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())

    def _parsePMTchildBranchTag(self, pnode):
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())

    def _parsePMTchildType(self, pnode):
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())

    def _parsePMTattributeInfo(self, pnode):
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())

    def _parsePMTattributeMappedName(self, pnode):
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())
    
    def _parsePMTattributeType(self, pnode):
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())
    
    def _parsePMTeventHandler(self, pnode):
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())

    def _parsePMTevent(self, pnode):
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())

    def _parsePMTeventArg(self, pnode):
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())

    def _parseGUIstyle(self, pnode):
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())

    def _parseGUIbehavior(self, pnode):
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())

    def _parseGUIdeleteUselessChilds(self, pnode):
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())

    def _parseGUIreadOnly(self, pnode):
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())

    def _parseGUIattributeBehavior(self, pnode):
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())

    def _parseGUImapToBranches(self, pnode):
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())
    
    def _parseGUIindividualType(self, pnode):
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())

    def _parseGUIsum(self, pnode):
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())

    def _parseGUIlist(self, pnode):
        print("Warning : virtual method has been called for a XSD object named ", pnode.nodeName())
    
    def _parseGUIopenOnDoubleClick(self, pnode):
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())
    
    def _parseGUIdisplayValue(self, pnode):
        print("Warning : virtual method has been called for a XSD object named", pnode.nodeName())
    
class DocPrimitiveComplexType(ParsedXSDObject):
    '''
    Class representation of a xsd::complextype node.
    '''
    def __init__(self, constructionObject=None, dictRef=None):
        '''
        Constructor.
        
        :param constructionObject: xsd node or a DocPrimitiveComplexType(Copy constructor).
        :param dictRef: Optional - Dictionary this object belongs to.
        '''
        ParsedXSDObject.__init__(self, constructionObject, dictRef)
        
        self.typeName = ""
        self.childsSeq = DocPrimitiveSequenceItem()
        self.attributesList = [] #DocPrimitiveAttribute List

        if self.isNull:
            return
        if isinstance(constructionObject, DocPrimitiveComplexType):
            #Copy constructor
            self.importDataFrom(constructionObject)
        else:
            if not self.isNull:
                self._parseXSDcomplexType(self.xsdTree)

    def importDataFrom(self, complexTypeReference):
        '''
        Copies constructor copy function.
        
        :param complexTypeReference: Copied object.
        :type complexTypeReference: :class:`.DocPrimitiveComplexType`.
        '''
        self.childsSeq = DocPrimitiveSequenceItem(complexTypeReference.childsSeq, self.dictRef)
        for attr in complexTypeReference.attributesList:
            self.attributesList.append(DocPrimitiveAttribute(attr, self.dictRef))

    def howManyAttributes(self):
        '''
        Returns the object's number of attributes.
        
        :return: Int.
        '''
        try:
            return len(self.attributesList)
        except AttributeError:
            return 0
        
    def _DEBUG_PRINT_INFOS(self):
        '''
        Useful debug function
        '''
        print(self.typeName)
        print("\tChilds : ")
        self.childsSeq._DEBUG_PRINT_INFOS()
        print("\tAttributes (", len(self.attributesList), "): ")
        attrIndex = 0
        for attr in self.attributesList:
            attrIndex += 1
            print("\t\t [", attrIndex, "] : ")
            attr._DEBUG_PRINT_INFOS()

    def _parseXSDcomplexType(self, pnode):
        '''
        Parses a child xsd::complextype node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        assert pnode.toElement().tagName() == "xsd:complexType", "DocPrimitiveComplexType::_parseXSDcomplexType() receive a node named " + pnode.toElement().tagName() + " instead of xsd:complexType."

        self.typeName = pnode.toElement().attribute("name", "")
        for currentChild in self._childsListGenerator(pnode):
            self._parseXSDthrowchild(currentChild)

    def _parseXSDcomplexContent(self, pnode):
        '''
        Parse a child xsd::complexcontent node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        for currentChild in self._childsListGenerator(pnode):
            self._parseXSDthrowchild(currentChild)
        
    def _parseXSDextension(self, pnode):
        '''
        Parse a child xsd::extension node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        extensionBase = pnode.toElement().attribute("base", "")
        if not extensionBase:
            print("Error : no base for extension!")
            return

        inheritedType = self.dictRef.getComplexType(extensionBase)
        if not inheritedType.isNull:
            self.importDataFrom(inheritedType)
        else:
            print("Warning : extension base", extensionBase, "does not exist!")

        if pnode.hasChildNodes():
            for currentChild in self._childsListGenerator(pnode):
                self._parseXSDthrowchild(currentChild)
                
    def _parseXSDrestriction(self, pnode):
        '''
        Parse a child xsd::restriction node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        restrictionBase = pnode.toElement().attribute("base", "")
        if restrictionBase == "":
            print("Error : no base for restriction!")

        inheritedType = self.dictRef.getComplexType(restrictionBase)
        if not inheritedType.isNull:
            self.importDataFrom(inheritedType)
        else:
            print("Warning : restriction base", restrictionBase, "does not exist!")

        if pnode.hasChildNodes():
            for currentChild in self._childsListGenerator(pnode):
                self._parseXSDthrowchild(currentChild)

    def _parseXSDattribute(self, pnode):
        '''
        Parse a child xsd::attribute node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        self.attributesList.append(DocPrimitiveAttribute(pnode, self.dictRef))

    def _parseXSDsequence(self, pnode):
        '''
        Parse a child xsd::sequence node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        self.childsSeq = DocPrimitiveSequenceItem(pnode, self.dictRef)

    def _parseXSDchoice(self, pnode):
        '''
        Parse a child xsd::choice node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        self.childsSeq = DocPrimitiveSequenceItem(pnode, self.dictRef)

class DocPrimitiveEvent(ParsedXSDObject):
    '''
    Class representation of a pmt:event node
    '''
    def __init__(self, constructionObject=None, dictRef=None):
        '''
        Constructor.
        
        :param constructionObject: Optional - xsd node or a DocPrimitiveEvent(Copy constructor).
        :param dictRef: Optional - Dictionary this object belongs to
        '''
        ParsedXSDObject.__init__(self, constructionObject, dictRef)
        if self.isNull:
            return

        if isinstance(constructionObject, DocPrimitiveEvent):
            #Copy constructor
            self.importDataFrom(constructionObject)
        else:
            self.eventName = constructionObject.toElement().attribute("name")
            self.gravity = constructionObject.toElement().attribute("gravity", "Error")
            self.actionList = []
            self.gravityLevel = {"None" : 0, "Notice" : 1, "Warning" : 2, "Error" : 3, "Fatal Error" : 4, "Sudden Destruction Of The Earth" : 5}
            self.argNbr = constructionObject.toElement().elementsByTagName("pmt:eventArg").length()

            if constructionObject.toElement().attribute("forceCorrection", "false").lower() == "true":
                self.actionList.append("forceCorrection")
            if constructionObject.toElement().attribute("warn", "false").lower() == "true":
                self.actionList.append("warn")
            if constructionObject.toElement().attribute("addComment", "false").lower() == "true":
                self.actionList.append("addComment")

            self.eventXML = constructionObject
            
    def importDataFrom(self, eventReference):
        '''
        Copies constructor copy function.
        
        :param eventReference: Copied object.
        :type eventReference: :class:`.DocPrimitiveEvent`.
        '''
        self.eventName = eventReference.eventName
        self.gravity = eventReference.gravity
        self.actionList = eventReference.actionList
        self.gravityLevel = eventReference.gravityLevel
        self.argNbr = eventReference.argNbr
        self.eventXML = eventReference.eventXML

    def _DEBUG_PRINT_INFOS(self):
        '''
        Useful debug function.
        '''
        print("\t\tGravity :", self.gravity)
        print("\t\tAction List :", self.actionList)
        print("\t\tArguments Number :", self.argNbr)
        print("\t\t", self.eventXML)
        return ""

    def generateErrorMsg(self, eventArgs):
        '''
        Creates and returns an error message.
        
        :param eventArgs: Error message contains slots that need to be modified for error message to make sense.
        :type eventArgs: String list
        :return: String.
        '''
        if len(eventArgs) != self.argNbr:
            print("Warning in DocPrimitiveEvent::generateErrorMsg() : received", len(eventArgs), "arguments, but expecting", self.argNbr)

        errorMsg = ""
        for currentChild in self._childsListGenerator(self.eventXML):
            if currentChild.isText():
                errorMsg += "".join(currentChild.nodeValue().split())
            elif currentChild.isElement():
                if currentChild.nodeName() == "pmt:eventArg":
                    argNbr = int(currentChild.toElement().attribute("argIndex"))
                    if argNbr > 0 and argNbr <= len(eventArgs):
                        errorMsg += " " + str(eventArgs[argNbr-1]) + " "
                    else:
                        print("Warning in DocPrimitiveEvent::generateErrorMsg() : unmatched index", argNbr)

        return errorMsg

class DocPrimitiveEventHandler(ParsedXSDObject):
    '''
    Class representation of a pmt:eventHandler node.
    '''
    def __init__(self, constructionObject=None, dictRef=None):
        '''
        Constructor.
        
        :param constructionObject: Optional - xsd node or a DocPrimitiveEventHandler(Copy constructor).
        :param dictRef: Optional - Dictionary this object belongs to.
        '''
        ParsedXSDObject.__init__(self, constructionObject, dictRef)
        self.eventsList = {}
        if self.isNull:
            return
        
        if isinstance(constructionObject, DocPrimitiveEventHandler):
            #Copy constructor
            self.importDataFrom(constructionObject)
        else:
            if not self.isNull:
                self._parseXSDthrowchild(constructionObject)

    def importDataFrom(self, eventHandlerReference):
        '''
        Copies constructor copy function.
        
        :param eventReference: Copied object.
        :type eventReference: :class:`.DocPrimitiveEventHandler`
        '''
        for currentEvent in eventHandlerReference.eventsList.keys():
            self.eventsList[currentEvent] = DocPrimitiveEvent(eventHandlerReference.getEventInfo(currentEvent), self.dictRef)

    def getEventInfo(self, eventName):
        '''
        Returns information about the event contained in eventList.
        
        :param eventName: Name of the event to return information for.
        :type eventName: String
        :return: :class:`.DocPrimitiveEvent`.
        '''
        if str(eventName) in self.eventsList.keys():
            return self.eventsList[eventName]
        else:
            print("Warning : No information about event named", eventName)
            return DocPrimitiveEvent()

    def _DEBUG_PRINT_INFOS(self):
        '''
        Useful debug function
        '''
        print(str(len(self.eventsList)) + " events defined :")
        for currentEvent in self.eventsList.keys():
            print("\t", currentEvent, ": ")
            self.eventsList[currentEvent]._DEBUG_PRINT_INFOS()

    def _parsePMTeventHandler(self, pnode):
        '''
        Parses a child xsd::eventHandler node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        for currentChild in self._childsListGenerator(pnode):
            self._parseXSDthrowchild(currentChild)

    def _parsePMTevent(self, pnode):
        '''
        Parse a child xsd::event node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        if pnode.toElement().attribute("eventName") in self.eventsList.keys():
            print("Warning in _parsePMTevent : overwriting", pnode.toElement().attribute("eventName"))
        self.eventsList[pnode.toElement().attribute("eventName")] = DocPrimitiveEvent(pnode, self.dictRef)

    def _parsePMTeventArg(self, pnode):
        '''
        Parse a child xsd::eventArg node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        print("Warning : <pmt:eventArg> called outside a <pmt:event>!")

class DocPrimitiveBehavior(ParsedXSDObject):
    '''
    Class representation of behavior nodes (gui::behavior).
    Define a behavior for a primitive, a child or an attribute.
    '''

    def __init__(self, assocObjectType, constructionObject=None, dictRef=None):
        '''
        Constructor.
        
        :param assocObjectType: Primtive or attribute.
        :param constructionObject: Optional - xsd node or a DocPrimitiveBehavior(Copy constructor).
        :param dictRef: Optional - Dictionary this object belongs to.
        '''
        self.behaviorsList = {} # keys : behavior names, values : list of dictionnaries of behavior arguments (one dictionary by behavior)
        self.type = assocObjectType
        self.list = []
        ParsedXSDObject.__init__(self, constructionObject, dictRef)
        if self.isNull:
            return

        if isinstance(constructionObject, DocPrimitiveBehavior):
            #Copy consttructo
            self.importDataFrom(constructionObject)
        else:
            self._parseXSDthrowchild(constructionObject)

    def importDataFrom(self, behaviorReference):
        '''
        Copies constructor copy function.
        
        :param behaviorReference: Copied object.
        :type behaviorReference: :class:`.DocPrimitiveBehavior`
        '''
        self.behaviorsList = behaviorReference.behaviorsList
        self.list = behaviorReference.behaviorsList 
        
    def hasBehavior(self, behaviorName):
        '''
        Tells if behavior is present in behavior list.
        
        :param behaviorName: Behavior's name.
        :type behaviorName: String
        :return: Boolean.
        '''
        return str(behaviorName) in self.behaviorsList.keys()

    def getBehavior(self, behaviorName):
        '''
        Returns a behavior's attributes.
        
        :param behaviorName: Behavior's name.
        :type behaviorName: String
        :return: Pair (Boolean, Dictionary).
        '''
        if self.hasBehavior(behaviorName):
            return True, self.behaviorsList[behaviorName]
        else:
            return False, {}

    def _addBehavior(self, behaviorName, behaviorDict):
        '''
        Adds a behavior to behavior list.
        
        :param behaviorName: Behavior's name.
        :param behaviorDict: Behavior's attributes.
        :type behaviorName: String
        :type behaviorDict: Dictionary
        '''
        self.behaviorsList[behaviorName] = behaviorDict
    
    def _DEBUG_PRINT_INFOS(self):
        '''
        Useful debug function.
        '''
        print(" behavior type is", self.type)
        print("\n\t\tListing :", self.behaviorsList)

    def _parseGUIbehavior(self, pnode):
        '''
        Parse a child xsd::eventArg node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        if self.type != "primitive":
            print("Warning : parseGUIbehavior() called on a different object than a primitive")
            return

        for currentChild in self._childsListGenerator(pnode):
            self._parseXSDthrowchild(currentChild)

    def _parseGUIdeleteUselessChilds(self, pnode):
        '''
        Parse a child gui::deleteUselessChilds node.
        
        :param pnode: Child to parse.
        :type pnode: Not used
        '''
        parametersD = {}
        self._addBehavior("deleteUselessChilds", parametersD)

    def _parseGUIreadOnly(self, pnode):
        '''
        Parse a child gui::readOnlys node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        parametersD = {"recursive" : pnode.toElement().attribute("recursive", "False")}
        self._addBehavior("readOnly", parametersD)

    def _parseGUIattributeBehavior(self, pnode):
        '''
        Parse a child gui::attributeBehavior.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        if self.type != "attribute":
            print("Warning : parseGUIattributeBehavior() called on a different object than an attribute!")
            return

        for currentChild in self._childsListGenerator(pnode):
            self._parseXSDthrowchild(currentChild)

    def _parseGUImapToBranches(self, pnode):
        '''
        Parse a child gui::mapToBranches.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        parametersD = {"regexp" : str(pnode.toElement().attribute("regexp", " ")),
                                                    "startIndex" : int(pnode.toElement().attribute("startIndex", "1")),
                                                    "endIndex" : int(pnode.toElement().attribute("endIndex", "1")),
                                                    "sum" : '0',
                                                    "editable" : False,
                                                    "displayAttribute" : False}

        if pnode.toElement().attribute("editable", "false") == "true":
            parametersD["editable"] = True

        if pnode.toElement().attribute("displayAttribute", "false") == "true":
            parametersD["displayAttribute"] = True

        self._addBehavior("mapToBranches", parametersD)
        
        for currentChild in self._childsListGenerator(pnode):
            self._parseXSDthrowchild(currentChild)

    def _parseGUIlist(self, pnode):
        '''
        Parse a child gui::list.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        parametersD = {"type" : pnode.toElement().attribute("type"), "allowEdition" : False}
        if pnode.toElement().attribute("allowEdition", "false") == "true":
            parametersD["allowEdition"] = True

        self.list.append(parametersD)

    def _parseGUIopenOnDoubleClick(self, pnode):
        '''
        Parse a child gui::openOnDoubleClick.
        
        :param pnode: Child to parse.
        :type pnode: Not used
        '''
        parametersD = {}
        self._addBehavior("openOnDoubleClick", parametersD)

    def _parseGUIdisplayValue(self,pnode):
        '''
        Parse a child gui::displayValue.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        parametersD = {}
        parametersD["position"] = pnode.toElement().attribute("position", "br")
        parametersD["showAttr"] = pnode.toElement().attribute("showAttr", "")
        parametersD["delimiter"] = pnode.toElement().attribute("delimiter", "")
        self._addBehavior("displayValue", parametersD)
    
    def _parseGUIindividualType(self, pnode):
        '''
        Parse a child gui::individualType.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        self.behaviorsList["mapToBranches"]["individualType"] = [pnode.toElement().attribute("definedBy", "xsd:double"),
                                                                 pnode.firstChild().nodeValue()]
    
    def _parseGUIsum(self, pnode):
        '''
        Parse a child gui::sum.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        self.behaviorsList["mapToBranches"]["sum"] = str(pnode.firstChild().nodeValue())
    
class DocPrimitiveAttribute(ParsedXSDObject):
    '''
    Class representation of a xsd::attribute node.
    '''

    def __init__(self, constructionObject=None, dictRef=None):
        '''
        Constructor.
        
        :param constructionObject: Optional - xsd node or a DocPrimitiveAttribute(Copy constructor).
        :param dictRef: Optional - Dictionary this object belongs to.
        '''
        
        ParsedXSDObject.__init__(self, constructionObject, dictRef)
        
        self.name = ""
        self.mappedName = {"en" : ""}
        self.required = False
        self.defValue = ""
        self.type = ""
        self.guiType = ""
        self.behavior = DocPrimitiveBehavior("attribute")
        self.possibleValues = []
        self.isReference = False
        self.pairedAttr = None
        self.autoFill = ""
        if self.isNull:
            return
        if isinstance(constructionObject, DocPrimitiveAttribute):
            #Copy constructor
            self.importDataFrom(constructionObject)
        else:
            if not self.isNull:
                self._parseXSDattribute(constructionObject)

    def importDataFrom(self, importAttribute):
        '''
        Copies constructor copy function.
        
        :param importAttribute: Copied object.
        :type importAttribute: :class:`.DocPrimitiveAttribute`
        '''
        self.name = importAttribute.name
        self.mappedName = importAttribute.mappedName
        self.required = importAttribute.required
        self.defValue = importAttribute.defValue
        self.isReference = importAttribute.isReference
        self.pairedAttr = importAttribute.pairedAttr
        self.type = importAttribute.type
        self.behavior = DocPrimitiveBehavior("attribute", importAttribute.behavior, self.dictRef)
        self.autoFill = importAttribute.autoFill
        self.possibleValues = importAttribute.possibleValues
        self.guiType = importAttribute.guiType

    def getMappedName(self, lang="en"):
        '''
        Return's attribute name for GUI.
        
        :param lang: Optional - Name language.
        :type lang: String
        :return: String.
        '''
        if lang not in self.mappedName.keys():
            return self.mappedName["en"]
        else:
            return self.mappedName[str(lang)]

    def getAttributeInfo(self, lang="en"):
        '''
        Returns an attribute's information.
        
        :param lang: Optional - Information's language.
        :type lang: String
        :return: String
        '''
        return ParsedXSDObject.getDocStr(self, lang)
    
    def _DEBUG_PRINT_INFOS(self):
        '''
        Useful debug function.
        '''
        print(self.name)
        print("\t\tMapped name :", self.mappedName)
        print("\t\tRequired :", self.required)
        print("\t\tDefault value :", self.defValue)
        print("\t\tType :", self.type)
        #print("\t\tAutofill :", self.autofill)
        print("\t\tAttribute behavior : ")
        self.behavior._DEBUG_PRINT_INFOS()

    def _parseXSDattribute(self, pnode):
        '''
        Parses a child xsd::attribute node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        assert pnode.toElement().tagName() == "xsd:attribute", "PmtXSDParser::_parseXSDattribute() receive a node named " + pnode.toElement().tagName() + " instead of xsd:attribute."

        self.name = pnode.toElement().attribute("name")
        if pnode.toElement().hasAttribute("type"):
            #Attributes with restrictions have their type described in restriction
            self.type = pnode.toElement().attribute("type").replace("xsd:", "")
        self.required = pnode.toElement().attribute("use", "") == "required"
        self.defValue = pnode.toElement().attribute("default", "")

        for currentChild in self._childsListGenerator(pnode):
            self._parseXSDthrowchild(currentChild)

    def _parseXSDannotation(self, pnode):
        '''
        Parse a child xsd::annotation node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        for currentChild in self._childsListGenerator(pnode):
            self._parseXSDthrowchild(currentChild)
            
    def _parseXSDsimpleType(self, pnode):
        '''
        Parse a child xsd::simpletype node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        if pnode.firstChild().nodeName() != "xsd:restriction" or pnode.childNodes().count() != 1:
            print("Warning : xsd:simpleType invalid child list")
        else:
            self._parseXSDrestriction(pnode.firstChild())
    
    def _parseXSDrestriction(self, pnode):
        '''
        Parse a child xsd::restriction node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        self.type = pnode.toElement().attribute("base").replace("xsd:", "")
        for currentChild in self._childsListGenerator(pnode): 
            self._parseXSDthrowchild(currentChild)
    
    def _parseXSDenumeration(self, pnode):
        '''
        Parse a child xsd::enumeration node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        self.possibleValues.append(pnode.toElement().attribute("value", ""))
              
    def _parseXSDappinfo(self, pnode):
        '''
        Parse a child xsd::appinfo node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        for currentChild in self._childsListGenerator(pnode):
            self._parseXSDthrowchild(currentChild)

    def _parsePMTattributeInfo(self, pnode):
        '''
        Parse a child pmt::attributeInfo node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        self.docStr[pnode.toElement().attribute("lang", "en")] = str(pnode.firstChild().nodeValue())
        self.isReference = (pnode.toElement().attribute("reference", "false") == "true")
        self.pairedAttr = pnode.toElement().attribute("pairedAttr", "")
        
    def _parsePMTattributeMappedName(self, pnode):
        '''
        Parse a child pmt::attributeMappedName node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        self.mappedName[pnode.toElement().attribute("lang", "en")] = str(pnode.firstChild().nodeValue())

    def _parseGUIattributeBehavior(self, pnode):
        '''
        Parse a child pmt::attributeBehavior node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        self.behavior = DocPrimitiveBehavior("attribute", pnode, self.dictRef)

    def _parsePMTattributeType(self, pnode):
        '''
        Parse a child pmt::attributeType node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        self.guiType = str(pnode.firstChild().nodeValue())
        
class DocPrimitiveSequenceItem(ParsedXSDObject):
    '''
    Class representation of a xsd node child of a xsd:sequence.
    Typicaly a xsd:element, xsd:sequence or xsd:choice.
    '''

    def __init__(self, definitionObject=None, dictRef=None):
        '''
        Constructor.
        
        :param definitionObject: Optional - xsd node or a DocPrimitiveSequenceItem(Copy constructor).
        :param dictRef: Optional - Dictionary this object belongs to.
        '''
        ParsedXSDObject.__init__(self, definitionObject, dictRef)
        self.repetate = [1, 1]
        self.itemType = ""
        self.storedObject = None
        
        self.behaviorAsChild = DocPrimitiveBehavior("child")
        if self.isNull:
            return
            
        if isinstance(definitionObject, DocPrimitiveSequenceItem):
            #Copy constructor
            self.importDataFrom(definitionObject)
        else:
            self.repetate = [1, 1]
            self.itemType = ""
            self.acceptedTypeDefBy = "staticType"
            self.acceptedTypeVal = "Any"
            self.storedObject = None
            self.branchTag = {"en" : ""}
    
            self.behaviorAsChild = DocPrimitiveBehavior("child")
            self._parseXSDthrowchild(definitionObject)
            if self.itemType == "choice":
                self.storedObject = DocPrimitiveChoice(self.xsdTree, dictRef)
            elif self.itemType == "sequence":
                self.storedObject = DocPrimitiveSequence(self.xsdTree, dictRef)
            elif self.itemType == "element":
                self.storedObject = DocPrimitive(self.xsdTree, dictRef)

    def importDataFrom(self, referenceItem):
        '''
        Copies constructor copy function.
        
        :param referenceItem: Copied object.
        :type referenceItem: :class:`.DocPrimitiveSequenceItem`
        '''
        self.repetate = referenceItem.repetate
        self.itemType = referenceItem.itemType
        self.acceptedTypeDefBy = referenceItem.acceptedTypeDefBy
        self.acceptedTypeVal = referenceItem.acceptedTypeVal
        self.branchTag = referenceItem.branchTag
        self.behaviorAsChild = DocPrimitiveBehavior("child", referenceItem.behaviorAsChild, self.dictRef)
        
        if referenceItem.isChoice():
            self.storedObject = DocPrimitiveChoice(referenceItem.toChoice(), self.dictRef)
        elif referenceItem.isElement():
            self.storedObject = DocPrimitive(referenceItem.toElement(), self.dictRef)
        elif referenceItem.isSequence():
            self.storedObject = DocPrimitiveSequence(referenceItem.toSequence(), self.dictRef)
        
    def _DEBUG_PRINT_INFOS(self):
        '''
        Useful debug function.
        '''
        if self.storedObject is not None:
            self.storedObject._DEBUG_PRINT_INFOS()

    def getMinRepetitions(self):
        '''
        Returns how many times the item should be minimaly (0 = optionnal).
        
        :return: Int.
        '''
        return self.repetate[0]

    def getMaxRepetitions(self):
        '''
        Return max number of times the item should be found (0 = unbounded).
        
        :return: Int.
        '''
        return self.repetate[1]
           
    def getAcceptedType(self):
        '''
        Returns an item's accepted type.
        Return type is a pair of the following possibilities :
        - First element : child, attribute or staticType.
        - Second element : Int, Double, String etc or child number or attribute's name.
        
        :return: Pair (child | attribute | staticType, Object)
        '''
        return self.acceptedTypeDefBy, self.acceptedTypeVal

    def isChoice(self):
        '''
        Tells if current item is a DocPrimitiveChoice.
        
        :return: Boolean.
        '''
        return self.itemType == "choice"

    def isSequence(self):
        '''
        Tells if current item is a DocPrimitiveSequence.
        
        :return: Boolean.
        '''
        return self.itemType == "sequence"

    def isElement(self):
        '''
        Tells if current item is a DocPrimitive.
        
        :return: Boolean.
        '''
        return self.itemType == "element"

    def toChoice(self):
        '''
        Cast to choice.
        
        :return: :class:`.DocPrimitiveChoice`.
        '''
        if self.isChoice():
            return self.storedObject
        else:
            print("Warning : Tentative to convert a DocPrimitiveSequenceItem into a DocPrimitiveChoice failed!")
            return DocPrimitiveChoice()

    def toSequence(self):
        '''
        Cast to sequence.
        
        :return: :class:`.DocPrimitiveSequence`.
        '''
        if self.isSequence():
            return self.storedObject
        else:
            print("Warning : Tentative to convert a DocPrimitiveSequenceItem >", self.xsdTree.nodeName(), "< into a DocPrimitiveSequence failed!")
            return DocPrimitiveSequence()

    def toElement(self):
        '''
        Cast to element.
        
        :return: :class:`.DocPrimitive`.
        '''
        if self.isElement():
            return self.storedObject
        else:
            print("Warning : Tentative to convert a DocPrimitiveSequenceItem into a DocPrimitive failed!")
            return DocPrimitive()

    def _parseXSDsequence(self, pnode):
        '''
        Parse a child xsd::sequence node.
        
        :param: pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        self.itemType = "sequence"
        self._checkItemCounts(pnode)

    def _parseXSDchoice(self, pnode):
        '''
        Parse a child xsd::choice node.
        
        :param: pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        self.itemType = "choice"
        self._checkItemCounts(pnode)

    def _parseXSDelement(self, pnode):
        '''
        Parse a child xsd::element node.
        
        :param: pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        self.itemType = "element"
        self._checkItemCounts(pnode)

    def _checkItemCounts(self, pnode):
        '''
        Looks how many time this item must be in sequence.
        
        :param pnode: PyQt4.QtXml.QDomNode
        '''
        if pnode.toElement().hasAttribute("minOccurs"):
            self.repetate[0] = int(pnode.toElement().attribute("minOccurs"))
        if pnode.toElement().hasAttribute("maxOccurs"):
            if pnode.toElement().attribute("maxOccurs") == "unbounded":
                self.repetate[1] = -1
            else:
                self.repetate[1] = int(pnode.toElement().attribute("maxOccurs"))

class DocPrimitiveChoice(DocPrimitiveSequenceItem):
    '''
    Class representation of a xsd:choice node
    '''

    def __init__(self, constructionObject=None, dictRef=None):
        '''
        Constructor.
        
        :param constructionObject: Optional - xsd node or a DocPrimitiveChoice(Copy constructor).
        :param dictRef: Optional - Dictionary this object belongs to.
        '''
        ParsedXSDObject.__init__(self, constructionObject, dictRef)
        
        self.argType = "Any"
        self.choicesList = []
        self.choiceDefault = ""
        self.acceptedTypeDefBy = "staticType"
        self.acceptedTypeVal = "Any"
        self.branchTag = {"en" : ""}
        self.behaviorAsChild = DocPrimitiveBehavior("child")
        
        if self.isNull:
            return
        if isinstance(constructionObject, DocPrimitiveChoice):
            #Copy constructor
            self.importDataFrom(constructionObject)
        else:
            if not self.isNull:
                self._parseXSDchoice(constructionObject)

    def importDataFrom(self, choiceReference, operationMode="extend"):
        '''
        Copies constructor copy function.
        
        :param choiceReference: Copied object.
        :param operationMode: Optional - Start from scratch or extend.
        :type choiceReference: :class:`.DocPrimitiveChoice`
        :type operationMode: String
        '''
        if operationMode == "erase":
            self.choicesList = []
        self.argType = choiceReference.argType
        self.branchTag = choiceReference.branchTag
        self.choiceDefault = choiceReference.choiceDefault
        for seqItem in choiceReference.choicesList:
            self.choicesList.append(DocPrimitiveSequenceItem(seqItem, self.dictRef))

    def _DEBUG_PRINT_INFOS(self):
        '''
        Useful debug function.
        '''
        print("Choice between : ")
        for seqItem in self.getChoices():
            print("\t\t", seqItem.name)

    def getChoices(self):
        '''
        Return a list of all the possible choices.
        
        :return: :class:`.DocPrimitiveSequenceItem` list.
        '''
        returnList = []
        for autorisedItem in self.choicesList:
            if autorisedItem.isElement():
                if self.dictRef.getAbstractPrimitive(autorisedItem.toElement().name).isNull:
                    #Not abstract, so we add it
                    returnList.append(autorisedItem.toElement())

                #Checking for subsitution
                tmpList = self.dictRef._getPossibleSubstitutions(autorisedItem.toElement().name)
                returnList.extend(tmpList)
            else:
                returnList.append(autorisedItem)

        return returnList

    def isValidChoice(self, pmtName):
        '''
        Tells if a primitive is a valid choice for this item.
        
        :param  pmtName: Name of the primitve we want to verify the validity.
        :type pmtName: String
        :return: Boolean.
        '''
        return pmtName in [item.name for item in self.getChoices()]

    def _parseXSDchoice(self, pnode):
        '''
        Parses a child xsd::choice node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        assert pnode.nodeName() == "xsd:choice", "DocPrimitiveChoice receive a root node other than xsd:choice"
        for currentChild in self._childsListGenerator(pnode):
            self._parseXSDthrowchild(currentChild)

    def _parseXSDannotation(self, pnode):
        '''
        Parse a child xsd::annotation node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        for currentChild in self._childsListGenerator(pnode):
            self._parseXSDthrowchild(currentChild)

    def _parseXSDappinfo(self, pnode):
        '''
        Parse a child xsd::appinfo node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        for currentChild in self._childsListGenerator(pnode):
            self._parseXSDthrowchild(currentChild)

    def _parseXSDelement(self, pnode):
        '''
        Parse a child xsd::element node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        self.choicesList.append(DocPrimitiveSequenceItem(pnode, self.dictRef))

    def _parseXSDsequence(self, pnode):
        '''
        Parse a child xsd::sequence node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        self.choicesList.append(DocPrimitiveSequenceItem(pnode, self.dictRef))

    def _parsePMTchildBranchTag(self, pnode):
        '''
        Parse a child pmt::childBranchTag.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        self.branchTag[pnode.toElement().attribute("lang", "en")] = str(pnode.firstChild().nodeValue())
       
    def _parsePMTchildType(self, pnode):
        '''
        Parse a child gui::childType.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        self.acceptedTypeDefBy = pnode.toElement().attribute("definedBy", "staticType")
        self.acceptedTypeVal = str(pnode.firstChild().nodeValue())

class DocPrimitiveSequence(DocPrimitiveSequenceItem):
    '''
    Class representation of a xsd:sequence node.
    '''
    def __init__(self, constructionObject = None, dictRef = None):
        '''
        Constructor.
        
        :param constructionObject: Optional - xsd node or a DocPrimitiveSequence(Copy constructor).
        :param dictRef: Optional - dictionary this object belongs to.
        '''
        ParsedXSDObject.__init__(self, constructionObject, dictRef)
        self.seqList = []
        if self.isNull:
            return
        if isinstance(constructionObject, DocPrimitiveSequence):
            #Copy constructor
            self.importDataFrom(constructionObject)
        else:
            if not self.isNull:
                self._parseXSDsequence(constructionObject)

    def importDataFrom(self, sequenceRef, operationMode = "extend"):
        '''
        Copies constructor copy function.
        
        :param sequenceRef: Copied object.
        :param operationMode: Optional - Start from scratch or extend.
        :type sequenceRef: :class:`.DocPrimitiveSequence`
        :type operationMode: String
        '''
        if operationMode == "erase":
            self.seqList = []
        self.maxRepetate = sequenceRef.maxRepetate
        for seqItem in sequenceRef.seqList:
            self.seqList.append(DocPrimitiveSequenceItem(seqItem, self.dictRef))

    def _DEBUG_PRINT_INFOS(self):
        '''
        Useful debug function.
        '''
        print("Sequence of", len(self.seqList))
        for item in self.seqList:
            print("\n\t")
            item._DEBUG_PRINT_INFOS()

    def howManyItems(self):
        '''
        Returns the number of items in the sequence list.
        
        :return: Int.
        '''
        return len(self.seqList)

    def getSimpleOrderedChildAt(self, beginningPos, childPos, allowRepetition=0):
        '''
        Returns the element of the sequence at position "childPos", parsing the sub-sequences if we have to do so.
        Be careful : this method is only available for children without sequence repetitions
        (trying to retrieve a child repetate will fail).
        
        :param beginningPos: Start position.
        :param childPos: The position of the child we want to retrieve.
        :param allowRepetition: Optional - Number of repetition to consider.
        :type beginningPos: Int
        :type childPos: Int
        :type allowRepetition: Int
        :return: :class:`.DocPrimitiveSequenceItem`.
        '''
        currentPos = beginningPos
        returnItem = DocPrimitiveSequenceItem()
        itemFound = False
        nbrRepetate = 0
        if self.howManyItems() < childPos:
            assert allowRepetition > 0, "In DocPrimitiveSequence::getSimpleOrderedChildAt() : too high position without allowing repetition!"

        while (nbrRepetate < self.maxRepetate or self.maxRepetate == -1) and not itemFound:
            for currentItem in self.nextChildInSequence():
                if currentItem.isSequence():
                    returnItem = currentItem.toSequence().getSimpleOrderedChildAt(currentPos, childPos, 1)
                    if not returnItem.isNull:
                        itemFound = True
                        break
                    else:
                        currentPos += (currentItem.toSequence().howManyItems())

                elif currentPos == childPos:
                    returnItem = currentItem
                    itemFound = True
                    break
                else:
                    currentPos += currentItem.getMinRepetitions()

            nbrRepetate += 1
        

        return returnItem

    def getMinimumChilds(self):
        '''
        Returns the minimum number of children this primitive sequence should have (without any repetition).
        
        :return: Int.
        '''
        currentCount = 0
        for currentItem in self.nextChildInSequence():
            if currentItem.isSequence():
                currentCount += currentItem.toSequence().getMinimumChilds()
            else:
                currentCount += currentItem.getMinRepetitions()

        return currentCount

    def getMaximumChilds(self):
        '''
        Return the maximum number of children this primitive sequence should have.
        
        :return: Int.
        '''
        currentCount = 0
        for currentItem in self.nextChildInSequence():
            if currentItem.isSequence():
                if currentItem.toSequence().getMaximumChilds() == -1:
                    return -1
                currentCount += currentItem.toSequence().getMaximumChilds()
            else:
                if currentItem.getMaxRepetitions() == -1:
                    return -1
                currentCount += currentItem.getMaxRepetitions()
                
        return currentCount

    def nextChildInSequence(self):
        '''
        Generator for next item of the sequence.
        '''
        for indexItem in range(self.howManyItems()):
            yield self.seqList[indexItem]

    def _parseXSDannotation(self, pnode):
        '''
        Parse a child xsd::annotation node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        for currentChild in self._childsListGenerator(pnode):
            if currentChild.nodeName() == "xsd:documentation":
                self.docStr = str(currentChild.firstChild().nodeValue())

    def _parseXSDsequence(self, pnode):
        '''
        Parse a child xsd::sequence node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        assert pnode.toElement().tagName() == "xsd:sequence", "PmtXSDParser::_parseXSDsequence() receive a node named " + pnode.toElement().tagName() + " instead of xsd:sequence."

        if pnode == self.xsdTree:
            tempRepetate = pnode.toElement().attribute("maxOccurs", "1")
            if tempRepetate == "unbounded":
                self.maxRepetate = -1
            else:
                self.maxRepetate = int(tempRepetate)

            for currentChild in self._childsListGenerator(pnode):
                self._parseXSDthrowchild(currentChild)
        else:
            self.seqList.append(DocPrimitiveSequenceItem(pnode, self.dictRef))

    def _parseXSDchoice(self, pnode):
        '''
        Parse a child xsd::choice node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        assert pnode.toElement().tagName() == "xsd:choice", "PmtXSDParser::_parseXSDchoice() receive a node named " + pnode.toElement().tagName() + " instead of xsd:choice."
        self.seqList.append(DocPrimitiveSequenceItem(pnode, self.dictRef))

    def _parseXSDelement(self, pnode):
        '''
        Parse a child xsd::element node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        assert pnode.toElement().tagName() == "xsd:element", "PmtXSDParser::_parseXSDelement() receive a node named " + pnode.toElement().tagName() + " instead of xsd:element."
        self.seqList.append(DocPrimitiveSequenceItem(pnode, self.dictRef))
        
class DocPrimitiveStyle(ParsedXSDObject):
    '''
    Class representation of a gui:style node.
    Under Construction.
    '''
    def __init__(self, primitiveXSDTree=QDomNode(), parent=None):
        '''
        Constructor.
        
        :param primitiveXSDTree: Optional - Deprecated
        :param parent: Optional - Deprecated
        '''
        self.fontName = ""
        self.fontSize = 12
        self.fontColor = QColor(0, 0, 0)
        self.textUnderlined = False
        self.textBold = False
        self.textItalic = False

        ParsedXSDObject.__init__(self, primitiveXSDTree, parent)
        if not self.isNull:
            self._parseGUIstyle(self.xsdTree)


class DocPrimitive(DocPrimitiveSequenceItem):
    '''
    Class representing a primitive's documentation, defined by multiple xsd structures and their associated class/instances.
    '''
    def __init__(self, constructionObject=None, dictRef=None):
        '''
        Constructor.
        
        :param constructionObject: Optional - xsd node or a DocPrimitive(Copy constructor).
        :param dictRef: Optional - Dictionary this object belongs to.
        '''
        ParsedXSDObject.__init__(self, constructionObject, dictRef)
        self.name = ""
        self.isRef = False
                
        self.complexType = DocPrimitiveComplexType()
        self.mappedName = {"en" : ""}
        self.returnTypeVal = "Void"
        self.returnTypeDefBy = "staticType"
        self.abstract = False
        self.style = DocPrimitiveStyle()
        self.behavior = DocPrimitiveBehavior("primitive")
        self.eventHandler = DocPrimitiveEventHandler()
        self.canSubsituteTo = ""

        if self.isNull:
            return
        if isinstance(constructionObject, DocPrimitive):
            #Copy constructor
            self.importDataFrom(constructionObject)
        else:
            if not self.isNull:
                self._parseXSDelement(self.xsdTree)

    def importDataFrom(self, primitiveReference):
        '''
        Copies constructor copy function.
        
        :param primitiveReference: Copied object.
        :type primitiveReference: :class:`.DocPrimitive`.
        '''
        self.complexType = DocPrimitiveComplexType(primitiveReference.complexType, self.dictRef)
        self.mappedName = primitiveReference.mappedName
        self.name = primitiveReference.name
        self.isRef = primitiveReference.isRef
        self.returnTypeVal = primitiveReference.returnTypeVal
        self.returnTypeDefBy = primitiveReference.returnTypeDefBy
        self.behavior = DocPrimitiveBehavior("primitive", primitiveReference.behavior, self.dictRef)
        self.eventHandler = DocPrimitiveEventHandler(primitiveReference.eventHandler, self.dictRef)

    def inheritedDataFrom(self, primitiveInherited):
        '''
        Inheritance constructor function.
        
        :param primitiveInherited: Inherited primitive.
        :type primitiveInherited: :class:`.DocPrimitive`.
        '''
        self.returnTypeVal = primitiveInherited.returnTypeVal
        self.returnTypeDefBy = primitiveInherited.returnTypeDefBy
        self.behavior = DocPrimitiveBehavior("primitive", primitiveInherited.behavior, self.dictRef)
        self.eventHandler = DocPrimitiveEventHandler(primitiveInherited.eventHandler, self.dictRef)
        self.canSubsituteTo = primitiveInherited.name

    def getPrimitiveBehavior(self):
        '''
        Returns an item's behavior.
        
        :return: :class:`.DocPrimitiveBehavior`.
        '''
        try:
            return self.behavior
        except AttributeError:
            return DocPrimitiveBehavior("primitive")

    def getSpecificEventInfo(self, eventName):
        '''
        Returns the info associated with eventName.
        
        :param eventName: Name of the event to retreive information of.
        :type eventName: String
        :return: :class:`.DocPrimitiveEvent`.
        '''
        return self.eventHandler.getEventInfo(eventName)

    def getSimpleOrderedChild(self, childPos):
        '''
        Returns the child item at given position.
        
        :param childPos: The position of the child we want to retrieve.
        :type childPos: Int
        :return: :class:`.DocPrimitiveSequenceItem`.
        '''
        if not self.complexType.childsSeq.isSequence():
            return self.complexType.childsSeq
        else:
            return self.complexType.childsSeq.toSequence().getSimpleOrderedChildAt(0, childPos, 1)

    def getMinimumNumChilds(self):
        '''
        Returns the minimum number of children this primitive should have.
        
        :return: Int.
        '''
        try:
            if self.complexType.childsSeq.isChoice() or self.complexType.childsSeq.isElement():
                return self.complexType.childsSeq.getMinRepetitions()
            elif self.complexType.childsSeq.isSequence():
                return self.complexType.childsSeq.toSequence().getMinimumChilds()
            else:
                return 0
        except AttributeError:
            return 0

    def getMaximumChilds(self):
        '''
        Returns the maximum number of children this primitive should have.
        
        :return: Int.
        '''
        if self.complexType.childsSeq.isChoice() or self.complexType.childsSeq.isElement():
            return self.complexType.childsSeq.getMaxRepetitions()
        elif self.complexType.childsSeq.isSequence():
            return self.complexType.childsSeq.toSequence().getMaximumChilds()
        else:
            return -1

    def howManyAttributes(self):
        '''
        Returns how many attributes this primitive has.
        
        :return: Int.
        '''
        return len(self.complexType.attributesList)

    def getAttribute(self, attributeName):
        '''
        Returns an attribute of this Primitive.
        
        :param attributeName: The name of the attribute we want to retrieve.
        :type attributeName: String
        :return: :class:`.DocPrimitiveAttribute`.
        '''
        for attr in self.complexType.attributesList:
            if attr.name == attributeName:
                return attr

        return DocPrimitiveAttribute()

    def getNextAttribute(self, attrNumberBegin=0):
        '''
        Attribute generator.
        
        :param attrNumberBegin: Optional - Position of the first attribute to yield.
        :type attrNumberBegin: Int
        '''
        for currentAttrIndex in range(attrNumberBegin, self.complexType.howManyAttributes()):
            yield self.complexType.attributesList[currentAttrIndex]

    def getMappedName(self, lang="en"):
        '''
        Returns the name for the GUI.
        
        :param lang: Optional - Language's name.
        :type lang: String
        '''
        if str(lang) not in self.mappedName.keys():
            return self.mappedName["en"]
        else:
            return self.mappedName[lang]

    def getReturnType(self):
        '''
        Returns a primitive's type.
        
        :return: Pair (String, String).
        '''
        return self.returnTypeDefBy, self.returnTypeVal
    
    def isPaired(self, attributeName):
        '''
        Returns true if attribute is paired to another attribute.
        This function is not quite efficient since it has to loop through all attributes, so use with care.
        
        :param attributeName: The name of the possibly paired attribute.
        :type attributeName: String
        :return: Boolean.
        '''
        for attr in self.complexType.attributesList:
            if attr.pairedAttr == attributeName:
                return True
    
    def _DEBUG_PRINT_INFOS(self):
        '''
        Useful debug function.
        '''
        print("################# PRIMITIVE DEBUG OUTPUT #################\n")
        print("Primitive name :", self.name)
        print("Mapped name :", self.mappedName)
        print("Is abstract :", self.abstract)
        print("Return type (", self.returnTypeDefBy, ") :", self.returnTypeVal)
        print("Event handler : ")
        self.eventHandler._DEBUG_PRINT_INFOS()
        print("Behaviors : ")
        self.behavior._DEBUG_PRINT_INFOS()
        print("Contains (complex type) : ")
        self.complexType._DEBUG_PRINT_INFOS()
        print("\n##########################################################")

    def _parseXSDannotation(self, pnode):
        '''
        Parses a child xsd::annotation node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        for currentChild in self._childsListGenerator(pnode):
            self._parseXSDthrowchild(currentChild)

    def _parseXSDappinfo(self, pnode):
        '''
        Parse a child xsd::appinfo node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        for currentChild in self._childsListGenerator(pnode):
            self._parseXSDthrowchild(currentChild)

    def _parseXSDcomplexType(self, pnode):
        '''
        Parse a child xsd::complexType node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        self.complexType = DocPrimitiveComplexType(pnode, self.dictRef)

    def _parseXSDelement(self, pnode):
        '''
        Parse a child xsd::element node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        pmtIsRef = bool(pnode.toElement().attribute("ref", ""))
        pmtIsNamed = bool(pnode.toElement().attribute("name", ""))
        pmtSubstitutionGroup = pnode.toElement().attribute("substitutionGroup")
        pmtTypeDef = pnode.toElement().attribute("type")

        if pmtIsRef and pmtIsNamed:
            print("Warning in PmtXSDParser::_parseXSDelement :  xsd:element tag contains both 'ref' and 'name' attributes! This element will be parsed as a new element (name attribute behavior)")

        if pmtIsNamed:
            self.name = pnode.toElement().attribute("name")
        elif pmtIsRef:
            self.name = pnode.toElement().attribute("ref")
            self.isRef = True
        else:
            print("Warning in PmtXSDParser::_parseXSDelement :  xsd:element tag does not contains 'ref' or 'name' attribute! This element will not be parsed.")

        self.abstract = (pnode.toElement().attribute("abstract").lower() == "true")

        if pmtSubstitutionGroup:
            pmtInherited = self.dictRef.getPrimitiveInfo(pmtSubstitutionGroup, True)
            if pmtInherited.isNull:
                print("Error : trying to inherits from an undefined primitive (", pmtSubstitutionGroup, ")")
                return
            self.inheritedDataFrom(pmtInherited)

        if pmtTypeDef:
            complexTypeUsed = self.dictRef.getComplexType(pmtTypeDef)
            
            if complexTypeUsed.isNull:
                print("Error : trying to use a complex type undefined (", pmtTypeDef, ")")
                return
            
            self.complexType = complexTypeUsed

        for currentChild in self._childsListGenerator(pnode):
            self._parseXSDthrowchild(currentChild)

    def _parseGUIbehavior(self, pnode):
        '''
        Parse a child gui::behavior node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        self.behavior = DocPrimitiveBehavior("primitive", pnode, self.dictRef)

    def _parseGUIstyle(self, pnode):
        '''
        Parse a child gui::style node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        self.style = DocPrimitiveStyle(pnode, self.dictRef)

    def _parsePMTinfo(self, pnode):
        '''
        Parse a child pmt::info node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        self.docStr[pnode.toElement().attribute("lang", "en")] = str(pnode.firstChild().nodeValue())

    def _parsePMTmappedName(self, pnode):
        '''
        Parse a child pmt::mappedName node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        self.mappedName[pnode.toElement().attribute("lang", "en")] = str(pnode.firstChild().nodeValue())

    def _parsePMTreturnType(self, pnode):
        '''
        Parse a child pmt::returnType node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        self.returnTypeDefBy = pnode.toElement().attribute("definedBy", "staticType")
        self.returnTypeVal = str(pnode.firstChild().nodeValue())

    def _parsePMTeventHandler(self, pnode):
        '''
        Parse a child pmt::eventhandler node.
        
        :param pnode: Child to parse.
        :type pnode: PyQt4.QtXml.QDomNode
        '''
        self.eventHandler = DocPrimitiveEventHandler(pnode, self.dictRef)