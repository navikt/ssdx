# -*- coding: utf-8 -*-
# encoding=utf8

from consolemenu.format import *
import os
import re
from consolemenu import *
from consolemenu.items import *
import subscripts.org as org
import subscripts.source as source
import subscripts.helper as helper
import subscripts.other as other
import subscripts.user as user




so = helper.col(helper.getDefaultScratchOrg(), [helper.c.y])
pr = helper.col(helper.getDefaultDevhub(), [helper.c.y])

title = "SSDX Helper"

menu_format = MenuFormatBuilder().set_border_style_type(MenuBorderStyleType.HEAVY_BORDER).set_prompt(" > ").set_title_align(
	'center').set_subtitle_align('center').set_left_margin(2).set_right_margin(10).show_header_bottom_border(True).show_prologue_bottom_border(True)

sub_menu_format = MenuFormatBuilder().set_border_style_type(MenuBorderStyleType.HEAVY_BORDER).set_prompt(" > ").set_title_align(
	'center').set_subtitle_align('center').set_left_margin(2).set_right_margin(10).show_header_bottom_border(True)

def createMenu(mainMenu):
	return ConsoleMenu(title=title, formatter=menu_format, show_exit_option=False)

def createOrgSubMenu(mainMenu):
	
	submenu = ConsoleMenu("Org Related Commands", formatter=sub_menu_format, show_exit_option=False)
	
	createScratchOrg = FunctionItem("CREATE Scratch Org", org.createScratchOrg, kwargs={"mainMenu": mainMenu})
	openScratchOrg = FunctionItem("OPEN Scratch Org", org.openScratchOrg, kwargs={"mainMenu": mainMenu})
	seeScratchOrg = FunctionItem("STATUS of Scratch Org", org.seeScratchOrgStatus, kwargs={"mainMenu": mainMenu})
	changeScratchOrg = FunctionItem("CHANGE Scratch Org", org.changeDefaultScratchOrg, kwargs={"mainMenu": mainMenu})
	deleteScratchOrg = FunctionItem("DELETE Scratch Org", org.deleteScratchOrg, kwargs={"mainMenu": mainMenu})
	changeOrg = FunctionItem("CHANGE default org", org.changeDefaultOrg, kwargs={"mainMenu": mainMenu})
	login = FunctionItem("LOGIN to org", org.login, kwargs={"mainMenu": mainMenu})

	exit = ExitItem("RETURN", mainMenu)
	sub_menu_format.show_item_top_border(exit.text, True)
	sub_menu_format.show_item_top_border(changeOrg.text, True)


	submenu.append_item(createScratchOrg)
	submenu.append_item(openScratchOrg)
	submenu.append_item(seeScratchOrg)
	submenu.append_item(changeScratchOrg)
	submenu.append_item(deleteScratchOrg)
	submenu.append_item(changeOrg)
	submenu.append_item(login)
	submenu.append_item(exit)


	subMenu = SubmenuItem("Org", submenu=submenu, menu=mainMenu)
	menu_format.show_item_top_border(subMenu.text, True)

	return [createScratchOrg, openScratchOrg, seeScratchOrg, changeScratchOrg], subMenu

def createSourceSubMenu(mainMenu):
	
	submenu = ConsoleMenu("Source Related Commands", formatter=sub_menu_format, show_exit_option=False)
	
	pull = FunctionItem("PULL changes", source.pull, kwargs={"mainMenu": mainMenu})
	push = FunctionItem("PUSH changes", source.push, kwargs={"mainMenu": mainMenu})
	manifest = FunctionItem("PULL from manifest", source.manifest, kwargs={"mainMenu": mainMenu})

	exit = ExitItem("RETURN", mainMenu)
	sub_menu_format.show_item_top_border(exit.text, True)

	submenu.append_item(pull)
	submenu.append_item(push)
	submenu.append_item(manifest)
	submenu.append_item(exit)

	subMenu = SubmenuItem("Source", submenu=submenu, menu=mainMenu)

	return [pull, push], subMenu

def createUserSubMenu(mainMenu):
	
	submenu = ConsoleMenu("User Related Commands", formatter=sub_menu_format, show_exit_option=False)
	
	create = FunctionItem("CREATE user", user.create, kwargs={"mainMenu": mainMenu})

	exit = ExitItem("RETURN", mainMenu)
	sub_menu_format.show_item_top_border(exit.text, True)

	submenu.append_item(create)
	submenu.append_item(exit)

	subMenu = SubmenuItem("User", submenu=submenu, menu=mainMenu)

	return [create], subMenu



def createOtherSubMenu(mainMenu):
	
	submenu = ConsoleMenu("Other Commands", formatter=sub_menu_format, show_exit_option=False)
	
	packageKey = FunctionItem("Add Package Key", other.createPackageKey, kwargs={"mainMenu": mainMenu})

	exit = ExitItem("RETURN", mainMenu)
	sub_menu_format.show_item_top_border(exit.text, True)

	submenu.append_item(packageKey)
	submenu.append_item(exit)

	subMenu = SubmenuItem("Other", submenu=submenu, menu=mainMenu)

	return [], subMenu

def createMenuItems(mainMenu):

	orgMenu = createOrgSubMenu(mainMenu)
	for x in orgMenu[0]:
		mainMenu.append_item(x)

	sourceMenu = createSourceSubMenu(mainMenu)
	for x in sourceMenu[0]:
		mainMenu.append_item(x)

	userMenu = createUserSubMenu(mainMenu)
	for x in userMenu[0]:
		mainMenu.append_item(x)

	otherMenu = createOtherSubMenu(mainMenu)

	mainMenu.append_item(orgMenu[1])
	mainMenu.append_item(sourceMenu[1])
	mainMenu.append_item(userMenu[1])
	mainMenu.append_item(otherMenu[1])