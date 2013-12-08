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

from functools import partial

import events
import network
import render
import spaceobjects
from version import Version


def handle_client(version, queue, nr, packet, args):
    if nr.stage == 0:
        if packet == 'handshake':
            if args[0] == network.HANDSHAKE:
                nr.stage = 1
            else:
                nr.sendp.disconnect('Bad handshake')
        else:
            return
    elif nr.stage == 1:
        if packet == 'login':
            verj, vern, username, passkey, room = args
            c_ver = Version('Vyolet', (verj, vern))
            if not (c_ver == version):
                nr.sendp.disconnect('Version Mismatch')
                return
            # TODO: verify passkey here
            if room != 'default':
                nr.sendp.disconnect('Invalid room')
                return
            nr.username = username
            nr.stage = 2
            queue.put((events.LOGIN, (username, nr)))
            nr.sendp.login_confirm()
        else:
            return
    # Main packet handlers
    else:
        if packet == 'disconnect':
            queue.put((events.LOGOUT, (nr.username,)))
        elif packet == 'space_object_req_render':
            queue.put((events.RUN, (partial(send_render, nr, args[0]),)))
        elif packet == 'thrust':
            nr.ship.thrust = spaceobjects.Vector(*args) / 128
        elif packet == 'edit_ship':
            nr.sendp.full_grid()


def send_render(nr, id_, game):
    if id_ in game.objects:
        render.send(nr, game.objects[id_])