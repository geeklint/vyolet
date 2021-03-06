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

import math
import random
from collections import namedtuple, defaultdict

from . import render
from . import shipparts
from .. import enum
from ..utils import colors, Nil, Vector

'''
Notes about coordinates:
"pixels" (used for render): smallest unit
"position": 1pos = 100px
"tile": 1tile = 100pos = 10000px
'''



#######################################
# Utility classes
#######################################

class PickleMixin(object):
    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__.update(state)


class NestedAttribute(PickleMixin):
    default = Nil

    def default_callable(self, *args, **kwargs):
        pass

    def __init__(self, prefix, obj):
        self.prefix = prefix
        self.obj = obj

    def __getattr__(self, attr):
        attr = '_'.join((self.prefix, attr))
        return getattr(self.obj, attr, self.default)


#######################################
# Base Class
#######################################

class SpaceObject(object):
    '''Base class for all space objects'''

    # .added: if we exist
    added = False

    # .dead: destroy us from world
    dead = False

    # .direction: our direction
    direction = 0

    # .invalidate: cause render to refresh
    invalidate = True

    # .static: don't allow us to move
    static = False

    def __init__(self, **kwargs):
        # .space: the master grid representing space
        self.space = kwargs.pop('space')
        # .pos: our location
        self.pos = kwargs.pop('pos')
        # add ourselves to the center tile
        self.add_to_space()
        # .vel: our velocity
        self.vel = kwargs.pop('vel', Vector.origin)
        # .acl: our acceleration
        self.acl = Vector.origin
        # .effects: effects we are 'playing'
        self.effects = []
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
        self.affect = NestedAttribute('affect', self)

    def spawn(self, Class, **kwargs):
        kwargs.setdefault('pos', self.pos)
        kwargs.update({'space':self.space, 'others':self.others})
        Class(**kwargs)

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
        if not self.static:
            pivot = self.pivot
            self._pos = Vector(*value)
            if self.pivot != pivot:
                if self.added:
                    self.rm_from_space()
                self.add_to_space()

    def get_nearby(self, distance=100):
        '''Get all space objects within a radius. Radii over 100 discouraged'''
        for tile in self.tiles:
            for space_object in tile.local:
                obj_dist = self.pos.distance(space_object.pos)
                if space_object.added and obj_dist <= distance:
                    yield space_object, obj_dist

    def render(self):
        '''Return a list of render commands and their arguments'''
        self.invalidate = False
        return [render.clear((0, 0, 0, 0)), ]

    def add_to_space(self):
        self.added = True
        self.tile = tile = self.tiles[4]
        tile.local.append(self)

    def rm_from_space(self):
        self.added = False
        self.tile.local.remove(self)

    def destroy(self):
        '''Remove this object from space'''
        self.rm_from_space()
        self.dead = True

    def tick(self, count):
        self.effects = []
        self.pos += self.vel
        self.vel += self.acl
        self.acl = Vector.origin


#######################################
# Mixin bases
#######################################


class Damageable(SpaceObject):
    '''Class which represents an object which can be damaged
    '''

    def affect_damage(self, direction, amount, dmg_type, cause):
        pass


class Targetable(Damageable):
    '''Class for objects which can be targeted (by ships)
    '''


class Mineable(SpaceObject):
    '''Class which represents an object which can be mined
    '''

    def affect_mine(self):
        pass


Atmosphere = namedtuple('Atmosphere', 'size color damage dmg_type')


