# -*- coding: utf-8 -*-

from SSRSpeed.types.proxy_types.proxy_type_base import ProxyTypeBase

class ProxyTypeV2Ray(ProxyTypeBase):
	def __init__(self):
		super(ProxyTypeV2Ray, self).__init__()
		self.type = "V2Ray"
		self.desc = "V2Ray"