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

import json

import pygame

import mainmenu
import text
from display import loop
from utils import DataFile

def get_settings():
    return {
        'fullscreen': False,
        'framerate': 60,
        'lang': 'en_us',
        'keys': [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
                 pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0,
                 pygame.K_s, pygame.K_e, pygame.K_a],
    }


def main(version):
    pygame.init()
    with DataFile('settings.json', get_settings, json, False) as settings:
        page = mainmenu.MainMenu()
        text._set_lang(settings['lang'])
        loop(settings, version, page)
    pygame.quit()
