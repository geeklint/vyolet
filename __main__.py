'''
    Copyright (c) 2013 Sky Leonard
    This file is part of Vyolet.

    Vyolet is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Vyolet is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Vyolet.  If not, see <http://www.gnu.org/licenses/>.
'''

import argparse
import os
import platform
import sys

from version import Version

APP_NAME = 'Vyolet'
VERSION = (0, 0, 'dev')

def default_dir():
    system = platform.system()
    if system == 'Darwin':
        return os.path.expanduser('~/Library/Vyolet')
    elif system == 'Windows':
        return os.path.expandvars('%APPDATA%')
    else:
        return os.path.expanduser('~/.vyolet')


ARGS = {
    '--server': {
        'help': 'run standalone server',
        'action': 'store_true',
    },
    '--nogui': {
        'help': 'do not launch server gui',
        'action': 'store_true',
    },
    '--rootdir': {
        'help': 'root directory for game files',
        'action': 'store',
        'default': default_dir()
    },
}

def main():
    version = Version(APP_NAME, VERSION)
    parser = argparse.ArgumentParser()
    for arg in ARGS:
        parser.add_argument(arg, **ARGS[arg])
    options = parser.parse_args()
    if not os.path.isdir(options.rootdir):
        os.makedirs(options.rootdir)
    os.chdir(options.rootdir)
    if options.server:
        pass
#         import servermain
#         return servermain.main(version)
    else:
        import clientmain
        return clientmain.main(version)


if __name__ == '__main__':
    sys.exit(main())

