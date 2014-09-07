import io
import json
import struct
from pyrouted.commands import Namespace
from pyroute2.netlink import NLMSG_TRANSPORT
from pyroute2.netlink import Marshal as NetlinkMarshal
from pyroute2.netlink.generic import cdatamsg

# re-export commands namespace (temporarily)
Commands = Namespace


##
# default JSON encoder
#
def default_encoder(obj):
    if isinstance(obj, set):
        return list(obj)
    else:
        return str(type(obj))


##
# main transport class
#
class Transport(object):
    '''
    Pyrouted transport protocol. It consists of two
    parts -- transport layer, methods `get()` and
    `put()`, and data marshalling, methods `loads()`
    and `dumps()`

    Right now it is JSON serialisation packet into
    netlink, but could be anything else as well.

    Transport object should be instantiated with an
    open SOCK_STREAM client connection. It doesn't
    close the socket upon the object destruction, it
    has nothing to do with fd management. Just a
    protocol implementation.
    '''

    def __init__(self, sock, marshal=json):
        self.sock = sock
        self.marshal = marshal
        self.netlink = NetlinkMarshal()
        self.netlink.msg_map = {NLMSG_TRANSPORT: cdatamsg}

    def loads(self, data):
        '''
        Load marshalled data from a string.
        '''
        return self.marshal.loads(data)

    def dumps(self, data):
        '''
        Dumps a structure to a string.
        '''
        return self.marshal.dumps(data, default=default_encoder)

    def get(self):
        '''
        Get the next message from a stream and return
        incapsulated data.
        '''
        # prepare I/O buffer
        data = io.BytesIO()
        # get the message length
        data.length = data.write(self.sock.recv(4))
        length = struct.unpack('I', data.getvalue())[0]
        # get the message
        data.length += data.write(self.sock.recv(length - 4))
        # parse the netlink layer -- there will be only one message
        msg = self.netlink.parse(data)[0]
        # get the data
        return self.loads(msg.get_attr('IPR_ATTR_CDATA'))

    def put(self, data):
        '''
        Marshal provided data end send it to the stream.
        '''
        # prepare the message
        msg = cdatamsg()
        # set the message type
        msg['header']['type'] = NLMSG_TRANSPORT
        # incapsulate the data
        msg['attrs'] = [['IPR_ATTR_CDATA', self.dumps(data)]]
        # encode and send
        msg.encode()
        return self.sock.send(msg.buf.getvalue())
