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
from functools import partial

import events
import gameloop
import network
from console import console
from version import Version
import threading


def handle_client(version, queue, nr, packet, args):
    if nr.stage == 0:
        if packet == 'handshake' and args[0] == network.HANDSHAKE:
            nr.stage = 1
        else:
            return
    elif nr.stage == 1:
        if packet == 'login':
            verj, vern, username, passkey, room = args
            c_ver = Version('Vyolet', (verj, vern))
            if c_ver != version:
                nr.sendp.disconnect('Version Mismatch')
                return
            # verify passkey here
            if room != 'default':
                nr.sendp.disconnect('Invalid room')
                return
            nr.username = username
            nr.stage = 2
            queue.put((events.LOGIN, (username, nr)))
        else:
            return
    else:
        # main packet handlers
        pass



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
            handle_client, self.version, self.event_queue, nr)


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
