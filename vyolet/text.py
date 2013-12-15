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
from utils import ensure_res, DataFile
import json


def _set_lang(lang):
    with DataFile(ensure_res('.'.join((lang, 'lang'))), {}, json) as data:
        Text._data.update(data)


class Text(object):
    _data = dict()

    def __getattr__(self, attr):
        return self._data[attr]

text = Text()