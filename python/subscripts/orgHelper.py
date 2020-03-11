# -*- coding: utf-8 -*-
# encoding=utf8

import subprocess
import subscripts.helper as helper
import subscripts.menuHelper as menuHelper

title = "SSDX Helper"

# ---------------------------------------------------------
# SUB-FUNCTIONS OF CREATING A SCRATCH ORG
# ---------------------------------------------------------

# DELETE PREVIOUS SCRATCH ORG
# ------------------------------

def createScratchOrg_deletePreviousScratchOrg(term):
	deletePrevious = False
	if (helper.getDefaultScratchOrg() != '[none]'):
		deletePrevious = menuHelper.askUserYesOrNo(term, True, True, 'Creating scratch org', ['Do you want to delete the old scratch org?'], False, False, False, True)

	menuHelper.clear(term, True, True, title, 'Creating scratch org', None)
	menuHelper.fixHeight(4)

	if (deletePrevious == 2): return deletePrevious
	if (deletePrevious):
		helper.startLoading("Deleting default Scratch Org")
		error = helper.tryCommand(term, ["sfdx force:org:delete -p"], False)[0]


# CREATE SCRATCH ORG
# ------------------------------

def createScratchOrg_createOrg(term, scratchOrgName):
	helper.startLoading("Creating new Scratch Org")
	results = helper.tryCommand(term, 
		["sfdx force:org:create " + 
		"-f ./config/project-scratch-def.json " + 
		"--setalias {} ".format(scratchOrgName) + 
		"--durationdays 5 " + 
		"--setdefaultusername"],
		True)
	return results


# INSTALL PACKAGES
# ------------------------------

from pathlib import Path

def installPackages():
	# TODO check if packages defined
	helper.startLoading("Installing packages defined in 'sfdx-project.json'")
	data = None
	try:
		data = helper.getDataFromJson("sfdx-project.json")
		if ("packageDirectories" not in data):
			helper.spinnerSuccess()
			return False, []
		data = data["packageDirectories"][0]
		if ("dependencies" not in data):
			helper.spinnerSuccess()
			return False, []
		data = data["dependencies"]
	except Exception as e:
		return True, [e]

	if (len(data) == 0):
		helper.spinnerSuccess()
		return False, []

	try:
		copyfile("./.ssdx/config/unsignedPluginWhiteList.json", str(Path.home()) + "/.config/sfdx/unsignedPluginWhiteList.json")
		helper.runCommand("sfdx plugins:install rstk-sfdx-package-utils@0.1.12")
	except Exception as e:
		return True, [e]

	packageKey = None
	try:
		f = open("./.ssdx/.packageKey", "r")
		if (f.mode == "r"):
			packageKey = f.read()
			f.close()
	except IOError:
		return True, [".packageKey file does not exists. Without it, packages cannot be installed. See Main Menu > Other"]
	
	keys = ''
	for iterator in range(len(data)):
		keys = "{} {}:{}".format(keys, iterator + 1, packageKey) # should be in the format of '1:key 2:key 3:key etc, one for each dependency

	try:
		helper.runCommand('sfdx rstk:package:dependencies:install -w 10 --noprecheck --installationkeys "{}"'.format(keys))
		helper.spinnerSuccess()
	except subprocess.CalledProcessError as e:
		output = e.output.decode('UTF-8')
		log(cmd, output, 'ERROR')
		return True, [output]
	except Exception as e:
		log(cmd, output, 'ERROR') # TODO add log everywhere
		return True, [e]
	return False, []


# PUSH METADATA
# ------------------------------

def createScratchOrg_pushMetadata(term):
	helper.startLoading("Pushing metadata")
	return helper.tryCommand(term, ["sfdx force:source:push"], True)


# PUSH METADATA
# ------------------------------
import os.path
from os import path
def createScratchOrg_pushNonDeployedMetadata(term):
	if (path.exists('./non_deployable_metadata')):
		helper.startLoading("Pushing non-deployed metadata")
		return helper.tryCommand(term,  ["sfdx force:source:deploy -p ./non_deployable_metadata"], True)
		

# FETCH PERM SETS
# ------------------------------

