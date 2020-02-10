# -*- coding: utf-8 -*-
# encoding=utf8

import subscripts.helper as helper
from yaspin import yaspin
import datetime, json

def create(mainMenu):
	
	print(helper.col("Which user definition to you want to user as baseline? (see ./config/users/)\n", [helper.c.y]))

	try:
		userTypes = helper.fetchFilesFromFolder("./config/users/", False)
		for i, user in enumerate(userTypes):
			print( "  {}: {}".format(i + 1, user.replace(".json", "")))
	except Exception as e:
		print(e)
		print("\nMake sure ")
		helper.pressToContinue(True, None)

	print()
	choice = helper.askForInputUntilEmptyOrValidNumber(len(userTypes)) 
	print()

	if (choice != -1):
		file = "./config/users/" + userTypes[choice]
		d = datetime.datetime.now().strftime('%d%m%y_%f')
		username = "{}{}@nav.no".format(userTypes[choice].replace(".json", ""), d)
		email = "{}{}@fake.no".format(userTypes[choice].replace(".json", ""), d)
		
		helper.startLoading("Creating user")
		res = helper.tryCommandWithException(["sfdx force:user:create -f {} username={} email={}".format(file, username, email)], True, True)
		error = res[1]

	if (not error):
		
		helper.startLoading("Fetching password")
		pw = helper.tryCommandWithException(["sfdx force:user:display -u {} --json".format(username)], True, True)
		if (not pw[1]):
			jsonOutput = json.loads(pw[0][0])
			if ("password" in jsonOutput['result']):
				password = jsonOutput['result']['password']
			if ("instanceUrl" in jsonOutput['result']):
				url = jsonOutput['result']['instanceUrl'].replace('https://', '').split('.cs')[0]


		print("\n URL: {}\n Username: {}\n Password: {}".format(url, username, password))
		print()
	helper.pressToContinue(True, None)

