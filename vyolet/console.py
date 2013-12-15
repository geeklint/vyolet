'''
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
import shlex
import threading
try:
    import readline
except ImportError:
    readline = None


class FallbackConsole(threading.Thread):

    def __init__(self):
        super(FallbackConsole, self).__init__()
        self.daemon = True
        self.prompt = '> '
        self.callback = lambda cmd: None
        self.start()

    def printf(self, fmt, *args, **kwargs):
        print ''.join(('\r', fmt.format(*args, **kwargs)))
        print self.prompt

    def run(self):
        while True:
            try:
                cmd_str = raw_input(self.prompt)
            except EOFError:
                cmd_str = 'stop'
            try:
                cmd = shlex.split(cmd_str)
            except ValueError:
                print 'Could not understand'
            else:
                if cmd:
                    self.callback(cmd)



class ReadlineConsole(FallbackConsole):
    def printf(self, fmt, *args, **kwargs):
        super(ReadlineConsole, self).printf(fmt, *args, **kwargs)
        readline.redisplay()


if True:  # readline is None:
    console = FallbackConsole()
else:
    console = ReadlineConsole()
