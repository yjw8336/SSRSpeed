# -*- coding: utf-8 -*-

from SSRSpeed.types.node_types.node_type_base import NodeTypeBase
from SSRSpeed.types.proxy_types.proxy_type_shadowsocks import ProxyTypeShadowsocks

class NodeShadowsocks(NodeTypeBase):
	def __init__(self):
		super(NodeShadowsocks, self).__init__()
		self.type = ProxyTypeShadowsocks()
	
		
