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
		deletePrevious = menuHelper.askUserYesOrNo(term, True, True, 'Creating scratch org', ['Do you want to delete the old scratch org? ({})'.format(helper.getDefaultScratchOrg())], False, False, False, True)

	menuHelper.clear(term, True, True, title, 'Creating scratch org', None)
	menuHelper.fixHeight(4)

	if (deletePrevious == 2): return deletePrevious
	if (deletePrevious):
		helper.startLoading("Deleting default Scratch Org")
		error = helper.tryCommand(term, ["sfdx force:org:delete -p"], False, True, False)[0]


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
		True, True, False)
	return results


# INSTALL PACKAGES
# ------------------------------

from pathlib import Path

def installPackages():

	packages = None
	try:
		packages = helper.getDataFromJson("sfdx-project.json")
		if ("packageDirectories" not in packages):
			return False, []
		packages = packages["packageDirectories"][0]
		if ("dependencies" not in packages):
			return False, []
		packages = packages["dependencies"]
	except Exception as e:
		return True, [e]
	

	if (len(packages) == 0): return False, []

	helper.startLoading("Installing packages defined in 'sfdx-project.json'")

	copyUnsignedWhitelist()
	
	results = helper.tryCommand(None, ["sfdx plugins:install rstk-sfdx-package-utils@0.1.12"], False, False, False)
	if (results[0]): return results

	packageKey = helper.getContentOfFile('./.ssdx/.packageKey')
	if (packageKey == None): return True, [".packageKey file does not exists. Without it, packages cannot be installed. See Main Menu > Other"]
	
	keys = getPackageKeys(packages, packageKey)

	cmd = 'sfdx rstk:package:dependencies:install -w 10 --noprecheck --installationkeys "{}"'.format(keys)

	try:
		helper.runCommand(cmd)
		helper.spinnerSuccess()
	except subprocess.CalledProcessError as e:
		output = e.output.decode('UTF-8')
		helper.log(cmd, output, 'ERROR')
		return True, [output]
	except Exception as e:
		helper.log(cmd, output, 'ERROR') # TODO add log everywhere
		return True, [e]
	return False, []


# PUSH METADATA
# ------------------------------

def createScratchOrg_pushMetadata(term):
	helper.startLoading("Pushing metadata")
	return helper.tryCommand(term, ["sfdx force:source:push"], True, True, False)


# PUSH METADATA
# ------------------------------
import os.path
from os import path
def createScratchOrg_pushNonDeployedMetadata(term):
	if (path.exists('./non_deployable_metadata')):
		helper.startLoading("Pushing non-deployed metadata")
		return helper.tryCommand(term,  ["sfdx force:source:deploy -p ./non_deployable_metadata"], True, True, False)
		

# FETCH PERM SETS
# ------------------------------

def assignPermsets(term):
	helper.startLoading("Assigning all permission sets")
	fetchPermsets()
	commands = [] 
	for permset in fetchPermsets():
		commands.append("sfdx force:user:permset:assign -n " + permset)
	return helper.tryCommand(term, commands, True, True, False)


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
	path = "./dummy-data/"

	copyUnsignedWhitelist()
	results = helper.tryCommand(None, ["sfdx plugins:install sfdx-wry-plugin@0.0.9"], False, False, False)
	if (results[0]): return results

	try:
		for folder in next(os.walk(path))[1]:
			if (folder.endswith(".out")):
				shutil.rmtree(path + folder)
		for folder in next(os.walk(path))[1]:
			cmd = 'sfdx wry:file:replace -i {} -o {}'.format(path + folder, path + folder + ".out")
			results = helper.tryCommand(None, [cmd], False, False, False)
			if (results[0]): return results
		for folder in next(os.walk(path))[1]:
			if (folder.endswith(".out")):
				cmd = 'sfdx force:data:tree:import --plan {}{}/plan.json'.format(path, folder)
				results = helper.tryCommand(None, [cmd], False, False, False)
				if (results[0]): return results
		helper.spinnerSuccess()
	except Exception as e:
		helper.log(cmd, e, 'ERROR')
		return True, [e]
	return False, []




# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

# RETRY QUESTION ON ERROR
# ----------------------------

def retry(term, results):
	if (results[0]):
		helper.spinnerError()
		text = results[1] # TODO separate output and question
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

def askUserForOrgs(term, lookingForRegularOrgs, text, subtitle):
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
		menuHelper.clear(term, True, True, title, subtitle, None)
		menuHelper.fixHeight(4)

		print(helper.col("You have no active {}!".format(kind), [helper.c.r]))
		helper.pressToContinue()
		return True

	print(helper.col("You have the following {}:".format(kind), [helper.c.y]))

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

def getPackageKeys(data, packageKey):
	keys = ''
	for iterator in range(len(data)):
		keys = "{} {}:{}".format(keys, iterator + 1, packageKey) # should be in the format of '1:key 2:key 3:key etc, one for each dependency
	return keys

def copyUnsignedWhitelist():
	try: copyfile("./.ssdx/config/unsignedPluginWhiteList.json", str(Path.home()) + "/.config/sfdx/unsignedPluginWhiteList.json")
	except Exception as e: return True, [e]