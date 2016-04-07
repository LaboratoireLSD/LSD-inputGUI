'''
Created on 2011-03-03

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

from PyQt4 import QtXml,QtCore
from util.opener import Opener

def fakeSingleton(PrefModel):
    '''
    Python Decorator, emulates a singleton behavior
    It emulates the behavior because if the user passes arguments to the constructor, we implicitly consider he wants a new instance of BaseTreatmentsModel
    Else, its acts as a singleton
    '''
    instance_container = []
    def wrapper(*args):
        '''
        @summary Wrapper function
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
    This is a class containing all the data found in the settings file
    '''

    def __init__(self, domTree,windowObject):
        '''
        @summary Constructor
        @param domTree : Processes's xml node
        @param scenarioDomTree : Scenarios's xml node
        @param windowObject : application's main window
        '''
        self.dom = domTree
        self.topObject = windowObject
        self.pref = {}
        self.parsePref()
        
    def getProjectName(self):
        '''
        @summary Return project's id
        '''
        return self.pref["project"]
    
    def setProjectName(self,projectName):
        '''
        @summary Set Project's name
        '''
        self.dom.firstChildElement("SC").firstChildElement("Project").setAttribute("label",projectName)
        self.parsePref()
    
    def getEmail(self):
        '''
        @summary Return user's e-mail
        '''
        return self.pref["mail"]
    
    def setEmail(self,email):
        '''
        @summary Set user's e-mail
        '''
        self.dom.firstChildElement("SC").firstChildElement("Mail").setAttribute("label",email)
        self.parsePref()
        
    def getMailCondition(self):
        '''
        @summary Return condition to send e-mail
        "b" = when job begins
        "e" = when job ends
        "a" = when job aborts
        "s" = when job suspended (someone kicks you off)
        "n" = don't send mail
        '''
        return self.pref["mailif"]
        
    def setMailCondition(self,mailCondition):
        '''
        @summary Return condition to send e-mail
        "b" = when job begins
        "e" = when job ends
        "a" = when job aborts
        "s" = when job suspended (someone kicks you off)
        "n" = don't send mail
        '''
        self.dom.firstChildElement("SC").firstChildElement("Mailif").setAttribute("label",mailCondition)
        self.parsePref()
        
    def getSimServer(self):
        '''
        @summary Return simulation server
        '''
        return self.pref["server"]
    
    def setSimServer(self,serverName):
        '''
        @summary Set simulation server's address
        '''
        self.dom.firstChildElement("SC").firstChildElement("Server").setAttribute("address",serverName)
        self.parsePref()
        
    def getUserName(self):
        '''
        @summary Return user's name
        '''
        return self.pref["user"]
    
    def setUserName(self,userName):
        '''
        @summary Set user's name
        '''
        self.dom.firstChildElement("SC").firstChildElement("Server").setAttribute("user",userName)
        self.parsePref()
        
    def parsePref(self):
        '''
        @summary Parse preference xml node and fill dictionary
        '''
        self.pref["project"] = self.dom.firstChildElement("SC").firstChildElement("Project").attribute("label")
        self.pref["mail"] = self.dom.firstChildElement("SC").firstChildElement("Mail").attribute("label")
        self.pref["mailif"] = self.dom.firstChildElement("SC").firstChildElement("Mailif").attribute("label")
        self.pref["server"] = self.dom.firstChildElement("SC").firstChildElement("Server").attribute("address")
        self.pref["user"] = self.dom.firstChildElement("SC").firstChildElement("Server").attribute("user")
        
