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

from display import loop
from utils import DataFile
import mainmenu

SETTINGS = {
    'fullscreen': False,
}


def main(version):
    pygame.init()
    page = mainmenu.MainMenu()
    with DataFile('settings.json', SETTINGS, json) as settings:
        loop(settings, version, page)
    pygame.quit()
