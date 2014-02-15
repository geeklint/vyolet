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
    block_until = time.time() + .05
    with DataFile('game.dat', Game, pickle, load=False) as game:
        while True:
            now = time.time()
            if now < block_until:
                time.sleep(block_until - now)
            block_until = now + .05
            game.tick()
            while True:
                try:
                    event, args = queue.get_nowait()
                except Queue.Empty:
                    break
                if event == events.QUIT:
                    game.despawn_all()
                    return
                elif event == events.CMD:
                    if args[0] == 'stop':
                        queue.put((events.QUIT, ()))
                elif event == events.LOGIN:
                    username, view = args
                    console.printf('{} logged in', username)
                    game.user_login(username, view)
                elif event == events.LOGOUT:
                    username, = args
                    console.printf('{} logged out', username)
                    game.user_logout(username)
                elif event == events.UCMD:
                    username, cmd, args = args
                    getattr(game.command(username), cmd)(*args)
