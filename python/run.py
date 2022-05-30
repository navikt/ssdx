# -*- coding: utf-8 -*-
# encoding=utf8

import subscripts.menu as menu

if __name__ == '__main__':
	term = menu.init()
	if len(sys.argv) > 1:
		param_name = sys.argv[1]
		if (param_name == "co"):
			menu.org.createScratchOrg(term)
			sys.exit()
	menu.show(term)




	