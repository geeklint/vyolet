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

# commands:
(CLEAR, COLOR, LINE, CIRCLE, DISK) = xrange(5)

def complete(func):
    def wrapper(*args):
        return (func(*args) + (0, 0, 0, 0, 0, 0, 0, 0))[:8]
    return wrapper

@complete
def clear():
    return (CLEAR, 0)


@complete
def color(r, g, b, a=0xff):
    return (COLOR, 4, r, g, b, a)


@complete
def line(points):
    pass


@complete
def circle(pos, radius, stroke):
    return (CIRCLE, 3, pos, radius, stroke)


@complete
def disk(pos, radius):
    return (DISK, 2, pos, radius)
