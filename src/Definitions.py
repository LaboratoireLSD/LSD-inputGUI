"""
Here are regrouped the common definitions for all the application.
"""

baseTypes = ["Float", "Int", "Bool", "String"]

integerTypes = ["Int"]
numberTypes = ["Int", "Float"]
atomTypes = ["Int", "Float", "Number", "Integer", "String", "Bool"]
floatTypes = ["Float"]

typesToNames = {"Float": "float",
             "Int": "integer",
             "Bool": "boolean",
             "String": "string",
             "Double": "double"}

typesToDefinitions = {"Int": "Integer",
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
           'Int':'Integer',
           'Float':'FPoint'}