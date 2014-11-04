import os
from pyroute2 import IPDB
from types import MethodType


##
# namespace
#
class Namespace(object):
    '''
    The command namespace -- the main container of all
    pyrouted commands.
    '''
    def __init__(self):
        self.ipdb = IPDB()

    def __call__(self, call):
        return getattr(self, call['name'])(*call.get('argv', []),
                                           **call.get('kwarg', {}))

    def _iscmd(self, command):
        return not command.startswith('_') and \
            isinstance(getattr(self, command), MethodType)

    def list(self):
        '''
        Return the list of all implemented commands.
        '''
        return [x for x in dir(self) if self._iscmd(x)]

    def help(self, command='all'):
        '''
        Return the docstring of the requested command.
        If `command == 'all'`, then return help for all
        implemented commands.
        '''
        ret = []
        if command == 'all':
            for c in dir(self):
                if self._iscmd(c):
                    ret.append(self.help(c))
        else:
            ret = (command, getattr(self, command).__doc__)
        return ret

    def get_env(self):
        '''
        Return the program environment.
        '''
        return dict(os.environ)

    def get_links(self):
        '''
        Get all the links.
        '''
        return [x.dump() for x in self.ipdb.by_index.values()]

    def get_link(self, name='lo'):
        '''
        Get one link.
        '''
        try:
            name = int(name)
        except ValueError:
            pass
        return self.ipdb.interfaces[name].dump()

    def restore(self, name, data):
        '''
        Restore link settings from snapshot
        '''
        interface = self.ipdb.interfaces[name]
        interface.commit(transaction=interface.load(data))
        return interface.dump()
