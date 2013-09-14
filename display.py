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

SIZES = [(640, 360), (854, 480), (1024, 576), (1280, 720), (1600, 900),
         (1920, 1080), (2048, 1152), (2560, 1440), (2880, 1620), (3840, 2160)]

def set_page(page):
    loop.page = page


def loop(settings):

    pygame.display.set_icon()
    pygame.display.set_caption()
    stop = False
    while not stop:
        winsize = settings['winsize']
        screen = pygame.display.set_mode(SIZES[winsize])
        while True:
            page = loop.page
            for event in pygame.event.get():
                pass
