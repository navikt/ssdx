# -*- coding: utf-8 -*-
# encoding=utf8

import subprocess, os
import subscripts.helper as helper
import subscripts.menuHelper as menuHelper

title = "SSDX Helper"

# ---------------------------------------------------------
# SUB-FUNCTIONS OF CREATING A SCRATCH ORG
# ---------------------------------------------------------

# DELETE PREVIOUS SCRATCH ORG
# ------------------------------

def createScratchOrg_deletePreviousScratchOrg(term, deletePrevious):
	
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

def createScratchOrg_installPackages():

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

	keysParam = ''
	path = helper.getConfig('locations.package-key')
	if (path is not None):
		packageKey = helper.getContentOfFile(path)
		if (packageKey == None): return True, ["{} file does not exists. Without it, packages cannot be installed. See Main Menu > Other > Add Package Key to add it.".format(path)]
	
		keys = getPackageKeys(packages, packageKey)
		keysParam = ' --installationkeys "{}"'.format(keys)

	cmd = 'sfdx rstk:package:dependencies:install -w 10 --noprecheck' + keysParam
	results = helper.tryCommand(None, [cmd], True, True, False)
	return results


# PUSH METADATA
# ------------------------------

def createScratchOrg_pushMetadata(term):
	helper.startLoading("Pushing metadata")
	return helper.tryCommand(term, ["sfdx force:source:push"], True, True, False)


# PUSH UNPACKAGABLE METADATA
# ------------------------------
def createScratchOrg_pushNonDeployedMetadata(term):
	path = helper.getConfig('locations.unpackagable')
	
	if (path is None):
		return False, []
	
	if (not helper.folderExists(path)):
		return True, ['Folder \'{}\' does not exists'.format(path)]
	
	helper.startLoading("Pushing unpackagable metadata")
	return helper.tryCommand(term,  ["sfdx force:source:deploy -p " + path], True, True, False)

# ASSIGN PERM SETS
# ------------------------------

import time

def createScratchOrg_assignPermsets(term):

	permsets = helper.getConfig('permsets_to_assign')

	if (permsets is None or not permsets):
		return False, []

	helper.startLoading("Assigning configured permission sets")
	commands = [] 
	for permset in permsets:
		commands.append("sfdx force:user:permset:assign -n " + permset)
	
	trysLeft = 12
	while(permsetGroupsAreNotComplete(term)):
		time.sleep(10)
		trysLeft -= 1
		if (trysLeft == 0): break

	results = helper.tryCommand(term, commands, True, False, False)

	helper.changeLoadingText("Assigned permission sets: {}".format(', '.join(permsets)))
	helper.spinnerSuccess()

	return results

import json, re

def permsetGroupsAreNotComplete(term):
	res = helper.tryCommand(term, ["sfdx force:apex:execute -f ./.ssdx/apex/validatePermsetGroups.cls --json"], False, False, False)

	if (not res[0]):
		jsonOutput = json.loads(res[1][0])
		if ("logs" in jsonOutput['result']):
			log = jsonOutput['result']['logs']
			amount = re.split("BEFORE(.*)AFTER", log)[3]
			return amount != '0'
	return false


# IMPORT DUMMY DATA
# ------------------------------

import shutil, os

def createScratchOrg_importDummyData():
	
	path = helper.getConfig('locations.dummy-data')
	if (path is None):
		return False, []
	if (not helper.folderExists(path)):
		return True, ['Folder \'{}\' does not exists'.format(path)]
	path = path + '/'

	helper.startLoading("Importing dummy data")

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


	menuFormat = menuHelper.getDefaultFormat()
	items = []
	originalItems = []
	for row in jsonOutput['result'][root]:
		alias = helper.ifKeyExists('alias', row)
		username = helper.ifKeyExists('username', row)
		orgId = helper.ifKeyExists('orgId', row)
		expirationDate = helper.ifKeyExists('expirationDate', row)
		defaultMarker = helper.ifKeyExists('defaultMarker', row).replace('(U)', 'X').replace('(D)', 'X')
		
		if (defaultMarker is not ''):
			if (helper.isMac()): defaultMarker = "✅ "
			else: defaultMarker = "✓"
		if (expirationDate is not ''): expirationDate = '({})'.format(expirationDate)
		if (alias == ""): alias = username

		line = " ".join([alias, defaultMarker, expirationDate])
		items.append([line, None, menuFormat])
		originalItems.append(alias)
	
	if (len(items) == 0):
		menuHelper.clear(term, True, True, title, subtitle, None)
		print(helper.col("You have no active {}!".format(kind), [helper.c.r]))
		helper.pressToContinue(term)
		return True

	items.append(menuHelper.getReturnButton(2))

	selection = menuHelper.giveUserChoices(term, True, True, items, 0, subtitle, text, False)
	if (selection == len(originalItems)): return None
	return originalItems[selection]


def getPackageKeys(data, packageKey):
	keys = ''
	for iterator in range(len(data)):
		keys = "{} {}:{}".format(keys, iterator + 1, packageKey) # should be in the format of '1:key 2:key 3:key etc, one for each dependency
	return keys

from shutil import copyfile
def copyUnsignedWhitelist():
	# TODO add folder creation 
	try: copyfile("./.ssdx/config/unsignedPluginWhiteList.json", str(Path.home()) + "/.config/sfdx/unsignedPluginWhiteList.json")
	except Exception as e: return True, [e]