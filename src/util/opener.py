'''
Created on 2009-09-16

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

from PyQt4.QtCore import QIODevice, QFile
from PyQt4.QtXml import QDomDocument

class Opener:
    ''' Opens and return the root node of a XML document '''
    
    def __init__(self, filepath, mode=QIODevice.ReadWrite):
        '''
        @summary Constructor
        @param filePath : XML file's path
        @param mode : QIODevice.OpenMode
        '''
        self.temp_dom = QDomDocument()
        self.fpath = filepath
        self.omode = mode
        self.openf()

    def openf(self):
        '''
        @summary Open file. On success, store root node in self.temp_dom
        '''
        assert QFile(self.fpath).exists(), "In Opener::openf : Cannot open File : "+str(self.fpath)+", file does not exist!"
        f = QFile(self.fpath)
        if f.open(self.omode):
            assert self.temp_dom.setContent(f), "In Opener::openf() : unable to parse XML dom of " + str(self.fpath)
        else:
            print("Warning in Opener::openf() : unable to open " + str(self.fpath))
        f.close()

    def getRootNode(self):
        '''
        @summary Return root node
        '''
        return self.temp_dom.documentElement()

    def getDomDocument(self):
        '''
        @summary Return QDomDocument instance
        '''
        return self.temp_dom