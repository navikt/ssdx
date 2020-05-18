# -*- coding: utf-8 -*-
# encoding=utf8

import subscripts.helper as helper
import subscripts.menuHelper as menuHelper
from yaspin import yaspin
import datetime, json

title = "SSDX Helper"

def create(term):
	
	path = helper.getConfig('locations.users')
	if (path is None):
		print(helper.col("\nEdit ./config/ssdx-config.json to add a default path for user configs", [helper.c.r]))
		helper.pressToContinue(term)
		return
	path = path + '/'

	text = "Which user definition to you want to user as baseline? (see {})".format(path)

	try:
		userTypes = helper.fetchFilesFromFolder(path, False)
	except Exception as e:
		print("Make sure users are configured in " + path)
		helper.pressToContinue(term)
	
	menuFormat = menuHelper.getDefaultFormat()
	items = []
	for userType in userTypes:
		items.append([userType.replace(".json", ""), None, menuFormat])

	items.append(menuHelper.getReturnButton(2))

	selection = menuHelper.giveUserChoices(term, True, True, items, 0, 'Create user', text, False)
	if (selection == len(items) - 1): return

	file = path + userTypes[selection]
	d = datetime.datetime.now().strftime('%d%m%y_%f')
	username = "{}{}@nav.no".format(userTypes[selection].replace(".json", ""), d)
	email = "{}{}@fake.no".format(userTypes[selection].replace(".json", ""), d)
	
	menuHelper.clear(term, True, True, title, 'Create user', None)
	helper.startLoading("Creating user")
	error = helper.tryCommand(term, ["sfdx force:user:create -f {} username={} email={}".format(file, username, email)], False, True, False)[0]

	if (not error):
		helper.startLoading("Fetching password")
		
		res = helper.tryCommand(term, ["sfdx force:user:display -u {} --json".format(username)], False, True, False)
		if (not res[0]):
			jsonOutput = json.loads(res[1][0])
			if ("password" in jsonOutput['result']):
				password = jsonOutput['result']['password']
			if ("instanceUrl" in jsonOutput['result']):
				url = jsonOutput['result']['instanceUrl'].replace('https://', '').split('.cs')[0]
		
		login = helper.tryCommand(term, ["sfdx force:org:open -u {} -r --json".format(username)], False, True, False)
		if (not login[0]):
			loginJsonOutput = json.loads(login[1][0])
			if ("url" in jsonOutput['result']):
				loginUrl = jsonOutput['result']['url']

		print("\n URL: {}\n Username: {}\n Password: {}\n\nInstant login: {}\n".format(url, username, password, loginUrl))
	helper.pressToContinue(term)

