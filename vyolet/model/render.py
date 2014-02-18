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

from ..enum import render

FMT = 'IB4B8l'  # (id, color,,, cmd, args,,,,,,,,,)

def send(view, obj):
    print repr(obj)
    for render in obj.render():
        view.space_object_render(obj.id_, *render)


def renderfunc(func):
    def wrapper(color, *args):
        color = (color + (0xff,))[:4]
        return color + (func(*args) + (0, 0, 0, 0, 0, 0, 0, 0))[:9]
    return wrapper

@renderfunc
def clear():
    return (render.CLEAR,)


@renderfunc
def line(points):
    while len(points) < 4:
        points += points[-1]
    arr = []
    for point in points:
        arr.extend(point)
    return (render.LINE,) + tuple(arr)


def lines(points):
    sects = []
    while len(points) > 4:
        sects.append(points[:4])
        points = points[4:]
    sects.append(points)
    return [line(sect) for sect in sects]


@renderfunc
def rect((x, y), (width, height)):
    return (render.RECT, x, y, width, height)


@renderfunc
def circle(pos, radius, fill):
    return (render.CIRCLE, pos[0], pos[1], radius, float(fill))
