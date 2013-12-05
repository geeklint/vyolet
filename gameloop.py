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

import Queue
import pickle
import random
import time
from collections import defaultdict

import events
import spaceobjects
import world_gen
from utils import DataFile


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

    def spawn_ship(self, username, source):
        if username in self.offline:
            ship = self.offline.pop(username)
            ship.add_to_space()
        else:
            ship = spaceobjects.UserShip(
                name=username, **self.spaceobject_params)
        self.online[username] = (ship, source)
        return ship

    def despawn_ship(self, username):
        ship, _source = self.online.pop(username)
        ship.rm_from_space()
        self.offline[username] = ship

    @property
    def spaceobject_params(self):
        return {
            'others': self.objects,
            'space': self.space}


def gameloop(queue):
    with DataFile('game.dat', Game, pickle) as game:
        while True:
            time.sleep(.05)
            while True:
                try:
                    event, args = queue.get_nowait()
                except Queue.Empty:
                    break
                if event == events.QUIT:
                    return
                elif event == events.CMD:
                    if args[0] == 'stop':
                        queue.put((events.QUIT, ()))
                elif event == events.LOGIN:
                    username, source = args
                    print 'join:', username
                    source.ship = game.spawn_ship(username, source)
            for obj in game.objects[:]:
                if not obj.added:
                    continue
                obj.tick()
                for other in obj.get_nearby():
                    if isinstance(other, spaceobjects.UserShip):
                        _ship, source = game.online[other.name]
                        if source.req_render or obj.invalidate:
                            for render in obj.render():
                                source.sendp.render(obj.id_, *render)
                        source.sendp.spaceobject(
                            obj.id_,
                            obj.pos[0], obj.pos[1], obj.direction,
                            other is obj)
