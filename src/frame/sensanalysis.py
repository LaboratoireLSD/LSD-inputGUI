"""
.. module:: sensanalysis

.. codeauthor::  Mathieu Gagnon <mathieu.gagnon.10@ulaval.ca>

:Created on: 2010-08-23

"""

from PyQt4 import QtCore
from PyQt4 import QtGui

class Ui_Analysis(object):
    '''
    This class is the mainWindow's tab containing the sensibility analysis information of the simulation.
    '''
    def __init__(self,parent):
        '''
        Constructor.
        
        :param parent: Application's mainWindow
        '''
        self.parent = parent
    
    def setupUi(self,Analysis):
        """
        Creates the widgets that will be displayed on the frame
        """

        Analysis.setObjectName("Analysis")
        #Layout for the comboBox
        self.cbLayout = QtGui.QHBoxLayout()
        #LAyout for the ADD DElete
        #  self.horizontalLayoutButtons = QtGui.QHBoxLayout()
        #MainLayout
        self.mainLayout = QtGui.QVBoxLayout()
        
        #Populating left splitter layout at first
        #Label
        self.addLabel = QtGui.QLabel("Add parameter : ")
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(75)
        font.setBold(True)
        self.addLabel.setFont(font)
        #Adding label to the its layout
        self.cbLayout.addWidget(self.addLabel)
        self.cbLayout.setAlignment(self.addLabel, QtCore.Qt.AlignLeft)
        
        #ComboBox
        self.comboBoxVar = QtGui.QComboBox()
        self.comboBoxVar.setMinimumWidth(1)
        self.comboBoxVar.setSizeAdjustPolicy(self.comboBoxVar.AdjustToContents)
        #Adding combobox to the its layout
        self.cbLayout.addWidget(self.comboBoxVar)
        self.cbLayout.setAlignment(self.comboBoxVar, QtCore.Qt.AlignLeft)

        #Doc
        self.docButton = QtGui.QPushButton("How Do I Use This?")
        self.cbLayout.addWidget(self.docButton)
        self.cbLayout.setAlignment(self.docButton, QtCore.Qt.AlignLeft)

        self.cbLayout.addStretch(0)

        #Sensibility Analysis Table
        self.saList = QtGui.QTableView()
        self.saList.setObjectName("saList")
        
        #My preferences
        self.saList.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding) 

        #Add Delete Buttons
        #  self.add = QtGui.QPushButton()
        #  self.add.setObjectName("add")
        #  self.add.setFixedSize(QtCore.QSize(77,25))
        #  self.horizontalLayoutButtons.addWidget(self.add)
        #  self.delete = QtGui.QPushButton()
        #  self.delete.setObjectName("delete")
        #  self.delete.setFixedSize(QtCore.QSize(77,25))
        #  self.horizontalLayoutButtons.addWidget(self.delete)
        
        #Setting the main LAyout and all the spacing
        #Adding child layout to the main Layout
        self.mainLayout.addLayout(self.cbLayout)
        self.mainLayout.addWidget(self.saList)
        # self.mainLayout.addLayout(self.horizontalLayoutButtons)
        Analysis.setLayout(self.mainLayout)
        self.mainLayout.setMargin(50)
        #  self.horizontalLayoutButtons.setSpacing(10)

        #  self.horizontalLayoutButtons.addItem(QtGui.QSpacerItem(100, 30, QtGui.QSizePolicy.Expanding))
        
        #pyuic auto-generated code
        self.retranslateUi(Analysis)
        # My preferences
        self.connect(self.comboBoxVar, QtCore.SIGNAL("activated(int)"), self.addParam)
        # self.connect(self.saList.horizontalHeader(), QtCore.SIGNAL("sectionDoubleClicked(int)"),self.fakeDelegate)
        # self.connect(self.add, QtCore.SIGNAL("clicked()"), self.addAnalysis)
        # self.connect(self.delete, QtCore.SIGNAL("clicked()"), self.deleteAnalysis)
        self.connect(self.docButton, QtCore.SIGNAL("clicked()"), self.generateDoc)
        
    def retranslateUi(self, analysis):
        """
        This function does nothing for the moment. It only "pass".
        """
        #  self.add.setText(QtGui.QApplication.translate("analysis", "Add", None, QtGui.QApplication.UnicodeUTF8))
        #  self.delete.setText(QtGui.QApplication.translate("analysis", "Delete", None, QtGui.QApplication.UnicodeUTF8))
        pass
    
    def addParam(self,paramNum):
        '''
        Tells the model to transfer a variable from the comboBox into the listView.
        
        :param paramNum: comboBox variable's index to transfer.
        :type paramNum: Int
        '''
        self.comboBoxVar.model().addParam(paramNum)
    
    # def fakeDelegate(self,headerNum):
        '''
        Create a line edit over the header so the user feel like he is editing the header
        @param headerNum : header number
        '''
    #     if headerNum == 0 or headerNum == 1 or headerNum == 2 or headerNum == 3:
    #         return
    #     self.editor = QtGui.QLineEdit(self.sender())
    #     self.editor.setGeometry(QtCore.QRect(self.saList.horizontalHeader().sectionPosition(headerNum )-self.saList.horizontalHeader().offset(),0,self.saList.horizontalHeader().sectionSize(headerNum),25))
    #     self.editor.setText(self.saList.model().headerData(headerNum,QtCore.Qt.Horizontal,QtCore.Qt.DisplayRole).toString())
    #     self.editor.setFocus(QtCore.Qt.MouseFocusReason)
    #     self.connect(self.editor, QtCore.SIGNAL("editingFinished ()"),self.endEditing)
    #     self.editor.show()
        
    def endEditing(self):
        '''
        Performs model update after analysis's name has been changed.
        '''
        headerNum = self.saList.horizontalHeader().logicalIndexAt(self.editor.pos().x(),self.editor.pos().y() )
        self.saList.model().setHeaderData(headerNum, QtCore.Qt.Horizontal, self.editor.text())
        self.editor.deleteLater()
    
    #  def addAnalysis(self):
        '''
        @summary Add new analysis
        '''
    #      self.saList.model().insertColumn(self.saList.model().columnCount())
    
    #  def deleteAnalysis(self):
        '''
        summary Delete analysis
        '''
    #      if self.saList.selectedIndexes():
    #          if self.saList.selectedIndexes()[0] > 1:
    #              self.saList.model().removeColumn(self.saList.selectedIndexes()[0].column()) 
    
    def generateDoc(self):
        '''
        Help window generating the HTML documentation.
        '''
        QtGui.QMessageBox.information(self, "Sensivity Analysis Help",
                                """<b>Pay extreme attention to the syntax, for errors will only show up in the console during files generation. Syntax is not case sensitive.</b>
                          <p><b>Supported laws :</b><UL TYPE="square">
<LI>uniform &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<i>(lower & upper lim only)</i>
<LI>randint &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<i>(lower & upper lim only)</i>
<LI>norm &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<i>(lowerLim, upperLim, sd, mean)</i>
<LI>discretenorm &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<i>(lowerLim, upperLim, sd, mean)</i>
<LI>beta &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<i>(lowerLim, upperLim, alpha, beta)</i>
<LI>gamma &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<i>(lowerLim, upperLim, k, theta)</i>
<LI>triang &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<i>(lowerLim, upperLim, c(element of [0,1]))</i>
<LI>poisson &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<i>(lowerLim, upperLim, mu)</i>
</UL></p>
                          <p><b>Notes on lower and upper limits :</b><br>A reroll is done if the randomly generated value falls outside of these limits. If the field is left empty, then default values of -inf and inf will be given respectively.</p>
                          <p><b>Notes on standard deviation, mean, and other optionnal parameters :</b><br>These parameters are only taken into consideration for laws that require them. Mean is always optional. If no mean is given, then the initial value is used.</p>
                          <p><b>Notes on vectors :</b><br>"unchanged" and "follower" options are added for vectors. "unchanged" means that no change will be done on this particular value. "follower" means that any change to others values will be countered here according to an inverse proportion. Therefore, only one instance of "follower" can be used. "follower" is particularly useful for probabilities, as it can ensure that the total remains equal to one.</p>
                          <p><b>To delete an entry:</b><br>Simply remove the values from all fields for that specific parameter. The parameter will remove itself automatically from the XML file when saving is done.</p>
                          <p><b>Univariate analysis:</b><br>Write "univariate" in the first non-used field. The field is ignored when doing a multiway analysis. Lower and upper limits are taken into consideration, so make sure those contain valid values and are never empty.""")
