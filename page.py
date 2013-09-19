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

class Page(object):
    def init(self, screen, size):
        self.screen = screen
        self.size = size
        self.buttons = []

    def add_button(self, button, pos):
        pass

    def input_quit(self):
        pass

    def input_click_up(self, event):
        pass

    def input_click_down(self, event):
        pass

    def input_click_move(self, event):
        pass