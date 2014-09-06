import io
import sys
import json
import struct
from pprint import pprint
from socket import AF_UNIX
from socket import SOCK_STREAM
from socket import socket
from pyroute2.netlink import NLMSG_TRANSPORT
from pyroute2.netlink import Marshal
from pyroute2.netlink.generic import cdatamsg

local = b'\x00bala'
remote = b'\x00pyrouted'

call = {'name': 'get_link',
        'argv': sys.argv[1:]}
s = socket(AF_UNIX, SOCK_STREAM, 0)
s.bind(local)
s.connect(remote)

msg = cdatamsg()
msg['header']['type'] = NLMSG_TRANSPORT
msg['attrs'] = [['IPR_ATTR_CDATA', json.dumps(call)]]
msg.encode()
s.send(msg.buf.getvalue())

marshal = Marshal()
marshal.msg_map = {NLMSG_TRANSPORT: cdatamsg}

data = io.BytesIO()
data.length = data.write(s.recv(4))
length = struct.unpack('I', data.getvalue())[0]
data.length += data.write(s.recv(length - 4))
msg = marshal.parse(data)[0]

pprint(json.loads(msg.get_attr('IPR_ATTR_CDATA')))
