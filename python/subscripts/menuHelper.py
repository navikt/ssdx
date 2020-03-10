# -*- coding: utf-8 -*-
# encoding=utf8

import subscripts.org as org
import subscripts.source as source
import subscripts.helper as helper
import subscripts.other as other
import subscripts.user as user
from blessed import Terminal

def setHeader(term, title, subtitle):
	
	with term.location(0, 4):
		print(term.white_on_darkgray(term.ljust(' ')))
		print(term.white_on_darkgray(term.center(term.bold('   {}'.format(title)))))
		print(term.white_on_darkgray(term.center('   {}'.format(subtitle))))
		print(term.white_on_darkgray(term.ljust(' ')))

def setInfoBar(term, listOfText, location):
	
	with term.location(0, location):
		print(term.white_on_darkgray(term.ljust(' ')))
		for x in listOfText: print(term.white_on_darkgray(term.ljust('   ' + x)))
		print(term.white_on_darkgray(term.ljust(' ')))

def clear(term, showHeader, showFooter, title, subtitle):
	print (term.home() + term.clear())
	if(showHeader): setHeader(term, title, subtitle)
	if(showFooter): setInfoBar(term, helper.getMenuInformation(), term.height - 1)

def getDefaultFormat():
	return { 'addTopSpace': False }

def getBackOrExitButton(isSubMenu):

	menuFormat = getDefaultFormat()
	menuFormat['addTopSpace'] = True

	if (isSubMenu):
		return ["Back", False, menuFormat ]
	else:
		return ["Exit", exit, menuFormat ]

def exit(term):
	raise SystemExit