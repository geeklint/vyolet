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

import cmath
import math

import pygame


def blit_center(surface, source, pos, *args):
    size = source.get_size()
    pos = (int(pos[0] - size[0] / 2), int(pos[1] - size[1] / 2))
    surface.blit(source, pos, *args)


def draw_vyolet_logo(surface, rect, color,
        ratio=(1 + math.cos(math.pi / 7))):
    if not isinstance(rect, pygame.Rect):
        rect = pygame.Rect(*rect)
    radius = rect.height - rect.height / ratio
    cx, cy = rect.centerx, rect.y + radius + 1
    angle = -math.pi * .5
    delta = 2 * math.pi / 7
    points = []
    for _ in xrange(7):
        point = cmath.rect(radius, angle)
        points.append((point.real + cx, point.imag + cy))
        angle += delta
    pygame.draw.polygon(surface, color, points)
    pygame.draw.aalines(surface, color, True, points)
