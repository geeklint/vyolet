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
from functools import partial

from . import render, spaceobjects, world_gen
from ..utils import Vector


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

    def user_login(self, username, view):
        if username in self.offline:
            ship = self.offline.pop(username)
            ship.add_to_space()
        else:
            ship = spaceobjects.UserShip(
                name=username, **self.spaceobject_params)
        self.online[username] = (ship, view)
        return ship

    def user_logout(self, username):
        ship, _view = self.online.pop(username)
        ship.rm_from_space()
        self.offline[username] = ship

    @property
    def spaceobject_params(self):
        return {
            'game': self,
            'others': self.objects,
            'space': self.space}

    def kick_user(self, username, message):
        ship, view = self.online.pop(username)
        ship.rm_from_space()
        self.offline[username] = ship
        view.disconnect(message)

    def kick_all(self, message):
        while self.online:
            username, (ship, view) = self.online.popitem()
            ship.rm_from_space()
            self.offline[username] = ship
            view.disconnect(message)

    def tick(self):
        self.tick_count = count = (self.tick_count + 1) % 24
        for obj in self.objects[:]:
            if obj is None:
                continue
            if obj.added:
                obj.tick(count)
            if isinstance(obj, spaceobjects.UserShip):
                view = self.online[obj.name][1]
                if obj.dead:
                    ship = spaceobjects.UserShip(
                        name=obj.name, **self.spaceobject_params)
                    self.online[obj.name] = (ship, view)
                else:
                    view.ship_stats(*obj.view_stats())
            invalidate = obj.invalidate
            for other, _dist in obj.get_nearby():
                if isinstance(other, spaceobjects.UserShip):
                    view = self.online[other.name][1]
                    if invalidate:
                        render.send(view, obj)
                    if not obj.dead:
                        view.space_object(
                            obj.id_,
                            obj.pos[0], obj.pos[1], obj.direction,
                            other is obj)
                    else:
                        view.space_object_dead(obj.id_)
                    for effect in obj.effects:
                        view.effect(*effect)
            if obj.dead:
                self.objects[obj.id_] = None

    def command(self, user):
        return self._UserCommand(self, user)

    class _UserCommand(object):
        def __init__(self, game, user):
            self.game = game
            self.user = user

        def __getattr__(self, attr):
            return partial(self.game._user_command, self.user, attr)

    def _user_command(self, user, command, *args):
        ship, view = self.online[user]
        if command == 'space_object_req_render':
            try:
                obj = self.objects[args[0]]
                if obj is None:
                    [][0]
            except IndexError:
                view.space_object_dead(args[0])
            else:
                render.send(view, self.objects[args[0]])
        elif command == 'set_color':
            color = args
            total = sum(color)
            if total < 0x80:
                if total:
                    factor = float(0x80) / sum(color)
                    r, g, b = color
                    color = (int(r * factor), int(g * factor), int(b * factor))
                else:
                    color = (0x2a, 0x2a, 0x2a)
            ship.color = color
        elif command == 'edit_ship':
            view.full_grid()
        elif command == 'thrust':
            ship.thrust = Vector(*args) / 128
        elif command == 'set_dest':
            ship.dest = Vector(*args)
        elif command == 'action':
            if args[0] < 10:
                ship.equipment[args[0]].act(ship)
        elif command == 'affect':
            ship.target = args