def assignPermsets(term):
	helper.startLoading("Assigning all permission sets")
	fetchPermsets()
	commands = [] 
	for permset in fetchPermsets():
		commands.append("sfdx force:user:permset:assign -n " + permset)
	return helper.tryCommand(term, commands, True)


import os
def fetchPermsets():
	try:
		permsets = helper.fetchFilesFromFolder("./force-app/main/default/permissionsets/", False)
		for i, permset in enumerate(permsets):
			permsets[i] = permset.replace(".permissionset-meta.xml", "")
		return permsets
	except Exception as e:
		helper.spinnerError()
		print(e)



# IMPORT DUMMY DATA
# ------------------------------

from shutil import copyfile
import shutil

def importDummyData():
	
	helper.startLoading("Importing dummy data")
	
	try:
		path = "./dummy-data/"
		copyfile("./.ssdx/config/unsignedPluginWhiteList.json", str(Path.home()) + "/.config/sfdx/unsignedPluginWhiteList.json")
		output = helper.runCommand("sfdx plugins:install sfdx-wry-plugin@0.0.9")
	
		for folder in next(os.walk(path))[1]:
			if (folder.endswith(".out")):
				shutil.rmtree(path + folder)

		for folder in next(os.walk(path))[1]:
			output = helper.runCommand('sfdx wry:file:replace -i {} -o {}'.format(path + folder, path + folder + ".out"))

		for folder in next(os.walk(path))[1]:
			if (folder.endswith(".out")):
				output = helper.runCommand('sfdx force:data:tree:import --plan {}{}/plan.json'.format(path, folder))

		helper.spinnerSuccess()
	except subprocess.CalledProcessError as e:
		log(cmd, e.output.decode('UTF-8'), 'ERROR')
		return True, [e.output.decode('UTF-8')]
	except Exception as e:
		log(cmd, e, 'ERROR')
		return True, [e]
	return False, []




# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

# RETRY QUESTION ON ERROR
# ----------------------------

def retry(term, results):
	helper.debug(results)
	if (results[0]):
		helper.spinnerError()
		text = results[1]
		for x in range(4): text.append('')
		text.append('Would you like to retry?')
		retry = menuHelper.askUserYesOrNo(term, False, False, 'Create scratch org', text, False, False, True, False)
		if (retry):
			menuHelper.clear(term, True, True, title, 'Create scratch org', None)
			menuHelper.fixHeight(4)
		return retry
	return False


# ASK USER FOR ORG
# ----------------------------

def askUserForOrgs(lookingForRegularOrgs, mainMenu, text):
	root = "scratchOrgs"
	kind = "Scratch Orgs"
	
	if (lookingForRegularOrgs):
		root = "nonScratchOrgs"
		kind = "orgs"

	helper.startLoading("Loading {}".format(kind))
	orgs = subprocess.check_output(["sfdx", "force:org:list", "--json"])
	jsonOutput = helper.loadJson(orgs)
	helper.stopLoading()

	header = ['', 'Alias', 'Username', 'Org Id', 'Expiration Date', 'Default']
	rows = []

	number = 1

	for row in jsonOutput['result'][root]:
		
		alias = helper.ifKeyExists('alias', row)
		username = helper.ifKeyExists('username', row)
		orgId = helper.ifKeyExists('orgId', row)
		expirationDate = helper.ifKeyExists('expirationDate', row)
		defaultMarker = helper.ifKeyExists('defaultMarker', row).replace('(U)', 'X').replace('(D)', 'X')
		
		rows.append([number, alias, username, orgId, expirationDate, defaultMarker ])
		number += 1

	if (len(rows) == 0):
		print(helper.col("\nYou have no active {}!".format(kind), [helper.c.r]))
		helper.pressToContinue()
		return

	print(helper.col("\nYou have the following {}:".format(kind), [helper.c.y]))

	helper.createTable(header, rows)

	print("\n" + text + helper.col(" [1-{}] (empty to exit)".format(len(rows)), [helper.c.y, helper.c.BOLD]))

	choice = helper.askForInputUntilEmptyOrValidNumber(len(rows))


	if (choice != -1):
		if (rows[choice][1]):
			return rows[choice][1]
		else:
			return rows[choice][2]
	else:
		return ""