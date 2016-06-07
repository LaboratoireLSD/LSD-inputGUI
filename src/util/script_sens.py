"""
.. module:: script_sens

.. codeauthor:: ?

:Created on: ?

"""
#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore
from util.opener import Opener

import scipy.stats
import shutil, os

dossier_in = ""
nb_de_fois = 0

def findCurrentValue(name="population"):
	if name == "population":
		f = Opener(dossier_in)
		rootNode = f.getRootNode()
		return int(rootNode.toElement().firstChildElement("Input").firstChildElement("PopulationManager").firstChildElement("Population").firstChild().toElement().attribute("size"))
	else:
		f = Opener(dossier_in[:-1]+".xml")
		rootNode = f.getRootNode()
		elt = rootNode.toElement().firstChildElement("System").firstChildElement("Parameters").firstChildElement("Entry")
		while elt.attribute("label") !=  name:
			elt = elt.nextSiblingElement("Entry")
		nombre = elt.firstChild().toElement()
		return float(nombre.toElement().attribute("value"))

def findCurrentValuesVector(name, vectorLength):
	values=[]
	f = Opener(dossier_in[:-1]+".xml")
	rootNode = f.getRootNode()
	elt = rootNode.toElement().firstChildElement("System").firstChildElement("Parameters").firstChildElement("Entry")
	while elt.attribute("label") != name:
		elt = elt.nextSiblingElement("Entry")
	nombre = elt.firstChildElement().toElement().childNodes()
	for v in range(vectorLength):
		values.append(str(nombre.item(v).toElement().attribute("value")))
	return [float(i) for i in values]

# parameter=name uniform lowerLim upperLim
# parameter=name randint lowerLim upperLim
# parameter=name norm lowerLim upperLim sd mu(default=current value)
# parameter=name discreteuniform lowerLim upperLim mu(default=current value)
# parameter=name lognormabs sd moyenne(default=current value)
# parameter=name discretelognormabs sd moyenne(default=current value)
# parameter=name beta lowerLim upperLim alpha beta
# parameter=name triang lowerLim upperLim c(ramené sur une distribution [0,1])
# parameter=name gamma lowerLim upperLim k theta
# parameter=name poisson lowerLim upperLim mu
def parameter(params):
	currentValue = findCurrentValue(params[0])

	n = 2		
	for i in params[2:]:
		params[n] = float(i)
		n += 1

	for i in range(nb_de_fois):
		if params[1] == "norm" or params[1] == "discretenorm":
			newValue = float("inf")
			while newValue >= params[3] or newValue <= params[2]:
				try:
					newValue = scipy.stats.norm.rvs(loc=params[5], scale=params[4])
				except IndexError:
					newValue = scipy.stats.norm.rvs(loc=currentValue, scale=params[4])
			if params[1] == "discretenorm":
				newValue = int(round(newValue))
		elif params[1] == "lognormabs" or params[1] == "discretelognormabs":
			try:	
				mu = numpy.log(params[3]**2/(params[2]**2+params[3]**2)**0.5)
				sd = (numpy.log(params[2]**2/(params[3]**2)+1))**0.5
				newValue = scipy.stats.lognorm.rvs(sd, loc=mu)
			except:
				mu = numpy.log(currentValue**2/(params[2]**2+currentValue**2)**0.5)
				sd = (numpy.log(params[2]**2/(currentValue**2)+1))**0.5
				newValue = scipy.stats.lognorm.rvs(sd, loc=mu)
			newValue = abs(newValue)
			if params[1] == "discretelognorm":
				newValue = int(round(newValue))
			elif params[1] == "uniform":
				newValue = scipy.stats.uniform.rvs(loc=params[2],scale=params[3]-params[2])
		elif params[1] == "randint":
			newValue = scipy.stats.randint.rvs(params[2],params[3]+1)
		elif params[1] == "beta":
			newValue = scipy.stats.beta.rvs(params[4], params[5], loc=params[2], scale=params[3]-params[2])
		elif params[1] == "triang":
			newValue = scipy.stats.triang.rvs(params[4], loc=params[2], scale=params[3]-params[2])
		elif params[1] == "gamma":
			newValue = float('inf')
			while newValue <= params[2] or newValue >= params[3]:
				newValue = scipy.stats.gamma.rvs(params[4], loc=params[2], scale=params[5])
		elif params[1] == "poisson":
			newValue = float('inf')
			while newValue <= params[2] or newValue >= params[3]:
				newValue = scipy.stats.poisson.rvs(params[4])
		else:
			raise AssertionError("Unknown law! (probably a typo)")
		
		pth = dossier_in + str(i) + ".xml"
		f = Opener(pth)
		rootNode = f.getRootNode()
		elt = rootNode.toElement().firstChildElement("System").firstChildElement("Parameters").firstChildElement("Entry")
		while elt.attribute("label") != params[0]:
			elt = elt.nextSiblingElement("Entry")
		nombre = elt.firstChild().toElement()
		nombre.toElement().setAttribute("value", str(newValue))
		fileP = QtCore.QFile(pth)
		fileP.open(QtCore.QIODevice.ReadWrite|QtCore.QIODevice.Truncate)
		tmpTextStream = QtCore.QTextStream()
		tmpTextStream.setDevice(fileP)
		rootNode.save(tmpTextStream, 5)
		fileP.close()


