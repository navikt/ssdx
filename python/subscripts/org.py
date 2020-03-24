# -*- coding: utf-8 -*-
# encoding=utf8

import subprocess, os, json, sys, time, webbrowser
import subscripts.helper as helper
import subscripts.orgHelper as orgHelper
import subscripts.menuHelper as menuHelper
from yaspin import yaspin

title = "SSDX Helper"

# -------------------------------------- #
# --------- CREATE SCRATCH ORG --------- #
# -------------------------------------- #

def createScratchOrg(term):

	scratchOrgName = helper.askForInput( [ ["Enter Scratch Org name (non-unique names replaces old ones)", [ helper.c.y ]] ] )
	while (not scratchOrgName): 
		menuHelper.clear(term, True, True, title, 'Create scratch org', None)
		scratchOrgName = helper.askForInput( [
			["Enter Scratch Org name (non-unique names replaces old ones)", [ helper.c.y ]], 
			["Please enter a name", [ helper.c.r ]] ] )

	deletePrevious = False
	if (helper.getDefaultScratchOrg() != '[none]'):
		deletePrevious = menuHelper.askUserYesOrNo(term, True, True, 'Creating scratch org', ['Do you want to delete the old scratch org? ({})'.format(helper.getDefaultScratchOrg())], False, False, False, True)
	
	if (deletePrevious == 2): return

	helper.runFunctionAsProcess(createScratchOrg_process, [term, scratchOrgName, deletePrevious])
	helper.pressToContinue(term)

def createScratchOrg_process(term, scratchOrgName, deletePrevious):

	menuHelper.clear(term, True, True, title, 'Creating scratch org', None)

	orgHelper.createScratchOrg_deletePreviousScratchOrg(term, deletePrevious)

	results, retry = [True, []], True
	while results[0] and retry:
		results = orgHelper.createScratchOrg_createOrg(term, scratchOrgName)
		retry = orgHelper.retry(term, results)
	if (results[0] and not retry): return True

	results, retry = [True, []], True
	while results[0] and retry:
		results = orgHelper.createScratchOrg_installPackages()
		retry = orgHelper.retry(term, results)
	if (results[0] and not retry): return True

	results, retry = [True, []], True
	while results[0] and retry:
		results = orgHelper.createScratchOrg_pushMetadata(term)
		retry = orgHelper.retry(term, results)
	if (results[0] and not retry): return True

	results, retry = [True, []], True
	while results[0] and retry:
		results = orgHelper.createScratchOrg_pushNonDeployedMetadata(term)
		retry = orgHelper.retry(term, results)
	if (results[0] and not retry): return True

	helper.startLoading("Opening Scratch Org")
	error = helper.tryCommand(term, ["sfdx force:org:open"], False, True, False)[0]

	results, retry = [True, []], True
	while results[0] and retry:
		results = orgHelper.createScratchOrg_assignPermsets(term)
		retry = orgHelper.retry(term, results)
	if (results[0] and not retry): return True

	results, retry = [True, []], True
	while results[0] and retry:
		results = orgHelper.createScratchOrg_importDummyData()
		retry = orgHelper.retry(term, results)
	if (results[0] and not retry): return True

	# helper.startLoading("Running Apex code from ./scripts/apex")
	# commands = [] 
	# for apexCode in helper.fetchFilesFromFolder("./scripts/apex/", True):
	# 	commands.append("sfdx force:apex:execute --apexcodefile " + apexCode)
	# error = helper.tryCommand(term, commands, True, True, False)[0]
	# if (error): return

	
# -------------------------------------- #
# ---------- OPEN SCRATCH ORG ---------- #
# -------------------------------------- #

def openScratchOrg(term):
	helper.runFunctionAsProcess(openScratchOrg_process, [term])
	helper.pressToContinue(term)
def openScratchOrg_process(term):
	helper.startLoading("Opening Scratch Org")
	helper.tryCommand(term, ["sfdx force:org:open"], True, True, False)[0]


# -------------------------------------- #
#  OPEN SCRATCH ORG (SEPCIFIC BROWSER)   #
# -------------------------------------- #

def openScratchOrgSpecificBrowser(term):
	menuFormat = menuHelper.getDefaultFormat()
	items = [['Chrome', None, menuFormat], ['Firefox', None, menuFormat], ['Opera', None, menuFormat]]
	if (helper.isMac()): items.append(['Safari', None, menuFormat])
	items.append(menuHelper.getReturnButton(2))
	selection = menuHelper.giveUserChoices(term, True, True, items, 0, 'Open Scratch Org (specify browser)', None, False)
	if (selection == len(items) - 1): return
		
	browserName = items[selection][0]
	browserChoice = browserName.lower()
	helper.startLoading("Opening Scratch Org in {}".format(browserName))
	jsonRaw = subprocess.check_output(["sfdx", "force:org:open", "-r", "--json"])
	jsonOutput = helper.loadJson(jsonRaw)
	url = helper.ifKeyExists("url", jsonOutput["result"])	
	
	res = webbrowser.get(browserChoice).open_new_tab(url)
	if (res): helper.spinnerSuccess()
	else:
		menuHelper.clear(term, True, True, title, 'Open Scratch Org (specify browser)', None)
		helper.startLoading("Opening Scratch Org")
		helper.spinnerError()
		print("Either {} is not running, or it's not installed.".format(browserName))

	helper.pressToContinue(term)
	
	


