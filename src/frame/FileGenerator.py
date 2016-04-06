'''
Created on 2010-09-28

@author:  Majid Malis
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
from PyQt4 import QtGui, QtCore
from util.opener import Opener
from random import randint
from random import SystemRandom
import util.script_sens
import copy
import io
import shutil
import os

class FileGenerator(QtGui.QDialog):
    '''
    This class allows user to create n configurations files
    Each file will be identical, except for Randomizer elements
    The user will have the possibility to modify Generator and/or Simulator randomizers, initial seeds being randomly computed 
    by this class
    '''

    def __init__(self,confFile,parent=None):
        '''
        @summary Constructor
        @param confFile : configuration file path
        @param parent : application's main window
        '''
        QtGui.QDialog.__init__(self,parent)
        self.baseFile = confFile
        self.parent = parent
        self.setMaximumSize(100, 150)
        self.setupUi()
    
    def setupUi(self):
        self.layout = QtGui.QVBoxLayout()
        self.checkBoxGen = QtGui.QCheckBox("Generator Seeds")
        self.checkBoxSim = QtGui.QCheckBox("Simulator Seeds")
        self.checkBoxSens = QtGui.QCheckBox("Multiway Analysis")
        self.checkBoxUni = QtGui.QCheckBox("Univariate Analysis")

      #  self.spinBoxNumSetup = QtGui.QSpinBox()
      #  self.spinBoxNumSetup.setRange(1,100)
      #  self.spinBoxNumSetup.setSingleStep(2)
      #  self.spinBoxNumSetup.setDisabled(True)
       
        self.layoutSpinBox = QtGui.QHBoxLayout()
        self.layoutSpinBox2 = QtGui.QHBoxLayout()
        self.layoutSpinBox3 = QtGui.QHBoxLayout()
        self.layoutSetup = QtGui.QHBoxLayout()

        self.labelSpinBox = QtGui.QLabel("Number of files per setup :")
        self.spinBoxNumFile = QtGui.QSpinBox()
        self.spinBoxNumFile.setMaximum(30000)
        self.spinBoxNumFile.setValue(100)
        self.layoutSpinBox.addWidget(self.labelSpinBox)
        self.layoutSpinBox.addWidget(self.spinBoxNumFile)

        self.labelSpinBox2 = QtGui.QLabel("Number of generator threads :")
        self.spinBoxGenThread = QtGui.QSpinBox()
        self.spinBoxGenThread.setMaximum(12)
        self.spinBoxGenThread.setValue(8)
        self.layoutSpinBox2.addWidget(self.labelSpinBox2)
        self.layoutSpinBox2.addWidget(self.spinBoxGenThread)

        self.labelSpinBox3 = QtGui.QLabel("Number of simulation threads :")
        self.spinBoxSimThread = QtGui.QSpinBox()
        self.spinBoxSimThread.setMaximum(12)
        self.spinBoxSimThread.setValue(8)
        self.layoutSpinBox3.addWidget(self.labelSpinBox3)
        self.layoutSpinBox3.addWidget(self.spinBoxSimThread)

     #   self.labelSpinBoxSet = QtGui.QLabel("Number of setups :")
     #   self.layoutSetup.addWidget(self.labelSpinBoxSet)
     #   self.layoutSetup.addWidget(self.spinBoxNumSetup)

        self.labelProgressB = QtGui.QLabel("Files generation progress  :")
        font = QtGui.QFont()
        font.setBold(True)
        self.labelProgressB.setFont(font)

        self.labelProgressB2 = QtGui.QLabel("Applying sensitivity analysis values :")
        self.labelProgressB2.setFont(font)

        self.progressB = QtGui.QProgressBar()
        self.progressB.setRange(0,1)
        self.counter = 0

        self.progressB2 = QtGui.QProgressBar()
        self.progressB2.setDisabled(True)
        self.counter2 = 0

        self.count = 0
        f = Opener(self.baseFile[:-14]+'sensanalysis.xml')
        rootNode = f.getRootNode()
        elt = rootNode.toElement().firstChildElement("Law").firstChildElement().toElement()
        while elt.attribute("name"):
            elt = elt.nextSiblingElement()
            self.count+=1
        if self.count == 0:
            self.progressB2.setRange(0,1)
        else:
            self.progressB2.setRange(0,self.count)

        self.comboBoxBits = QtGui.QComboBox()
        self.labelBits = QtGui.QLabel("System's bit length")
        self.comboBoxBits.addItem("64 bits")
        self.comboBoxBits.addItem("32 bits")
        self.layoutBits = QtGui.QHBoxLayout()
        self.layoutBits.addWidget(self.labelBits)
        self.layoutBits.addWidget(self.comboBoxBits)
        self.dialogButtonBox = QtGui.QDialogButtonBox()
        self.dialogButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok )
        self.layout.addWidget(self.checkBoxSim)
        self.layout.addWidget(self.checkBoxGen)
        self.layout.addWidget(self.checkBoxSens)
        self.layout.addWidget(self.checkBoxUni)
        self.layout.addLayout(self.layoutSetup)
        self.layout.addLayout(self.layoutBits)
        self.layout.addLayout(self.layoutSpinBox)
        self.layout.addLayout(self.layoutSpinBox2)
        self.layout.addLayout(self.layoutSpinBox3)
        self.layout.addWidget(self.labelProgressB)
        self.layout.addWidget(self.progressB)
        self.layout.addWidget(self.labelProgressB2)
        self.layout.addWidget(self.progressB2)
        self.layout.addWidget(self.dialogButtonBox)
        self.layout.setAlignment(self.dialogButtonBox, QtCore.Qt.AlignRight)
        self.setWindowTitle("File generator")
        self.setLayout(self.layout)
    
        self.checkBoxGen.setChecked(True)
        self.checkBoxSim.setChecked(True)
        self.checkBoxSens.setChecked(False)
        self.checkBoxUni.setChecked(False)
        QtCore.QObject.connect(self.dialogButtonBox,QtCore.SIGNAL("accepted()"),self.generate)
        QtCore.QObject.connect(self.dialogButtonBox,QtCore.SIGNAL("rejected()"),self.reject)
        QtCore.QObject.connect(self.checkBoxGen,QtCore.SIGNAL("toggled(bool)"),self.checkWatcher)
        QtCore.QObject.connect(self.checkBoxSim,QtCore.SIGNAL("toggled(bool)"),self.checkWatcher)
        QtCore.QObject.connect(self.spinBoxNumFile,QtCore.SIGNAL("valueChanged(int)"),self.updateProgressLim)
        QtCore.QObject.connect(self.checkBoxSens,QtCore.SIGNAL("toggled(bool)"),self.checkAnalysis)
        QtCore.QObject.connect(self.checkBoxUni,QtCore.SIGNAL("toggled(bool)"),self.checkAnalysis)
     #   QtCore.QObject.connect(self.spinBoxNumSetup,QtCore.SIGNAL("valueChanged(int)"),self.ensureEvenVal)
       # QtCore.QObject.connect(self.checkBoxSens,QtCore.SIGNAL("toggled(bool)"),self.sensImpact)

    def updateProgressLim(self,lim):
        if lim == 0:
            return
        self.progressB.setMaximum(lim)

   # def updateProgressLim2(self,lim):
    #    self.progressB2.setMaximum(self.count*lim)
           

   # def sensImpact(self,state):
    #    self.updateProgressLim(self.spinBoxNumFile.value())
    
  #  def ensureEvenVal(self, val):
  #      if val < 10:
  #          return
  #      elif (val & 1):
  #          self.spinBoxNumSetup.setValue(val+1)

    def checkAnalysis(self, state):
        if state:
            if self.sender() == self.checkBoxSens:
                self.checkBoxUni.setChecked(False)
           #     self.spinBoxNumSetup.setDisabled(True)
           #     self.spinBoxNumSetup.setValue(1)
            else:
                self.checkBoxSens.setChecked(False)
           #     self.spinBoxNumSetup.setDisabled(False)
           #     self.spinBoxNumSetup.setValue(2)

      #  if not state:
      #      if self.sender() == self.checkBoxUni:
      #          self.spinBoxNumSetup.setDisabled(True)
      #          self.spinBoxNumSetup.setValue(1)

    def checkWatcher(self,state):
        '''
        @summary Make sure at least one checkBox is checked at anytime
        @param state : check state of the sender
        ''' 
        if not state:
            if self.sender() == self.checkBoxGen:
                if not self.checkBoxSim.isChecked():
                    self.checkBoxGen.setChecked(True)
            else:
                if not self.checkBoxGen.isChecked():
                    self.checkBoxSim.setChecked(True)
                    
    def generate(self):
        '''
        @summary Generate configuration file with different random seeds
        ''' 
        i = 0
        while True:
            try:
                os.remove(self.baseFile[:-4] + "_" + str(i) + ".xml")
                i += 1
            except:
                break
        for dirname, dirnames, filenames in os.walk('.'):
            if dirname[-2:] == 'LO' or dirname[-2:] == 'UP':
                shutil.rmtree(dirname)


        f = Opener(self.baseFile)
        rootNode = f.getRootNode()
        GeneratorSeeds = rootNode.toElement().firstChildElement("Input").firstChildElement("PopulationManager").firstChildElement("Generator").firstChildElement("RandomizerInfo")
        SimulatorSeeds = rootNode.toElement().firstChildElement("Simulation").firstChildElement("RandomizerInfo")
        paramNode = rootNode.toElement().firstChildElement("System").firstChildElement("Parameters")
        EntryNodes = paramNode.elementsByTagName("Entry")
        threadsGenerator = self.spinBoxGenThread.value()
        threadsSimulator = self.spinBoxSimThread.value()

        elt = paramNode.firstChildElement("Entry")
        while elt.attribute("label") != "threads.simulator":
            elt = elt.nextSiblingElement("Entry")
        elt = elt.firstChild().toElement()
        elt.toElement().setAttribute("value", str(threadsSimulator))

        elt = paramNode.firstChildElement("Entry")
        while elt.attribute("label") != "threads.generator":
            elt = elt.nextSiblingElement("Entry")
        elt = elt.firstChild().toElement()
        elt.toElement().setAttribute("value", str(threadsGenerator))

        if self.checkBoxGen.isChecked():
            if threadsGenerator < GeneratorSeeds.childNodes().count():
                compteur = GeneratorSeeds.childNodes().count()-threadsGenerator
                while compteur !=0 :
                    GeneratorSeeds.removeChild(GeneratorSeeds.lastChild())
                    compteur = compteur -1
            else:
                compteur = threadsGenerator-GeneratorSeeds.childNodes().count()
                while compteur != 0 :
                    GeneratorSeeds.appendChild(GeneratorSeeds.ownerDocument().createElement("Randomizer"))
                    compteur = compteur -1
                
        if self.checkBoxSim.isChecked():
            if threadsSimulator < SimulatorSeeds.childNodes().count():
                compteur = SimulatorSeeds.childNodes().count()-threadsSimulator
                while compteur !=0 :
                    SimulatorSeeds.removeChild(SimulatorSeeds.lastChild())
                    compteur = compteur -1
            else:
                compteur = threadsSimulator-SimulatorSeeds.childNodes().count()
                while compteur != 0 :
                    SimulatorSeeds.appendChild(SimulatorSeeds.ownerDocument().createElement("Randomizer"))
                    compteur = compteur -1

        #Generator pseudo-random numbers for seeds
        fileNumber = 0
        tmpTextStream = QtCore.QTextStream()
        randomGenerator = SystemRandom()
        if self.comboBoxBits.currentIndex() == 0:
            bitLength = 64
            maxLong = 18446744073709551615 
        else:
            bitLength = 32 
            maxLong = 4294967295

        while fileNumber != self.spinBoxNumFile.value():
            if self.checkBoxGen.isChecked():
                for i in range(0,GeneratorSeeds.childNodes().count()):
                    currentRand = GeneratorSeeds.childNodes().item(i)
                    currentRand.toElement().setAttribute("state","")
                    try :
                        randomLong = randomGenerator.getrandbits(bitLength)
                    except NotImplementedError:
                        randomLong = randint(1,maxLong)
                    currentRand.toElement().setAttribute("seed",randomLong)
            if self.checkBoxSim.isChecked():
                for i in range(0,SimulatorSeeds.childNodes().count()):
                    currentRand = SimulatorSeeds.childNodes().item(i)
                    currentRand.toElement().setAttribute("state","")
                    try :
                        randomLong = randomGenerator.getrandbits(bitLength)
                    except NotImplementedError:
                        randomLong = randint(1,maxLong)
                    currentRand.toElement().setAttribute("seed",randomLong)
            fileP = QtCore.QFile(self.baseFile.rsplit(".")[0] + ("_") + str(fileNumber) + ".xml")
            fileP.open(QtCore.QIODevice.ReadWrite|QtCore.QIODevice.Truncate)
            tmpTextStream.setDevice(fileP)
            rootNode.save(tmpTextStream,5)
            fileP.close()
            fileNumber += 1
            self.counter += 1
            self.progressB.setValue(self.counter)

        if self.checkBoxSens.isChecked() or self.checkBoxUni.isChecked():
            path = str(self.baseFile[:-4])+"_"
            util.script_sens.main(path, self.spinBoxNumFile.value(),self.progressB2,self.progressB2.value(),self.checkBoxUni.isChecked())

        self.accept()