def parameter_uni(params):
	if params[-1] != "univariate":
		return
	dir_up = dossier_in[:-11] + "univariate_" + params[0][4:] + "_UP/"
	dir_lo = dossier_in[:-11] + "univariate_" + params[0][4:] + "_LO/"
	os.mkdir(dir_up)
	os.mkdir(dir_lo)
	params[2] = float(params[2])
	params[3] = float(params[3])
	for i in range(nb_de_fois):
		pth = dossier_in + str(i) + ".xml"
		shutil.copy(pth, dir_lo)
		shutil.copy(pth, dir_up)
		
		f = Opener(dir_lo + "parameters_" + str(i) + ".xml")
		rootNode = f.getRootNode()
		elt = rootNode.toElement().firstChildElement("System").firstChildElement("Parameters").firstChildElement("Entry")
		while elt.attribute("label") != params[0]:
			elt = elt.nextSiblingElement("Entry")
		nombre = elt.firstChild().toElement()
		nombre.toElement().setAttribute("value", str(params[2]))
		fileP = QtCore.QFile(dir_lo + "parameters_" + str(i) + ".xml")
		fileP.open(QtCore.QIODevice.ReadWrite|QtCore.QIODevice.Truncate)
		tmpTextStream = QtCore.QTextStream()
		tmpTextStream.setDevice(fileP)
		rootNode.save(tmpTextStream, 5)
		fileP.close()

		f = Opener(dir_up + "parameters_" + str(i) + ".xml")
		rootNode = f.getRootNode()
		elt = rootNode.toElement().firstChildElement("System").firstChildElement("Parameters").firstChildElement("Entry")
		while elt.attribute("label") != params[0]:
			elt = elt.nextSiblingElement("Entry")
		nombre = elt.firstChild().toElement()
		nombre.toElement().setAttribute("value", str(params[3]))
		fileP = QtCore.QFile(dir_up + "parameters_" + str(i) + ".xml")
		fileP.open(QtCore.QIODevice.ReadWrite|QtCore.QIODevice.Truncate)
		tmpTextStream = QtCore.QTextStream()
		tmpTextStream.setDevice(fileP)
		rootNode.save(tmpTextStream, 5)
		fileP.close()

	for v in (dir_lo, dir_up):
		os.chdir(v)
		os.symlink('../Environment', './Environment')
		os.symlink('../Libraries', './Libraries')
		os.symlink('../Populations', './Populations')
		os.symlink('../Processes', './Processes')
		os.symlink('../XSD', './XSD')


def vector(params):
	vectorLength = len(params[1])
	currentValues = findCurrentValuesVector(params[0], vectorLength)
	n = 2
	for i in params[2:]:
		for v in range(vectorLength):
			try:
				if params[n][v]:
					params[n][v] = float(i[v])
			except IndexError:
				pass
		n += 1
	
	for i in range(nb_de_fois):
		newValues=[]
		for v in range(vectorLength):
			if params[1][v] == "uniform":
				newValues.append(scipy.stats.uniform.rvs(loc=params[2][v],scale=params[3][v]-params[2][v]))
			elif params[1][v] == "randint":
				newValues.append(scipy.stats.randint.rvs(loc=params[2][v],scale=params[3][v]-params[2][v]+1))
			elif params[1][v] == "unchanged" or params[1][v] == "follower":
				newValues.append(currentValues[v])
			elif params[1][v] == "norm" or params[1][v] == "discretenorm":
				newValue = float('inf')
				while newValue >= params[3][v] or newValue <= params[2][v]:
					try:
						newValue = scipy.stats.norm.rvs(loc=params[5][v], scale=params[4][v])
					except IndexError:
						newValue = scipy.stats.norm.rvs(loc=currentValues[v], scale=params[4][v])
				if params[1][v] == "discretenorm":
					newValue = int(round(newValue))
				newValues.append(newValue)
			elif params[1][v] == "beta":
				newValues.append(scipy.stats.beta.rvs(params[4][v], params[5][v], loc=params[2][v], scale=params[3][v]-params[2][v]))
			elif params[1][v] == "triang":
				newValues.append(scipy.stats.triang.rvs(params[4][v], loc=params[2][v], scale=params[3][v]-params[2][v]))
			elif params[1][v] == "gamma":
				newValue = float('inf')
				while newValue <= params[2][v] or newValue >= params[3][v]:
					newValue = scipy.stats.gamma.rvs(params[4][v], loc=params[2][v], scale=params[5][v])
				newValues.append(newValue)
			elif params[1][v] == "poisson":
				newValue = float('inf')
				while newValue <= params[2][v] or newValue >= params[3][v]:
					newValue = scipy.stats.poisson.rvs(params[4][v])
				newValues.append(newValue)
			else:
				raise AssertionError("Unknown law! (probably a typo somewhere)")
		
		if "follower" in params[1]:
			checkIntegrity(params[1],currentValues,newValues)
		
		pth = dossier_in + str(i) + ".xml" 
		f = Opener(pth)
		
		rootNode = f.getRootNode()

		elt = rootNode.toElement().firstChildElement("System").firstChildElement("Parameters").firstChildElement("Entry")
		while elt.attribute("label") != params[0]:
			elt = elt.nextSiblingElement("Entry")
		nombre = elt.firstChildElement().toElement().childNodes()
		for v in range(vectorLength):
			nombre.item(v).toElement().setAttribute("value", str(newValues[v]))
		fileP = QtCore.QFile(pth)
		fileP.open(QtCore.QIODevice.ReadWrite|QtCore.QIODevice.Truncate)
		tmpTextStream = QtCore.QTextStream()
		tmpTextStream.setDevice(fileP)
		rootNode.save(tmpTextStream, 5)
		fileP.close()


