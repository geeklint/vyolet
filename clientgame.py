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
        self.size = [0, 0]
        self.original = pygame.Surface((0, 0)).convert_alpha()
        self.box = [0, 0, 0, 0]
        self._rotate()
        gp.nr.sendp.space_object_req_render(id_)

    @property
    def rect(self):
        size = self.image.get_rect().size
        x = 100 * self.x - self.gp.origin_x - size[0] / 2
        y = 100 * self.y - self.gp.origin_y - size[1] / 2
        rect = pygame.Rect((x, y), size)
        return rect

    _direction = 0
    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        self._direction = value
        self._rotate()

    def _rotate(self):
        image = self.original.copy()
        if self.direction:
            image = pygame.transform.rotate(image,
                                            self.direction * 180 / math.pi)
        self.image = image

    def _resize_points(self, *points):
        box = self.box[:]
        for x, y in points:
            if x < -box[0] or x > box[0]:
                box[0] = abs(x)
            if y < -box[1] or y > box[1]:
                box[1] = abs(y)
        if box != self.box:
            width = box[0] * 2
            height = box[1] * 2
            image = pygame.Surface((width, height)).convert_alpha()
            image.fill((0, 0, 0, 0))
            dx = box[0] - self.box[0]
            dy = box[1] - self.box[1]
            image.blit(self.original, (dx, dy))
            self.box = box
            self.original = image

    def render(self, r, g, b, a, cmd, *args):
        color = (r, g, b, a)
        if cmd == render.CLEAR:
            self.original = pygame.Surface((0, 0)).convert_alpha()
            self.box = [0, 0, 0, 0]
        elif cmd == render.CIRCLE:
            x, y, r, s = args[:4]
            self._resize_points(
                (x + r, y), (x - r, y), (x, y + r), (x, y - r))
            dx, dy = self.box[:2]
            pygame.draw.circle(self.original, color, (x + dx, y + dy), r, s)
        else:
            print 'unk cmd', cmd
        self._rotate()


class SpriteFactory(defaultdict):
    def __init__(self, gp):
        super(SpriteFactory, self).__init__()
        self.gp = gp

    def __missing__(self, key):
        self[key] = sprite = SpaceSprite(self.gp, key)
        return sprite


class GamePage(page.Page):
    def __init__(self, nr):
        self.nr = nr
        nr.recv_callback = self.recv_callback
        self.objects = SpriteFactory(self)
        self.origin = (0, 0)
        self.size = (0, 0)
        self.thrust = [False, False, False, False]

    @property
    def origin_x(self):
        return self.origin[0] - self.size[0] / 2
    @property
    def origin_y(self):
        return self.origin[1] - self.size[1] / 2

    def recv_callback(self, packet, args):
        if packet == 'disconnect':
            print 'dc', args
            display.set_page(mainmenu.MainMenu())
        elif packet == 'space_object':
            id_, x, y, d, origin = args
            self.objects[id_].x = x
            self.objects[id_].y = y
            self.objects[id_].direction = d
            if origin:
                self.origin = (100 * x, 100 * y)
        elif packet == 'space_object_dead':
            self.objects.pop(args[0])
        elif packet == 'space_object_render':
            print self.objects
            self.objects[args[0]].render(*args[1:])

#     def input_click_down(self, (x, y), button):
#         x += self.origin_x
#         y += self.origin_y
#         x /= 100.
#         y /= 100.
#         self.nr.sendp.set_dest(x, y)

    def input_key_down(self, key, mod, code):
        nsew = (pygame.K_RIGHT, pygame.K_LEFT, pygame.K_DOWN, pygame.K_UP)
        if key in nsew:
            self.thrust[nsew.index(key)] = True
            self.nr.sendp.thrust(*self.thrust)

    def input_key_up(self, key, mod):
        nsew = (pygame.K_RIGHT, pygame.K_LEFT, pygame.K_DOWN, pygame.K_UP)
        if key in nsew:
            self.thrust[nsew.index(key)] = False
            self.nr.sendp.thrust(*self.thrust)

    def draw(self, screen, size):
        self.screen = screen
        self.size = size
        screen.fill(colors.BLACK)
        SpaceSprite.group.draw(screen)
        pygame.display.flip()

    def tick(self):
        self.draw(self.screen, self.size)
