from pyroute2 import RemoteIPRoute


def make_spec(node, config):
    if '@' in node:
        username, hostname = node.split('@')
    else:
        username = config['ssh_user']
        hostname = node
    return (node, {'class': RemoteIPRoute,
                   'persistent': False,
                   'protocol': 'ssh',
                   'hostname': hostname,
                   'username': username,
                   'identity_file': config['ssh_key'],
                   'check_host_keys': 'ignore'})
