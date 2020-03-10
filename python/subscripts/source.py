# -*- coding: utf-8 -*-
# encoding=utf8

import subprocess, os, json
import subscripts.helper as helper
import subscripts.menuHelper as menuHelper

title = "SSDX Helper"

def pull(term):
	pushOrPull(term, "pull", False)

def push(term):
	pushOrPull(term, "push", False)

def pushOrPull(term, value, isForce):

	force, forceText = "", ""
	if (isForce):
		force = "-f"
		forceText = " with force"

	subtitle = "{}ing Metadata{}".format(value, forceText)
	helper.startLoading(subtitle)

	results = helper.tryCommand(term, ["sfdx force:source:{} {}".format(value, force)], True)
	if (results[0]):
		text = results[1]
		for x in range(4):
			text.append('')
		text.append('Do you want to {} using force? (-f flag)'.format(value))
		retryWithForce = menuHelper.askUserYesOrNo(term, False, False, subtitle, text, False, False, True)
		if (retryWithForce):
			menuHelper.clear(term, True, True, title, subtitle, None)
			
			with term.location(0, 5):
				pushOrPull(term, value, True)
	else:
		helper.pressToContinue()



def manifest(term):
	print(helper.col("Which manifest do you want to pull using?", [helper.c.y]))

	manifests = helper.fetchFilesFromFolder("./manifest/", True)
	header = ["Number", "Manifest"]
	rows = []

	for i, manifest in enumerate(manifests):
		rows.append([i + 1, manifest.replace("./manifest/", "").replace(".xml", "")])
	
	helper.createTable(header, rows)
	
	choice = helper.askForInputUntilEmptyOrValidNumber(len(rows))

	if (choice != -1):
		print()
		manifest = "./manifest/" + rows[choice][1] + ".xml"
		helper.startLoading("Pulling Metadata from Manifest {}".format(manifest))
		error = helper.tryCommand(term, ["sfdx force:source:retrieve -x {}".format(manifest)], True)[0]
		if (error): return

	helper.pressToContinue()