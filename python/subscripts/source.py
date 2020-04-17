# -*- coding: utf-8 -*-
# encoding=utf8

import subprocess, os, json
import subscripts.helper as helper
import subscripts.menuHelper as menuHelper

title = "SSDX Helper"

def pull(term):
	pushOrPull(term, "pull", False, True)

def push(term):
	pushOrPull(term, "push", False, True)

def pushOrPull(term, value, isForce, seeOutput):

	force, forceText = "", ""
	if (isForce):
		force = "-f"
		forceText = " with force"

	subtitle = "{}ing Metadata{}".format(value, forceText)
	helper.startLoading(subtitle)

	results = helper.tryCommand(term, ["sfdx force:source:{} {}".format(value, force)], True, True, seeOutput)
	if (results[0] and not isForce):
		text = results[1]
		text.append(helper.col('\nDo you want retry {}ing using force? (-f flag)'.format(value), [helper.c.y, helper.c.UL]))
		retryWithForce = menuHelper.askUserYesOrNo(term, False, False, subtitle, text, False, False, False, False)
		if (retryWithForce):
			menuHelper.clear(term, True, True, title, subtitle, None)
			pushOrPull(term, value, True, seeOutput)
	else:
		helper.pressToContinue(term)



def manifest(term):
	
	text = "Which manifest do you want to pull using?"

	path = helper.getConfig('locations.manifest') + '/'

	manifests = helper.fetchFilesFromFolder(path, True)
	header = ["Number", "Manifest"]
	rows = []

	for i, manifest in enumerate(manifests):
		rows.append([i + 1, manifest.replace(path, "").replace(".xml", "")])
	
	menuFormat = menuHelper.getDefaultFormat()
	items = []
	for manifest in manifests:
		items.append([manifest.replace(path, "").replace(".xml", ""), None, menuFormat])

	items.append(menuHelper.getReturnButton(2))

	selection = menuHelper.giveUserChoices(term, True, True, items, 0, 'Pull Metadata (manifest)', text, False)
	if (selection == len(items) - 1): return
	
	menuHelper.clear(term, True, True, title, 'Create user', None)
	manifest = path + rows[selection][1] + ".xml"

	helper.startLoading("Pulling Metadata from Manifest {}".format(manifest))
	helper.tryCommand(term, ["sfdx force:source:retrieve -x {}".format(manifest)], True, True, True)[0]
	
	helper.pressToContinue(term)