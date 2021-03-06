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

import os
import socket
import pygame

import display
import drawing
import mainmenu
import network
import page
import utils
from modalviews.editship import EditShip
from modalviews.settings import Settings
from sprite import SpriteFactory
from sprite.effectsprite import EffectSprite
from sprite.spacesprite import SpaceSprite
from text import text
from utils import colors


class LoadingPage(page.Page):
    def __init__(self, addr):
        self.addr = addr

    def init(self, settings):
        super(LoadingPage, self).init(settings)
        room, addr, port = self.addr
        try:
            conn = socket.create_connection((addr, port), 5.0)
        except (socket.error, socket.timeout):
            display.set_page(mainmenu.MainMenu())
        else:
            self.nr = nr = network.NetworkReciever(conn, self.recv_packet)
            nr.sendp.handshake(network.HANDSHAKE)
            username = os.environ['VYOLET_PLAYER_NAME']
            nr.sendp.login(0, 0, username, 'password', room)


    def draw(self, screen, size):
        self.screen = screen
        self.size = size
        self.origin = size[0] // 2, size[1] // 2
        screen.fill(colors.BLACK)
        font = pygame.font.SysFont('monospace', 24)
        label = font.render(text.loading, True, colors.WHITE)
        drawing.blit_center(screen, label, self.origin)
        pygame.display.flip()

    def recv_packet(self, packet, args):
        if packet == 'disconnect':
            print 'dc', args
            display.set_page(mainmenu.MainMenu())
        elif packet == 'login_confirm':
            display.set_page(GamePage(self.nr, self.settings))


class PNGLoader(object):
    def __getattr__(self, name):
        filename = '.'.join((name, 'png'))
        png = pygame.image.load(utils.ensure_res(filename)).convert()
        setattr(self, name, png)
        return png


