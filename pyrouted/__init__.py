import io
import json
import struct
from pyroute2.netlink import NLMSG_TRANSPORT
from pyroute2.netlink import Marshal
from pyroute2.netlink.generic import cdatamsg


##
# default JSON encoder
#
def default_encoder(obj):
    if isinstance(obj, set):
        return list(obj)
    else:
        return str(type(obj))


class Transport(object):
    '''
    Pyrouted transport protocol. It consists of two
    parts -- transport layer, methods `get()` and
    `put()`, and data marshalling, methods `loads()`
    and `dumps()`

    Right now it is JSON serialisation packet into
    netlink, but could be anything else as well.
    '''

    def __init__(self, sock):
        self.sock = sock
        self.marshal = Marshal()
        self.marshal.msg_map = {NLMSG_TRANSPORT: cdatamsg}

    def loads(self, data):
        return json.loads(data)

    def dumps(self, data):
        return json.dumps(data, default=default_encoder)

    def get(self):
        # prepare I/O buffer
        data = io.BytesIO()
        # get the message length
        data.length = data.write(self.sock.recv(4))
        length = struct.unpack('I', data.getvalue())[0]
        # get the message
        data.length += data.write(self.sock.recv(length - 4))
        # parse the netlink layer -- there will be only one message
        msg = self.marshal.parse(data)[0]
        # get the data
        return self.loads(msg.get_attr('IPR_ATTR_CDATA'))

    def put(self, data):
        # prepare the message
        msg = cdatamsg()
        # set the message type
        msg['header']['type'] = NLMSG_TRANSPORT
        # incapsulate the data
        msg['attrs'] = [['IPR_ATTR_CDATA', self.dumps(data)]]
        # encode and send
        msg.encode()
        return self.sock.send(msg.buf.getvalue())
