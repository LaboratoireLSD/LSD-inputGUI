# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 09:02:21 2016

@author: mathieu boily
"""

import getopt
import sys
import subprocess
import os
import zipfile
import contextlib
import datetime
import shutil

"""
Takes a number, in bytes, as argument.
Converts this number in kb, mb, gb or tb ans returns it with the corresponding unit as string.
"""
def formatSize(size):
    units = ["Bytes", "Kb", "Mb", "Gb", "Tb"]
    count = 0
    
    while size > 1024:
        size /= 1024
        count += 1
        
    return str(round(size, 1)) + " " + units[count]
    
"""
Iterates through all folders and writes their size, creation date and version.
Creates a file in each folder describing these metadata.
"""
def folderSize(folderName, fileName):
    #Current date for the creation date.
    today = datetime.datetime.now().strftime("%d-%m-%Y")
    """
    Recursive function. Goes to the deepest folder and comes back.
    """
    def aux(path):
        folderSize = 0
        for subdir in os.listdir(path):
            #For each files in the current one.
            current = os.path.join(path, subdir)
            if os.path.isdir(current):
                #If the file is a directory, calls himself to go deeper.
                subfoldersSize = aux(current)
                folderSize += subfoldersSize
            else:
                #If it's a normal file, get its size.
                tmp = os.stat(current).st_size
                folderSize += tmp
                
        metadata = {}
        if os.path.isfile(os.path.join(path, fileName)):
            #if the metadata file already exists
            with open(os.path.join(path, fileName)) as file:
                #Open it and retreive each metadata.
                for line in file:
                    tmp = line.split(":")
                    metadata[tmp[0]] = tmp[1]
            metadata["size"] = formatSize(folderSize)
            metadata["version"] = int(metadata["version"]) + 1
            metadata["creation date"] = today
        else:
            #If it doesn't exist, we create it.
            metadata["size"] = formatSize(folderSize)
            metadata["creation date"] = today
            metadata["version"] = 1
            
        with open(os.path.join(path, fileName), "w") as file:
            #Writes the new metadata for this folder
            for key, value in metadata.items():
                file.write(key + ":" + str(value).strip() + "\n")
        
        return folderSize
    
    aux(folderName)

def main(argv):
    projectName = ""
    configurationFile = ""
    scenario = ""
    advParameters = ""
    rapId = ""
    
    try:
        #Accepted arguments
        options, arguments = getopt.getopt(argv, "p:c:s:o:r:", ["project=", "configuration-file=", "scenario=", "options=", "rap-id="])
    except getopt.GetoptError as error:
        print(error)
        sys.exit(2)
    
    #Parsing all the options
    for opt, arg in options:
        if (opt in ('-p', '--project')):
            projectName = arg
        elif (opt in ("-c", "--configuration-file")):
            configurationFile = arg
        elif (opt in ("-s", "--scenario")):
            scenario = arg
        elif (opt in ("-o", "--options")):
            advParameters = " -p " + arg
        elif (opt in ("-r", "--rap-id")):
            rapId = arg
            
    #SCHNAPS requires at least these 3 arguments. Plus, we need the rapId for the scratch folder.
    if not projectName or not configurationFile or not scenario or not rapId:
        print("Missing arguments for SCHNAPS")
        sys.exit(2)
        
    #Empty the standard and error output files
    if os.path.isfile("standard_output.out"):
        open("standard_output.out", "w").close()
    if os.path.isfile("error_output.err"):
        open("error_output.err", "w").close()
        
    #Extracting the project in $SCRATCH
    with contextlib.closing(zipfile.ZipFile(projectName, "r")) as projectZip:
        #Not using directly "$SCRATCH", because the environment variable is not recognized here.
        projectZip.extractall("/scratch/" + rapId)
    
    output = subprocess.Popen(["schnaps", "-c", configurationFile, "-d", os.path.join("/scratch", rapId, projectName[:-4]), "-s", scenario, "-p", advParameters], stdout=subprocess.PIPE)
    
    #Printing the output of SCHNAPS, if any.
    print(output.communicate()[0])
    
    #Creates the metadata file in each directory of the project.
    #Do not modify the metadata's filename, unless you modify it also in the configuration file of Koksoak's website (/var/www/html/conf.php)
    folderSize(os.path.join("/scratch", rapId, projectName[:-4]), ".meta")
    
    #Zip the results as an archive, because paramiko doesn't support folder tranfert over sftp.
    zipf = zipfile.ZipFile(os.path.join("/scratch", rapId, projectName), "w", zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(os.path.join("/scratch", rapId, projectName[:-4])):
        for file in files:
            absname = os.path.abspath(os.path.join(root, file))
            arcname = absname[len(os.path.join("/scratch", rapId, projectName[:-4])) + 1:]
            zipf.write(os.path.join(root, file), arcname)
            
    # Removes the project folder from $SCRATCH
    if (os.path.exists(os.path.join("/scratch", rapId, projectName[:-4]))):
        shutil.rmtree(os.path.join("/scratch", rapId, projectName[:-4]))


main(sys.argv[1:])