# -*- coding: utf-8 -*-

class ProxyTypeBase(object):
	def __init__(self):
		self.type = ""
		self.desc = ""

	def __eq__(self, other):
		return self.type == other.type
		
