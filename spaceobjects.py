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

import math
from collections import namedtuple

import render

class Vector(namedtuple('Vector', 'x y')):
    '''Class to represent vectors'''
    
    def distance(self, other):
        '''Return the straight-line distance from this vector to another'''
        return math.sqrt((self.x-other.x)**2 + (self.y-other.y)**2)
    
    def __neg__(self):
        '''Negative vector'''
        return Vector(-self.x, -self.y)
    
    def __add__(self, other):
        '''Vector addition'''
        return Vector(self.x+other.x, self.y+other.y)
        
    def __sub__(self, other):
        '''Vector subtraction'''
        return Vector(self.x-other.x, self.y-other.y)
        
    def __mul__(self, other):
        '''Dot product when by Vector, scale otherwise'''
        if isinstance(other, Vector):
            return self.x * other.x + self.y * other.y
        else:
            return Vector(self.x * other, self.y * other)
    
    def __len__(self):
        return math.sqrt(self.x**2 + self.y**2)

Vector.origin = Vector(0.0, 0.0)


class SpaceObject(object):
    '''Base class for all space objects'''
    def __init__(self, **kwargs):
        # .space: the master grid representing space
        self.space = kwargs.pop('space')
        # .pos: our location
        self.pos = kwargs.pop('pos')
        # .pivot: the coord of the tile of space which we are on
        self.pivot = self.get_pivot()
        # .close_space: the 9x9 grid of space tiles closest to us
        self.tiles = self.get_tiles()
        # add ourselves to the center tile
        self.tiles[4].local.append(self)
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
    
    def get_pivot(self):
        '''Get the coord of the tile of space which we are on'''
        return Vector(int(self.pos.x / 100), int(self.pos.y / 100))
    
    def get_tiles(self):
        '''Get the 9x9 grid of space tiles closest to us'''
        around = (-1, 0, 1)
        x, y = self.pivot
        return [self.space[x+nx, y+ny] for nx in around for ny in around]
    
    def get_nearby(self, distance=100):
        '''Get all space objects within a radius. Radii over 100 discouraged'''
        for tile in self.tiles:
            for space_object in tile.local:
                obj_dist = self.pos.distance(space_object.pos)
                if obj_dist <= distance:
                    yield space_object, obj_dist
    
    def render(self):
        '''Return a list of render commands and their arguments'''
        return [render.clear(),]
    
    class Affect(object):
        def __init__(self, obj):
            self.obj = obj
            
        def __getattr__(self, attr):
            return lambda *e: None
        
    def destroy(self):
        '''Remove this object from space'''
        self.tiles[4].local.remove(self)
        self.others[self.id_] = None
    
    def tick(self):
        self.pos += self.vel
        self.vel += self.acl
        self.acl = Vector.origin


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
                render.color(atmos.color),
                render.disk(atmos.size)))
        return display

    def tick(self):
        super(DamageSphere, self).tick()
        for sp_obj, dist in self.get_nearby():
            if dist < (self.size * 100):
                for atmos in self.atmospheres:
                    if dist < (atmos.size * 100):
                        sp_obj.damage(None, atmos.damage, atmos.dmg_type, self)
                        break
            sp_obj.acl += (self.size / dist**2) * (self.pos - sp_obj.pos)


class Mineable(SpaceObject):
    
