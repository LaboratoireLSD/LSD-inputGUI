"""
.. module:: opener

.. codeauthor:: Marc-André Gardner

:Created on: 2009-09-16

"""
from PyQt4.QtCore import QIODevice, QFile
from PyQt4.QtXml import QDomDocument

class Opener:
    ''' Opens and return the root node of a XML document. '''
    
    def __init__(self, filepath, mode=QIODevice.ReadWrite):
        '''
        Constructor.
        
        :param filePath: XML file's path.
        :param mode: Optional - QIODevice.OpenMode.
        :type filePath: String
        :type mode: QIODevice.OpenMode
        '''
        self.temp_dom = QDomDocument()
        self.fpath = filepath
        self.omode = mode
        self.openf()

    def openf(self):
        '''
        Opens file. On success, store root node in self.temp_dom.
        '''
        assert QFile(self.fpath).exists(), "In Opener::openf : Cannot open File : " + self.fpath + ", file does not exist!"
        f = QFile(self.fpath)
        if f.open(self.omode):
            assert self.temp_dom.setContent(f), "In Opener::openf() : unable to parse XML dom of " + self.fpath
        else:
            print("Warning in Opener::openf() : unable to open", self.fpath)
        f.close()

    def getRootNode(self):
        '''
        Returns the root node.
        
        :return: PyQt4.QtXml.QDomElement
        '''
        return self.temp_dom.documentElement()
