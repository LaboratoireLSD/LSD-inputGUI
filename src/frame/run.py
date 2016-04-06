'''

Created on 2010-08-03

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

from PyQt4 import QtCore
from PyQt4 import QtGui

from model.baseTreatmentsModel import BaseTreatmentsModel
from model.PrefModel import PrefModel
import subprocess
import os
import shutil
#import pexpect


LocalSimulatorPath = "/home/mathieu/workspace/lsdsimulation/Simulator/Release/SCHNAPS.so"
LibPath = "/home/mathieu/workspace/lsdsimulation/Libs"
DefaultResultPath = "/home/mathieu/workspace/lsdsimulation/Results"

class schnaps(QtGui.QDialog):
    '''
    This class is intented to be loaded from XMLbc when its time to launch a simulation
    Class name has to be the same as the fileName or it XMLbc won't be able to pop up the dialog
    This is experimental code and architecture and will need improvement
    This class inherits QDialog, and most of its function are reimplemented
    '''

    def __init__(self,parent= None,topWObject= None):
        '''
        @summary Constructor
        @param parent : Tab associated with this dialog
        @param topWObject : application's mainWindow
        '''
        QtGui.QDialog.__init__(self,parent)
        self.mainWindow = topWObject
        self.setupUi()
        
        
    def setupUi(self):
        
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(90, 200, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        
        self.labelScenario = QtGui.QLabel("Scenarios")
        self.listScenario = QtGui.QListWidget()
        self.setupScenarios(self.listScenario)
        self.labelOptions = QtGui.QLabel("Options")
        self.listOptions = QtGui.QListWidget()
        self.setupOptions(self.listOptions)
        self.horizontalLayoutGen = QtGui.QHBoxLayout()
        self.horizontalLayoutSim = QtGui.QHBoxLayout()
        self.horizontalLayoutPrintPath = QtGui.QHBoxLayout()
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.addWidget(self.labelScenario)
        self.verticalLayout.addWidget(self.listScenario)
        self.verticalLayout.addWidget(self.labelOptions)
        self.verticalLayout.addWidget(self.listOptions)
        #Repetition widgets
        self.horizontalLayoutRuns = QtGui.QHBoxLayout()
        self.runLabel = QtGui.QLabel("Run each scenario ")
        self.repSpinBox = QtGui.QSpinBox()
        self.repSpinBox.setValue(1)
        self.repSpinBox.setMaximum(500)
        self.timeLabel = QtGui.QLabel("time(s)")
        self.horizontalLayoutRuns.addWidget(self.runLabel)
        self.horizontalLayoutRuns.addWidget(self.repSpinBox)
        self.horizontalLayoutRuns.addWidget(self.timeLabel)
        self.horizontalLayoutRuns.setAlignment(QtCore.Qt.AlignLeft)
        self.verticalLayout.addLayout(self.horizontalLayoutRuns)
        #Estimated runtime widgets
        self.horizontalLayoutEstimation = QtGui.QHBoxLayout()
        self.estimationLabel = QtGui.QLabel("Estimated runtime : ")
        self.estSpinBox = QtGui.QSpinBox()
        self.estSpinBox.setMaximum(100000)
        self.secLabel = QtGui.QLabel("seconds")
        self.horizontalLayoutEstimation.addWidget(self.estimationLabel)
        self.horizontalLayoutEstimation.addWidget(self.estSpinBox)
        self.horizontalLayoutEstimation.addWidget(self.secLabel)
        self.horizontalLayoutEstimation.setAlignment(QtCore.Qt.AlignLeft)
        self.verticalLayout.addLayout(self.horizontalLayoutEstimation)
        #Defining layout for threads.generator and threads.simulator and print.prefix
        self.checkBoxShowAdvancedOptions = QtGui.QCheckBox("Advanced options")
        self.verticalLayout.addWidget(self.checkBoxShowAdvancedOptions)
        self.widgetAdvancedContainer = QtGui.QWidget()
        self.widgetAdvancedContainer.setLayout(QtGui.QVBoxLayout())
        self.labelGen = QtGui.QLabel("threads.generator")
        self.labelGen.setFixedWidth(120)
        self.spinBoxGen = QtGui.QSpinBox()
        self.spinBoxGen.setValue(8)
        self.horizontalLayoutGen.addWidget(self.labelGen)
        self.horizontalLayoutGen.addWidget(self.spinBoxGen)
        self.widgetAdvancedContainer.layout().addLayout(self.horizontalLayoutGen)
        self.labelSim = QtGui.QLabel("threads.simulator")
        self.labelSim.setFixedWidth(120)
        self.spinBoxSim = QtGui.QSpinBox()
        self.spinBoxSim.setValue(8)
        self.horizontalLayoutSim.addWidget(self.labelSim)
        self.horizontalLayoutSim.addWidget(self.spinBoxSim)
        self.widgetAdvancedContainer.layout().addLayout(self.horizontalLayoutSim)
        self.horizontalLayoutGen.setAlignment(self.spinBoxGen, QtCore.Qt.AlignLeft)
        self.horizontalLayoutSim.setAlignment(self.spinBoxSim, QtCore.Qt.AlignLeft)
        #Print prefix
        self.labelPrintPath = QtGui.QLabel("print.prefix")
        self.lineEditPath = QtGui.QLineEdit()
        self.horizontalLayoutPrintPath.addWidget(self.labelPrintPath)
        self.horizontalLayoutPrintPath.addWidget(self.lineEditPath)
        self.widgetAdvancedContainer.layout().addLayout(self.horizontalLayoutPrintPath)
        self.buttonBrowse = QtGui.QPushButton("Browse")
        self.buttonBrowse.setFixedWidth(60)
        self.widgetAdvancedContainer.layout().addWidget(self.buttonBrowse)
        self.widgetAdvancedContainer.layout().setAlignment(self.buttonBrowse, QtCore.Qt.AlignRight)
        
        
        self.verticalLayout.addWidget(self.widgetAdvancedContainer)
        self.checkBoxLocal = QtGui.QCheckBox("Simulate locally")
        self.checkBoxLocal.setAutoExclusive(True)
        self.checkBoxLSD = QtGui.QCheckBox("Simulate on LSD Server")
        self.checkBoxLSD.setAutoExclusive(True)
        self.checkBoxServer = QtGui.QCheckBox("Simulate on CLUMEQ's supercomputer (default : Colosse)")
        self.checkBoxServer.setAutoExclusive(True)
        self.checkBoxServer.setChecked(True)
        self.verticalLayout.addWidget(self.checkBoxLocal)
        self.verticalLayout.addWidget(self.checkBoxLSD)
        self.verticalLayout.addWidget(self.checkBoxServer)
        self.verticalLayout.addWidget(self.buttonBox)
        self.setLayout(self.verticalLayout)
        
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.checkBoxShowAdvancedOptions, QtCore.SIGNAL("toggled(bool)"), self.expOrColAdv)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QObject.connect(self.buttonBrowse, QtCore.SIGNAL("clicked()"), self.browse)
        QtCore.QMetaObject.connectSlotsByName(self)
        
        self.checkBoxShowAdvancedOptions.setChecked(False)
        self.widgetAdvancedContainer.setVisible(False)
        
    def expOrColAdv(self,toggled):
        '''
        @summary Collapse/Expand Advanced options
        @param toggled : boolean, tells if state is collapsed or expanded
        '''
        if toggled:
            self.widgetAdvancedContainer.setVisible(True)
        else:
            self.widgetAdvancedContainer.setVisible(False)
            
    def browse(self):
        '''
        @summary This function is called when self.buttonBrowse is pressed
        '''
        file = QtGui.QFileDialog.getExistingDirectory(self,self.tr("Open Directory"),DefaultResultPath)
                                                
        if not file.isNull():
            self.lineEditPath.setText(file)
    
    def setupScenarios(self, list):
        '''
        @summary This function is called when to populate list with all scenarios found in template file
        @param list : the list we want to populate with scenario names
        '''
        baseTrModel = BaseTreatmentsModel()
        list.addItems(baseTrModel.getViewScenariosDict())
        for item in [list.item(row) for row in range(0,list.count())] :
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            
    def setupOptions(self,list):
        '''
        @summary This function is called when to populate list with all options known at this time to be compatible with schnaps
        @param list : the list we want to populate with options
        '''
        list.addItems(["Save log","Save input","Save output","Save conf"])
        for item in [list.item(row) for row in range(0,list.count())]:
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
        
    def accept(self):
        '''
        @summary This function is called when the ok button has been pressed, triggering the launch of a simulation
        '''
        model = PrefModel()
        
        if not  [self.listScenario.item(row) for row in range(0,self.listScenario.count()) if self.listScenario.item(row).checkState()==QtCore.Qt.Checked]:
            QtGui.QMessageBox.warning( self, "No scenario selected", "Choose one or more scenarios or press Cancel")
            return
        
        
        self.createFiles()
        return
        if not os.path.exists(self.mainWindow.folderPath[0:-1]+".lsd"):
            QtGui.QMessageBox.warning(self,"Could not find valid project file","LSD Input Gui could not find a valid project file to send to the simulator. Perhaps project has not been saved?")
            shutil.rmtree("Tmp")
            return
        elif self.mainWindow.dirty:
            sendAnyway = QtGui.QMessageBox.question(self,"Unsaved changes","It seems like project contains unsaved changes. Send anyway?")
            if not sendAnyway:
                shutil.rmtree("Tmp")
                return
        if not model.getSimServer():
            server, keepGoing = QtGui.QInputDialog.getText(self, "Unspecified simulation server", "Specify simulation server\n Example : colosse.clumeq.ca")
            if keepGoing:
                model.setSimServer(server)
            else:
                shutil.rmtree("Tmp")
                return
            
        serverText = "User name to connect to " + str(model.getSimServer())
        
        if not model.getUserName():
            user, keepGoing = QtGui.QInputDialog.getText(self, "Login", serverText)
            if keepGoing:
                model.setUserName(user)
            else:
                #Make sure to clear folder or bad things can occur
                shutil.rmtree("Tmp")
                return
        
        #First, download configuration file on server
        #Presume user has already set up a pub key with the server
        try:
            subprocess.check_call(["scp", self.mainWindow.folderPath[0:-1]+".lsd",model.getUserName()+"@"+model.getSimServer()+":/home/"+model.getUserName()+"/SCHNAPS/Configs"])
        except subprocess.CalledProcessError:
            QtGui.QMessageBox.critical(self,"Error occured","Could not transfer configuration file to server")
            #Make sure to clear folder or bad things can occur
            shutil.rmtree("Tmp")
            return
        
        #Then, untar configuration file
        try:
            subprocess.check_call(["ssh", model.getUserName()+"@"+model.getSimServer(),"unzip -o SCHNAPS/Configs/"+self.mainWindow.projectName+".lsd"])
        except subprocess.CalledProcessError:
            QtGui.QMessageBox.critical(self,"Error occured","Could not uncompress configuration file!")
            #Make sure to clear folder or bad things can occur
            shutil.rmtree("Tmp")
            return
        
        #REmove archive from server
        try:
            subprocess.check_call(["ssh", model.getUserName()+"@"+model.getSimServer(),"rm SCHNAPS/Configs/"+self.mainWindow.projectName+".lsd"])
        except subprocess.CalledProcessError:
            QtGui.QMessageBox.critical(self,"Error occured","Could not delete archive after uncompression!")
            #Make sure to clear folder or bad things can occur
            shutil.rmtree("Tmp")
            return
        
        #Now, send Tmp folder on server
        #First, rename it
        os.rename("Tmp",self.mainWindow.projectName)
        #Then. throw it on server
        try:
            subprocess.check_call(["scp","-r", self.mainWindow.projectName,model.getUserName()+"@"+model.getSimServer()+":/home/"+model.getUserName()])
        except subprocess.CalledProcessError:
            QtGui.QMessageBox.critical(self,"Error occured","Could not transfer scripts file to server")
            #Make sure to clear folder or bad things can occur
            shutil.rmtree(self.mainWindow.projectName)
            return
        
        #Then, we only need to launch SCHNAPS!
        try:
            subprocess.check_call(["ssh", model.getUserName()+"@"+model.getSimServer(),self.mainWindow.projectName+"/Launch_"+self.mainWindow.projectName+"_0.sh"])
        except subprocess.CalledProcessError:
            QtGui.QMessageBox.critical(self,"Error occured","Could not start the simulation")
            #Make sure to clear folder or bad things can occur
            shutil.rmtree(self.mainWindow.projectName)
            return
        
        #Make sure to clear folder or bad things can occur
        shutil.rmtree(self.mainWindow.projectName)
        
    
    def createFiles(self):
        #Here is where we need some mental gymnastic
        os.mkdir("Tmp")
        numberOfRep = self.repSpinBox.value()
        numberOfScenarios = len([self.listScenario.item(row) for row in range(0,self.listScenario.count()) if self.listScenario.item(row).checkState()==QtCore.Qt.Checked])
        numberOfRuns = numberOfRep*numberOfScenarios
        #Cannot launch more than 500 item arrays
        if numberOfRuns > 500:
            numberOfScenPerFiles = 500/numberOfRep
            scenarioList = [self.listScenario.item(row).text() for row in range(0,self.listScenario.count()) if self.listScenario.item(row).checkState()==QtCore.Qt.Checked]
            compteur = 0
            currScenList = []
            
            while scenarioList:
                if compteur % numberOfScenPerFiles  == 0 and compteur != 0:
                    keepGoing = self.createSGEscript(currScenList, "submit_" + self.mainWindow.projectName + "_" + str(compteur/numberOfScenPerFiles) + ".sh")
                    if not keepGoing:
                        shutil.rmtree("Tmp")
                        return
                    currScenList = []
                scenarioList.reverse()
                currScenList.append(scenarioList.pop())
                scenarioList.reverse()
                compteur+=1
            
            #Look if there still is/are scenario(s) in list
            if currScenList:
                fileName = "submit_" + self.mainWindow.projectName + "_" + str(compteur/numberOfScenPerFiles+1) + ".sh"
                keepGoing = self.createSGEscript(currScenList, fileName)
                if not keepGoing:
                    shutil.rmtree("Tmp")
                    return
        
        else:
            scenarioList = [self.listScenario.item(row).text() for row in range(0,self.listScenario.count()) if self.listScenario.item(row).checkState() == QtCore.Qt.Checked]
            keepGoing = self.createSGEscript(scenarioList, "submit_" + self.mainWindow.projectName + ".sh")
            if not keepGoing:
                shutil.rmtree("Tmp")
                return
        
        #Now that file creation is over, we have to create launch scripts
        self.createLaunchScript()
        
    def createSGEscript(self,scenarioList,fileName):
        '''
        @summary Function creates a SGE script that can be used to launch SCHNAPS on Colosse
        @param scenarioList : List of scenarios for the script
        @param fileNumber : number of the file. All files related to the same project are numbered
        '''
        #Get preference model as multiple information is needed and contained in preferences
        model = PrefModel()
        
        #Copy script template to temp dir
        shutil.copy("util/submit.sh", "Tmp/"+fileName)
        
        #Open file
        SGEscript = open("Tmp/"+fileName,'a')
        #Specify project number
        SGEscript.write("# Specifies  the  project (RAPI number from CCDB) to  which this job is assigned.\n")
        if not model.getProjectName():
            #Need to create or own dialog with a line edit with an input mask
            pNumberDialog = QtGui.QDialog()
            pNumberDialogLayout = QtGui.QHBoxLayout()
            pNumberDialogMainLayout = QtGui.QVBoxLayout()
            pNumberDialogLabel = QtGui.QLabel("CCDB 8 character-code : ")
            pNumberDialogInp = QtGui.QLineEdit()
            pNumberDialogInp.setInputMask("NNN-NNN-NN")
            pNumberDialogLayout.addWidget(pNumberDialogLabel)
            pNumberDialogLayout.addWidget(pNumberDialogInp)
            pNumberDialog.setWindowTitle("CCDB project number required")
            pNumberDialogButtonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal,pNumberDialog)
            pNumberDialogMainLayout.addLayout(pNumberDialogLayout)
            pNumberDialogMainLayout.addWidget(pNumberDialogButtonBox)
            pNumberDialog.setLayout(pNumberDialogMainLayout)
            QtCore.QObject.connect(pNumberDialogButtonBox, QtCore.SIGNAL("accepted()"), pNumberDialog.accept)
            QtCore.QObject.connect(pNumberDialogButtonBox, QtCore.SIGNAL("rejected()"), pNumberDialog.reject)
            pNumberDialog.exec_()
            if pNumberDialog.result():
                model.setProjectName(pNumberDialogInp.text())
            else:
                return False
        SGEscript.write("#$ -P "+model.getProjectName()+"\n\n")
        #Specify mail
        SGEscript.write("\n# List of users to which the server that executes the job has to send mail.\n")
        if not model.getEmail():
            email, accepted = QtGui.QInputDialog.getText(self,"Mail required","User e-mail :")
            if accepted:
                model.setEmail(email)
            else:
                return False
        SGEscript.write("#$ -M "+model.getEmail()+"\n\n")
        #Specify condition when to send the mail
        SGEscript.write("\n# Under which circumstances mail is to be sent?\n")
        SGEscript.write("#$ -m "+model.getMailCondition()+"\n\n")
        #Create Arrays
        arraySize = len(scenarioList*self.repSpinBox.value())
        SGEscript.write("\n# Serial Array jobs (format = min-max:step).\n")
        SGEscript.write("#$ -t 1:"+str(arraySize)+":1\n\n")
        #Define queue and number of cores
        #We take simulation cores asked by user. For maximum performance user should avoid specifying different number of cores
        #for the generator and the simulator
        SGEscript.write("\n# Parallel programming environment (PE) to instantiate and the numbers of cores.\n")
        SGEscript.write("#$ -pe default "+str(self.spinBoxSim.value())+"   # (allocated on a single host max=8)\n\n")
        #Estimated runtime
        SGEscript.write("\n# All jobs must be submitted with an estimated run time. (in seconds).\n")
        SGEscript.write("#$ -l h_rt="+str(self.estSpinBox.value())+"\n\n")
        #Error Scripts
        SGEscript.write("\n# The path used for the standard output stream of the job.\n")
        SGEscript.write("#$ -o $HOME/SCHNAPS/Configs/"+self.mainWindow.projectName+"/Job.out\n\n")
        SGEscript.write("\n# The path used for the standard error stream of the job.\n")
        SGEscript.write("#$ -e $HOME/SCHNAPS/Configs/"+self.mainWindow.projectName+"/Job.err\n\n")
        
        #SGE commands done, now we can concentrate on the job itself
        #First, export libraries
        SGEscript.write("\nLD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/SCHNAPS/Libs\n")
        SGEscript.write("export LD_LIBRARY_PATH\n")
        #Then, request job info from pbs scheduler
        SGEscript.write("\nTASKID=$(( ${SGE_TASK_ID} - 1 ))\n")
        SGEscript.write("SCENARIO_NB=$(( $TASKID % "+str(len(scenarioList))+" ))\n")
        SGEscript.write("RUN=$(( $TASKID / "+str(len(scenarioList))+" ))\n")
        #Then, write Scenario loop
        SGEscript.write("\ncase $SCENARIO_NB in\n\n")
        for scenNumber in range(0,len(scenarioList)):
            SGEscript.write("\t"+str(scenNumber)+') SCENARIO="'+scenarioList[scenNumber]+'";;\n')
        SGEscript.write('\t* ) echo "Unknown Scenario number!"\n')
        SGEscript.write('\nesac\n\n')
        #Create variable for dir and parameters considering there might be sensibility analysis
        SGEscript.write("#Next lines are for parameters sent via the command line\n")
        SGEscript.write("""args=("$@")\n""")
        SGEscript.write("params=''\n")
        SGEscript.write("folder=''\n")
        SGEscript.write("for ((paramNumber=0; paramNumber<$#/2; paramNumber++))\n")
        SGEscript.write("\tdo\n")
        SGEscript.write("""\tparams=$params",ref."${args[2*$paramNumber]}"="${args[2*$paramNumber+1]}","\n""")
        SGEscript.write("""\tfolder=$folder"/"${args[2*$paramNumber]}"/"${args[2*$paramNumber+1]}\n""")
        SGEscript.write("\tdone\n")
        #Write mkdir command
        SGEscript.write("\nmkdir -p $HOME/SCHNAPS/Results/"+self.mainWindow.projectName+"/$SCENARIO/$folder/$RUN\n\n")
        #End with Launch command
        logOption =  "true" if self.listOptions.item(0).data(QtCore.Qt.CheckStateRole).toInt() == QtCore.Qt.Checked else "false"
        inputOption = "true" if self.listOptions.item(1).data(QtCore.Qt.CheckStateRole).toInt() == QtCore.Qt.Checked else "false"
        outputOption= "true" if self.listOptions.item(2).data(QtCore.Qt.CheckStateRole).toInt() == QtCore.Qt.Checked else "false"
        SGEscript.write("\nfuncCall = '$HOME/SCHNAPS/Simulator/Release/SCHNAPS.so -d $HOME/SCHNAPS/Configs/"+self.mainWindow.projectName+" -c parameters_$RUN.xml -s $SCENARIO -p print.prefix=$HOME/SCHNAPS/Results/"+self.mainWindow.projectName+"/$SCENARIO/$folder/$RUN/,print.input="+inputOption+",print.output="+outputOption+",print.log="+logOption+"'")
        SGEscript.write("\nfuncCall = $funcCall$params\n\n")
        SGEscript.write("$funcCall\n\n")
        SGEscript.write("#Generate md5 checksum for LSD server to verify file integrity after transfer\n")
        SGEscript.write("md5sum $HOME/SCHNAPS/Results/"+self.mainWindow.projectName+"/$SCENARIO/$folder/$RUN/Output.gz | awk '{print $1}' > $HOME/SCHNAPS/Results/"+self.mainWindow.projectName+"/$SCENARIO/$folder/$RUN/Output.md5\n")
        SGEscript.write("md5sum $HOME/SCHNAPS/Results/"+self.mainWindow.projectName+"/$SCENARIO/$folder/$RUN/Summary.gz | awk '{print $1}' > $HOME/SCHNAPS/Results/"+self.mainWindow.projectName+"/$SCENARIO/$folder/$RUN/Summary.md5\n")
        SGEscript.close()
        return True
    def createLaunchScript(self):
        '''
        @summary Creates the scripts that will launch the jobs on Colosse
        '''
        fileList = os.listdir("Tmp")
        
        numLaunchFile = (len(fileList)/50 + 1) if len(fileList) % 50 else len(fileList)/50
        for i in range(0,numLaunchFile):
            currFile = open('Tmp/Launch_'+str(self.mainWindow.projectName)+'_'+str(i)+'.sh','w')
            currFile.write('#!/bin/bash\n\n')
            for j in range((50*i),(50*(i+1))):
                try:
                    currFile.write("qsub"+" -N "+self.mainWindow.projectName[0:4]+"_"+str(j)+" "+self.mainWindow.projectName+"/"+fileList[j]+"\n\n")
                except IndexError:
                    currFile.close()
                    break
            currFile.close()
            
    def createFileList(self,scenarioList):
        '''
        @summary Creates the the file list that is going to be used by Koksoak(LSD's server) to figure if there are still running jobs on Colosse
        @param scenarioList : List of scenarios for the script
        '''
        
        fListFile = open('Tmp/fileList.txt','a')
        
        for scen in scenarioList:
            for rep in range(0,self.repSpinBox.value()):
                fListFile.write('$HOME/SCHNAPS/Results/'+self.mainWindow.projectName+'/'+scen+'/'+str(rep)+'\n')
            
        fListFile.close()        
    