# -------------------------------------- #
# --------- DELETE SCRATCH ORG --------- #
# -------------------------------------- #

def deleteScratchOrg(term):
	text = helper.col("Which Scratch Org do you want to delete?", [helper.c.r, helper.c.BOLD])
	org = orgHelper.askUserForOrgs(term, False, text, 'Delete Scratch Orgs')
	
	if (org is None or org is True): return
	
	deleteScratchOrg = menuHelper.askUserYesOrNo(term, True, True, 'Main menu', ['Are you sure you want to delete this org? ({})'.format(org)], True, False, False, False)

	if (deleteScratchOrg):
		print()
		helper.startLoading("Deleting Scratch Org")
		error = helper.tryCommand(term, ["sfdx force:org:delete -p -u " + org], True, True, False)[0]
		if (error): return
		
		print("Successfully deleted scratch org '{}'".format(org))

	
	helper.pressToContinue(term)


# -------------------------------------- #
# --------- CHANGE SCRATCH ORG --------- #
# -------------------------------------- #

def changeDefaultScratchOrg(term):
	
	text = helper.col("Which Scratch Org do you want to set as your default?", [helper.c.y])
	org = orgHelper.askUserForOrgs(term, False, text, 'Change Default Scratch Org')
	
	if (org is None or org is True): return

	data = helper.getDataFromJson(".sfdx/sfdx-config.json")
	data["defaultusername"] = org

	with open(".sfdx/sfdx-config.json", "w") as jsonFile:
		json.dump(data, jsonFile)

	print("Successfully changed default scratch org.\nPushing and pulling will now be directed to '{}'".format(org))

	helper.pressToContinue(term)


# -------------------------------------- #
# ------------- CHANGE ORG ------------- #
# -------------------------------------- #

def changeDefaultOrg(term):
		
	text = helper.col("Which Org do you want to set as your default? (Used for Scratch Org creation)", [helper.c.y])
	org = orgHelper.askUserForOrgs(term, True, text, 'Change Default Org')
	
	if (org is None or org is True): return
	
	data = helper.getDataFromJson(".sfdx/sfdx-config.json")
	data["defaultdevhubusername"] = org

	with open(".sfdx/sfdx-config.json", "w") as jsonFile:
		json.dump(data, jsonFile)

	print("Successfully changed default org.\nScratch orgs will now be created from '{}'".format(org))

	helper.pressToContinue(term)


# -------------------------------------- #
# ------- SEE SCRATCH ORG STATUS ------- #
# -------------------------------------- #

def seeScratchOrgStatus(term):
	helper.runFunctionAsProcess(seeScratchOrgStatus_process, [term])
	helper.pressToContinue(term)
def seeScratchOrgStatus_process(term):
	helper.startLoading("Loading Scratch Org details")
	details = subprocess.check_output(["sfdx", "force:org:display", "--json", "--verbose"])
	helper.stopLoading()
	jsonOutput = json.loads(details)

	pre = helper.c.BOLD
	post = helper.c.ENDC

	rows = []

	if ("alias" in jsonOutput['result']):
		rows.append(["Alias", jsonOutput['result']['alias']])
	rows.append(["Username", jsonOutput['result']['username']])
	
	days = ("{} days (next {}, on {})".format(
		helper.convertDateToDaysRemaining(jsonOutput['result']['expirationDate']),
		helper.convertDateToDay(jsonOutput['result']['expirationDate']),
		helper.convertDateFormat(jsonOutput['result']['expirationDate'])))
	rows.append(["Days left", days])
	rows.append(["Status", jsonOutput['result']['status']])
	rows.append(["",""])
	
	rows.append(["ID", jsonOutput['result']['id']])
	rows.append(["Created Date", jsonOutput['result']['createdDate']])
	rows.append(["Edition", jsonOutput['result']['edition']])
	rows.append(["Dev Hub ID", jsonOutput['result']['devHubId']])
	rows.append(["Org Name", jsonOutput['result']['orgName']])
	rows.append(["Access Token", jsonOutput['result']['accessToken']])
	rows.append(["SFDX Auth Url", jsonOutput['result']['sfdxAuthUrl']])
	rows.append(["Instance Url", jsonOutput['result']['instanceUrl']])

	menuHelper.clear(term, False, False, None, None, None)
	helper.createTable([], rows)



# -------------------------------------- #
# ------------ LOGIN TO ORG ------------ #
# -------------------------------------- #

def login(term):
	helper.runFunctionAsProcess(login_process, [term])
	helper.pressToContinue(term)
def login_process(term):
	helper.startLoading("Waiting for login in browser")
	helper.tryCommand(term, ["sfdx force:auth:web:login -d"], True, True, False)[0]
