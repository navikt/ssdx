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
	showMenuItems(term, subMenus, 0, False, 'Main menu')

def display_screen(term, items, selection, subtitle):
	
	menuHelper.clear(term, True, True, title, subtitle)
	with term.location(0, 5):
		for (idx, m) in enumerate(items):
			if (m[2]['addTopSpace']):
				print()
			if idx == selection:
				print('> {t.bold_yellow}{title}'.format(t=term, title=m[0]))
			else:
				print('  {t.normal}{title}'.format(t=term, title=m[0]))

def showMenuItems(term, items, selection, isSubMenu, subtitle):
	
	with term.fullscreen():
		display_screen(term, items, selection, subtitle)
		selection_inprogress = True
		with term.cbreak():
			while selection_inprogress:
				key = term.inkey()
				if key.is_sequence:
					if key.name == 'KEY_TAB':
						selection += 1
					if key.name == 'KEY_DOWN':
						selection += 1
					if key.name == 'KEY_UP':
						selection -= 1
					if key.name == 'KEY_ENTER':
						selection_inprogress = False
				selection = selection % len(items)
				display_screen(term, items, selection, subtitle)

		shouldContinue = runSelection(term, items, selection)
		
		if (shouldContinue):
			showMenuItems(term, items, selection, isSubMenu, subtitle)


def runSelection(term, items, selection):
	
	item = items[selection]

	# call function if item is function
	if (callable(item[1])):
		menuHelper.clear(term, True, True, title, item[0])
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

	submenu.append(["Pull changes", source.pull, menuFormat])
	submenu.append(["Push changes", source.push, menuFormat])
	submenu.append(["Pull using manifests", source.manifest, menuFormat])

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
