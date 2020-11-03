#!/bin/bash

PYTHON="coverage run -p"
URL=http://192.168.2.191/file

mkdir -p tmp

$PYTHON shadowsocks/local.py -c tests/aes.json &
LOCAL=$!

$PYTHON shadowsocks/server.py -c tests/aes.json --forbidden-ip "" &
SERVER=$!

sleep 3

time curl -o tmp/expected $URL
time curl -o tmp/result --socks5-hostname 192.168.2.191:1081 $URL

kill -s SIGINT $LOCAL
kill -s SIGINT $SERVER

sleep 2

diff tmp/expected tmp/result || exit 1
