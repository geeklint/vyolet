#!/usr/bin/env python
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
import os
import pickle
import random
import sys

import Image

SIZE = (1600, 900)
MAX_ATTEMPTS = 100
SEED = 'V'


def dist((x1, y1), (x2, y2)):
    return math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)


def gen_points(centiiter):
    print 'generating points'
    points = []
    for i in xrange(100):
        print '\r%d%%' % i,
        for _ in xrange(centiiter):
            new_point = random.randrange(SIZE[0]), random.randrange(SIZE[1])
            for point in points:
                if dist(point, new_point) < 5:
                    break
            else:
                points.append(new_point)
    print
    return points


def draw_points(centiiter, points):
    print 'adding points to image'
    img = Image.new(mode='L', size=SIZE)
    for x, y in points:
        color = random.randrange(1, 256)
        for dx, dy in ((-1, 0), (0, -1), (0, 0), (0, 1), (1, 0)):
            target = ((x + dx) % SIZE[0], (y + dy) % SIZE[1])
            img.putpixel(target, color)
    img.save('stars.%d.png' % centiiter)


def main(argv):
    if not argv[1:]:
        print 'Usage: gen_stars.py [n]'
        return 1
    centiiter = int(sys.argv[1])
    random.seed(SEED * centiiter)
    pointsfilename = 'points.%d.p' % centiiter
    if os.path.exists(pointsfilename):
        with open(pointsfilename) as pointsfile:
            points = pickle.load(pointsfile)
    else:
        points = gen_points(centiiter)
        with open(pointsfilename, 'w') as pointsfile:
            pickle.dump(points, pointsfile)
    draw_points(centiiter, points)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
