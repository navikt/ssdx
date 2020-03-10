# -*- coding: utf-8 -*-
# encoding=utf8

import os, json, time, sys, datetime, subprocess
try:
	from select import select
except ImportError:
	import msvcrt
from yaspin import yaspin
from yaspin.spinners import Spinners
from beautifultable import BeautifulTable
import subscripts.menuHelper as menuHelper


# Loading icon
# ---------------------------------------------

spinner = yaspin(Spinners.dots12, color="yellow")

def startLoading(text):
	spinner.text = col(text.upper(), [c.y, c.BOLD]) + " "
	spinner.start()

def stopLoading():
	spinner.stop()
	print()

def spinnerSuccess():
	if (os.name == "posix"):
		spinner.ok("✅ ")
	else:
		spinner.ok("✓ ")
	stopLoading()

def spinnerError():
	if (os.name == "posix"):
		spinner.fail("💥 ")
	else:
		spinner.fail("✖ ")
	stopLoading()


# General
# ---------------------------------------------

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

def askForInput(texts):
	print()
	for row in texts:
		print (col(row[0], row[1]))
	return input(" > ")

def printHeader(text, color):
	print()
	print(col(text, color))
	print("----------------------------------------------")


# Input
# ---------------------------------------------

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

		if(not choice.isnumeric()): # if input is empty OR not numeric, then stop
			wrongInput()
		elif (int(choice) < 1 or int(choice) > max):
			wrongInput()
		else:
			return int(choice) - 1





# commands
# ---------------------------------------------

def pressToContinue():
	print(col("\nPress enter to return to the previous menu", [c.y, c.UL]))
	input()

def tryCommand(term, commands, clearBeforeShowingError):
	try:
		outputs = []
		for cmd in commands:
			output = runCommand(cmd).decode('UTF-8')
			outputs.append(output)
			log(cmd, output, 'INFO')
		spinnerSuccess()
		return False, outputs # return error = False

	except subprocess.CalledProcessError as e:
		if (clearBeforeShowingError): menuHelper.clear(term, False, False, None, None, None)
		spinnerError()
		output = e.output.decode('UTF-8')
		# print(output)
		print("test")
		log(cmd, output, 'ERROR')
		return True, [output] # return error = True
		
	return False # return error = False

def runCommand(cmd):
	return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)



# files and folders
# ---------------------------------------------

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

def copyFile(file, path):
	try:
		copyfile(file, str(Path.home()) + path)
	except Exception as e:
		print(e)
		pressToContinue()


def debug(function, output):
	log(function, output, 'DEBUG')

def log(function, output, status):

	now = datetime.datetime.now()

	filename = now.strftime("%Y_%m_%d_")
	
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
	if (key
	 in value):
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