class GamePage(page.Page):
    def __init__(self, nr, settings):
        self.nr = nr
        self.settings = settings
        nr.recv_callback = self.recv_packet
        self.objects = SpriteFactory(SpaceSprite, self)
        self.origin = (0, 0)
        self.redraw = True
        self.size = (0, 0)
        self.stats = (1, 1, 1, 1)
        self.equiped = (0,) * 10
        self.modal = None
        self.autopilot = True
        self.affect = 0
        self.thrust = [False, False, False, False]
        self.font = pygame.font.SysFont('monospace', 12)
        self.png = PNGLoader()
        if settings['antialias']:
            self.drawing = drawing.AADrawing()
        else:
            self.drawing = drawing.Drawing()

    @property
    def origin_x(self):
        return self.origin[0] - self.size[0] / 2
    @property
    def origin_y(self):
        return self.origin[1] - self.size[1] / 2

    def modal_rect(self, size):
        x = int(size[0] * .10)
        y = int(size[1] * .10)
        size = (x * 8, y * 8)
        return pygame.Rect(x, y, size[0], size[1])

    #######################################
    # Main functions
    #######################################

    def recv_packet(self, packet, args):
        if packet == 'disconnect':
            print 'dc', args
            display.set_page(mainmenu.MainMenu())
        elif packet == 'space_object':
            id_, x, y, d, origin = args
            self.objects[id_].x = x
            self.objects[id_].y = y
            self.objects[id_].direction = d
            if origin and (self.settings['scroll_bg']
                    or .4 * self.size[0] < abs(self.origin[0] - 100 * x)
                    or .4 * self.size[1] < abs(self.origin[1] - 100 * y)):
                self.origin = (100 * x, 100 * y)
                self.redraw = True
        elif packet == 'space_object_dead':
            dead = self.objects.pop(args[0], None)
            if dead is not None:
                dead.kill()
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
            self.modal = EditShip(args)

    def input_click_down(self, (x, y), button):
        if self.modal:
            rect = self.modal_rect(self.size)
            if rect.collidepoint(x, y):
                self.modal.input_click_down(
                    (x + rect.x, y + rect.y), button)
            else:
                self.modal = None
        elif y > self.hud_y(self.size):
            self.hud_click_down((x, y - self.hud_y(self.size)), button)
        elif button == 1:
            for obj in SpaceSprite.group:
                rect = obj.rect
                if (rect.collidepoint(x, y)
                        and obj.mask.get_at((x - rect.x, y - rect.y))):
                    self.nr.sendp.affect(self.affect, obj.id_)
                    break
        elif button == 3:
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
        if self.modal:
            rect = self.modal_rect(self.size)
            if rect.collidepoint(x, y):
                self.modal.input_click_up(
                    (x - rect.x, y - rect.y), button)
            else:
                self.modal = None
        elif y > self.hud_y(self.size):
            self.hud_click_up((x, y - self.hud_y(self.size)), button)
        elif button == 3 and not self.autopilot:
            self.nr.sendp.thrust(0, 0)

    def input_move(self, (x, y), buttons):
        if self.modal:
            rect = self.modal_rect(self.size)
            x = max(rect.x, min(rect.right, x)) - rect.x
            y = max(rect.y, min(rect.bottom, y)) - rect.y
            self.modal.input_move((x, y), buttons)
        elif not self.autopilot and 3 in buttons:
            offset = (self.size[0] / 2., self.size[1] / 2.)
            factor = max(offset)
            x = 0x7f * (x - offset[0]) / factor
            y = 0x7f * (y - offset[1]) / factor
            self.nr.sendp.thrust(x, y)

    def input_key_down(self, key, mod, code):
        if self.modal:
            self.modal.input_key_down(key, mod, code)
        else:
            try:
                cmd = self.settings['keys'].index(key)
            except ValueError:
                pass
            else:
                if cmd < 10:
                    self.nr.sendp.action(cmd)
                elif cmd == 10:
                    self.modal = Settings(self)
                elif cmd == 11:
                    self.nr.sendp.edit_ship()
                elif cmd == 12:
                    self.autopilot = not self.autopilot
                    self.nr.sendp.thrust(0, 0)
                elif cmd == 13:
                    self.affect = int(not self.affect)

    def input_key_up(self, key, mod):
        if self.modal:
            self.modal.input_key_up(key, mod)

    def draw(self, screen, size):
        split_screen = self.split_screen(screen, size)
        if self.redraw or size != self.size or self.settings['scroll_bg']:
            self.redraw = False
            self.full_draw(split_screen)
        else:
            self.update_draw(split_screen)
        if self.modal:
            model_rect = self.modal_rect(size)
            model_screen = screen.subsurface(model_rect)
            self.modal.draw(model_screen, model_rect.size)
        pygame.display.flip()
        self.screen = screen
        self.size = size

    def full_draw(self, split_screen):
        self.draw_bg(*split_screen[0])
        self.draw_sprites(*split_screen[0])
        self.hud_draw(*split_screen[1])
        self.hud_update(*split_screen[1])

    def update_draw(self, split_screen):
        self.draw_sprites(*split_screen[0])
        self.hud_update(*split_screen[1])

    def draw_sprites(self, screen, size):
        SpaceSprite.group.clear(screen, self.saved_bg)
        EffectSprite.group.clear(screen, self.saved_bg)
        SpaceSprite.group.draw(screen)
        EffectSprite.group.update(screen)
        EffectSprite.group.draw(screen)

    def tick(self):
        self.draw(self.screen, self.size)

    #######################################
    # HUD
    #######################################

    def hud_y(self, size):
        return size[1] - min(size[1] / 7, 128)

    def split_screen(self, screen, size):
        hud_y = self.hud_y(size)
        vp_size = (size[0], hud_y)
        viewport = screen.subsurface(pygame.Rect((0, 0), vp_size))
        hud_size = (size[0], size[1] - hud_y)
        hud_screen = screen.subsurface(pygame.Rect((0, hud_y), hud_size))
        return ((viewport, vp_size), (hud_screen, hud_size))

    def hud_draw(self, screen, size):
        width = int(size[1] * 808 / 128)
        image = pygame.transform.smoothscale(self.png.hud, (width, size[1]))
        self.hud_scaled = image
        self.hud_x = size[0] / 2 - width / 2
        self.hud_e_bar_t = int(79 * size[1] / 128. + 0.5)
        self.hud_f_bar_t = int(102 * size[1] / 128. + 0.5)
        self.hud_bar_r = int(661 * width / 808. + 0.5)
        self.hud_bar_w = int(514 * width / 808. + 0.5)
        self.hud_bar_h = int(17 * size[1] / 128. + 0.5)
        screen.fill(colors.GRAY)

    def hud_update(self, screen, size):
        image = self.hud_scaled.copy()
        missing = 1 - float(self.stats[0]) / (self.stats[1] or 1)
        width = self.hud_bar_w * missing
        x = self.hud_bar_r - width
        rect = pygame.Rect(x, self.hud_e_bar_t, width, self.hud_bar_h)
        pygame.draw.rect(image, colors.BLACK, rect)
        missing = 1 - float(self.stats[2]) / (self.stats[3] or 1)
        width = self.hud_bar_w * missing
        x = self.hud_bar_r - width
        rect = pygame.Rect(x, self.hud_f_bar_t, width, self.hud_bar_h)
        pygame.draw.rect(image, colors.BLACK, rect)
        screen.blit(image, (self.hud_x, 0))

    def hud_click_down(self, (x, y), button):
        pass

    def hud_click_up(self, (x, y), button):
        pass

    #######################################
    # Utility
    #######################################

    def draw_bg(self, screen, size):
        surface = pygame.Surface(size)
        x = -self.origin[0] % 1600
        y = -self.origin[1] % 900
        cells = ((x - 1600, y - 900), (x, y - 900), (x + 1600, y - 900),
                 (x - 1600, y), (x, y), (x + 1600, y),
                 (x - 1600, y + 900), (x, y + 900), (x + 1600, y + 900))
        for pos in cells:
            if (-1600 < pos[0] < 1600 + size[0]
                    and -900 < pos[1] < 900 + size[1]):
                rect = pygame.Rect(pos, (1600, 900))
                surface.blit(self.png.stars, rect)
        self.saved_bg = surface
        screen.blit(surface, (0, 0))

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
