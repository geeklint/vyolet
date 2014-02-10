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
import os
import shutil
import zipfile
from collections import namedtuple

class DataFile(object):
    def __init__(self, filename, default, pickler, load=True):
        self.filename = filename
        self.pickler = pickler
        if load and os.path.exists(filename):
            with open(filename) as datafile:
                self.data = pickler.load(datafile)
        else:
            self.data = default()

    def __enter__(self):
        return self.data

    def __exit__(self, *exc):
        try:
            with open(self.filename, 'w') as datafile:
                self.pickler.dump(self.data, datafile)
        except Exception:
            print 'save failed'


RES_PREFIX = 'res'
# need to do this at import time because we cd later
ABS_FILE = os.path.abspath(__file__)

def ensure_res(res):
    if not os.path.isdir(RES_PREFIX):
        os.makedirs(RES_PREFIX)
    dst = os.path.join(RES_PREFIX, res)
    if not os.path.exists(dst):
        dirname = os.path.dirname
        container = dirname(dirname(dirname(ABS_FILE)))
        if os.path.isdir(container):
            shutil.copy(os.path.join(container, dst), dst)
        else:
            with zipfile.ZipFile(container) as sfx:
                with open(dst, 'wb') as dstfile:
                    shutil.copyfileobj(sfx.open('/'.join((RES_PREFIX, res))),
                                       dstfile)
    return dst


def singleton(item):
    return item()


@singleton
class Nil(object):
    def __call__(self, *args, **kwargs):
        return self

    def __getattribute__(self, *args, **kwargs):
        return self

    def __getitem__(self, item):
        return self


class Vector(namedtuple('Vector', 'x y')):
    '''Class to represent vectors'''

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

    def __rmul__(self, other):
        return self * other

    def __div__(self, div):
        return self * (1. / div)

    def __pow__(self, exp):
        return Vector(self.x ** exp, self.y ** exp)

    def __abs__(self):
        '''Magnitude'''
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def unit(self):
        '''Vector along this vector with mag == 1'''
        if abs(self):
            return self * (1. / abs(self))
        else:
            return Vector.origin

    def angle(self):
        return math.atan2(self.y, self.x) * 180 / math.pi

    @classmethod
    def rect(cls, radius, angle):
        z = cmath.rect(radius, angle)
        return cls(z.real, z.imag)

    origin = (0.0, 0.0)

Vector.origin = Vector(0.0, 0.0)
