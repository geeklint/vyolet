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
from ..utils import Vector

# m: motioned, t: targeted, r: rotated
EFFECTS = {
    1: ('mt', (0, 0, 2, 2)),
}


class DummyTarget(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y


class EffectSprite(RelativeSprite):
    group = pygame.sprite.RenderPlain()

    mask_src = None

    def __init__(self, gp, id_, cr, cg, cb, from_, tox, toy, to_obj, duration):
        super(EffectSprite, self).__init__(gp, self.group)
        if self.mask_src is None:
            EffectSprite.mask_src = mask_src = gp.effects_src
            mask_src.set_colorkey((0xff, 0xff, 0xff))
        try:
            effect, box = EFFECTS[id_]
        except KeyError:
            self.kill()
        else:
            self.x = from_.x
            self.y = from_.y
            self.motioned = 'm' in effect
            self.rotated = 'r' in effect
            self.target = to_obj if 't' in effect else DummyTarget(tox, toy)
            self.original = pygame.Surface((box[2], box[3]))
            self.original.fill((cr, cg, cb))
            mask = self.mask_src.subsurface(pygame.Rect(*box))
            self.original.blit(mask, (0, 0))
            self.duration = duration
            self.update()
            self.rotate()

    def update(self):
        self.duration -= 1
        if not self.duration:
            self.kill()
        else:
            to = Vector(self.target.x, self.target.y)
            me = Vector(self.x, self.y)
            if self.motioned:
                me = me + ((to - me) / self.duration)
                self.x = me.x
                self.y = me.y
            if self.rotated:
                self.direction = (to - me).angle()
                self.rotate()




