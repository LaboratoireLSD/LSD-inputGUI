"""
.. module:: PrefModel

.. codeauthor:: Mathieu Gagnon <mathieu.gagnon.10@ulaval.ca>

:Created on: 2011-03-03

"""

from PyQt4 import QtXml,QtCore
from functools import wraps

def fakeSingleton(PrefModel):
    '''
    Python Decorator, emulates a singleton behavior
    It emulates the behavior because if the user passes arguments to the constructor, we implicitly consider he wants a new instance of BaseTreatmentsModel
    Else, its acts as a singleton
    '''
    instance_container = []
    @wraps(PrefModel)
    def wrapper(*args):
        '''
        Wrapper function
        '''
        if not len(instance_container):
            #Create BaseTreatmentsModel if it doesn't exist
            instance_container.append(PrefModel(*args))
        elif len(args):
            #If it exists and arguments are passed through the constructor, create new instance
            instance_container[0] = PrefModel(*args)
        #return singleton or new instance
        return instance_container[0]
    return wrapper

@fakeSingleton
class PrefModel:
    '''
    This is a class containing all the data found in the settings file.
    '''

    def __init__(self, domTree, windowObject):
        '''
        Constructor.
        
        :param domTree: Processes's xml node.
        :param scenarioDomTree: Scenarios's xml node.
        :param windowObject: Application's main window.
        '''
        self.dom = domTree
        self.topObject = windowObject
        self.pref = {}
        self.parsePref()
        
    def getProjectName(self):
        '''
        Returns the project's id.
        
        :return: String
        '''
        return self.pref["project"]
    
    def setProjectName(self, projectName):
        '''
        Set Project's name.
        
        :param projectName: New name of the project.
        :type projectName: String
        '''
        self.dom.firstChildElement("SC").firstChildElement("Project").setAttribute("label",projectName)
        self.parsePref()
    
    def getEmail(self):
        '''
        Returns the user's e-mail.
        
        :return: String
        '''
        return self.pref["mail"]
    
    def setEmail(self, email):
        '''
        Set user's e-mail.
        
        :param email: New user's email.
        :type email: String
        '''
        self.dom.firstChildElement("SC").firstChildElement("Mail").setAttribute("label",email)
        self.parsePref()
        
    def getMailCondition(self):
        '''
        Returns the condition to send e-mail.
            "b" = when job begins
            "e" = when job ends
            "a" = when job aborts
            "s" = when job suspended (someone kicks you off)
            "n" = don't send mail
            
        :return: String
        '''
        return self.pref["mailif"]
        
    def setMailCondition(self, mailCondition):
        '''
        Set condition to send e-mail
            "b" = when job begins
            "e" = when job ends
            "a" = when job aborts
            "s" = when job suspended (someone kicks you off)
            "n" = don't send mail
            
        :param mailCondition: Set the condition to send email.
        :type mailCondition: String
        '''
        self.dom.firstChildElement("SC").firstChildElement("Mailif").setAttribute("label",mailCondition)
        self.parsePref()
        
    def getSimServer(self):
        '''
        Returns the simulation server.
        
        :return: String
        '''
        return self.pref["server"]
    
    def setSimServer(self, serverName):
        '''
        Set simulation server's address.
        
        :param serverName: New server's address.
        :type serverName: String
        '''
        self.dom.firstChildElement("SC").firstChildElement("Server").setAttribute("address",serverName)
        self.parsePref()
        
    def getUserName(self):
        '''
        Returns the user's name.
        
        :return: String
        '''
        return self.pref["user"]
    
    def setUserName(self, userName):
        '''
        Set the user's name.
        
        :param userName: New user's name.
        :type userName: String
        '''
        self.dom.firstChildElement("SC").firstChildElement("Server").setAttribute("user",userName)
        self.parsePref()
        
    def parsePref(self):
        '''
        Parse preference xml node and fill dictionary.
        '''
        self.pref["project"] = self.dom.firstChildElement("SC").firstChildElement("Project").attribute("label")
        self.pref["mail"] = self.dom.firstChildElement("SC").firstChildElement("Mail").attribute("label")
        self.pref["mailif"] = self.dom.firstChildElement("SC").firstChildElement("Mailif").attribute("label")
        self.pref["server"] = self.dom.firstChildElement("SC").firstChildElement("Server").attribute("address")
        self.pref["user"] = self.dom.firstChildElement("SC").firstChildElement("Server").attribute("user")
        
