# -*- coding: utf-8 -*-

from SSRSpeed.types.proxy_types.proxy_type_base import ProxyTypeBase

class ProxyTypeShadowsocksr(ProxyTypeBase):
	def __init__(self):
		super(ProxyTypeShadowsocksr, self).__init__()
		self.type = "ShadowsocksR"
		self.desc = "SSR"