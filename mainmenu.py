'''
<<<<<<< HEAD
This file is part of Vyolet.
=======
    Copyright (c) 2013 Sky Leonard
    This file is part of Vyolet.
>>>>>>> 7cc1555f3fa8648894f0e50def250dbed0f8354e

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

import page

class MainMenu(page.Page):
    line = []

    def draw(self, screen, size):
        self.screen = screen
        self.size = w, h = size
        self.origin = ox, oy = w // 2, h // 2
        print 'draw origin', self.origin
        r, _angle = cmath.polar(ox + oy * 1j)
        angle = math.pi / 2
        d = 2 * math.pi / 7
        color = (0xff, 0xff, 0xff, 0xff)
        for _ in xrange(7):
            end = cmath.rect(r, angle)
            end = (ox + int(end.real), oy + int(end.imag))
            print 'draw end', end
            pygame.draw.line(screen, color, (ox, oy), end)
            angle += d
        pygame.draw.lines(screen, color, False, self.line)
        pygame.display.flip()

    def input_click_up(self, event):
        x, y = event.pos
        self.line.append((x, y))
        _r, angle = cmath.polar(
            (x - self.origin[0]) + (y - self.origin[1]) * 1j)
        angle += 2 * math.pi
        angle %= 2 * math.pi
        print 'angle:', angle / (math.pi)
        angle -= math.pi / 2
        index = int(angle / (2 * math.pi / 7))
        print 'index:', index
