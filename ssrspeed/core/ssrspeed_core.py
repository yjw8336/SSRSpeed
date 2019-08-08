#coding:utf-8

#TODO: Code Refactor Stage 2: Automatic identification of proxy types

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

from ..config_parser import ShadowsocksParser as SSParser
from ..config_parser import ShadowsocksRParser as SSRParser
from ..config_parser import V2RayParser

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
		self.subscriptionUrl = ""
		self.configFile = ""
		
		self.__timeStampStart = -1
		self.__timeStampStop = -1
		self.__client = None
		self.__parser = None
		self.__stc = None
		self.__platformInfo = check_platform()
		self.__results = []
		self.__status = "stopped"
	
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

	def consoleReadSubscription(self, url):
		if (self.__parser):
			self.__parser.readSubscriptionConfig(url)

	def consoleReadFileConfigs(self, filename):
		if (self.__parser):
			self.__parser.readGuiConfig(filename)


	def startTest(self):
		self.__timeStampStart = time.time()
		self.__stc = SpeedTest(self.__parser, self.__client,self.testMethod)
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

	def __getParserByProxyType(self,proxyType):
		if (proxyType == "SSR" or proxyType == "SSR-C#"):
			return SSRParser()
		elif(proxyType == "SS"):
			return SSParser()
		elif(proxyType == "V2RAY"):
			return V2RayParser()

	def __getClientByProxyType(self,proxyType):
		if (proxyType == "SSR"):
			return SSRClient()
		elif (proxyType == "SSR-C#"):
			client = SSRClient()
			client.useSsrCSharp = True
			return client
		elif(proxyType == "SS"):
			return SSClient()
		elif(proxyType == "V2RAY"):
			return V2RayClient()

	def cleanResults(self):
		self.__results = []
		if (self.__stc):
			self.__stc.resetStatus()

	def getResults(self):
		return self.__results

	def webGetResults(self):
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
	
	def __readNodes(self):
		self.__parser.cleanConfigs()
		if (self.configFile):
			self.__parser.readGuiConfig(self.configFile)
		elif(self.subscriptionUrl):
			self.__parser.readSubscriptionConfig(self.subscriptionUrl)
		else:
			logger.critical("No config.")
			sys.exit(1)
	
	def filterNodes(self,fk=[],fgk=[],frk=[],ek=[],egk=[],erk=[]):
		self.__parser.excludeNode([],[],config["excludeRemarks"])
		self.__parser.filterNode(fk,fgk,frk)
		self.__parser.excludeNode(ek,egk,erk)
	#	print(len(self.__parser.getAllConfig()))
		self.__parser.printNode()
		logger.info("{} node(s) will be test.".format(len(self.__parser.getAllConfig())))

	def importAndExport(self,filename,split=0):
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



