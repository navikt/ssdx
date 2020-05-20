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

	helper.pressToContinue(term)

	
# -------------------------------------- #
# ---------- OPEN SCRATCH ORG ---------- #
# -------------------------------------- #

def openScratchOrg(term):
	helper.startLoading("Opening Scratch Org")
	helper.tryCommand(term, ["sfdx force:org:open"], True, True, False)[0]
	helper.pressToContinue(term)


# -------------------------------------- #
#  OPEN SCRATCH ORG (SEPCIFIC BROWSER)   #
# -------------------------------------- #

def openScratchOrgSpecificBrowser(term):
	menuFormat = menuHelper.getDefaultFormat()
	items = [['Chrome', None, menuFormat], ['Firefox', None, menuFormat], ['Opera', None, menuFormat]]
	if (helper.isMac()): items.append(['Safari', None, menuFormat])
	items.append(menuHelper.getReturnButton(2))
	selection = menuHelper.giveUserChoices(term=term, showHeader=True, showFooter=True, items=items, selection=0, subtitle='Open Scratch Org (specify browser)', middleText=None, printAtBottom=False)
	if (selection == len(items) - 1): return
		
	browserName = items[selection][0]
	browserChoice = browserName.lower()
	helper.startLoading("Opening Scratch Org in {}".format(browserName))

	output = helper.tryCommand(term=term, commands=["sfdx force:org:open -r --json"], clearBeforeShowingError=False, stopSpinnerAfterSuccess=False, printOutputAfterSuccess=False)

	if (not output[0]): # not failing

		jsonOutput = helper.loadJson(output[1][0])
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
	orgs = orgHelper.askUserForOrgs(term, False, text, 'Delete Scratch Orgs', selectMultiple=True)
	helper.debug(orgs)
	if not orgs:
		menuHelper.clear(term, False, False, title, 'Delete Scratch Orgs', None)
		print("Did not delete any scratch orgs")
		helper.pressToContinue(term)
		return
	
	elif (len(orgs) > 1): text = 'Are you sure you want to delete these orgs?'
	else: text = 'Are you sure you want to delete this org?'

	deleteScratchOrg = menuHelper.askUserYesOrNo(term, True, True, 'Main menu', [text + ' ({})'.format(', '.join(orgs))], True, False, False, False)

	if (deleteScratchOrg):
		menuHelper.clear(term, False, False, title, 'Delete Scratch Orgs', None)
		for org in orgs:
			helper.startLoading("Deleting Org: {}".format(org))
			error = helper.tryCommand(term, ["sfdx force:org:delete -p -u " + org], True, True, False)[0]
			if (error): return
		
	helper.pressToContinue(term)


# -------------------------------------- #
# --------- CHANGE SCRATCH ORG --------- #
# -------------------------------------- #

def changeDefaultScratchOrg(term):
	
	text = helper.col("Which Scratch Org do you want to set as your default?", [helper.c.y])
	org = orgHelper.askUserForOrgs(term, False, text, 'Change Default Scratch Org', selectMultiple=False)
	
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
	org = orgHelper.askUserForOrgs(term, True, text, 'Change Default Org', selectMultiple=False)
	
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
	helper.startLoading("Loading Scratch Org details")
	
	output = helper.tryCommand(term=term, commands=["sfdx force:org:display --json --verbose", "sfdx force:org:open --json -r"], clearBeforeShowingError=False, stopSpinnerAfterSuccess=True, printOutputAfterSuccess=False)
	if (output[0]): 
		helper.pressToContinue(term)
		return

	jsonOutput = json.loads(output[1][0])
	jsonOutputLoginUrl = json.loads(output[1][1])
	
	helper.stopLoading()

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
	
	rows.append(["Login Url", jsonOutputLoginUrl['result']['url']])


	menuHelper.clear(term, False, False, None, None, None)
	helper.createTable([], rows)
	helper.pressToContinue(term)



# -------------------------------------- #
# ------------ LOGIN TO ORG ------------ #
# -------------------------------------- #

def login(term):

	subtitle = 'Login to Org'

	menuFormat = menuHelper.getDefaultFormat()
	items = [["Production Org / Developer Edition / DevHub", None, menuFormat], ["Sandbox", None, menuFormat], menuHelper.getReturnButton(2)]
	selection = menuHelper.giveUserChoices(term=term, showHeader=True, showFooter=True, items=items, selection=0, subtitle=subtitle, middleText="Choose Org type", printAtBottom=False)

	if (selection == 2): return
	param = ""
	if (selection == 0):
		setAsDefault = menuHelper.askUserYesOrNo(term, True, True, subtitle, ['Set this org as default DevHub? (scratch orgs will be made using this org)'], True, False, False, True)
		if (not setAsDefault): return
		if (setAsDefault):
			param = "-d"
	if (selection == 1):
		param = "-r https://test.salesforce.com"


	menuHelper.clear(term, True, True, title, subtitle, None)
	orgName = helper.askForInput( [ ["Enter name for org", [ helper.c.y ]] ] )
	if (orgName):
		param += " -a " + orgName
	menuHelper.clear(term, True, True, title, subtitle, None)

	helper.startLoading("Waiting for login in browser")
	helper.tryCommand(term, ["sfdx force:auth:web:login " + param], True, True, False)[0]
	helper.pressToContinue(term)
