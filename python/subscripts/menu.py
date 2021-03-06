# -*- coding: utf-8 -*-
# encoding=utf8

import subscripts.org as org
import subscripts.source as source
import subscripts.package as package
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

	# with term.fullscreen(): # ! Removed to be able to scroll to see more data when needed
	showMenuItems(term, subMenus, 0, False, 'Main menu')

def showMenuItems(term, items, selection, isSubMenu, subtitle):
	
	selection = menuHelper.giveUserChoices(term=term, showHeader=True, showFooter=True, items=items, selection=selection, subtitle=subtitle, middleText=None, printAtBottom=False)
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
	
	items = []
	items.append(createOrgSubMenu(term))
	items.append(createSourceSubMenu(term))
	items.append(createPackageSubMenu(term))
	items.append(createUserSubMenu(term))
	items.append(createOtherSubMenu(term))

	for subMenu in items:
		subMenu[1].append(menuHelper.getReturnButton(0))

	items.append(menuHelper.getReturnButton(1))

	return items
	
def createOrgSubMenu(term):
	
	submenu = []
	menuFormat = menuHelper.getDefaultFormat()
	menuFormatWithSpace = menuHelper.getDefaultFormat()
	menuFormatWithSpace['addTopSpace'] = True

	submenu.append(["Create Scratch Org", org.createScratchOrg, menuFormat])
	submenu.append(["Open Scratch Org", org.openScratchOrg, menuFormat])
	submenu.append(["Open Scratch Org (specify browser)", org.openScratchOrgSpecificBrowser, menuFormat])
	
	submenu.append(["Status of Scratch Org", org.seeScratchOrgStatus, menuFormatWithSpace])
	submenu.append(["Delete Scratch Orgs", org.deleteScratchOrg, menuFormat])
	submenu.append(["Change Default Scratch Org", org.changeDefaultScratchOrg, menuFormat])
	
	submenu.append(["Change Default Org", org.changeDefaultOrg, menuFormatWithSpace])
	submenu.append(["Login to Org", org.login, menuFormat])
	

	return "Org Related Commands", submenu, menuFormat

def createSourceSubMenu(term):

	menuFormat = menuHelper.getDefaultFormat()
	menuFormatWithSpace = menuHelper.getDefaultFormat()
	menuFormatWithSpace['addTopSpace'] = True
	
	submenu = []

	submenu.append(["Pull Metadata", source.pull, menuFormat])
	submenu.append(["Push Metadata", source.push, menuFormat])
	
	submenu.append(["Pull Metadata (manifest)", source.manifest, menuFormatWithSpace])

	return "Source Related Commands", submenu, menuFormat

def createPackageSubMenu(term):
	menuFormat = menuHelper.getDefaultFormat()
	menuFormatWithSpace = menuHelper.getDefaultFormat()
	menuFormatWithSpace['addTopSpace'] = True
	
	submenu = []

	submenu.append(["Re-Install Packages", package.reinstall, menuFormat])

	return "Package Related Commands", submenu, menuFormatWithSpace

def createUserSubMenu(term):
	
	menuFormat = menuHelper.getDefaultFormat()
	submenu = []

	submenu.append(["Create user", user.create, menuFormat])
	return "User Related Commands", submenu, menuFormat

def createOtherSubMenu(term):
	
	menuFormat = menuHelper.getDefaultFormat()
	submenu = []

	submenu.append(["Add Package Key", other.createPackageKey, menuFormat])
	submenu.append(["Re-Import Dummy Data", other.reImportDummyData, menuFormat])
	return "Other Commands", submenu, menuFormat
