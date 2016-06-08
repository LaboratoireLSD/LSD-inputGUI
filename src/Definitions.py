"""
Here are regrouped the common definitions for all the application.
"""

baseTypes = ["Double", "Float", "Int", "Bool", "String", "UInt", "Long", "ULong"]

integerTypes = ["Int", "Long", "UInt", "ULong"]
numberTypes = ["Int", "Double", "Float", "Long", "UInt", "ULong", "Integer"]
atomTypes = ["Int", "Double", "Float", "Long", "UInt", "ULong", "Number", "Integer", "String", "Char", "Bool"]
floatTypes = ["Double", "Float"]

convTable = {"Double": "double",
             "Float": "float",
             "Int": "integer",
             "Long": "long",
             "ULong": "unsignedLong",
             "UInt": "unsignedInt",
             "Bool": "boolean",
             "String": "string"}

typeTree={'Atom':'Any','Void':'Any','Number':'Atom','Bool':'Atom','String':'Atom',
          'Char':'Atom','FPoint':'Number','Integer':'Number','UInt':'Integer',
          'Int':'Integer','ULong':'Integer','Long':'Integer','Float':'FPoint','Double':'FPoint'}