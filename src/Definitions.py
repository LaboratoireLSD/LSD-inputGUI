"""
Here are regrouped the common definitions for all the application.
"""

baseTypes = ["Float", "Int", "UInt", "Bool", "String"]

integerTypes = ["Int", "UInt"]
numberTypes = ["Int", "UInt", "Float"]
atomTypes = ["Int", "UInt", "Float", "Number", "Integer", "String", "Bool"]
floatTypes = ["Float"]

typesToNames = {"Float": "float",
                "Int": "integer",
                "UInt": "unsignedInt",
                "Bool": "boolean",
                "String": "string"}

typesToDefinitions = {"Int": "Integer",
                      "UInt": "Natural",
                      "Float": "Real",
                      "Bool": "Boolean",
                      "String": "String",
                      "Number": "Number",
                      "Integer": "Integer",
                      "Atom": "Any",
                      "Any": "Any",
                      "Void": "Empty",
                      "Unknown": "Unknown"}

treeTypes={'Atom':'Any','Void':'Any',
           'Number':'Atom','Bool':'Atom','String':'Atom',
           'FPoint':'Number','Integer':'Number',
           'Int':'Integer', 'UInt': 'Integer',
           'Float':'FPoint'}

def typeToName(baseType):
    """
    Takes a base model and returns its real long name. Ex : UInt -> unsignedInt
    
    :param baseType: String representing the base type.
    :return: Full name of the base type.
    """
    return typesToNames[convertType(baseType)]

def typeToDefinition(baseType):
    """
    Useful when it comes to apply a function to a list with 'map' by instance.
    
    :param baseType: String representing the base type.
    :return: Definition of the base type as string.
    """
    return typesToDefinitions[convertType(baseType)]

def definitionToType(definition):
    """
    Acts like a double sided dictionary. Finds a type based on its definition.
    
    :param definition: String representing the definition of the base type.
    :return: Base type as string.
    """
    for key, value in typesToDefinitions.items():
        if value == definition:
            return key
    return definition

def convertType(baseType):
    """
    Converts a type into another if necessary. Since old projects may have old base types.
    
    :param baseType: String representing a base type.
    :return: New base type if necessary, as string.
    """
    baseType = definitionToType(baseType)
    if not baseType:
        return "Void"
    if baseType in ["Double"]:
        return "Float"
    if baseType in ["Long"]:
        return "Int"
    if baseType in ["ULong"]:
        return "UInt"
    if baseType in ["Char"]:
        return "String"
    return baseType