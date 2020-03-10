# -*- coding: utf-8 -*-
# encoding=utf8

import subprocess, os, json, sys, time, os.path
from os import path
import subscripts.helper as helper
import subscripts.orgHelper as orgHelper
import subscripts.menuHelper as menuHelper
from yaspin import yaspin

title = "SSDX Helper"

def createScratchOrg(term):

	scratchOrgName = helper.askForInput( [ ["Enter Scratch Org name (non-unique names replaces old ones)", [ helper.c.y ]] ] )
	# deletePrevious = helper.askForInput( [ 
	# 	["Do you wanna delete the old scratch org? [y/n]", [ helper.c.y ]],
	# 	["(NOTE! The currently active org will NOT be recoverable)", [ helper.c.r, helper.c.BOLD ]]
	# ] )

	deletePrevious = False
	if (helper.getDefaultScratchOrg() != '[none]'):
		deletePrevious = menuHelper.askUserYesOrNo(term, True, True, 'Creating scratch org', ['Do you want to delete the old scratch org?'], False, False, False)

	menuHelper.clear(term, True, True, title, 'Creating scratch org', None)

	with term.location(0, 5):

		if(deletePrevious):
			helper.startLoading("Deleting default Scratch Org")
			error = helper.tryCommand(term, ["sfdx force:org:delete -p"], False)[0]

		helper.startLoading("Creating new Scratch Org")
		error = helper.tryCommand(term, 
			["sfdx force:org:create " + 
			"-f ./config/project-scratch-def.json " + 
			"--setalias {} ".format(scratchOrgName) + 
			"--durationdays 5 " + 
			"--setdefaultusername"],
			True)[0]
		if (error): return

		helper.startLoading("Installing packages defined in 'sfdx-project.json'")
		error = orgHelper.installPackages()
		if (error): return

		helper.startLoading("Pushing metadata")
		error = helper.tryCommand(term,  ["sfdx force:source:push"], True)[0]
		if (error): return

		if (path.exists('./non_deployable_metadata')):
			helper.startLoading("Pushing non-deployable metadata")
			error = helper.tryCommand(term,  ["sfdx force:source:deploy -p ./non_deployable_metadata"], True)[0]
			if (error): return

		helper.startLoading("Opening Scratch Org")
		error = helper.tryCommand(term, ["sfdx force:org:open"], False)[0]

		helper.startLoading("Assigning all permission sets")
		orgHelper.fetchPermsets()
		commands = [] 
		for permset in orgHelper.fetchPermsets():
			commands.append("sfdx force:user:permset:assign -n " + permset)
		error = helper.tryCommand(term, commands, True)[0]
		if (error): return

		helper.startLoading("Importing dummy data")
		error = orgHelper.importDummyData()
		if (error): return

		# helper.startLoading("Running Apex code from ./scripts/apex")
		# commands = [] 
		# for apexCode in helper.fetchFilesFromFolder("./scripts/apex/", True):
		# 	commands.append("sfdx force:apex:execute --apexcodefile " + apexCode)
		# error = helper.tryCommand(term, commands, True)[0]
		# if (error): return

		helper.pressToContinue()


def openScratchOrg(term):
	helper.startLoading("Opening Scratch Org")
	error = helper.tryCommand(term, ["sfdx force:org:open"], True)[0]
	if (error): return
	helper.pressToContinue()


def deleteScratchOrg(term):
	text = helper.col("Which Scratch Org do you want to delete?", [helper.c.r, helper.c.BOLD])
	org = orgHelper.askUserForOrgs(False, term, text)
	deleteScratchOrg = helper.askForInput( [ ["Are you sure you want to delete {}? {}[y/n]".format(org, helper.c.y), [ helper.c.r, helper.c.BOLD ]] ] )
	if(deleteScratchOrg == "y"):
		print()
		helper.startLoading("Deleting Scratch Org")
		error = helper.tryCommand(term, ["sfdx force:org:delete -p -u " + org], True)[0]
		if (error): return
	helper.pressToContinue()


def changeDefaultScratchOrg(term):
	
	text = helper.col("Which Scratch Org do you want to set as your default?", [helper.c.y])
	org = orgHelper.askUserForOrgs(False, term, text)
	

	if (org):
		data = helper.getDataFromJson(".sfdx/sfdx-config.json")

		data["defaultusername"] = org
	
		with open(".sfdx/sfdx-config.json", "w") as jsonFile:
			json.dump(data, jsonFile)

		print(helper.col("\nSuccessfully changed default scratch org.", [helper.c.y]))
		print(helper.col("Pushing and pulling will now be directed to '{}'".format(org), [helper.c.ly]))
	else:
		print(helper.col("\nThe default org was NOT changed.", [helper.c.y]))
	helper.pressToContinue()


def changeDefaultOrg(term):
		
	text = helper.col("Which Org do you want to set as your default? (Used for Scratch Org creation)", [helper.c.y])
	org = orgHelper.askUserForOrgs(True, term, text)
	
	if (org):
		data = helper.getDataFromJson(".sfdx/sfdx-config.json")

		tmp = data["defaultdevhubusername"]
		data["defaultdevhubusername"] = org

		with open(".sfdx/sfdx-config.json", "w") as jsonFile:
			json.dump(data, jsonFile)

		print(helper.col("\nSuccessfully changed default org.", [helper.c.y]))
		print(helper.col("Scratch orgs will now be created from '{}'".format(org), [helper.c.ly]))
	else:
		print(helper.col("\nThe default org was NOT changed.", [helper.c.y]))
	helper.pressToContinue()


def seeScratchOrgStatus(term):

	helper.startLoading("Loading Scratch Org details")
	details = subprocess.check_output(["sfdx", "force:org:display", "--json"])
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
	rows.append(["Instance Url", jsonOutput['result']['instanceUrl']])

	helper.createTable([], rows)

	helper.pressToContinue()

def login(term):
	helper.startLoading("Waiting for login in browser")
	error = helper.tryCommand(term, ["sfdx force:auth:web:login -d"], True)[0]
	if (error): return
	helper.pressToContinue()
