# -*- coding: utf-8 -*-

import time
import asyncio
import aiohttp
from aiohttp_socks import SocksVer, SocksError, SocksConnector, SocksConnectionError

STOP_TASK = False
BUFFER_SIZE = 4096
TOTAL_RED = 0
DELTA_RED = 0
START_TIME = -1
STATISTICS_TIME = -1
TIME_USED = 0
count = 0

async def fetch(url: str, i: int):
	global TOTAL_RED, STOP_TASK, TIME_USED, STATISTICS_TIME
	print(f"{i}: Creating connector.")
	connector = SocksConnector(
		socks_ver = SocksVer.SOCKS5,
		host = "127.0.0.1",
		port = 1080,
		rdns = True
	)
	print(f"{i}: Connector created.")
	async with aiohttp.ClientSession(connector=connector) as session:
		print(f"{i}: Session created")
		print(f"{i}: Awaiting response.")
		async with session.get(url) as response:
			while not STOP_TASK:
				chunk = await response.content.read(BUFFER_SIZE)
				if not chunk:
					STOP_TASK = True
					print(f"{i} No chunk.")
					break
				TOTAL_RED += len(chunk)
				TIME_USED = time.time() - START_TIME
				if TIME_USED >= 10:
					STOP_TASK = True
					print(f"{i} Task time up.")
					break
				if time.time() - STATISTICS_TIME > 0.5:
					STATISTICS_TIME = time.time()
					await statistics()


async def statistics():
	global DELTA_RED
	print(f"Current Speed = {(TOTAL_RED - DELTA_RED) / 1024 / 1024 / 0.5} MB/s")
	DELTA_RED = TOTAL_RED

if __name__ == "__main__":
	loop = asyncio.new_event_loop()
	task_list = []
	for i in range(0, 5):
		task_list.append(
			loop.create_task(
				fetch(
					"https://dl.google.com/dl/android/studio/install/3.4.1.0/android-studio-ide-183.5522156-windows.exe",
					i
				)
			)
		)
	#task_list.append(loop.create_task(statistics()))
	print("Starting Event Loop.")
	START_TIME = time.time()
	loop.run_until_complete(asyncio.wait(task_list))
	loop.close()
	mb_red = TOTAL_RED / 1024 / 1024
	print(f"Downloaded data: {mb_red} MB")
	print(f"AvgSpeed: {mb_red / TIME_USED} MB/s")


