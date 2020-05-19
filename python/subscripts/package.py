# -*- coding: utf-8 -*-
# encoding=utf8

import subscripts.helper as helper
import subscripts.orgHelper as orgHelper

title = "SSDX Helper"

def reinstall(term):
	results, retry = [True, []], True
	while results[0] and retry:
		results = orgHelper.createScratchOrg_installPackages()
		retry = orgHelper.retry(term, results)
	if (results[0] and not retry): return True
