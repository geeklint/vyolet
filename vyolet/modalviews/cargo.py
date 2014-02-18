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

class Cargo(ModalView):
    def __init__(self, gp):
        super(Cargo, self).__init__(gp)
        self.tab = 0
        self.page = 0
        self.items = []
        gp.nr.sendp.req_cargo(self.tab, self.page)

    def recv_packet(self, packet, args):
        if packet == 'cargo':
            tab, page = args[:2]
            if args[:2] == (self.tab, self.page):
                items, aux = args[2:66], args[66:]
                self.items = zip(items, aux)

    def draw(self, screen, size):
        pass
