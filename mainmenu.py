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
import cmath
import math

import pygame.gfxdraw

import colors
import display
import drawing
import gamemenus
import page
from text import text

class MainMenu(page.Page):
    highlight = None
    use_gfx = True

    def draw_highlight(self, surface, points, color):
        if self.use_gfx:
            (x1, y1), (x2, y2), (x3, y3) = points
            args = (surface, x1, y1, x2, y2, x3, y3, color)
            pygame.gfxdraw.aatrigon(*args)
            pygame.gfxdraw.filled_trigon(*args)
        else:
            pygame.draw.polygon(surface, points, color)

    def draw(self, screen, size):
        texts = [
            text.menu_multiplayer,
            '',
            text.menu_credits,
            text.menu_quit,
            text.menu_settings,
            '',
            text.menu_singleplayer]
        self.screen = screen
        self.size = w, h = size
        self.origin = ox, oy = w // 2, h // 2
        r, _angle = cmath.polar(ox + oy * 1j)
        angle = -math.pi / 2
        d = 2 * math.pi / 7
        self.screen.fill((0, 0, 0))
        font = pygame.font.SysFont('monospace', 16)
        for index in xrange(7):
            if index == self.highlight:
                left = cmath.rect(int(r * 1.25), angle)
                left = (ox + int(left.real), oy + int(left.imag))
                right = cmath.rect(int(r * 1.25), angle + d)
                right = (ox + int(right.real), oy + int(right.imag))
                self.draw_highlight(
                    screen, (self.origin, left, right), colors.VYOLET)
            label = font.render(texts[index], True, colors.WHITE)
            pos = cmath.rect(int(r / 2.5), angle + d / 2)
            pos = (ox + int(pos.real), oy + int(pos.imag))
            drawing.blit_center(screen, label, pos)
            angle += d
        pygame.display.flip()

    def get_index(self, (x, y)):
        _r, angle = cmath.polar(
            (x - self.origin[0]) + (y - self.origin[1]) * 1j)
        angle += 3 * math.pi
        angle -= math.pi / 2
        index = int(angle / (2 * math.pi / 7))
        return index % 7

    def input_click_up(self, pos, button):
        if button == 1:
            index = self.get_index(pos)
            if index == 0:
                page = gamemenus.MultiplayerMenu()
            elif index == 2:
                page = gamemenus.CreditsPage()
            elif index == 3:
                pygame.quit()
                return
            elif index == 4:
                page = gamemenus.SettingsMenu()
            elif index == 6:
                page = gamemenus.SingleplayerMenu()
            else:
                return
            display.set_page(page)

    def input_move(self, pos, buttons):
        index = self.get_index(pos)
        if self.highlight != index:
            self.highlight = index
            self.draw(self.screen, self.size)
