# -*- coding: utf-8 -*-

import binascii
from copy import deepcopy
import logging
import requests

from ..utils import b64plus
from ..types.nodes import NodeShadowsocks, NodeShadowsocksR, NodeV2Ray
from .base_configs import shadowsocks_get_config, v2ray_get_config
from .shadowsocks_parsers import ParserShadowsocksBasic, ParserShadowsocksSIP002, ParserShadowsocksClash, ParserShadowsocksD
from .shadowsocksr_parsers import ParserShadowsocksR

from config import config
LOCAL_ADDRESS = config["localAddress"]
LOCAL_PORT = config["localPort"]
TIMEOUT = 10

logger = logging.getLogger("Sub")

class UniversalParser:
	def __init__(self):
		self.__nodes = []
		self.__ss_base_cfg = shadowsocks_get_config(LOCAL_ADDRESS, LOCAL_PORT, TIMEOUT)

	@property
	def nodes(self):
		return deepcopy(self.__nodes)

	def __get_ss_base_config(self):
		return deepcopy(self.__ss_base_cfg)

	def parse_subscription(self, url: str):
		header = {
			"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
		}
		rep = requests.get(url,headers = header, timeout=15)
		rep.encoding = "utf-8"
		rep = rep.content.decode("utf-8").strip()

		#Try base64 decode
		try:
			logger.info("Try Shadowsocks Basic Parser.")
			links = (b64plus.decode(rep).decode("utf-8")).split("\n")
			logger.debug("Base64 decode success.")
			#Single link parse
			for link in links:
				node = None
				if link.find("ss://") != -1:
					#Shadowsocks
					cfg = None
					try:
						pssb = ParserShadowsocksBasic(self.__get_ss_base_config())
						cfg = pssb.parse_single_link(link)
					except ValueError:
						pssip002 = ParserShadowsocksSIP002(self.__get_ss_base_config())
						cfg = pssip002.parse_single_link(link)
					if cfg:
						node = NodeShadowsocks(cfg)
					else:
						logger.warn(f"Invalid shadowsocks link {link}")

				elif link.find("ssr://") != -1:
					#ShadowsocksR
					pssr = ParserShadowsocksR(self.__get_ss_base_config())
					cfg = pssr.parse_single_link(link)
					if cfg:
						node = NodeShadowsocksR(cfg)
					else:
						logger.warn(f"Invalid shadowsocksR link {link}")

				elif link.find("vmess://") != -1:
					#Vmess link (V2RayN and Quan)
					#TODO: V2Ray link parse
					pass
				else:
					logger.warn(f"Unsupport link: {link}")

				if node:
					self.__nodes.append(node)
		except binascii.Error:
			logger.info("Base64 decode failed.")
			#Try Clash and ShadowsocksD Parser
