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

import random
from collections import defaultdict

from . import render, spaceobjects, world_gen


class SpaceTile(object):
    def __init__(self):
        self.local = []


class Game(object):
    seed = random.randrange(2 ** 31)
    def __init__(self):
        self.space = defaultdict(SpaceTile)
        self.objects = []
        self.online = dict()
        self.offline = dict()
        self.generator = world_gen.DefaultGenerator()
        self.generator.init(self)
        self.tick_count = 0

    def user_login(self, username, source):
        if username in self.offline:
            ship = self.offline.pop(username)
            ship.add_to_space()
        else:
            ship = spaceobjects.UserShip(
                name=username, **self.spaceobject_params)
        self.online[username] = (ship, source)
        ship.conn = source
        source.ship = ship
        return ship

    def user_logout(self, username):
        ship, _source = self.online.pop(username)
        ship.rm_from_space()
        self.offline[username] = ship
        ship.conn = None

    @property
    def spaceobject_params(self):
        return {
            'game': self,
            'others': self.objects,
            'space': self.space}

    def kick_user(self, username, message):
        ship, source = self.online.pop(username)
        ship.rm_from_space()
        self.offline[username] = ship
        source.sendp.disconnect(message)

    def kick_all(self, message):
        while self.online:
            username, (ship, source) = self.online.popitem()
            ship.rm_from_space()
            self.offline[username] = ship
            source.sendp.disconnect(message)

    def tick(self):
        self.tick_count = count = (self.tick_count + 1) % 24
        for obj in self.objects[:]:
            if not obj.added:
                continue
            obj.tick(count)
            for other, _dist in obj.get_nearby():
                if isinstance(other, spaceobjects.UserShip):
                    _ship, source = self.online[other.name]
                    if obj.invalidate:
                        render.send(source, obj)
                    source.sendp.space_object(
                        obj.id_,
                        obj.pos[0], obj.pos[1], obj.direction,
                        other is obj)
