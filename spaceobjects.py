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

import cmath
import math
import random
from UserDict import DictMixin
from collections import namedtuple, defaultdict

import render
import shipparts

'''
Notes about coordinates:
"pixels" (used for render): smallest unit
"position": 1pos = 100px
"tile": 1tile = 100pos = 10000px
'''



#######################################
# Utility classes
#######################################

class Vector(namedtuple('VectorBase', 'x y')):
    '''Class to represent vectors'''

    @property
    def distance(self, other):
        '''Return the straight-line distance from this vector to another'''
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def __neg__(self):
        '''Negative vector'''
        return Vector(-self.x, -self.y)

    def __add__(self, other):
        '''Vector addition'''
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        '''Vector subtraction'''
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        '''Dot product when by Vector, scale otherwise'''
        if isinstance(other, Vector):
            return self.x * other.x + self.y * other.y
        else:
            return Vector(self.x * other, self.y * other)

    def __len__(self):
        '''Magnitude'''
        return math.sqrt(self.x ** 2 + self.y ** 2)

    @classmethod
    def rect(cls, radius, angle):
        z = cmath.rect(radius, angle)
        return cls(z.real, z.imag)

Vector.origin = Vector(0.0, 0.0)


class NestedAttribute(object):
    default = None

    def __init__(self, obj):
        self.obj = obj

    def __getattr__(self, attr):
        attr = '_'.join((self.__class__.__name__.lower(), attr))
        return getattr(self.obj, attr, self.default)


class Stats(DictMixin):
    def __init__(self):
        self.data = dict()

    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value

    def __getitem__(self, key):
        boost = self.get('_'.join((key, 'boost')), 0)
        return (1 + boost) * self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        self.data.pop(key)


#######################################
# Base Class
#######################################

class SpaceObject(object):
    '''Base class for all space objects'''
    def __init__(self, **kwargs):
        # .space: the master grid representing space
        self.space = kwargs.pop('space')
        # .pos: our location
        self.pos = kwargs.pop('pos')
        # add ourselves to the center tile
        self.add_to_space()
        # .vel: our velocity
        self.vel = kwargs.pop('vel')
        # .acl: our acceleration
        self.acl = Vector.origin
        # .others: all other space objects
        self.others = others = kwargs.pop('others')
        for i, other in enumerate(others):
            if other is None:
                self.id_ = i
                others[i] = self
                break
        else:
            self.id_ = len(others)
            others.append(self)
        # .affect: a collection of functions which another object can use
        self.affect = self.Affect(self)

    @property
    def pivot(self):
        '''Get the coord of the tile of space which we are on'''
        return Vector(int(self.pos.x / 100), int(self.pos.y / 100))

    @property
    def tiles(self):
        '''Get the 9x9 grid of space tiles closest to us'''
        around = (-1, 0, 1)
        x, y = self.pivot
        return [self.space[x + nx, y + ny] for nx in around for ny in around]

    _pos = Vector(0, 0)
    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        pivot = self.pivot
        self._pos = Vector(*value)
        if self.pivot != pivot:
            self.rm_from_space()
            self.add_to_space()

    def get_nearby(self, distance=100):
        '''Get all space objects within a radius. Radii over 100 discouraged'''
        for tile in self.tiles:
            for space_object in tile.local:
                obj_dist = self.pos.distance(space_object.pos)
                if obj_dist <= distance:
                    yield space_object, obj_dist

    def render(self):
        '''Return a list of render commands and their arguments'''
        return [render.clear(), ]

    class Affect(NestedAttribute):
        def default(self, *args):
            pass

    def add_to_space(self):
        self.tile = tile = self.tiles[4]
        tile.local.append(self)

    def rm_from_space(self):
        self.tile.local.remove(self)
        self.others[self.id_] = None

    def destroy(self):
        '''Remove this object from space'''
        self.rm_from_space()

    def tick(self):
        self.pos += self.vel
        self.vel += self.acl
        self.acl = Vector.origin


#######################################
# Mixin bases
#######################################



