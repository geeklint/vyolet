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

class TextBox(object):
    text = ''
    _pos = 0

    def __init__(self, font, fontsize, color, maxsize, update, callback):
        self.font = font
        self.fontsize = fontsize
        self.color = color
        self.maxsize = maxsize
        self.update = update
        self.callback = callback

    @property
    def pos(self):
        return self._pos
    @pos.setter
    def pos(self, value):
        if value < 0:
            value = 0
        elif value > len(self.text):
            value = len(self.text)
        self._pos = value

    def input_key_down(self, key, mod, code):
        if 0x1f < key < 0x7f:
            self.text = code.join(
                (self.text[:self.pos], self.text[self.pos:]))
            self.pos += 1
        elif key == pygame.K_BACKSPACE and self.pos != 0:
            self.pos -= 1
            self.text = ''.join(
                (self.text[:self.pos], self.text[self.pos + 1:]))
        elif key == pygame.K_DELETE:
            self.text = ''.join(
                (self.text[:self.pos], self.text[self.pos + 1:]))
        elif key == pygame.K_RETURN:
            self.callback(self.text)
        elif key in (pygame.K_UP, pygame.K_HOME, pygame.K_PAGEUP):
            self.pos = 0
        elif key in (pygame.K_DOWN, pygame.K_END, pygame.K_PAGEDOWN):
            self.pos = len(self.text)
        elif key == pygame.K_LEFT:
            self.pos -= 1
        elif key == pygame.K_RIGHT:
            self.pos += 1
        else:
            return
        self.update(self)

    def render(self):
        font = pygame.font.SysFont(self.font, self.fontsize)
        pre = font.render(self.text[:self.pos], True, self.color)
        post = font.render(self.text[self.pos:], True, self.color)
        presize, postsize = pre.get_width(), post.get_width()
        size = presize + 1 + postsize
        if size < self.maxsize or presize <= self.maxsize // 2:
            offset = 0
        elif postsize <= self.maxsize // 2:
            offset = self.maxsize - size
        else:
            offset = self.maxsize // 2 - presize
        height = max(pre.get_height(), post.get_height())
        surface = pygame.Surface((self.maxsize, height))
        surface.blit(pre, (offset, 0))
        offset += presize
        pygame.draw.aaline(
            surface, self.color, (offset + 1, 1), (offset + 1, height - 1))
        offset += 1
        surface.blit(post, (offset, 0))
        return surface
