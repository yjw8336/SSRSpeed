# -*- coding: utf-8 -*-

class NodeTypeBase(object):
	def __init__(self):
		self.server = ""
		self.server_port = 0
		self.remarks = "N/A"
		self.group = "N/A"
		self.local_port = 1087
		self.local_address = "127.0.0.1"
		self.type = None

	def __eq__(self, other):
		return (self.server == other.server and self.server_port == other.server_port)
		
