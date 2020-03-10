# -*- coding: utf-8 -*-
# encoding=utf8

import subscripts.org as org
import subscripts.source as source
import subscripts.helper as helper
import subscripts.menuHelper as menuHelper
import subscripts.other as other
import subscripts.user as user
from blessed import Terminal

title = "SSDX Helper"

def init():
	term = Terminal()
	term.hidden_cursor() 
	return term

def show(term):
	subMenus = getSubMenus(term)

	# with term.fullscreen():
	showMenuItems(term, subMenus, 0, False, 'Main menu')

def showMenuItems(term, items, selection, isSubMenu, subtitle):
	
	selection = menuHelper.giveUserChoices(term, True, True, items, selection, subtitle, None, False)

	shouldContinue = runSelection(term, items, selection)
	
	if (shouldContinue):
		showMenuItems(term, items, selection, isSubMenu, subtitle)


def runSelection(term, items, selection):
	
	item = items[selection]

	# call function if item is function
	if (callable(item[1])):
		menuHelper.clear(term, True, True, title, item[0], None)
		with term.location(0, 5):
			item[1](term)
			return True

	# open list sub menu if item is list
	if isinstance(item[1], list):
		showMenuItems(term, item[1], 0, True, item[0])
		return True

	# return value if item is bool (used for returning from a sub-menu)
	if isinstance(item[1], bool):
		return item[1]

	# fallback of doing nothing, but staying in same submenu
	return True

def getSubMenus(term):
	
	orgMenu = createOrgSubMenu(term)
	sourceMenu = createSourceSubMenu(term)
	userMenu = createUserSubMenu(term)
	otherMenu = createOtherSubMenu(term)

	items = []
	items.append(orgMenu)
	items.append(sourceMenu)
	items.append(userMenu)
	items.append(otherMenu)

	for subMenu in items:
		subMenu[1].append(menuHelper.getBackOrExitButton(True))

	items.append(menuHelper.getBackOrExitButton(False))

	return items
	
def createOrgSubMenu(term):
	
	submenu = []
	menuFormat = menuHelper.getDefaultFormat()

	submenu.append(["Create Scratch Org", org.createScratchOrg, menuFormat])
	submenu.append(["Open Scratch Org", org.openScratchOrg, menuFormat])
	submenu.append(["Status of Scratch Org", org.seeScratchOrgStatus, menuFormat])
	submenu.append(["Change Default Scratch Org", org.changeDefaultScratchOrg, menuFormat])
	submenu.append(["Delete Scratch Orgs", org.deleteScratchOrg, menuFormat])
	submenu.append(["Change Default Org", org.changeDefaultOrg, menuFormat])
	submenu.append(["Login to Org", org.login, menuFormat])

	return "Org Related Commands", submenu, menuFormat

def createSourceSubMenu(term):
	
	menuFormat = menuHelper.getDefaultFormat()
	submenu = []

	submenu.append(["Pull Metadata", source.pull, menuFormat])
	submenu.append(["Push Metadata", source.push, menuFormat])
	submenu.append(["Pull Metadata (manifest)", source.manifest, menuFormat])

	return "Source Related Commands", submenu, menuFormat

def createUserSubMenu(term):
	
	menuFormat = menuHelper.getDefaultFormat()
	submenu = []

	submenu.append(["Create user", user.create, menuFormat])
	return "User Related Commands", submenu, menuFormat

def createOtherSubMenu(term):
	
	menuFormat = menuHelper.getDefaultFormat()
	submenu = []

	submenu.append(["Add Package Key", other.createPackageKey, menuFormat])
	return "Other Commands", submenu, menuFormat
