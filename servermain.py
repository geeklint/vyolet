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

import asyncore
import Queue
import threading
from functools import partial

import events
import gameloop
import network
import handler
from console import console


class Listener(asyncore.dispatcher):
    shutdown = False

    def __init__(self, version, queue):
        self.version = version
        self.event_queue = queue
        sock = network.server_connection(network.PORT)
        if sock is None:
            raise ValueError('Could not open connection')
        asyncore.dispatcher.__init__(self, sock=sock)
        self.accepting = True

    def readable(self):
        if self.shutdown:
            while asyncore.socket_map:
                _k, nr = asyncore.socket_map.popitem()
                if isinstance(nr, network.NetworkReciever):
                    nr.sendp.disconnect('Server shutdown')
            raise asyncore.ExitNow
        return asyncore.dispatcher.readable(self)

    def handle_accept(self):
        conn, addr = self.accept()
        console.printf('Connected by {}', repr(addr))
        nr = network.NetworkReciever(sock=conn, recv_callback=None)
        nr.stage = 0
        nr.recv_callback = partial(
            handler.handle_client, self.version, self.event_queue, nr)


def on_command(queue, cmd):
    queue.put((events.CMD, cmd))


def main(version):
    console.printf('Starting Vyolet Server version {}', version.short)
    eventqueue = Queue.Queue()
    console.callback = partial(on_command, eventqueue)
    listener = Listener(version, eventqueue)
    threading.Thread(target=asyncore.loop, args=(5.0, True)).start()
    gameloop.gameloop(eventqueue)
    listener.shutdown = True
