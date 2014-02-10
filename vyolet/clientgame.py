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

import socket
import pygame
from collections import defaultdict

from text import text
import display
import mainmenu
import network
import page
import utils
import drawing
from utils import colors
from model import render


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
        drawing.blit_center(screen, label, self.origin)
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
        self._direction = -value
        self._rotate()

    def _rotate(self):
        image = self.original.copy()
        if self.direction:
            image = pygame.transform.rotate(image, self.direction)
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
                (x + r, y + r), (x - r, y - r))
            dx, dy = self.box[:2]
            pygame.draw.circle(self.original, color, (x + dx, y + dy), r, s)
        elif cmd == render.RECT:
            x, y, width, height = args[:4]
            self._resize_points(
                (x, y), (x + width, y + height))
            dx, dy = self.box[:2]
            rect = pygame.Rect(dx + x, dy + y, width, height)
            print 'rect', rect
            pygame.draw.rect(self.original, color, rect)
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
        self.stats = (1, 1, 1, 1)
        self.equiped = (0,) * 10
        self.model = None
        self.autopilot = True
        self.thrust = [False, False, False, False]
        self.font = pygame.font.SysFont('monospace', 12)
        self.bg_src = self.load_image('stars.png')
        self.hud_src = self.load_image('hud.png')
        self.parts_src = self.load_image('parts.png')
        self.equip_src = self.load_image('equipment.png')

    def load_image(self, filename):
        return pygame.image.load(utils.ensure_res(filename)).convert()

    @property
    def origin_x(self):
        return self.origin[0] - self.size[0] / 2
    @property
    def origin_y(self):
        return self.origin[1] - self.size[1] / 2

    @property
    def model_rect(self):
        x = int(self.size[0] * .10)
        y = int(self.size[1] * .10)
        size = (x * 8, y * 8)
        return pygame.Rect(x, y, size[0], size[1])

    #######################################
    # Main functions
    #######################################

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
            self.objects[args[0]].render(*args[1:])
        elif packet == 'ship_stats':
            self.stats = args
        elif packet == 'full_grid':
            self.model = FullGridModel(args)

    def input_click_down(self, (x, y), button):
        if self.model:
            pass
        elif y > self.size[1] * 6 / 7:
            self.hud_click_down((x, y), button)
        else:
            if self.autopilot:
                self.nr.sendp.set_dest((self.origin_x + x) / 100.,
                                       (self.origin_y + y) / 100.)
            else:
                offset = (self.size[0] / 2., self.size[1] / 2.)
                factor = max(offset)
                x = 0x7f * (x - offset[0]) / factor
                y = 0x7f * (y - offset[1]) / factor
                self.nr.sendp.thrust(x, y)

    def input_click_up(self, (x, y), button):
        if self.model:
            rect = self.model_rect
            if rect.collidepoint(x, y):
                self.model.input_click_down(
                    (x + rect.x, y + rect.y), button)
            else:
                self.model = None
        elif y > self.size[1] * 6 / 7:
            self.hud_click_up((x, y), button)
        if not self.autopilot:
            self.nr.sendp.thrust(0, 0)

    def input_key_down(self, key, mod, code):

        try:
            cmd = self.settings['keys'].index(key)
        except ValueError:
            pass
        else:
            if cmd < 10:
                self.nr.sendp.action(cmd)
            elif cmd == 10:
                self.nr.sendp.edit_ship()
            elif cmd == 11:
                pass
            elif cmd == 12:
                self.autopilot = not self.autopilot
                self.nr.sendp.thrust(0, 0)

    def input_key_up(self, key, mod):
        pass

    def draw(self, screen, size):
        if size != self.size:
            self.full_draw(screen, size)
        else:
            self.delta_draw(screen, size)
        self.screen = screen
        self.size = size

    def full_draw(self, screen, size):
        self.delta_draw(screen, size)

    def delta_draw(self, screen, size):
        self.draw_bg(screen, size)
        SpaceSprite.group.draw(screen)
        self.hud_draw(screen, size)
        self.model_draw(screen, size)
        pygame.display.flip()

    def tick(self):
        self.draw(self.screen, self.size)

    #######################################
    # HUD
    #######################################

    def hud_draw(self, screen, size):
        image = self.hud_src.copy()
        missing = 1 - float(self.stats[0]) / (self.stats[1] or 1)
        width = 514 * missing
        x = 661 - width
        rect = pygame.Rect(x, 79, width, 17)
        pygame.draw.rect(image, colors.BLACK, rect)
        missing = 1 - float(self.stats[2]) / (self.stats[3] or 1)
        width = 514 * missing
        x = 661 - width
        rect = pygame.Rect(x, 102, width, 17)
        pygame.draw.rect(image, colors.BLACK, rect)
        height = min(size[1] / 7, 128)
        width = int(height / 128. * 808)
        image = pygame.transform.smoothscale(image, (width, height))
        x = size[0] / 2 - width / 2
        y = size[1] - height
        rect = pygame.Rect(0, y, size[0], height)
        pygame.draw.rect(screen, colors.GRAY, rect)
        screen.blit(image, (x, y))

    def hud_click_down(self, (x, y), button):
        pass

    def hud_click_up(self, (x, y), button):
        pass

    #######################################
    # Model
    #######################################

    def model_draw(self, screen, size):
        if self.model:
            x = int(size[0] * .10)
            y = int(size[1] * .10)
            size = (x * 8, y * 8)
            surf = pygame.Surface(size)
            self.model.draw(self, surf, size)
            rect = pygame.Rect(x - 5, y - 5, size[0] + 10, size[1] + 10)
            pygame.draw.rect(screen, colors.VYOLET, rect)
            rect = pygame.Rect(x, y, size[0], size[1])
            screen.blit(surf, rect)

    #######################################
    # Utility
    #######################################

    def draw_bg(self, screen, size):
        x = -self.origin[0] % 1600
        y = -self.origin[1] % 900
        cells = ((x - 1600, y - 900), (x, y - 900), (x + 1600, y - 900),
                 (x - 1600, y), (x, y), (x + 1600, y),
                 (x - 1600, y + 900), (x, y + 900), (x + 1600, y + 900))
        for pos in cells:
            if -1600 < pos[0] < 1600 and -900 < pos[1] < 900:
                rect = pygame.Rect(pos, (1600, 900))
                screen.blit(self.bg_src, rect)

    def draw_icon(self, screen, source, pos, id_, aux=0, size=(48, 48)):
        offset = (id_ * size[0] % source.get_rect().width,
                  int(id_ * size[1] / source.get_rect().width))
        area = pygame.Rect(offset, size)
        screen.blit(source, pos, area)
        if aux:
            pygame.draw.line(
                screen,
                (0xff - aux, aux, 0),
                (0, size[1] - 2), (size[0] * aux / 255., size[1] - 2),
                2)


class FullGridModel(object):
    def __init__(self, items):
        self.items = items

    def draw(self, gp, screen, size):
        self.screen = screen
        self.size = size
        item_size = min(size[0] / 17, size[1] / 13)
        items = iter(self.items)
        for x in xrange(17):
            for y in xrange(13):
                self.gp.draw_icon(
                    screen, self.gp.parts_src, (x * 48, y * 48), next(items))

    def input_click_down(self, (x, y), button):
        pass