def checkIntegrity(types, currentValues, newValues):
	if types.count("follower") > 1:
		raise AssertionError("More than 1 instance of follower.")
	toChange = types.index("follower")
	toStay = 0
	for _ in range(len(types)-types.count("unchanged")):
		while types[toStay] == "unchanged":
			toStay += 1
			howMuch = currentValues[toStay] - newValues[toStay]
			newValues[toChange] += howMuch
			toStay += 1
		

# start here
def main(path, fileNumber, progB, count, univariate=False):
	global dossier_in, nb_de_fois
	dossier_in = str(path)
	nb_de_fois = fileNumber

	f = Opener(path[:-11]+'sensanalysis.xml')
	rootNode = f.getRootNode()
	elt = rootNode.toElement().firstChildElement("Law").toElement()
	elt2 = elt.firstChildElement().toElement()
	while elt2.toElement().attribute("name"):
		params = []
		params.append(elt2.attribute("name"))
		vectorCheck = elt2.firstChildElement().toElement().firstChildElement().toElement()
		EstVector = False
		if vectorCheck.attribute("value"):
			vectorCheck=elt2.firstChildElement().toElement().childNodes()
			EstVector = True
			vectorCount=vectorCheck.length()
			arr = []
			for i in range(vectorCount):
				arr.append(vectorCheck.item(i).toElement().attribute("value"))
			params.append(arr)

		if not EstVector:
			params.append(elt2.firstChildElement().toElement().attribute("value"))
		intermediary = elt.nextSiblingElement()
		limCount = 0
		while True:
			tmp = intermediary.firstChildElement().toElement()
			if not tmp.attribute("name") and limCount != 0 and limCount != 1:
				break
			limParam = False
			defaultValue = False
			while tmp.attribute("name") != params[0]:
				tmp=tmp.nextSiblingElement()
				if not tmp.attribute("name"):
					if (limCount == 0 or limCount == 1) and (params[1] != "unchanged" or params[1] != "follower"):
						if EstVector:
							for n in params[1]:
								if n != "unchanged" or n != "follower":
									defaultValue = True
									break
							limParam = True if not defaultValue else False
							break
						else:
							defaultValue = True
							break
					else:
						limParam = True
						break
			if limParam:
				break
			if not EstVector:
				if not defaultValue:
					params.append(tmp.firstChildElement().attribute("value"))
				elif limCount == 0:
					params.append("-inf")
				else:
					params.append("inf")
			else:
				arr = []
				if defaultValue:
					if limCount == 0:
						for i in range(vectorCount):
							arr.append("-inf")
					else:
						for i in range(vectorCount):
							arr.append("inf")
				else:
					tmp = tmp.firstChildElement().toElement().childNodes()
					for i in range(vectorCount):
						if not tmp.item(i).toElement().attribute("value"):
							if limCount == 0:
								arr.append("-inf")
							elif limCount == 1:   
								arr.append("inf")
							else:
								arr.append("0")
						else:
							arr.append(str(tmp.item(i).toElement().attribute("value")))
				params.append(arr)
			intermediary = intermediary.nextSiblingElement()
		limCount += 1
		
		if EstVector:
			for i in range(1, 4):
				for v in range(vectorCount):
					try:
						params[i][v] = params[i][v].lower()
					except IndexError:
						pass
			if not univariate:
				vector(params)
			else:
				continue
		else:
			for i in range(1, 4):
				params[i] = params[i].lower()
			if not univariate:
				if params[-1] == "univariate":
					params.pop()
				parameter(params)
			else:
				parameter_uni(params)
		count += 1
		progB.setValue(count)

		elt2 = elt2.nextSiblingElement()
