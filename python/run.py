# -*- coding: utf-8 -*-
# encoding=utf8

import os
import subscripts.menu as menu
import subscripts.helper as helper
from blessed import Terminal

if __name__ == '__main__':
	term = menu.init()
	menu.show(term)
	