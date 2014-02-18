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

import pygame

from . import RelativeSprite
from ..enum import render

class SpaceSprite(RelativeSprite):
    group = pygame.sprite.RenderPlain()
    def __init__(self, id_, gp):
        super(SpaceSprite, self).__init__(gp, self.group)
        self.drawing = gp.drawing
        self.id_ = id_
        self.x = self.y = 0
        self.size = [0, 0]
        self.original = pygame.Surface((0, 0)).convert_alpha()
        self.box = [0, 0, 0, 0]
        self.rotate()
        gp.nr.sendp.space_object_req_render(id_)

    def _resize_points(self, *points):
        box = self.box[:]
        for x, y in points:
            if x < -box[0] or x > box[0]:
                box[0] = abs(x)
            if y < -box[1] or y > box[1]:
                box[1] = abs(y)
        if box != self.box:
            width = box[0] * 2
            height = box[1] * 2
            image = pygame.Surface((width, height))
            image.set_colorkey((0, 0, 0))
            image.fill((0, 0, 0))
            dx = box[0] - self.box[0]
            dy = box[1] - self.box[1]
            image.blit(self.original, (dx, dy))
            self.box = box
            self.original = image

    def render(self, r, g, b, a, cmd, *args):
        color = (r, g, b, a)
        if cmd == render.CLEAR:
            self.original = pygame.Surface((0, 0))
            self.original.set_colorkey((0, 0, 0))
            self.box = [0, 0, 0, 0]
        elif cmd == render.CIRCLE:
            x, y, r, s = args[:4]
            self._resize_points(
                (x + r, y + r), (x - r, y - r))
            dx, dy = self.box[:2]
            self.drawing(
                self.original).color(color).circle(x + dx, y + dy, r, s)
        elif cmd == render.RECT:
            x, y, width, height = args[:4]
            self._resize_points(
                (x, y), (x + width, y + height))
            dx, dy = self.box[:2]
            rect = pygame.Rect(dx + x, dy + y, width, height)
            self.drawing(self.original).color(color).rect(rect)
        else:
            print 'unk cmd', cmd
        self.rotate()