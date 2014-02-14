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

from collections import defaultdict

import pygame

class SpriteFactory(defaultdict):
    def __init__(self, SpriteClass, *args, **kwargs):
        super(SpriteFactory, self).__init__()
        self.SpriteClass = SpriteClass
        self.args = args
        self.kwargs = kwargs

    def __missing__(self, key):
        self[key] = sprite = self.SpriteClass(key, *self.args, **self.kwargs)
        return sprite


class CursorSprite(pygame.sprite.Sprite):
    def __init__(self):
        self.image = pygame.Surface((1, 1))

    def __call__(self, x, y):
        self.rect = pygame.Rect(x, y, 1, 1)
        return self