class DamageSphere(SpaceObject):
    '''Class which represents a large round body which will do damage to
       things that crash into it.
    '''
    def __init__(self, **kwargs):
        super(DamageSphere, self).__init__(**kwargs)
        self.atmospheres = sorted(
            self.get_atmospheres(kwargs.pop('atmosphere')))
        self.size = self.atmospheres[-1].size

    def get_atmospheres(self, key):
        '''Return a list of Atmospheres'''
        pass

    def render(self):
        display = super(DamageSphere, self).render()
        enum = 1
        total = len(self.atmospheres)
        for atmos in sorted(self.atmospheres, reverse=True):
            alpha = int(0xff * (float(enum) / total))
            display.append(
                render.circle(
                    (atmos.color + (alpha,)),
                    (0, 0),
                    atmos.size,
                    True))
            enum += 1
        return display

    def tick(self, count):
        super(DamageSphere, self).tick(count)
        for sp_obj, dist in self.get_nearby():
            if sp_obj is self:
                continue
            if dist < (self.size / 100.):
                for atmos in self.atmospheres:
                    if dist < (atmos.size / 100.):
                        sp_obj.affect.damage(
                            (self.pos - sp_obj.pos).angle(),
                            atmos.damage,
                            atmos.dmg_type,
                            self)
                        break


class Gravity(SpaceObject):
    gravity = .00001
    def tick(self, count):
        super(Gravity, self).tick(count)
        for obj, dist in self.get_nearby():
            if dist:
                acl = Vector.origin
                acl += (self.gravity / dist ** 2) * (self.pos - obj.pos)
                obj.acl += acl



class Static(SpaceObject):
    def __init__(self, **kwargs):
        super(Static, self).__init__(**kwargs)
        self.static = True


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

    def tick(self, count):
        super(Satallite, self).tick(count)
        self.orbit_angle += self.orbit_speed
        self.pos = self.orbit_pos()


class Ship(Targetable):
    def __init__(self, **kwargs):
        super(Ship, self).__init__(**kwargs)
        self.stats = defaultdict(lambda: 0.0)
        self.parts = shipparts.PartsContainer(self)
        self.parts.sub((0, 0), shipparts.Cockpit())
        self.autopilot = False
        self.target = None
        self.equipment = [lambda ship: None] * 10
        self.cargo = {
            'resources': [],
            'parts': [shipparts.Armor()],
            'equipment': [],
        }

    def affect_damage(self, direction, amount, dmg_type, cause):
        slope = math.tan(math.radians(self.direction - direction))
        dx = 1 if abs(direction) > 90 else -1
        dy = -int(math.copysign(1, direction))
        wreckage = shipparts.Wreckage()
        cells = set()
        for x in xrange(0, dx * 9, dx):
            y = int(slope * x + 0.5)
            if abs(y) < 7:
                cells.add((x, y))
        for y in xrange(0, dy * 7, dy):
            x = int((y - 0.5) / slope)
            if abs(x) < 9:
                cells.add((x, y))
        for x, y in sorted(
                cells, key=lambda (x, y): (dx * x, dy * y), reverse=True):
            if self.parts[x, y] is not None:
                amount = self.parts[x, y].damage(
                    direction, amount, dmg_type, cause)
                if amount is None:
                    break
                else:
                    self.parts.sub((x, y), wreckage)
        else:
            for item_type in self.cargo:
                for item in self.cargo[item_type]:
                    self.spawn(FloatingItem, item_type=item_type, item=item)
            self.destroy()

    _color = colors.VYOLET
    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self.invalidate = True


    _thrust = Vector.origin
    @property
    def thrust(self):
        return self._thrust

    @thrust.setter
    def thrust(self, value):
        self._thrust = value
        self.autopilot = False

    _dest = Vector.origin
    @property
    def dest(self):
        return self._dest

    @dest.setter
    def dest(self, value):
        self._dest = value
        if abs(self.vel) > .01:
            self.autopilot = 2
        else:
            self.autopilot = 1
            self.ap_last_d = self.pos.distance(value)
            self.ap_halfway = .5 * self.ap_last_d
            self.ap_t = 0
            self.ap_working_thrust = None

    def render(self):
        display = super(Ship, self).render()
        display.extend(self.parts.render(self.color))
        return display

    def view_stats(self):
        return (
            self.stats['energy'],
            self.stats['max_energy'],
            self.stats['fuel'],
            self.stats['max_fuel'])

    def get_thrust(self, amount):
        thrust = 0
        for part in self.parts:
            thrust += part.thrust(self, amount) / self.stats['weight']
        return thrust

    def tick(self, count):
        super(Ship, self).tick(count)
        for part in self.parts:
            part.tick(self)
        if self.autopilot == 2:
            if abs(self.vel) < .01:
                self.dest = self.dest  # redo autopilot
            else:
                self.acl -= self.get_thrust(1) * self.vel.unit()
        elif self.autopilot == 1:
            towards = self.dest - self.pos
            if abs(towards) < .01 and abs(self.vel) < .01:
                self.pos = self.dest
                self.vel = Vector.origin
                self.autopilot = False
            else:
                thrust = self.get_thrust(1)
                if abs(towards) <= self.ap_halfway:
                    if self.ap_last_d < abs(towards):
                        self.dest = self.dest  # redo autopilot
                    else:
                        thrust = -thrust
                self.ap_last_d = abs(towards)
                self.direction = towards.angle()
                self.acl += thrust * towards.unit()
        else:
            thrust = abs(self.thrust)
            self.direction = self.thrust.angle()
            for part in self.parts:
                amount = part.thrust(self, thrust) / self.stats['weight']
                self.acl += self.thrust * amount
        if self.target:
            affect, target_id = self.target
            target_obj = self.others[target_id]
            req_cls = {enum.affect.ATTACK: Targetable,
                       enum.affect.MINE: Mineable}[affect]
            if (target_obj is None
                    or self.pos.distance(target_obj.pos) > self.stats['range']
                    or target_id == self.id_
                    or not isinstance(target_obj, req_cls)
                    or target_obj.dead):
                self.target = None
            else:
                if affect == enum.affect.ATTACK:
                    direction = (self.pos - target_obj.pos).angle()
                    amounts = defaultdict(lambda: 0)
                    if not count:
                        amounts['laser'] += 10
                    for type_, amount in amounts.iteritems():
                        target_obj.affect.damage(
                            direction, amount, type_, self)
                        self.effects.append((
                            enum.effect.DOT,
                            self.color[0],
                            self.color[1],
                            self.color[2],
                            self.id_,
                            0, 0,
                            target_id,
                            .5))
                elif affect == enum.affect.MINE:
                    pass


