import io
import json
import struct
from socket import MSG_PEEK
from pyrouted.commands import Namespace
from pyroute2.netlink import NLMSG_TRANSPORT
from pyroute2.netlink import Marshal as NetlinkMarshal
from pyroute2.netlink.generic import cdatamsg

try:
    from http.client import parse_headers as Headers
except ImportError:
    from mimetools import Message as Headers

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
        self.proto = 'netlink'
        self.rfile = sock.makefile('rb')
        self.wfile = sock.makefile('wb')
        self.marshal = marshal
        self.netlink = NetlinkMarshal()
        self.netlink.msg_map = {NLMSG_TRANSPORT: cdatamsg}

    def release(self):
        self.rfile.close()
        self.wfile.close()

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
        # get the message length or type
        init = self.sock.recv(4, MSG_PEEK)
        # POST -- request, server side
        # HTTP -- response, client side
        if str(init) in ('POST', 'HTTP'):
            # set proto -- ignored by the client
            self.proto = 'http_server'
            # get & dismiss the request line
            self.rfile.readline()
            # parse headers
            headers = Headers(self.rfile)
            # get the length
            length = int(headers.getheader('content-length', 0))
            # read the data
            data = self.rfile.read(length)
        else:
            # set proto
            self.proto = 'netlink'
            # get the length
            length = struct.unpack('I', init)[0]
            # get the message
            data.length = data.write(self.sock.recv(length))
            # parse the netlink layer -- there will be only one message
            msg = self.netlink.parse(data)[0]
            # get the data
            data = msg.get_attr('IPR_ATTR_CDATA')
        return self.loads(data)

    def put(self, data):
        '''
        Marshal provided data end send it to the stream.
        '''
        data = self.dumps(data)
        if self.proto.startswith('http'):
            # client side
            if self.proto == 'http':
                # send request
                self.wfile.write(b'POST / HTTP/1.0\n')
                self.wfile.write(b'User-Agent: pyroute-client\n')
            elif self.proto == 'http_server':
                # send response
                self.wfile.write(b'HTTP/1.0 200 OK\n')
                self.wfile.write(b'Server: pyrouted\n')
            # common headers
            self.wfile.write(b'Connection: Close\n')
            self.wfile.write(b'Content-Type: application/json\n')
            self.wfile.write(b'Content-Length: %i\n\n' % (len(data)))
            # send the data
            ret = self.wfile.write(data)
            # don't forget to flush the data!
            self.wfile.flush()
            # FIXME: return len with headers!
            # bytes sent -- only data
            return ret
        elif self.proto == 'netlink':
            # prepare the message
            msg = cdatamsg()
            # set the message type
            msg['header']['type'] = NLMSG_TRANSPORT
            # incapsulate the data
            msg['attrs'] = [['IPR_ATTR_CDATA', data]]
            # encode and send
            msg.encode()
            # bytes sent
            return self.sock.send(msg.buf.getvalue())
