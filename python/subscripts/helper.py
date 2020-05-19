# -*- coding: utf-8 -*-
# encoding=utf8

import os, json, time, sys, datetime, subprocess, multiprocessing
from os import path
try:
	from select import select
except ImportError:
	import msvcrt
from yaspin import yaspin
from yaspin.spinners import Spinners
from beautifultable import BeautifulTable
import subscripts.menuHelper as menuHelper
from pathlib import Path


# Loading icon
# ---------------------------------------------

spinner = yaspin(Spinners.dots12, color="yellow")

def startLoading(text):
	spinner.text = col(text.upper(), [c.y, c.BOLD]) + " "
	spinner.start()

def changeLoadingText(text):
	spinner.text = col(text.upper(), [c.y, c.BOLD]) + " "

def stopLoading():
	spinner.stop()
	print()

def spinnerSuccess():
	if (isMac()): spinner.ok("✅ ")
	else: spinner.ok("✓ ")
	stopLoading()

def spinnerError():
	if (isMac()): spinner.fail("💥 ")
	else: spinner.fail("✖ ")
	stopLoading()



# General
# ---------------------------------------------

def isMac():
	return os.name == "posix"

class c:

	r = '\033[31m'
	g = '\033[32m'
	y = '\033[33m'
	b = '\033[34m'

	lr = '\033[91m'
	lg = '\033[92m'
	ly = '\033[93m'
	lb = '\033[94m'

	BOLD = '\033[1m'
	UL = '\033[4m'

	ENDC = '\033[0m'

def col(string, adjustment):
	for adj in adjustment:
		string = adj + string + c.ENDC
	return string


# Input
# ---------------------------------------------

def askForInput(texts):
	for row in texts:
		print (col(row[0], row[1]))
	return input(" > ")

def wrongInput():
	print(col("Wrong input!\n", [c.r]))

def askForInputUntilEmptyOrValidNumber(max):

	choice = -1
	while (choice is not None):

		choice = input(" > ")

		try:
			if (not choice.strip()):
				return -1
		except:
			continue

		if (not choice.isnumeric()): # if input is empty OR not numeric, then stop
			wrongInput()
		elif (int(choice) < 1 or int(choice) > max):
			wrongInput()
		else:
			return int(choice) - 1

def pressToContinue(term):
	
	print(col("\nPress any key to return to the previous menu", [c.y, c.UL]))
	with term.cbreak():
		while True:
			key = term.inkey()
			if key.is_sequence or key: return


# commands
# ---------------------------------------------

def tryCommand(term, commands, clearBeforeShowingError, stopSpinnerAfterSuccess, printOutputAfterSuccess):
	try:
		outputs = []
		for cmd in commands:
			output = runCommand(cmd).decode('UTF-8')
			outputs.append(output)
			log(cmd, output, 'INFO')
		if (stopSpinnerAfterSuccess): spinnerSuccess()
		if (printOutputAfterSuccess):
			menuHelper.clear(term, False, False, None, None, None)
			for x in outputs: print (x)
		return False, outputs # return error = False

	except subprocess.CalledProcessError as e:
		
		output = e.output.decode('UTF-8')		
		spinnerError()
		if (clearBeforeShowingError):
			menuHelper.clear(term, False, False, None, None, None)

		print(output)
		log(cmd, output, 'ERROR')

		return True, [output] # return error = True
		
	return False # return error = False

def runCommand(cmd):
	return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)



# files and folders
# ---------------------------------------------

def getConfig(params):
	data = getDataFromJson("config/ssdx-config.json")
	paramsList = params.split('.')

	current = data
	for param in paramsList:
		if (param in current):
			current = current[param]		
		else:
			return None

	if (current == ''):
		return None

	if (paramsList[0] == 'locations'):
		return './' + current
	return current

def folderExists(folder):
	return path.exists(folder)

def fetchFilesFromFolder(folder, keepPath):
	directory = os.fsencode(folder)
	files = []
	for file in os.listdir(directory):
		filename = os.fsdecode(file)
		if (keepPath):
			files.append(folder + filename)
		else:
			files.append(filename)
	
	return files

def getContentOfFile(file):
	try:
		f = open(file, "r")
		tmp = f.read()
		f.close()
		return tmp
	except IOError:
		return None

def debug(output):
	log('', output, 'DEBUG')

def log(function, output, status):

	now = datetime.datetime.now()

	filename = now.strftime("%Y_%m_%d_")

	Path(".ssdx/logs").mkdir(parents=True, exist_ok=True)

	f = open(".ssdx/logs/{}.log".format(filename + status), "a")
	allFiles = open(".ssdx/logs/{}.log".format(filename + 'ALL'), "a")

	dateFormatted = now.strftime("%H:%M:%S %a %d.%m.%Y") 
	title = "[{}][{}]['{}']".format(dateFormatted, status, function)
	
	f.write("\n\n{}\n--------------------------------------------------------------\n{}".format(title, output))
	f.close()
	
	allFiles.write("\n\n{}\n--------------------------------------------------------------\n{}".format(title, output))
	allFiles.close()
	



# Salesforce DX
# ---------------------------------------------

def getDefaultScratchOrg():
	data = getDataFromJson(".sfdx/sfdx-config.json")	
	
	if ("defaultusername" in data):
		if (data["defaultusername"] is None):
			return "[none]"
		else:
			return data["defaultusername"]
	else:
		return "[none]"

def getDefaultDevhub():
	data = getDataFromJson(".sfdx/sfdx-config.json")	

	if ("defaultdevhubusername" in data):
		if (data["defaultdevhubusername"] is None):
			return "[none]"
		else:
			return data["defaultdevhubusername"]
	else:
		return "[none]"

def getMenuInformation(): 
	info = []
	info.append("SCRATCH ORG: {}".format(getDefaultScratchOrg()))
	info.append("DEV HUB: {}".format(getDefaultDevhub()))
	# info.append("BRANCH: {}".format(getDefaultScratchOrg()))

	return info



# JSON
# ---------------------------------------------

def getDataFromJson(path):
	try:
		with open(path, "r") as jsonFile:
			return json.load(jsonFile)
	except IOError:
		f = open(path, "w+")
		f.write('{}')
		f.close()
		return getDataFromJson(path)

def convertDateToDaysRemaining(date_string):
	start = datetime.datetime.now()
	end = datetime.datetime.strptime(date_string, "%Y-%m-%d")
	delta = end-start
	return delta.days + 1

def convertDateToDay(date_string):
	d = datetime.datetime.strptime(date_string, "%Y-%m-%d")
	return d.strftime("%A")
	
def convertDateFormat(date_string):
	d = datetime.datetime.strptime(date_string, "%Y-%m-%d")
	return d.strftime("%d. %b")

def loadJsonAndContainsErrors(jsonString):
	jsonOutput = json.loads(jsonString)
	if ("status" in jsonOutput):
		if (jsonOutput["status"] == "0"): return False
		if (jsonOutput["status"] == "1"): return True

def loadJson(jsonString):
	return json.loads(jsonString)

def ifKeyExists(key, value):
	if (key in value):
		return value[key]
	else:
		return ""



# Table
# ---------------------------------------------
def createTable(header, rows):
	table = BeautifulTable()
	table.set_style(BeautifulTable.STYLE_BOX)
	if (len(header) > 0):
		table.column_headers = header
	for row in rows:
		table.append_row(row)
	table.column_alignments = BeautifulTable.ALIGN_LEFT
	print (table)