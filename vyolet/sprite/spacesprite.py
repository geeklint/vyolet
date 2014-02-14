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

from ..model import render

class SpaceSprite(pygame.sprite.DirtySprite):
    group = pygame.sprite.RenderPlain()
    def __init__(self, id_, gp):
        super(SpaceSprite, self).__init__(self.group)
        self.gp = gp
        self.id_ = id_
        self.x = 0
        self.y = 0
        self.size = [0, 0]
        self.original = pygame.Surface((0, 0)).convert_alpha()
        self.box = [0, 0, 0, 0]
        self._rotate()
        gp.nr.sendp.space_object_req_render(id_)

    @property
    def rect(self):
        size = self.image.get_rect().size
        x = 100 * self.x - self.gp.origin_x - size[0] / 2
        y = 100 * self.y - self.gp.origin_y - size[1] / 2
        rect = pygame.Rect((x, y), size)
        return rect

    _direction = 0
    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        self._direction = -value
        self._rotate()

    def _rotate(self):
        image = self.original.copy()
        if self.direction:
            image = pygame.transform.rotate(image, self.direction)
        self.image = image

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
            image = pygame.Surface((width, height)).convert_alpha()
            image.fill((0, 0, 0, 0))
            dx = box[0] - self.box[0]
            dy = box[1] - self.box[1]
            image.blit(self.original, (dx, dy))
            self.box = box
            self.original = image

    def render(self, r, g, b, a, cmd, *args):
        color = (r, g, b, a)
        if cmd == render.CLEAR:
            self.original = pygame.Surface((0, 0)).convert_alpha()
            self.box = [0, 0, 0, 0]
        elif cmd == render.CIRCLE:
            x, y, r, s = args[:4]
            self._resize_points(
                (x + r, y + r), (x - r, y - r))
            dx, dy = self.box[:2]
            pygame.draw.circle(self.original, color, (x + dx, y + dy), r, s)
        elif cmd == render.RECT:
            x, y, width, height = args[:4]
            self._resize_points(
                (x, y), (x + width, y + height))
            dx, dy = self.box[:2]
            rect = pygame.Rect(dx + x, dy + y, width, height)
            print 'rect', rect
            pygame.draw.rect(self.original, color, rect)
        else:
            print 'unk cmd', cmd
        self._rotate()