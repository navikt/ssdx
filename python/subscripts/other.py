# -*- coding: utf-8 -*-
# encoding=utf8

import subscripts.helper as helper
import subscripts.orgHelper as orgHelper

def createPackageKey(term):
	
	path = helper.getConfig('locations.package-key')
	if (path is None):
		print(helper.col("\nEdit ./config/ssdx-config.json to add a default path for package keys", [helper.c.r]))
		helper.pressToContinue(term)
		return

	packageKey = helper.askForInput( [ ["Enter the password needed to install packages", [ helper.c.y ]] ] )
	try:
		f = open(path, "w")
	except IOError:
		f = open(path, "x")
	finally:
		f.write(packageKey)
		f.close()
		print(helper.col("\nSuccessfully added key to {}".format(path), [helper.c.y, helper.c.UL]))
		helper.pressToContinue(term)



# -------------------------------------- #
# -------- RE-IMPORT DUMMY DATA -------- #
# -------------------------------------- #

def reImportDummyData(term):
	results, retry = [True, []], True
	while results[0] and retry:
		results = orgHelper.createScratchOrg_importDummyData()
		retry = orgHelper.retry(term, results)
	if (results[0] and not retry): return True
	helper.pressToContinue(term)
