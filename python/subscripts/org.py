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
	deletePrevious = helper.askForInput( [ 
		["Do you wanna delete the old scratch org? [y/n]", [ helper.c.y ]],
		["(NOTE! The currently active org will NOT be recoverable)", [ helper.c.r, helper.c.BOLD ]]
	] )

	menuHelper.clear(term, True, True, title, 'Creating scratch org')

	with term.location(0, 5):

		if(deletePrevious == "y"):
			helper.startLoading("Deleting default Scratch Org")
			helper.tryCommandWithException(
				["sfdx force:org:delete -p"],
				False, False)[1]

		helper.startLoading("Creating new Scratch Org")
		error = helper.tryCommandWithException(
			["sfdx force:org:create " + 
			"-f ./config/project-scratch-def.json " + 
			"--setalias {} ".format(scratchOrgName) + 
			"--durationdays 5 " + 
			"--setdefaultusername"],
			True, True)[1]
		if (error): return

		helper.startLoading("Installing packages defined in 'sfdx-project.json'")
		error = orgHelper.installPackages()
		if (error): return

		helper.startLoading("Pushing metadata")
		error = helper.tryCommandWithException( ["sfdx force:source:push"], True, True)[1]
		if (error): return

		if (path.exists('./non_deployable_metadata')):
			helper.startLoading("Pushing non-deployable metadata")
			error = helper.tryCommandWithException( ["sfdx force:source:deploy -p ./non_deployable_metadata"], True, True)[1]
			if (error): return

		helper.startLoading("Opening Scratch Org")
		error = helper.tryCommandWithException(["sfdx force:org:open"], False, False)[1]

		helper.startLoading("Assigning all permission sets")
		orgHelper.fetchPermsets()
		commands = [] 
		for permset in orgHelper.fetchPermsets():
			commands.append("sfdx force:user:permset:assign -n " + permset)
		error = helper.tryCommandWithException(commands, True, True)[1]
		if (error): return

		helper.startLoading("Importing dummy data")
		error = orgHelper.importDummyData()
		if (error): return

		# helper.startLoading("Running Apex code from ./scripts/apex")
		# commands = [] 
		# for apexCode in helper.fetchFilesFromFolder("./scripts/apex/", True):
		# 	commands.append("sfdx force:apex:execute --apexcodefile " + apexCode)
		# error = helper.tryCommandWithException(commands, True, True)[1]
		# if (error): return

		helper.pressToContinue(False, 20)


def openScratchOrg(term):
	helper.startLoading("Opening Scratch Org")
	error = helper.tryCommandWithException(["sfdx force:org:open"], True, True)[1]
	if (error): return
	helper.pressToContinue(True, 10)


def deleteScratchOrg(term):
	text = helper.col("Which Scratch Org do you want to delete?", [helper.c.r, helper.c.BOLD])
	org = orgHelper.askUserForOrgs(False, term, text)
	deleteScratchOrg = helper.askForInput( [ ["Are you sure you want to delete {}? {}[y/n]".format(org, helper.c.y), [ helper.c.r, helper.c.BOLD ]] ] )
	if(deleteScratchOrg == "y"):
		print()
		helper.startLoading("Deleting Scratch Org")
		error = helper.tryCommandWithException(["sfdx force:org:delete -p -u " + org], True, True)[1]
		if (error): return
	helper.pressToContinue(False, 10)


def changeDefaultScratchOrg(term):
	
	text = helper.col("Which Scratch Org do you want to set as your default?", [helper.c.y])
	org = orgHelper.askUserForOrgs(False, term, text)
	

	if (org):
		data = helper.getDataFromJson(".sfdx/sfdx-config.json")

		tmp = data["defaultusername"]
		data["defaultusername"] = org

		with open(".sfdx/sfdx-config.json", "w") as jsonFile:
			json.dump(data, jsonFile)

		print(helper.col("\nSuccessfully changed default scratch org.", [helper.c.y]))
		print(helper.col("Pushing and pulling will now be directed to '{}'".format(org), [helper.c.ly]))
	else:
		print(helper.col("\nThe default org was NOT changed.", [helper.c.y]))
	helper.pressToContinue(False, 10)


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
	helper.pressToContinue(False, 10)


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

	helper.pressToContinue(True, None)

def login(term):
	helper.startLoading("Waiting for login in browser")
	error = helper.tryCommandWithException(["sfdx force:auth:web:login -d"], True, True)[1]
	if (error): return
	helper.pressToContinue(False, 10)
