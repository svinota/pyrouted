from pyroute2 import RemoteIPRoute


def make_spec(node, config):
    if '@' in node:
        username, node = node.split('@')
    else:
        username = config['user']
    return (node, {'class': RemoteIPRoute,
                   'persistent': False,
                   'protocol': 'ssh',
                   'hostname': node,
                   'username': username,
                   'identity_file': config['ssh_key'],
                   'check_host_keys': 'ignore'})
