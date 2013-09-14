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

class DataFile(object):
    def __init__(self, filename, data, pickler):
        self.filename = filename
        self.pickler = pickler
        if os.path.exists(filename):
            with open(filename) as datafile:
                self.data = pickler.load(datafile)
        else:
            self.data = data

    def __enter__(self):
        return self.data

    def __exit__(self, *exc):
        with open(self.filename, 'w') as datafile:
            self.pickler.dump(self.data, datafile)