class Damageable(SpaceObject):
    '''Class which represents an object which can be damaged
    '''

    @staticmethod
    def reduce(amount, resist):
        return int(100 * amount / (100. + resist))

    def affect_damage(self, direction, amount, dmg_type, cause):
        pass



class Mineable(SpaceObject):
    '''Class which represents an object which can be mined
    '''

    def affect_mine(self):
        pass


class DamageSphere(SpaceObject):
    '''Class which represents a large round body which will do damage to
       things that crash into it.
    '''
    def __init__(self, **kwargs):
        super(DamageSphere, self).__init__(**kwargs)
        self.atmospheres = sorted(
            self.get_atmospheres(kwargs.pop('atmosphere')))
        self.size = self.atmospheres[-1].size

    Atmosphere = namedtuple('Atmosphere', 'size color damage dmg_type')

    def get_atmospheres(self, key):
        '''Return a list of Atmospheres'''
        pass

    def render(self):
        display = super(DamageSphere, self).render()
        for atmos in sorted(self.atmospheres, reverse=True):
            display.extend((
                render.color(*atmos.color),
                render.disk(atmos.size)))
        return display

    def tick(self):
        super(DamageSphere, self).tick()
        for sp_obj, dist in self.get_nearby():
            if dist < (self.size / 100.):
                for atmos in self.atmospheres:
                    if dist < (atmos.size / 100.):
                        sp_obj.affect.damage(
                            None, atmos.damage, atmos.dmg_type, self)
                        break
            sp_obj.acl += (self.size / dist ** 2) * (self.pos - sp_obj.pos)


class Satallite(SpaceObject):
    def __init__(self, **kwargs):
        self.orbit_radius = kwargs.pop('orbit_radius')
        self.orbit_origin = kwargs.pop('orbit_origin')
        self.orbit_speed = kwargs.pop('orbit_speed')
        self.orbit_angle = kwargs.pop('orbit_angle')
        kwargs.setdefault('pos', self.orbit_pos())
        super(Satallite, self).__init__(**kwargs)

    def orbit_pos(self):
        rel_pos = Vector.rect(self.orbit_radius, self.orbit_angle)
        if isinstance(self.orbit_origin, SpaceObject):
            origin = self.orbit_origin.pos
        else:
            origin = Vector(*self.orbit_origin)
        return origin + rel_pos

    def tick(self):
        super(Satallite, self).tick()
        self.orbit_angle += self.orbit_speed
        self.pos = self.orbit_pos()


class Ship(Damageable):
    def __init__(self, **kwargs):
        super(Ship, self).__init__(**kwargs)
        self.stats = Stats()
        self.parts = shipparts.PartsContainer()
        self.parts.sub((0, 0), shipparts.Cockpit())

    def refresh_stats(self):
        self.stats.clear()
        for part in self.parts:
            for stat in part.stats:
                self.stats[stat] += part.stats[stat]

    @property
    def dest(self):
        if isinstance(self._dest, SpaceObject):
            dest = self._dest.pos
            if self.pos.distance(dest) > 100:
                self._dest = dest
            return dest
        else:
            return self._dest

    @dest.setter
    def dest(self, value):
        if isinstance(value, SpaceObject):
            self._dest = value
        else:
            self._dest = Vector(*value)


#######################################
# Primary classes
#######################################

class Sun(DamageSphere):
    def get_atmospheres(self, key):
        rand = random.Random(key)
        atmos = []
        size = 10
        for i in xrange(5):
            dmg_type = 'true' if size < 100 else 'fire'
            dmg = 1000. / size
            color = (int(0xff * (size / 410.)), 0, 0)
            atmos.append(self.Atmosphere(size, color, dmg, dmg_type))
            size += rand.triangular(100)
        return atmos


class Planet(DamageSphere, Satallite, Mineable):
    pass


class UserShip(Ship):

    def __init__(self, username, **kwargs):
        kwargs.setdefault('pos', self.starting_location)
        super(UserShip, self).__init__(**kwargs)

    @property
    def starting_location(self):
        Vector.rect(200, random.randrange(360) * math.pi / 180)




