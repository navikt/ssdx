# -*- coding: utf-8 -*-
# encoding=utf8

import subscripts.org as org
import subscripts.source as source
import subscripts.helper as helper
import subscripts.other as other
import subscripts.user as user
from blessed import Terminal

title = "SSDX Helper"

# input
# ---------------------------------------------------------------------

def askUserYesOrNo(term, showHeader, showFooter, subtitle, middleText, defaultYes, needConfirmation, printAtBottom, canCancel ):

	menuFormat = getDefaultFormat()

	if (defaultYes): items = [['Yes', None, menuFormat], ['No', None, menuFormat]]
	else: items = [['No', None, menuFormat], ['Yes', None, menuFormat]]

	if (canCancel): items.append(getReturnButton(2))

	selection = giveUserChoices(term, showHeader, showFooter, items, 0, subtitle, middleText, printAtBottom)
	
	if (defaultYes):
		if (needConfirmation and selection == 0):
			selection = askUserYesOrNo(term, showHeader, showFooter, subtitle, ['Are you sure?'], False, False, False)
		return (selection + 1) % len(items)
	else:
		return selection

	return False

def giveUserChoices(term, showHeader, showFooter, items, selection, subtitle, middleText, printAtBottom):
	
	displayScreen(term, showHeader, showFooter, items, selection, subtitle, middleText, printAtBottom)
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
			displayScreen(term, showHeader, showFooter, items, selection, subtitle, middleText, printAtBottom)

	clear(term, showHeader, showFooter, title, subtitle, middleText)
	return selection

# viewport
# ---------------------------------------------------------------------

def displayScreen(term, showHeader, showFooter, items, selection, subtitle, middleText, printAtBottom):
	
	length = getLength(term, middleText)
	if (printAtBottom): length = term.height - 1 # send to clear as well

	clear(term, showHeader, showFooter, title, subtitle, middleText)
	with term.location(0, length):
		printData(term, items, selection)

def printData(term, items, selection):
	for (idx, m) in enumerate(items):
		if (m[2]['addTopSpace']): print()
		if idx == selection: print('> {t.bold_yellow}{title}'.format(t=term, title=m[0]))
		else: print('  {t.normal}{title}'.format(t=term, title=m[0]))
		
def clear(term, showHeader, showFooter, title, subtitle, middle):
	print (term.home() + term.clear())
	if (showHeader):
		setHeader(term, title, subtitle)
		fixHeight(4)
	if (showFooter): setFooter(term, helper.getMenuInformation(), term.height - 1)	
	if (middle != None): setMiddle(term, title, middle)

def setHeader(term, title, subtitle):
	with term.location(0, 4):
		print(term.white_on_darkgray(term.ljust(' ')))
		print(term.white_on_darkgray(term.center(term.bold('   {}'.format(title)))))
		print(term.white_on_darkgray(term.center('   {}'.format(subtitle))))
		print(term.white_on_darkgray(term.ljust(' ')))

def setMiddle(term, title, middle):
	for x in middle:
		print(x)

def setFooter(term, listOfText, location):
	with term.location(0, location):
		print(term.white_on_darkgray(term.ljust(' ')))
		for x in listOfText: print(term.white_on_darkgray(term.ljust('   ' + x)))
		print(term.white_on_darkgray(term.ljust(' ')))



# helper
# ---------------------------------------------------------------------

def getLength(term, middleText):

	length = 5
	if (middleText != None):
		length += len(middleText) + 1 # all rows + an extra row for prettier formatting
		for text in middleText:
			length += int((len(text) - 1) / term.width)	# extra row if text goes to new line
	return length

def getDefaultFormat():
	return { 'addTopSpace': False }

def fixHeight(length):
	for x in range(length):
		print()

def getReturnButton(type):

	menuFormat = getDefaultFormat()
	menuFormat['addTopSpace'] = True

	if (type == 0):
		return ["Back", False, menuFormat ]
	elif (type == 1):
		return ["Exit", exit, menuFormat ]
	elif (type == 2):
		return ["Cancel", False, menuFormat ]


def exit(term):
	exit = askUserYesOrNo(term, True, True, 'Main menu', ['Are you sure you want to exit?'], True, False, False, False)
	if (exit):
		raise SystemExit