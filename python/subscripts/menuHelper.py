# -*- coding: utf-8 -*-
# encoding=utf8

import subscripts.org as org
import subscripts.source as source
import subscripts.helper as helper
import subscripts.other as other
import subscripts.user as user
from blessed import Terminal

title = "SSDX Helper"

def setHeader(term, title, subtitle):
	
	with term.location(0, 4):
		print(term.white_on_darkgray(term.ljust(' ')))
		print(term.white_on_darkgray(term.center(term.bold('   {}'.format(title)))))
		print(term.white_on_darkgray(term.center('   {}'.format(subtitle))))
		print(term.white_on_darkgray(term.ljust(' ')))

def setMiddle(term, title, middle):
	
	with term.location(0, 6):
		for x in middle:
			print(x)

def setInfoBar(term, listOfText, location):
	
	with term.location(0, location):
		print(term.white_on_darkgray(term.ljust(' ')))
		for x in listOfText: print(term.white_on_darkgray(term.ljust('   ' + x)))
		print(term.white_on_darkgray(term.ljust(' ')))

def clear(term, showHeader, showFooter, title, subtitle, middle):
	print (term.home() + term.clear())
	if(showHeader): setHeader(term, title, subtitle)
	if(showFooter): setInfoBar(term, helper.getMenuInformation(), term.height - 1)
	
	if(middle != None): setMiddle(term, title, middle)

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
	exit = askUserYesOrNo(term, True, True, 'Main menu', ['Are you sure you want to exit?'], True, False, False)
	if (exit):
		raise SystemExit



def askUserYesOrNo(term, showHeader, showFooter, subtitle, question, defaultYes, confirm, printAtBottom ):

	menuFormat = getDefaultFormat()

	if (defaultYes): items = [['Yes', None, menuFormat], ['No', None, menuFormat]]
	else: items = [['No', None, menuFormat], ['Yes', None, menuFormat]]

	selection = giveUserChoices(term, showHeader, showFooter, items, 0, subtitle, question, printAtBottom)
	
	if (defaultYes):
		if (confirm and selection == 0):
			selection = askUserYesOrNo(term, showHeader, showFooter, subtitle, ['Are you sure?'], False, False)
		return (selection + 1) % 2
	else:
		return selection

	return False

def displayScreen(term, showHeader, showFooter, items, selection, subtitle, question, printAtBottom):
	
	length = 5
	if (question != None): length += 3
	if (printAtBottom): length = term.height - 1

	clear(term, showHeader, showFooter, title, subtitle, question)
	with term.location(0, length):
		printData(term, items, selection)
		

def printData(term, items, selection):
	for (idx, m) in enumerate(items):
		if (m[2]['addTopSpace']): print()
		if idx == selection: print('> {t.bold_yellow}{title}'.format(t=term, title=m[0]))
		else: print('  {t.normal}{title}'.format(t=term, title=m[0]))

def giveUserChoices(term, showHeader, showFooter, items, selection, subtitle, question, printAtBottom):
	
	displayScreen(term, showHeader, showFooter, items, selection, subtitle, question, printAtBottom)
	selection_inprogress = True
	with term.cbreak():
		while selection_inprogress:
			key = term.inkey()
			if key.is_sequence:
				if key.name == 'KEY_TAB': selection += 1
				if key.name == 'KEY_DOWN': selection += 1
				if key.name == 'KEY_UP': selection -= 1
				if key.name == 'KEY_BACKSPACE': return len(items) - 1
				if key.name == 'KEY_ENTER': selection_inprogress = False
			selection = selection % len(items)
			displayScreen(term, showHeader, showFooter, items, selection, subtitle, question, printAtBottom)

	return selection