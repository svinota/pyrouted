import json
import bottle
from pyrouted.util import make_spec


def route(method, path):
    def decorator(f):
        f.http_route = path
        f.http_method = method
        return f
    return decorator


class APIv1(object):

    prefix = '/v1'

    def __init__(self, ndb, config):
        self.ndb = ndb
        self.config = config

    @route('GET', '/sources')
    def sources_list(self, mode='short'):
        ret = {}
        mode = bottle.request.query.mode or mode
        for name, spec in self.ndb.sources.items():
            ret[name] = {'class': spec.nl.__class__.__name__,
                         'status': spec.status}
            if mode == 'full':
                ret[name]['config'] = spec.nl_kwarg
        return bottle.template('{{!ret}}', ret=json.dumps(ret))

    @route('PUT', '/sources')
    def sources_restart(self):
        node = bottle.request.body.getvalue().decode('utf-8')
        self.ndb.sources[node].start()

    @route('POST', '/sources')
    def sources_add(self):
        data = bottle.request.body.getvalue().decode('utf-8')
        node, spec = make_spec(data, self.config)
        self.config['sources'].append(node)
        self.ndb.connect_source(node, spec)

    @route('DELETE', '/sources')
    def sources_del(self):
        node = bottle.request.body.getvalue().decode('utf-8')
        self.config['sources'].remove(node)
        self.ndb.disconnect_source(node)

    @route('GET', '/config')
    def config_get(self):
        return bottle.template('{{!ret}}',
                               ret=json.dumps(self.config))

    @route('PUT', '/config')
    def config_dump(self):
        path = bottle.request.body.getvalue().decode('utf-8')
        self.config.dump(path)

    @route('GET', '/<name:re:(%s|%s|%s|%s|%s|%s)>' % ('interfaces',
                                                      'addresses',
                                                      'routes',
                                                      'neighbours',
                                                      'vlans',
                                                      'bridges'))
    def view(self, name):
        ret = []
        obj = getattr(self.ndb, name)
        for line in obj.dump():
            ret.append(line)
        return bottle.template('{{!ret}}', ret=json.dumps(ret))

    @route('GET', '/query/<name:re:(%s|%s|%s|%s)>' % ('nodes',
                                                      'p2p_edges',
                                                      'l2_edges',
                                                      'l3_edges'))
    def query(self, name):
        ret = []
        obj = getattr(self.ndb.query, name)
        for line in obj():
            ret.append(line)
        return bottle.template('{{!ret}}', ret=json.dumps(ret))
