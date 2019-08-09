# -*- coding: utf-8 -*-

import binascii
from copy import deepcopy
import logging
import requests

from ..utils import b64plus
from ..types.nodes import NodeShadowsocks, NodeShadowsocksR, NodeV2Ray
from .base_configs import shadowsocks_get_config, V2RayBaseConfigs
from .shadowsocks_parsers import ParserShadowsocksBasic, ParserShadowsocksSIP002, ParserShadowsocksD
from .shadowsocksr_parsers import ParserShadowsocksR
from .v2ray_parsers import ParserV2RayN, ParserV2RayQuantumult
from .clash_parser import ParserClash

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

	def parse_links(self, links: list):
		#Single link parse
		result = []
		for link in links:
			node = None
			if link[:5] == "ss://":
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

			elif link[:6] == "ssr://":
				#ShadowsocksR
				pssr = ParserShadowsocksR(self.__get_ss_base_config())
				cfg = pssr.parse_single_link(link)
				if cfg:
					node = NodeShadowsocksR(cfg)
				else:
					logger.warn(f"Invalid shadowsocksR link {link}")

			elif link[:8] == "vmess://":
				#Vmess link (V2RayN and Quan)
				#V2RayN Parser
				cfg = None
				logger.info("Try V2RayN Parser.")
				pv2rn = ParserV2RayN()
				try:
					cfg = pv2rn.parseSubsConfig(link)
				except ValueError:
					pass
				if not cfg:
					#Quantumult Parser
					logger.info("Try Quantumult Parser.")
					pq = ParserV2RayQuantumult()
					try:
						cfg = pq.parseSubsConfig(link)
					except ValueError:
						pass
				if not cfg:
					logger.error("Parse link {} failed.".format(link))
				else:
					gen_cfg = V2RayBaseConfigs.generate_config(cfg, LOCAL_ADDRESS, LOCAL_PORT)
					node = NodeV2Ray(gen_cfg)
			else:
				logger.warn(f"Unsupport link: {link}")

			if node:
				result.append(node)

		return result

	def __parse_clash(self, clash_cfg: str) -> list:
		result = []
		pc = ParserClash(shadowsocks_get_config(LOCAL_ADDRESS, LOCAL_PORT, TIMEOUT))
		pc.parse_config(clash_cfg)
		cfgs = pc.config_list
		for cfg in cfgs:
			if cfg["type"] == "ss":
				result.append(NodeShadowsocks(cfg["config"]))
			elif cfg["type"] == "vmess":
				result.append(
					NodeV2Ray(
						V2RayBaseConfigs.generate_config(cfg["config"], LOCAL_ADDRESS, LOCAL_PORT)
					)
				)

		return result
	
	def print_nodes(self):
		for item in self.nodes:
			logger.info(
				"{} - {}".format(
					item.config["group"],
					item.config["remarks"]
				)
			)
		print(self.__nodes[0].config)
		print(f"{len(self.__nodes)} node(s) in list.")

	def read_subscription(self, url: str):
		header = {
			"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
		}
		rep = requests.get(url,headers = header, timeout=15)
		rep.encoding = "utf-8"
		rep = rep.content.decode("utf-8")

		parsed = False
		#Try ShadowsocksD Parser
		if rep[:6] == "ssd://":
			parsed = True
			logger.info("Try ShadowsocksD Parser.")
			pssd = ParserShadowsocksD(shadowsocks_get_config(LOCAL_ADDRESS, LOCAL_PORT, TIMEOUT))
			cfgs = pssd.parseSubsConfig(b64plus.decode(rep[6:]).decode("utf-8"))
			for cfg in cfgs:
				self.__nodes.append(NodeShadowsocks(cfg))
		if parsed: return

		#Try base64 decode
		try:
			rep = rep.strip()
			logger.info("Try Shadowsocks Basic Parser.")
			links = (b64plus.decode(rep).decode("utf-8")).split("\n")
			logger.debug("Base64 decode success.")
			self.__nodes = self.parse_links(links)
		except binascii.Error:
			logger.info("Base64 decode failed.")
		if parsed: return

		#Try Clash Parser
		self.__nodes = self.__parse_clash(rep)
		
