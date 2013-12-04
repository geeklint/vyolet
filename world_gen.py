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

import random

import spaceobjects
import math

class Random(random.Random):
    def randangle(self):
        return self.randrange(360) * (math.pi / 180)


class GeneratorState(object):
    pass


class Generator(object):
    def init(self, game):
        game.generator_state = GeneratorState()
        game.generator_state.size = 0
        game.generator_state.rand = Random(game.seed)
        self.next(game)

class DefaultGenerator(Generator):
    def next(self, game):
        rand = game.generator_state.rand
        if game.generator_state.size == 0:
            sun = spaceobjects.Sun(
                pos=(0, 0), atmosphere=rand.randrange(2 ** 31),
                **game.spaceobject_params)
            grow = 5
            game.generator_state.size += rand.randrange(100)
        else:
            sun = game.objects[0]
            grow = 2
        while grow:
            spaceobjects.Planet(
                orbit_origin=sun,
                orbit_radius=game.generator_state.size,
                orbit_speed=rand.randangle() / 360,
                orbit_angle=rand.randangle(),
                atmosphere=rand.randrange(2 ** 31),
                **game.spaceobject_params)
            game.generator_state.size += rand.randrange(100)
            grow -= 1
