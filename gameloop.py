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

import pickle
from collections import defaultdict

import events
from utils import DataFile
import spaceobjects


class SpaceTile(object):
    def __init__(self):
        self.local = []


class Game(object):
    def __init__(self):
        self.space = defaultdict(SpaceTile)
        self.objects = []
        self.online = dict()
        self.offline = dict()

    def spawn_ship(self, username):
        if username in self.offline:
            ship = self.offline.pop()
            ship.add_to_space()
        else:
            ship = spaceobjects.UserShip(
                username, *self.spaceobject_params)
        self.online[username] = ship
        return ship

    def despawn_ship(self, username):
        ship = self.online.pop(username)
        ship.rm_from_space()
        self.offline[username] = ship

    @property
    def spaceobject_params(self):
        return {
            'others': self.objects,
            'space': self.space}


def gameloop(queue):
    with DataFile('game.dat', Game(), pickle) as game:
        while True:
            event, args = queue.get()
            if event == events.QUIT:
                return
            elif event == events.LOGIN:
                username, source = args
                source.ship = game.spawn_ship(username)

