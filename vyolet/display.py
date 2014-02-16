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

import asyncore
import select

import pygame

from utils import ensure_res

SIZES = [(640, 360), (854, 480), (1024, 576), (1280, 720), (1600, 900),
         (1920, 1080), (2048, 1152), (2560, 1440), (2880, 1620), (3840, 2160)]

SET_PAGE = pygame.USEREVENT + 0

def set_page(page):
    pygame.event.post(pygame.event.Event(SET_PAGE, {'page': page}))


def winloop(settings, screen, page):
    page.draw(screen, screen.get_size())
    clock = pygame.time.Clock()
    poll_net = asyncore.poll2 if hasattr(select, 'poll') else asyncore.poll
    while True:
        clock.tick(settings['framerate'])
        poll_net(0.0, asyncore.socket_map)
        page.tick()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                page.input_quit()
                pygame.quit()
                return True
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                page.draw(screen, event.size)
            elif event.type == pygame.MOUSEBUTTONUP:
                page.input_click_up(event.pos, event.button)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                page.input_click_down(event.pos, event.button)
            elif event.type == pygame.MOUSEMOTION:
                page.input_move(event.pos, event.buttons)
            elif event.type == pygame.KEYDOWN:
                page.input_key_down(event.key, event.mod, event.unicode)
            elif event.type == pygame.KEYUP:
                page.input_key_up(event.key, event.mod)
            elif event.type == SET_PAGE:
                page = event.page
                page.init(settings)
                page.draw(screen, screen.get_size())


def loop(settings, version, page):
    icon = pygame.image.load(ensure_res('icon.png'))
    pygame.display.set_icon(icon)
    pygame.display.set_caption(version.title)
    while True:
        if settings['fullscreen']:
            screen = pygame.display.set_mode((0, 0),
                pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE)
        else:
            screen = pygame.display.set_mode((900, 500), pygame.RESIZABLE)
        if winloop(settings, screen, page):
            break
