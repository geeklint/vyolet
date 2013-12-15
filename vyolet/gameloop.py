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

import Queue
import pickle
import time

import events
from console import console
from utils import DataFile
from model.game import Game

def gameloop(queue):
    with DataFile('game.dat', Game, pickle, load=False) as game:
        while True:
            time.sleep(.05)
            game.tick()
            while True:
                try:
                    event, args = queue.get_nowait()
                except Queue.Empty:
                    break
                if event == events.QUIT:
                    game.despawn_all()
                    return
                elif event == events.RUN:
                    args[0](game)
                elif event == events.CMD:
                    if args[0] == 'stop':
                        queue.put((events.QUIT, ()))
                elif event == events.LOGIN:
                    username, source = args
                    console.printf('{} logged in', username)
                    game.user_login(username, source)
                elif event == events.LOGOUT:
                    username, = args
                    console.printf('{} logged out', username)
                    game.user_logout(username)
