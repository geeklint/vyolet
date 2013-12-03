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

class PartsContainer(object):

    MASK, N, S, E, W = 0b1111, 0b1000, 0b100, 0b10, 0b1

    def __init__(self, (width, height)=(17, 13)):
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

    def pack(self):
        pass

    def __iter__(self):
        for col in self.data:
            for part in col:
                if part is not None:
                    yield part


class ShipPart(object):
    pass


class Cockpit(ShipPart):
    pass


