# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 15:31:59 2016

@author: mathieu boily
"""

import os, sys, getopt, ntpath, re
from lxml import etree as ET

try:
    import paramiko
except:
    print("Error : Paramiko isn't installed on your system.")
    print("Before installing it, make sure you have the correct dependencies with : 'sudo apt-get install build-essential libssl-dev libffi-dev python-dev'")
    print("Then, install pip with 'sudo apt-get install python-pip' and paramiko with 'sudo pip install paramiko'\n")
    sys.exit(2)    

def showHelp():
    print("\n\n")
    print("Possible arguments :\n")
    
    print("     -p, --project <path>               Complete path to the project (folder's name)")
    print("     -u, --username <name>              Username on Colosse for the ssh connection")
    print("     -e, --email <email>                Colosse will send an email to this address when the simulation will begin and end")
    print("     [-m, --mode <1-4>]                 --Missing explanations-- Default = 2")
    print("     [-x, --push-execution]             Pushes also the execution script. If not used, it assumes that it's already there")
    print("     [-d, --duration <HH:MM:SS>]        Maximum duration of the simulation. Default = 48:00:00. Cannot exceed 48h")
    print("     [-o, --options <option>]           Options for SCHNAPS. See its doc for more information.")
    print("     [-h, --help]                       Shows the help page\n\n")
    print("For help about the RSA key : http://doc.fedora-fr.org/wiki/SSH_:_Authentification_par_cl%C3%A9")

def main(argv):
    submitScriptName = "generated_submit.pbs"
    submitScriptPath = "~/"
    executionScriptName = "task_runner.py"
    executionScriptPath = "~/"
    cronJobScriptName = "results_fetcher.py"
    cronJobScriptPath = "/home/lsdadmin/scripts/"
    pushExecutionScript = False
    emailTo = ""
    duration = "48:00:00"
    rapId = "wny-790-aa"
    username = ""
    projectPath = ""
    projectName = ""
    scenarios = []
    scenariosToString = "" #Will be used to pass all the scenario to the execution script
    advParameters = "" #Advanced parameters - Schnaps
    jobId = ""
    mode = 2 # How jobs will be created 
    nbTasks = 0 # Tasks in the array of jobs
    nbIterations = 0
    
    #Accepted arguments
    try:
        options, arguments = getopt.getopt(argv, "hxp:u:e:d:o:m:", ["help", "project=", "username=", "push-execution", "email=", "duration=", "options=", "mode="])
    except getopt.GetoptError as error:
        print (error)
        showHelp()
        sys.exit(2)
        
    if not options: #If no options given
        showHelp()
        sys.exit(2)
    
    #Parsing all the options
    for opt, arg in options:
        if (opt in ('-h', '--help')):
            showHelp()
            sys.exit()
        elif (opt in ('-p', '--project')):
            if os.path.isdir(arg):
                projectPath = arg
                if projectPath.endswith("/"):
                    projectPath = projectPath[:-1]
                projectName = ntpath.basename(projectPath)
            else:
                print("Invalid project's folder")
                showHelp()
                sys.exit(2)
        elif (opt in ("-u", "--username")):
            username = arg
        elif (opt in ("-x", "--push-execution")):
            pushExecutionScript = True
        elif (opt in ("-e", "--email")):
            emailTo = arg
        elif (opt in ("-d", "--duration")):
            if re.match("([0-9]+):([0-5][0-9]):([0-5][0-9])", arg):
                duration = arg
            else:
                print("Error : Duration must be HH:MM:SS\n")
                showHelp()
                sys.exit(2)
        elif (opt in ("-o", "--options")):
            advParameters = " -o " + arg
        elif (opt in ("-,", "--mode")):
            mode = int(arg)
            
    # Getting scenarios. Find the first "parameters_x.xml" in project to retrieve scenarios
    parameterName = [fileName for fileName in os.listdir(projectPath) if os.path.isfile(os.path.join(projectPath, fileName)) and fileName.startswith("parameters_")]
    parametersFile = ET.parse(os.path.join(projectPath, parameterName[0]))
    nbIterations = len(parameterName) - 1 # Number of parameters_x.xml files = number of iterations
    for scenario in parametersFile.xpath("/Simulator/Simulation/Scenarios/Scenario"):
        scenarios.append(scenario.get("processIndividual"))
        scenariosToString += " -s " + scenarios[-1]
        
    if not username or not scenarios or not projectName or not emailTo:
        #Project, scenario, email and username are necessary
        #Project must be the LSD archive
        showHelp()
        sys.exit(2)
        
    # Getting the number of jobs depending on the chosen mode
    if mode == 1:
        # 1 job per simulation (Ex. 5 scenarios with 100 simulations = 500 jobs)
        nbTasks = len(scenarios) * nbIterations
    elif mode == 2:
        # 1 job per iteration
        nbTasks = nbIterations
    elif mode == 3:
        # 1 job per scenario
        nbTasks = len(scenarios)
    else:
        # 1 job for all
        nbTasks = 1
       
    #Submission script content
    submitScriptContent = ("#!/bin/bash\n"
                           "#PBS -A " + rapId + "\n" #Rap ID
                           "#PBS -l walltime=" + duration + "\n" #Max duration HH:MM:SS
                           "#PBS -l nodes=1:ppn=8\n" #Total nodes and hearts
                           #"#PBS -q test\n" #Which queue. Can be omitted.
                           "#PBS -N " + projectName + "\n" #Job's name
                           "#PBS -o output_" + projectName + "_%I.out\n" #Standard output
                           "#PBS -e error_" + projectName + "_%I.err\n" #Error output
                           "#PBS -t [0-" + str(nbTasks) + "]%50\n" # Array of jobs. Max 50 jobs at the same time. Can be anything else than 50 (don't know the max)
                           
                           "python " + os.path.join(executionScriptPath, executionScriptName) + " -p " + projectName + " -m " + str(mode) + " -t $MOAB_JOBARRAYINDEX -i " + str(nbIterations) + scenariosToString + advParameters + " -r " + rapId + "\n" #Executing the 2nd script
                           )
    
    print("Connection to Colosse by ssh.")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    k = paramiko.RSAKey.from_private_key_file(os.path.expanduser("~/.ssh/id_rsa"))
    ssh.connect(hostname="colosse.calculquebec.ca", username=username, pkey=k)
        
    print("Generating the submit script on Colosse.")
    ssh.exec_command("echo '" + submitScriptContent + "' > " + os.path.join(submitScriptPath, submitScriptName) + "\n")
    
    if pushExecutionScript:
        print("Sending the execution script.")
        os.system("scp " + os.path.join(os.path.dirname(os.path.realpath(__file__)), executionScriptName) + " " + username + "@colosse.calculquebec.ca:")

    print("Sending the project folder to : " + username + "@colosse.calculquebec.ca:/scratch/" + rapId)
    os.system("scp -r " + projectPath + " " + username + "@colosse.calculquebec.ca:/scratch/" + rapId)

    print("Launching the submit script.")
    stin, stout, sterr = ssh.exec_command("msub " + os.path.join(submitScriptPath, submitScriptName) + "\n")
    sterrRead = sterr.readlines() #If ssh returns an error
    stoutRead = stout.readlines() #If the ssh returns a normal output
    
    if sterrRead:
        #An error has occurred
        print(sterrRead)
    if stoutRead:
        #Printing the return of the previous commands.
        if type(stoutRead) is list and str.isdigit(str(stoutRead[1]).strip()):
            print("Job's id : " + stoutRead[1])
            jobId = stoutRead[1].strip()
        else:
            print(str(stoutRead))
            print("Couldn't get the job's id. Exiting without creating a cron job on Koksoak.")
            sys.exit(2)
    
    ssh.close()
    
    print("-------------------------------")
    print("Connection to Koksoak by ssh.")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    k = paramiko.RSAKey.from_private_key_file(os.path.expanduser("~/.ssh/id_rsa"))
    ssh.connect(hostname="koksoak.gel.ulaval.ca", username="lsdadmin", pkey=k)
    
    print("Creating a cron job on Koksoak.")
    stin, stout, sterr = ssh.exec_command("python " + os.path.join(cronJobScriptPath, cronJobScriptName) + " -u " + username + " -i " + jobId + " -p " + projectName + " -e " + emailTo + " -c\n")
    sterrRead = sterr.readlines() #If ssh returns an error
    stoutRead = stout.readlines() #If the ssh returns a normal output
    
    if sterrRead:
        #An error has occurred
        if type(sterrRead) is list:
            for line in sterrRead:
                print(line)
        else:
            print(sterrRead)
    if stoutRead:
        #Printing the return of the previous commands.
        if type(stoutRead) is list:
            for line in stoutRead:
                print(line)
        else:
            print(stoutRead)
    
    ssh.close()
    print("Done")

main(sys.argv[1:])