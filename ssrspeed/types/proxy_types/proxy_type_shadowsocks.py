# -*- coding: utf-8 -*-

from SSRSpeed.types.proxy_types.proxy_type_base import ProxyTypeBase

class ProxyTypeShadowsocks(ProxyTypeBase):
	def __init__(self):
		super(ProxyTypeShadowsocks, self).__init__()
		self.type = "Shadowsocks"
		self.desc = "SS"