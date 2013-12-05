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
import math
import socket
import pygame
from collections import defaultdict
from functools import partial

from text import text
import colors
import display
import mainmenu
import network
import page
import render
import utils


class LoadingPage(page.Page):
    def __init__(self, (room, addr, port)):
        try:
            conn = socket.create_connection((addr, port), 5.0)
        except (socket.error, socket.timeout):
            display.set_page(mainmenu.MainMenu())
        else:
            self.nr = nr = network.NetworkReciever(conn, self.recv_callback)
            nr.sendp.handshake(network.HANDSHAKE)
            nr.sendp.login(0, 0, 'name', 'pass', room)

    def draw(self, screen, size):
        self.screen = screen
        self.size = size
        self.origin = size[0] // 2, size[1] // 2
        screen.fill(colors.BLACK)
        font = pygame.font.SysFont('monospace', 24)
        label = font.render(text.loading, True, colors.WHITE)
        utils.blit_center(screen, label, self.origin)
        pygame.display.flip()

    def recv_callback(self, packet, args):
        if packet == 'disconnect':
            print 'dc', args
            display.set_page(mainmenu.MainMenu())
        elif packet == 'login_confirm':
            display.set_page(GamePage(self.nr))


class SpaceSprite(pygame.sprite.DirtySprite):
    group = pygame.sprite.RenderPlain()
    def __init__(self, gp, id_):
        super(SpaceSprite, self).__init__(self.group)
        self.gp = gp
        self.id_ = id_
        self.x = 0
        self.y = 0
        self.direction = 0
        self.box = [0, 0, 0, 0]
        self._image = pygame.Surface((0, 0))

    @property
    def image(self):
        if self.direction:
            return pygame.transform.rotate(
                self._image, self.direction * 180 / math.pi)
        else:
            return self._image

    @property
    def rect(self):
        x = self.x + self.box[0] - 
        y = self.y + self.box[1]
        width = self.box[2] - self.box[0]
        height = self.box[3] - self.box[1]
        return pygame.Rect(x, y, width, height)

    def _resize_points(self, *points):
        box = self.box[:]
        for x, y in points:
            if x < box[0]:
                box[0] = x
            elif x > box[2]:
                box[2] = x
            if y < box[1]:
                box[1] = y
            elif y > box[3]:
                box[3] = y
        if box != self.box:
            width = box[2] - box[0]
            height = box[3] - box[1]
            image = pygame.Surface(width, height)
            old = self.rect.copy()
            old.x = self.box[0] - box[0]
            old.y = self.box[1] - box[1]
            image.blit(self._image, old)
            self._image = image

    def render(self, cmd, r, g, b, a, *args):
        color = (r, g, b, a)
        if cmd == render.CLEAR:
            self._image = pygame.Surface((0, 0))
            self.box = [0, 0, 0, 0]
        elif cmd == render.CIRCLE:
            x, y, r, s = args[:3]
            self._resize_points(
                (x + r, y), (x - r, y), (x, y + r), (x, y - r))
            pygame.draw.circle(self._image, color, (x, y), r, s)



class GamePage(page.Page):
    def __init__(self, nr):
        self.nr = nr
        nr.recv_callback = self.recv_callback
        self.objects = defaultdict(partial(SpaceSprite, self))
        self.origin = (0, 0)
        self.size = (0, 0)

    def recv_callback(self, packet, args):
        if packet == 'disconnect':
            print 'dc', args
            display.set_page(mainmenu.MainMenu())
        elif packet == 'space_object':
            id_, x, y, d, origin = args
            self.objects[id_].pos = (x, y)
            self.objects[id_].direction = d
            if origin:
                self.origin_x = x - self.size[0] / 2
                self.origin_y = y - self.size[1] / 2
        elif packet == 'space_object_dead':
            self.objects.pop(args[0])
        elif packet == 'space_object_render':
            self.objects[args[0]].render(*args)

    def draw(self, screen, size):
        self.screen = screen
        self.size = size
        screen.fill(colors.BLACK)
        SpaceSprite.group.draw(screen)
