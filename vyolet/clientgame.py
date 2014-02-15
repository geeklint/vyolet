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

import display
import drawing
import mainmenu
import network
import page
import utils
from modelviews import FullGridModel
from sprite import SpriteFactory, CursorSprite
from sprite.effectsprite import EffectSprite
from sprite.spacesprite import SpaceSprite
from text import text
from utils import colors


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


class GamePage(page.Page):
    def __init__(self, nr):
        self.nr = nr
        nr.recv_callback = self.recv_callback
        self.objects = SpriteFactory(SpaceSprite, self)
        self.origin = (0, 0)
        self.cursor_sprite = CursorSprite()
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
        self.effects_src = self.load_image('effects.png')

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
        elif packet == 'effect':
            id_, cr, cg, cb, from_, tox, toy, to_obj, duration = args
            from_ = self.objects[from_]
            to_obj = self.objects[to_obj]
            duration = int(duration * self.settings['framerate'])
            EffectSprite(
                self, id_, cr, cg, cb, from_, tox, toy, to_obj, duration)
        elif packet == 'ship_stats':
            self.stats = args
        elif packet == 'full_grid':
            self.model = FullGridModel(args)

    def input_click_down(self, (x, y), button):
        if self.model:
            pass
        elif y > min(self.size[1] * 6 / 7, self.size[1] - 128):
            self.hud_click_down((x, y), button)
        else:
            targets = pygame.sprite.spritecollide(
                self.cursor_sprite(x, y), SpaceSprite.group, False,
                pygame.sprite.collide_mask)
            if targets:
                print 'targets'
                self.nr.sendp.affect(self.affect, targets[0].id_)
            elif self.autopilot:
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
            elif cmd == 13:
                self.affect = int(not self.affect)

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
        EffectSprite.group.draw(screen)
        self.hud_draw(screen, size)
        self.model_draw(screen, size)
        pygame.display.flip()

    def tick(self):
        EffectSprite.group.update()
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
