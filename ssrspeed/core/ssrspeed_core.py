#coding:utf-8

#Code Refactor Stage 2: Automatic identification of proxy types
#Proxy Type Identification Done.
#TODO: Automatic client selection.

import time
import logging
import json
import threading
import sys
import os

logger = logging.getLogger("Sub")

from ..client_launcher import ShadowsocksClient as SSClient
from ..client_launcher import ShadowsocksRClient as SSRClient
from ..client_launcher import V2RayClient

from ..config_parser import UniversalParser

from ..result import ExportResult
from ..result import importResult
from ..result import Sorter

from ..speed_test import SpeedTest
from ..utils import check_platform

from config import config

class SSRSpeedCore(object):
	def __init__(self):
		
		self.testMethod = "SOCKET"
		self.proxyType = "SSR"
		self.webMode = False
		self.colors = "origin"
		self.sortMethod = ""
		self.testMode = "TCP_PING"
		
		self.__timeStampStart = -1
		self.__timeStampStop = -1
		self.__parser = UniversalParser()
		self.__stc = None
		self.__results = []
		self.__status = "stopped"

	'''
	def webGetColors(self):
		return config["exportResult"]["colors"]
	
	def webGetStatus(self):
		return self.__status
	
	
	def webReadSubscription(self,url,proxyType):
		parser = self.__getParserByProxyType(proxyType)
		if (parser):
			parser.readSubscriptionConfig(url)
			return parser.getAllConfig()
		return []

	def webReadFileConfigs(self, filename, proxyType):
		parser = self.__getParserByProxyType(proxyType)
		if parser:
			parser.readGuiConfig(filename)
			return parser.getAllConfig()
		return []
	
	def webSetup(self,**kwargs):
		self.testMethod = kwargs.get("testMethod","SOCKET")
		self.proxyType = kwargs.get("proxyType","SSR")
		self.colors = kwargs.get("colors","origin")
		self.sortMethod = kwargs.get("sortMethod","")
		self.testMode = kwargs.get("testMode","TCP_PING")
		self.__parser = self.__getParserByProxyType(self.proxyType)
		self.__client = self.__getClientByProxyType(self.proxyType)
	

	def webSetConfigs(self,configs):
		if (self.__parser):
			self.__parser.cleanConfigs()
			self.__parser.addConfigs(configs)
	'''
	
	def console_setup(self,
		test_mode: str,
		test_method: str,
		color: str = "origin",
		sort_method: str = "",
		url: str = "",
		cfg_filename: str = ""
	):
		self.testMethod = test_method
		self.testMode = test_mode
		self.sortMethod = sort_method
		self.colors = color
		if self.__parser:
			if cfg_filename:
				self.__parser.read_gui_config(cfg_filename)
			elif url:
				self.__parser.read_subscription(url)
			else:
				raise ValueError("Subscription URL or configuration file must be set !")

	def start_test(self):
		self.__timeStampStart = time.time()
		self.__stc = SpeedTest(self.__parser, self.testMethod)
		self.__status = "running"
		if (self.testMode == "TCP_PING"):
			self.__stc.tcpingOnly()
		elif(self.testMode == "ALL"):
			self.__stc.fullTest()
		elif (self.testMode == "WEB_PAGE_SIMULATION"):
			self.__stc.webPageSimulation()
		self.__status = "stopped"
		self.__results = self.__stc.getResult()
		self.__timeStampStop = time.time()
		self.__exportResult()

	def clean_result(self):
		self.__results = []
		if (self.__stc):
			self.__stc.resetStatus()

	def get_results(self):
		return self.__results

	def web_get_results(self):
		if (self.__status == "running"):
			if (self.__stc):
				status = "running"
			else:
				status = "pending"
		else:
			status = self.__status
		r = {
			"status":status,
			"current":self.__stc.getCurrent() if (self.__stc and status == "running") else {},
			"results":self.__stc.getResult() if (self.__stc) else []
		}
		return r

	def filter_nodes(self, fk=[], fgk=[], frk=[], ek=[], egk=[], erk=[]):
	#	self.__parser.excludeNode([],[],config["excludeRemarks"])
		self.__parser.filter_nodes(fk, fgk, frk, ek, egk, erk + config["excludeRemarks"])
		self.__parser.print_nodes()
		logger.info("{} node(s) will be test.".format(len(self.__parser.nodes)))
	

	def import_and_export(self,filename,split=0):
		self.__results = importResult(filename)
		self.__exportResult(split,2)
		self.__results = []

	def __exportResult(self,split = 0,exportType= 0):
		er = ExportResult()
		er.setTimeUsed(self.__timeStampStop - self.__timeStampStart)
		if self.testMode == "WEB_PAGE_SIMULATION":
			er.exportWpsResult(self.__results, exportType)
		else:
			er.setColors(self.colors)
			er.export(self.__results,split,exportType,self.sortMethod)



