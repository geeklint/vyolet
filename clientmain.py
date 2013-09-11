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

import json
import os

import pygame
pygame.init()

DEFAULT_SETTINGS = {
    ''
}

[(640, 360), (854, 480), (1024, 576), (1280, 720), (1600, 900), (1920, 1080), (2048, 1152), (2560, 1440), (2880, 1620), (3840, 2160)]

def main():
    if not os.path.exists('settings.json'):
        
    screen = pygame.display.set_mode(())
