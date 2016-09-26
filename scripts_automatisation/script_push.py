# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 15:31:59 2016

@author: mathieu boily
"""

import os, sys, getopt, ntpath, re

try:
    import paramiko
except:
    print("Error : Paramiko isn't installed on your system.")
    print("Please, install pip with 'sudo apt-get install python-pip' and then 'sudo pip install paramiko'\n")
    sys.exit(2)
    
try:
    import scp
except:
    print("Error : scp.py must be in the same folder as this script.")
    print("Link to download if needed : https://github.com/jbardin/scp.py/blob/master/scp.py")
    sys.exit(2)
    

def showHelp():
    print("\n\n")
    print("Possible arguments :\n")
    
    print("     -p, --project <path>               Complete path to the project (LSD file)")
    print("     -s, --scenario <name>              Name of the scenario to run")
    print("     -u, --username <name>              Username on Colosse for the ssh connection")
    print("     -e, --email <email>                Colosse will send an email to this address when the simulation will begin and end")
    print("     [-x, --push-execution]             Pushes also the execution script. If not used, it assumes that it's already there")
    print("     [-d, --duration <HH:MM:SS>]        Maximum duration of the simulation. Default = 24:00:00")
    print("     [-c, --configuration-file <name>]  Name of the parameters file. Default = parameters.xml")
    print("     [-o, --options <option>]           Options for SCHNAPS. See its doc for more information.")
    print("     [-h, --help]                       Shows the help page\n\n")
    print("For help about the RSA key : http://doc.fedora-fr.org/wiki/SSH_:_Authentification_par_cl%C3%A9")

def main(argv):
    submitScriptName = "generated_submit.pbs"
    submitScriptPath = "~/"
    executionScriptName = "script_execution.py"
    executionScriptPath = "~/"
    cronJobScriptName = "cron_colosse_results.py"
    cronJobScriptPath = "/home/lsdadmin/scripts/"
    pushExecutionScript = False
    emailTo = ""
    duration = "24:00:00"
    rapId = "wny-790-aa"
    username = ""
    projectPath = ""
    projectName = ""
    configurationFile = "parameters.xml"
    scenario = ""
    advParameters = "" #Advanced parameters - Schnaps
    jobId = ""
    
    #Accepted arguments
    try:
        options, arguments = getopt.getopt(argv, "hxp:u:e:d:c:s:o:", ["help", "project=", "username=", "push-execution", "email=", "duration=", "configuration-file=", "scenario=", "options="])
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
            projectPath = arg
            projectName = ntpath.basename(arg)
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
        elif (opt in ("-c", "--configuration-file")):
            configurationFile = arg
        elif (opt in ("-s", "--scenario")):
            scenario = arg
        elif (opt in ("-o", "--options")):
            advParameters = " -o " + arg
    
    if not username or not scenario or not projectName or not projectName.lower().endswith(".lsd") or not emailTo:
        #Project, scenario, email and username are necessary
        #Project must be the LSD archive
        showHelp()
        sys.exit(2)
        
    #Submission script content
    submitScriptContent = ("#!/bin/bash\n"
                           "#PBS -A " + rapId + "\n" #Rap ID
                           "#PBS -l walltime=" + duration + "\n" #Max duration HH:MM:SS
                           "#PBS -l nodes=1:ppn=8\n" #Total nodes and hearts
                           #"#PBS -q test\n" #Which queue. Can be omitted.
                           "#PBS -N " + projectName[:-4] + "\n" #Job's name
                           "#PBS -o standard_output.out\n" #Standard output
                           "#PBS -e error_output.err\n" #Error output
                           "#PBS -m bea\n" #Email settings. Will send email at : b = beginning of job, e = end, a = abort
                           "#PBS -M " + emailTo + "\n" #Email address
                           
                           "python " + os.path.join(executionScriptPath, executionScriptName) + " -p " + projectName + " -c " + configurationFile + " -s " + scenario + advParameters + " -r " + rapId + "\n" #Executing the 2nd script
                           )
    
    print("Connection to Colosse by ssh.")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    k = paramiko.RSAKey.from_private_key_file(os.path.expanduser("~/.ssh/id_rsa"))
    ssh.connect(hostname="colosse.calculquebec.ca", username=username, pkey=k)
    scpClient = scp.SCPClient(ssh.get_transport())
    
    print("Generating the submit script.")
    ssh.exec_command("echo '" + submitScriptContent + "' > " + os.path.join(submitScriptPath, submitScriptName) + "\n")
    
    if pushExecutionScript:
        print("Sending the execution script.")
        # put( full path of current script + execution script name, full path on Koksoak)
        scpClient.put(os.path.join(os.path.dirname(os.path.realpath(__file__)), executionScriptName), os.path.join(executionScriptPath, executionScriptName))
    
    if os.path.isfile(projectPath):
        print("Sending the project file to : " + username + "@colosse.calculquebec.ca:/home/" + username + "/" + projectName)
        scpClient.put(projectPath, projectName)
    else:
        print("Error : The project path is not correct.")
        sys.exit(2)
   
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
    
    scpClient.close()
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