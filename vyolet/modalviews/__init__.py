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

class ModalView(object):
    def __init__(self, gp):
        self.gp = gp

    def close(self):
        self.gp.modal = None

    def border(self, screen, size):
        offset = (0, 0)
        drawing = self.gp.drawing(screen)
        for rgb in (0x52, 0x21, 0x00):
            drawing = drawing.color((0, 0, 0, 0xff - rgb))
            for _ in xrange(2 if rgb else 1):
                size = (size[0] - 1, size[1] - 1)
                points = [offset, (offset[0], size[1]),
                          size, (size[0], offset[1])]
                drawing.lines(points, True)
                offset = (offset[0] + 1, offset[1] + 1)
        size = (size[0] - offset[0], size[1] - offset[1])
        screen = screen.subsurface((offset, size))
        screen.fill((0x80, 0x80, 0x80))
        return screen, size

    def draw(self, screen, size):
        pass

    def recv_packet(self, packet, args):
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
