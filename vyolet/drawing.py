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


class Drawing(object):
    def __call__(self, surface):
        self.surface = surface
        return self

    def color(self, color):
        self._color = color
        return self

    def rect(self, rect):
        self.surface.fill(self._color, rect)
        return self

    def polygon(self, points, fill):
        width = 0 if fill else 1
        pygame.draw.polygon(self.surface, self._color, points, width)

    def circle(self, x, y, r, fill):
        width = 0 if fill else 1
        pygame.draw.circle(self.surface, self._color, (x, y), r, width)
        return self

    def line(self, spos, epos):
        pygame.draw.line(self.surface, self._color, spos, epos)
        return self


class AADrawing(Drawing):
    def __init__(self):
        import pygame.gfxdraw
        self.gfxdraw = pygame.gfxdraw

    def polygon(self, points, fill):
        if fill:
            super(AADrawing, self).polygon(points, fill)
        pygame.draw.aalines(self.surface, self._color, True, points)

    def circle(self, x, y, r, fill):
        if fill:
            self.gfxdraw.filled_circle(self.surface, x, y, r, self._color)
        self.gfxdraw.aacircle(self.surface, x, y, r, self._color)
        return self

    def line(self, spos, epos):
        pygame.draw.aaline(self.surface, self._color, spos, epos)
        return self
