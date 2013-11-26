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

import pygame

from utils import ensure_res

SIZES = [(640, 360), (854, 480), (1024, 576), (1280, 720), (1600, 900),
         (1920, 1080), (2048, 1152), (2560, 1440), (2880, 1620), (3840, 2160)]

SET_PAGE = pygame.USEREVENT + 0
UPDATE_SIZE = pygame.USEREVENT + 1

def set_page(page):
    pygame.event.post(pygame.event.Event(SET_PAGE, {'page': page}))


def update_size():
    pygame.event.post(pygame.event.Event(UPDATE_SIZE))


def winloop(screen, holdpage):
    page = holdpage[0]
    page.init(screen)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                page.input_quit()
                pygame.quit()
                return True
            elif event.type == pygame.MOUSEBUTTONUP:
                page.input_click_up(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                page.input_click_down(event)
            elif event.type == pygame.MOUSEMOTION:
                page.input_move(event)
            elif event.type == SET_PAGE:
                holdpage[0] = page = event.page
                page.init(screen)
            elif event.type == UPDATE_SIZE:
                return False


def loop(settings, version, page):
    pygame.display.set_icon(ensure_res('icon.png'))
    pygame.display.set_caption(version.title)
    holdpage = [page, ]
    while True:
        winsize = settings['winsize']
        screen = pygame.display.set_mode(SIZES[winsize])
        if winloop(screen, holdpage):
            break
