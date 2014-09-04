import sys
import json
from pprint import pprint
from socket import AF_UNIX
from socket import SOCK_DGRAM
from socket import socket

local = b'\x00bala'
remote = b'\x00pyrouted'

call = {'name': 'get_link',
        'argv': sys.argv[1:]}
s = socket(AF_UNIX, SOCK_DGRAM, 0)
s.bind(local)
s.connect(remote)
s.sendto(json.dumps(call), remote)
pprint(json.loads(s.recv(16384)))
