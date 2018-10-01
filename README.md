# pyrouted

Pyroute2 network database: system service

## install

```
$ sudo pip install pyrouted
$ sudo systemctl start pyrouted
$ curl http://localhost:8700/v1/addresses
```

## configuration

```
$ vim /etc/pyrouted/pyrouted.conf
```

What to adjust:

1. service user: `sudo vim /lib/systemd/system/pyrouted.service`
2. access remote systems: check the directory permissions and the SSH key -- see the config file.
3. run the service on a UNIX socket: change `listen` in the configuration file to `/var/run/pyrouted/api`, to access use `curl --unix-socket /var/run/pyrouted/api http://localhost/v1/addresses`
