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
from ..enum import effect

# m: motioned, t: targeted, r: rotated


class DummyTarget(RelativeSprite):
    group = pygame.sprite.Group()
    def __init__(self, x, y, origin_source):
        super(DummyTarget, self).__init__(origin_source, self.group)
        self.x = y
        self.y = y


class EffectSprite(pygame.sprite.Sprite):
    group = pygame.sprite.RenderPlain()

    image_size = (0, 0)
    @classmethod
    def get_image(cls, size):
        if size[0] > cls.image_size[0] or size[1] > cls.image_size[1]:
            new_size = (max(size[0], cls.image_size[0]),
                        max(size[1], cls.image_size[1]))
            cls.image = pygame.Surface(new_size)
            cls.image.set_colorkey((0, 0, 0))
            cls.image.fill((0, 0, 0))
            cls.image_size = new_size
        rect = pygame.Rect((0, 0), size)
        return cls.image.subsurface(rect)

    def __init__(self, gp, id_, cr, cg, cb, from_, tox, toy, to_obj, duration):
        super(EffectSprite, self).__init__(self.group)
        try:
            targeted, self.draw = EFFECTS[id_]
        except KeyError:
            self.kill()
        else:
            self.drawing = gp.drawing
            self.color = (cr, cg, cb)
            self.from_ = from_
            self.to = to_obj if targeted else DummyTarget(tox, toy, gp)
            self.remaining = self.duration = duration

    def draw(self, drawing, fx, fy, tx, ty, remaining):
        pass

    def update(self, screen):
        self.remaining -= 1
        if not self.remaining:
            self.kill()
        else:
            drawing = self.drawing(screen).color(self.color)
            remaining = self.remaining / float(self.duration)
            tx, ty = self.to.rect.topleft
            fx, fy = self.from_.rect.topleft
            self.rect = self.draw(drawing, fx, fy, tx, ty, remaining)
            self.image = self.get_image(self.rect.size)


def draw_DOT(drawing, fx, fy, tx, ty, remaining):
    print 'draw_DOT'
    x = int((fx - tx) * remaining + tx)
    y = int((fy - ty) * remaining + ty)
    rect = pygame.Rect(x, y, 2, 2)
    drawing.rect(rect)
    return rect


def draw_LINE(drawing, fx, fy, tx, ty, remaining):
    drawing.line((fx, fy))
    rect = pygame.Rect(tx, ty, fx - tx, fy - ty)
    rect.normalize()
    return rect


EFFECTS = {
    effect.DOT: (True, draw_DOT),
    effect.LINE: (True, draw_LINE),
}
