#coding:utf-8

import os
import sys
import time
import json
import logging

logger = logging.getLogger("Sub")

class ExporterWps(object):
	def __init__(self, result):
		self.__results = result

	def export(self):
		filename = "./results/" + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + ".js"
		res = "var res = " + json.dumps(self.__results,sort_keys=True,indent=4,separators=(',',':'))
		with open(filename,"w+",encoding="utf-8") as f:
			f.writelines(res)
			f.close()
		logger.info("Result exported as %s" % filename)

