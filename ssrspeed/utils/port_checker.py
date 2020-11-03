# -*- coding: utf-8 -*-

import socket

def check_port(port: int):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(3)
	s.connect(("192.168.2.191", port))
	s.shutdown(2)

