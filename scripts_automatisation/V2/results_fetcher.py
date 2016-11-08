# -*- coding: utf-8 -*-
"""
Created on Mon Aug  8 08:36:17 2016

@author: mathieu boily
"""

import paramiko
import os
import sys
import zipfile
import getopt
import contextlib
import smtplib
from email.mime.text import MIMEText
from crontab import CronTab

def showHelp():
    print("\n\n")
    print("Possible arguments :\n")
    print("     -u, --username <name>              Username on Colosse for the ssh connection")
    print("     -p, --project <name>               Project's name")
    print("     -i, --id <job's id>                Job's id given by Colosse")
    print("     -e, --email <address@ulaval.ca>    Person to join when the simulation is done")
    print("     [-c]                               Create a new cron job\n")
    print("For help about the RSA key : http://doc.fedora-fr.org/wiki/SSH_:_Authentification_par_cl%C3%A9")

def main(argv):
    rapId = "wny-790-aa"
    username = ""
    jobId = ""
    projectName = ""
    create = False
    email = ""
 
    try:
        options, arguments = getopt.getopt(argv, "hcu:i:p:e:", ["help", "create", "username=", "id=", "project=", "email="])
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
        elif (opt in ("-u", "--username")):
            username = arg
        elif (opt in ("-i", "--id")):
            jobId = arg
        elif (opt in ("-p", "--project")):
            projectName = arg
        elif (opt in ("-c", "--create")):
            create = True
        elif (opt in ("-e", "--email")):
            email = arg
    
    if not username or not jobId or not projectName:
        #Username, project's name and job's id are required
        showHelp()
        sys.exit(2)
        
    if create:
        #Creates a cron job
        try:
            cron = CronTab(user="lsdadmin")
            cronJob = cron.new("/usr/bin/python /home/lsdadmin/scripts/results_fetcher.py -u " + username + " -i " + jobId + " -p " + projectName + " -e " + email, comment=jobId)
            cronJob.minute.every(15)
            #print(cron.render())
            cron.write()
            print("Cron job with job id " + jobId + " created successfully")
            sys.exit(0)
        except Exception as e:
            print("An error has occured while creating the cron job : " + str(e))
            sys.exit(0)
    
    
    #Setting up the ssh
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    k = paramiko.RSAKey.from_private_key_file(os.path.expanduser("/home/lsdadmin/.ssh/id_rsa"))
    ssh.connect(hostname="colosse.calculquebec.ca", username=username, pkey=k)
    
    #Looking for active jobs
    stin, stout, sterr = ssh.exec_command("showq -u $USER\n")
    
    #Getting the output from the last command
    output = stout.readlines()
    
    category = "" #Used to know if we are reading active, eligible or blocked jobs
    active = False
    eligible = False
    blocked = False
    for line in output:
        if "active jobs-----" in line:
            category = "active"
            continue
        elif "eligible jobs-----" in line:
            category = "eligible"
            continue
        elif "blocked jobs-----" in line:
            category = "blocked"
            continue
        
        if category == "active":
            if line.startswith(jobId):
                active = True
        elif category == "eligible":
            if line.startswith(jobId):
                eligible = True
        elif category == "blocked":
            if line.startswith(jobId):
                blocked = True
          
    if not active and not eligible and not blocked:
        #Simulation is done
        
        try:
            #Getting the project
            os.system("scp " + username + "@colosse.calculquebec.ca:" +  os.path.join("/scratch", rapId, projectName) + " /media/safe/Results/")
            
            # removing the project from Colosse in $SCRATCH and home (Avoid conflict when simulating multiple times the same project)
            ssh.exec_command("rm -r '" + os.path.join("/scratch", rapId, projectName) + "\n")
            ssh.exec_command("rm -r '" + os.path.join("/home", username, projectName) + "\n")
            
            #Rename project if alreay exists
            extension = ""
            counter = 1
            if (os.path.isdir("/media/safe/Results/" + projectName[:-4])):
                extension = "_" + str(counter)
                while (os.path.isdir("/media/safe/Results/" + projectName[:-4] + extension)):
                    counter += 1
                    extension = "_" + str(counter)
            
            #Extracting the project
            with contextlib.closing(zipfile.ZipFile("/media/safe/Results/" + projectName, "r")) as projectZip:
                projectZip.extractall("/media/safe/Results/" + projectName[:-4] + extension)
                
            #Removing the archive
            os.remove("/media/safe/Results/" + projectName)
        except:
            pass
        
        #Now that the simulation is done, we remove the cron job.
        cron = CronTab(user="lsdadmin")
        cron.remove_all(comment=jobId)
        cron.write()
        print("Cron job with job id " + jobId + " removed successfully")
        
        #Sending an email to the user
        try:
            server = "smtp.ulaval.ca"

            msg = MIMEText("Simulation called '" + projectName + "' is done and now on Koksoak")
            msg["Subject"] = "Simulation '" + projectName + "' is done"
            msg["From"] = "no-reply@ulaval.ca"
            msg["To"] = email
            
            smtp = smtplib.SMTP(server)
            smtp.sendmail("no-reply@ulaval.ca", [email], msg.as_string())
            smtp.quit()
        except:
            pass
    
    ssh.close() 
    
main(sys.argv[1:])