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

import clientgame
import colors
import display
import mainmenu
import network
import page
import textbox
import utils
from text import text

class SingleplayerMenu(page.Page):
    pass


class MultiplayerMenu(page.Page):
    def __init__(self):
        self.textbox = textbox.TextBox(
            'monospace', 18, colors.WHITE, 100, self.update, self.enter)

    def draw(self, screen, size):
        self.screen = screen
        self.size = size
        self.origin = size[0] // 2, size[1] // 2
        screen.fill(colors.BLACK)
        font = pygame.font.SysFont('monospace', 24)
        label = font.render(text.enter_address, True, colors.WHITE)
        utils.blit_center(screen, label, (self.origin[0], size[1] // 3))
        box = (int(size[0] * .12), self.origin[1] - 13,
               int(size[0] * .76), 24)
        pygame.draw.rect(screen, colors.WHITE, box, 2)
        self.textbox.maxsize = int(size[0] * .75)
        self.update(self.textbox)

    def input_key_down(self, key, mod, code):
        self.textbox.input_key_down(key, mod, code)

    def update(self, textbox):
        self.textbox.color = colors.WHITE
        utils.blit_center(self.screen, textbox.render(), self.origin)
        pygame.display.flip()

    def enter(self, text):
        try:
            room, addr, port = network.parse_address(text)
        except ValueError:
            self.textbox.color = colors.RED
            self.update(self.textbox)
        else:
            import socket
            try:
                conn = socket.create_connection((addr, port), 5.0)
            except (socket.error, socket.timeout):
                display.set_page(mainmenu.MainMenu())
            else:
                nr = network.NetworkReciever(conn)
                nr.sendp.handshake(network.HANDSHAKE)
                nr.sendp.login(0, 0, 'name', 'pass', room)
                display.set_page(clientgame.LoadingPage(nr))


class SettingsMenu(page.Page):
    pass


class CreditsPage(page.Page):
    _pos = 0

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        if value < 0:
            value = 0
        elif value > 0:
            pass
        self._pos = value

    def input_click_down(self, pos, button):
        if button == 4:
            pos -= 1
        elif button == 5:
            pos += 1

