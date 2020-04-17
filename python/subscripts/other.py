# -*- coding: utf-8 -*-
# encoding=utf8

import subscripts.helper as helper

def createPackageKey(term):
	
	packageKey = helper.askForInput( [ ["Enter the password needed to install packages", [ helper.c.y ]] ] )
	path = helper.getConfig('locations.package-key')
	
	try:
		f = open(path, "w")
	except IOError:
		f = open(path, "x")
	finally:
		f.write(packageKey)
		f.close()
		print(helper.col("\nSuccessfully added key to {}".format(path), [helper.c.y, helper.c.UL]))
		helper.pressToContinue(term)

