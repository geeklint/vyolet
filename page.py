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

import pygame

class Page(object):
    def draw(self, screen, size):
        screen.fill((0xff, 0x00, 0x00))
        pygame.display.flip()

    def input_quit(self):
        pass

    def input_click_up(self, pos, button):
        pass

    def input_click_down(self, pos, button):
        pass

    def input_move(self, pos, buttons):
        pass

    def input_key_down(self, key, mod, code):
        pass

    def input_key_up(self, key, mod):
        pass
