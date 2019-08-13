# -*- coding: utf-8 -*-

import time
import copy
import logging
import asyncio
import aiohttp
from aiohttp_socks import SocksVer, SocksError, SocksConnector, SocksConnectionError

logger = logging.getLogger("Sub")

STOP_TASK = False
BUFFER_SIZE = 4096
TOTAL_RED = 0
DELTA_RED = 0
START_TIME = -1
STATISTICS_TIME = -1
TIME_USED = 0
SPEED_LIST = []

async def _fetch(url: str, host: str = "127.0.0.1", port: int = 1087):
	global TOTAL_RED, STOP_TASK, TIME_USED, STATISTICS_TIME
	#print(f"{i}: Creating connector.")
	connector = SocksConnector(
		socks_ver = SocksVer.SOCKS5,
		host = host,
		port = port,
		rdns = True
	)
	#print(f"{i}: Connector created.")
	async with aiohttp.ClientSession(connector=connector, headers={"User-Agent": "curl/11.45.14"}) as session:
		#print(f"{i}: Session created")
		#print(f"{i}: Awaiting response.")
		async with session.get(url) as response:
			while not STOP_TASK:
				chunk = await response.content.read(BUFFER_SIZE)
				if not chunk:
					#STOP_TASK = True
					#print(f"{i} No chunk.")
					break
				TOTAL_RED += len(chunk)
				TIME_USED = time.time() - START_TIME
				if TIME_USED >= 10:
					STOP_TASK = True
					#print(f"{i} Task time up.")
					break
				if time.time() - STATISTICS_TIME > 0.5:
					STATISTICS_TIME = time.time()
					await _statistics()


async def _statistics():
	global DELTA_RED, SPEED_LIST
	speed = (TOTAL_RED - DELTA_RED) / 0.5
	speed_mb = speed / 1024 / 1024
	DELTA_RED = TOTAL_RED
	#print(f"Current Speed = {speed} MB/s, Time used {TIME_USED}s")
	print("\r[" + "=" * int(TIME_USED // 0.5) + "> [{:.2f} MB/s]".format(speed_mb), end='')
	SPEED_LIST.append(speed)

def _init():
	global STOP_TASK, TOTAL_RED, DELTA_RED, START_TIME, STATISTICS_TIME, TIME_USED, SPEED_LIST
	STOP_TASK = False
	TOTAL_RED = 0
	DELTA_RED = 0
	STATISTICS_TIME = -1
	TIME_USED = 0
	SPEED_LIST.clear()
	START_TIME = time.time()

def start(
	url: str,
	proxy_host = "127.0.0.1",
	proxy_port: int = 1087,
	workers: int = 4
	):
	logger.info(f"Running st_async, workers: {workers}")
	loop = asyncio.new_event_loop()
	tasks = []
	#TODO: Rules match
	for i in range(0, workers):
		tasks.append(
			loop.create_task(
				_fetch(url, proxy_host, proxy_port)
			)
		)
	_init()
	loop.run_until_complete(asyncio.wait(tasks))
	loop.close()
	mb_red = TOTAL_RED / 1024 / 1024
	print("\r[" + "=" * int(TIME_USED // 0.5) + "] [{:.2f} MB/s]".format(mb_red / TIME_USED), end='\n')
	logger.info("Fetched {:.2f} MB in {:.2f}s".format(mb_red, TIME_USED))
	tmp_speed_list = copy.deepcopy(SPEED_LIST)
	tmp_speed_list.sort()
	max_speed = 0
	if len(tmp_speed_list) > 12:
		msum = 0
		for i in range(12, len(tmp_speed_list) - 2):
			msum += tmp_speed_list[i]
			max_speed = msum / (len(tmp_speed_list) - 2 - 12)
	else:
		max_speed = TOTAL_RED / TIME_USED
	if TIME_USED:
		return (TOTAL_RED / TIME_USED, max_speed, SPEED_LIST, TOTAL_RED)
	else:
		return (0, 0, [], 0)