#######################################
# Primary classes
#######################################


class Sun(DamageSphere, Static, Gravity):
    def get_atmospheres(self, key):
        rand = random.Random(key)
        atmos = []
        size = 10
        for _i in xrange(50):
            dmg_type = 'true' if size < 100 else 'fire'
            dmg = 1000. / size
            color = (0xff, int(0xff) * (size / 1000.), 0)
            atmos.append(Atmosphere(size, color, dmg, dmg_type))
            size += rand.triangular(20)
        return atmos


class Planet(DamageSphere, Satallite, Mineable):
    def get_atmospheres(self, key):
        self.gaseous = bool(key & 1)
        return [Atmosphere(100, (0, 0xff, 0), 0, 'none')]


class UserShip(Ship):
    def __init__(self, **kwargs):
        self.name = kwargs.pop('name')
        kwargs['pos'] = Vector.rect(6, random.randrange(360) * math.pi / 180)
        super(UserShip, self).__init__(**kwargs)


class FloatingItem(Damageable):
    def __init__(self, **kwargs):
        self.item_type = kwargs.pop('item_type')
        self.item = kwargs.pop('item')
        super(FloatingItem, self).__init__(**kwargs)

    def affect_damage(self, direction, amount, dmg_type, cause):
        self.destroy()

    def render(self):
        display = super(FloatingItem, self).render()
        display.extend([
            render.circle(colors.WHITE, (0, 0), 10, False),
            render.rect(colors.WHITE, (-2, -2), (4, 4))])
        return display

    def tick(self, count):
        super(FloatingItem, self).tick(count)
        for obj, _dist in self.get_nearby(.1):
            if isinstance(obj, Ship):
                obj.cargo[self.item_type].append(self.item)
                self.destroy()
