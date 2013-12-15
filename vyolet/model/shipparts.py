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
from . import render

class PartsContainer(object):

#     MASK, N, S, E, W = 0b1111, 0b1000, 0b100, 0b10, 0b1

    def __init__(self, ship, (width, height)=(17, 13)):
        self.ship = ship
        self.data = [[None] * height for _ in xrange(width)]
        self.size = (width, height)
        self.origin = (width // 2, height // 2)

    def _shift(self, (x, y)):
        return (self.origin[0] - x, self.origin[1] - y)

    def _in_bounds(self, (x, y)):
        return all((x >= 0, y >= 0, x < self.size[0], y < self.size[1]))

    def _get_adjacent(self, (x, y)):
        adj = ((x - 1, y),
               (x + 1, y),
               (x, y - 1),
               (x, y + 1))
        for x, y in adj:
            if self._in_bounds((x, y)) and self.data[x][y] is not None:
                yield x, y

    def __getitem__(self, (x, y)):
        x, y = self._shift((x, y))
        return self.data[x][y]

    def sub(self, (x, y), value):
        x, y = self._shift((x, y))
        old = self.data[x][y]
        self.data[x][y] = value
        if old is not None:
            old.on_rm(self.ship)
        if value is not None:
            value.on_add(self.ship)
        return old

    def can_add(self, (x, y)):
        return bool(list(self._get_adjacent((x, y))))

    def can_remove(self, (x, y)):
        if (x, y) == (0, 0):
            return False
        x, y = self._shift((x, y))
        solid = set([self.origin])
        for nx, ny in self._get_adjacent((x, y)):
            post = set([(x, y)])
            pre = set([(nx, ny)])
            while pre:
                p = pre.pop()
                if p in post:
                    continue
                elif p in solid:
                    post -= set([(nx, ny)])
                    solid |= post
                    break
                else:
                    pre |= set(self._get_adjacent(p))
                    post.add(p)
            else:
                return False
        return True

    def render(self, color):
        display = []
        x = -10 * self.size[0] / 2
        for col in self.data:
            y = -10 * self.size[1] / 2
            for part in col:
                if part is not None:
                    display.append(
                        render.rect(color, (x, y), (10, 10)))
                y += 10
            x += 10
        return display

    def __iter__(self):
        for col in self.data:
            for part in col:
                if part is not None:
                    yield part


all_parts = dict()

def part_metaclass(name, parents, attr):
    obj = type(name, parents, attr)
    all_parts[attr['id_']] = obj
    return obj


#######################################
# Mixin Bases
#######################################


class ShipPart(object):
    __metaclass__ = part_metaclass
    id_ = -1

    health = 100

    def on_add(self, ship):
        pass

    def on_rm(self, ship):
        pass

    def thrust(self, ship, amount):
        return 0

    def tick(self, ship):
        pass


class StatsMixin(ShipPart):
    stats = dict()

    def on_add(self, ship):
        super(StatsMixin, self).on_add(ship)
        for stat, value in self.stats.iteritems():
            ship.stats[stat] += value

    def on_rm(self, ship):
        super(StatsMixin, self).on_rm(ship)
        for stat, value in self.stats.iteritems():
            ship.stats[stat] -= value


class RegenMixin(ShipPart):

    regen = dict()

    def calc_regen(self, ship, stat, amount):
        max_stat = ship.stats[''.join(('max_', stat))]
        if ship.stats[stat] < max_stat:
            amount = min(amount, max_stat - ship.stats[stat])
            ship.stats[stat] += amount

    def tick(self, ship):
        super(RegenMixin, self).tick(ship)
        for stat, value in self.regen.iteritems():
            self.calc_regen(ship, stat, value)


#######################################
# Primary Classes
#######################################


class NonePart(ShipPart):
    id_ = 0


class Cockpit(StatsMixin, RegenMixin):
    id_ = 1

    stats = {
        'weight': 200,
        'energy': 100,
        'max_energy': 100,
        'fuel': 100,
        'max_fuel': 100,
    }

    regen = {
        'energy': 1,
    }

    def thrust(self, ship, amount):
        if ship.stats['energy'] > 10 * amount:
            ship.stats['energy'] -= 10 * amount
            return .1 * amount
        else:
            return 0


class Capacitor(StatsMixin):
    id_ = 2

    stats = {
        'weight': 100,
        'max_energy': 100,
    }


class FuelTank(StatsMixin):
    id_ = 3

    stats = {
        'max_fuel': 100,
    }


class RocketEngine(StatsMixin):
    id_ = 4

    stats = {
        'weight': 100,
    }

    def thrust(self, ship, amount):
        if ship.stats['fuel'] > amount:
            ship.stats['fuel'] -= amount
            return .5 * amount
        else:
            return 0


class Armor(StatsMixin):
    id_ = 5

    health = 500

    stats = {
        'weight': 500,
    }
