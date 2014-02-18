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

from . import ModalView

class EditShip(ModalView):
    def __init__(self, gp, items):
        super(EditShip, self).__init__(gp)
        self.items = items

    def draw(self, screen, size):
        self.screen = screen
        self.size = size
        # item_size = min(size[0] / 17, size[1] / 13)
        items = iter(self.items)
        for x in xrange(17):
            for y in xrange(13):
                self.gp.draw_icon(
                    screen, self.gp.png.parts, (x * 48, y * 48), next(items))

    def input_click_down(self, (x, y), button):
        pass
