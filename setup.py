#!/usr/bin/env python
from distutils.core import setup

readme = open("README.md", "r")


setup(name='pyrouted',
      version='0.2.4',
      description='Python Network Database',
      author='Peter V. Saveliev',
      author_email='peter@svinota.eu',
      url='https://github.com/svinota/pyrouted',
      license='dual license GPLv2+ and Apache v2',
      packages=['pyrouted', ],
      install_requires=['bottle',
                        'mitogen',
                        'pyroute2 >= 0.5.3'],
      scripts=['src/pyrouted'],
      data_files=[('/lib/systemd/system', ['pyrouted.service', ]),
                  ('/etc/pyrouted', ['pyrouted.conf', ])],
      classifiers=['License :: OSI Approved :: GNU General Public ' +
                   'License v2 or later (GPLv2+)',
                   'License :: OSI Approved :: Apache Software License',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries :: ' +
                   'Python Modules',
                   'Topic :: System :: Networking',
                   'Topic :: System :: Systems Administration',
                   'Operating System :: POSIX :: Linux',
                   'Intended Audience :: Developers',
                   'Intended Audience :: System Administrators',
                   'Intended Audience :: Telecommunications Industry',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Development Status :: 4 - Beta'],
      long_description=readme.read())
