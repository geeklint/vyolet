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

import asyncore
import re
import socket
import struct
from collections import namedtuple
from functools import partial

from model import render


HANDSHAKE = '\x69\x83\x82\xe2\xf4\x63\x22\x3b\x13\x91\xba\x28\x9b\x6f\x3d\x1d'
PORT = 49777

PACKETS = [
    0x00, 'ping', 'x',  # () c <-> s
    0x01, 'handshake', '16s',  # (handshake, ) c -> s
    0x02, 'login', 'BB32p16s16p',  # (version,, name, authkey, room) c -> s
    0x03, 'login_confirm', 'x',  # () s -> c

    0x20, 'space_object', 'I2df?',  # (id, pos,, direction, you) s -> c
    0x21, 'space_object_dead', 'I',  # (id, ) s -> c
    0x22, 'space_object_render', render.FMT,
    0x23, 'space_object_req_render', 'I',  # (id, ) s -> c
    0x24, 'effect', 'B3BI2dIf',  # (id_, color,,, from, to,, to, time) s -> c

    0x30, 'ship_stats', 'IIII',  # (e, max_e, f, max_f) s -> c
    0x31, 'set_color', '3B',  # (r, g, b) c -> s
    0x32, 'edit_ship', 'x',  # () c -> s
    0x33, 'full_grid', '',  # (items, damage) s -> c
    0x34, 'small_grid', 'x',  # not implemented
    0x35, 'cargo_clear', 'x',  # () s <-> c (also, req)
    0x36, 'cargo_item', 'HB',  # (item, damage) s -> c
    0x37, 'do_edit', '2bHB',  # (pos,, replacewith)
    0x38, 'engineering_clear', 'x',  # () s <-> c (also, req)
    0x39, 'engineering_option', 'H',  # (item,) s -> c
    0x3a, 'engineer_item', 'H',  # (item,) c -> s

    0x40, 'thrust', 'bb',  # (direction,,) c -> s
    0x41, 'set_dest', '2d',  # (dest,,) c -> s
    0x42, 'action', 'BffI',  # (action, x, y, obj) c -> s
    0x43, 'affect', 'BI',  # (affect, target) c -> s

    0xff, 'disconnect', '32p',  # (reason, ) c <-> s
]

def parse_packets():
    num_names = dict()
    name_nums = dict()
    num_fmts = dict()
    for i in range(0, len(PACKETS), 3):
        num, name, fmt = PACKETS[i:i + 3]
        num_names[num] = name
        name_nums[name] = num
        num_fmts[num] = fmt
    Packets = namedtuple('Packets', ['num_names', 'name_nums', 'num_fmts'])
    return Packets(num_names, name_nums, num_fmts)

def server_connection(port):
    sock = None
    for res in socket.getaddrinfo(None, port, socket.AF_UNSPEC,
                                  socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
        af, socktype, proto, _canonname, sa = res
        try:
            sock = socket.socket(af, socktype, proto)
        except socket.error:
            sock = None
            continue
        try:
            sock.bind(sa)
            sock.listen(5)
        except socket.error:
            sock.close()
            sock = None
            continue
        break
    return sock


def str_to_floats(text):
    '''Function to convert string to floats, for render text'''
    text += '   '  # 3 spaces
    floats = list()
    for i in range(0, min(len(text), 32), 4):
        sub_text = text[i:i + 4]
        f = struct.unpack('>f', struct.pack('>4s', sub_text))[0]
        floats.append(f)
    return floats

def floats_to_str(floats):
    '''Function to convert floats to string, for render text'''
    text = str()
    for f in floats:
        text += struct.unpack('>4s', struct.pack('>f', f))[0]
    return text.rstrip()


address_re = re.compile(r'^(?:(\w+)@)?(\w+(?:\.\w+)+)(?::(\d+))?$')
def parse_address(address):
    match = re.match(address_re, address)
    if match is None:
        raise ValueError('Parse Error')
    room, address, port = match.groups()
    room = room or 'default'
    port = int(port or PORT)
    return (room, address, port)

class NetworkReciever(asyncore.dispatcher_with_send):
    data = ''

    def __init__(self, sock, recv_callback):
        asyncore.dispatcher_with_send.__init__(self, sock)
        self.packets = parse_packets()
        self.recv_callback = recv_callback
        self.sendp = self.SendPacket(self)

    class SendPacket(object):
        def __init__(self, nr):
            self.nr = nr

        def __getattr__(self, name):
            return partial(
                self.nr.send_packet, self.nr.packets.name_nums[name])

    def send_packet(self, packet, *args):
        self.d('<', self.packets.num_names[packet], args)
        fmt = ''.join(('>B', self.packets.num_fmts[packet]))
        self.send(struct.pack(fmt, packet, *args))

    def handle_read(self):
        data = ''.join((self.data, self.recv(8192)))
        while data:
            packet = struct.unpack('>B', data[0])[0]
            try:
                fmt = self.packets.num_fmts[packet]
            except KeyError:
                print 'unk packet', hex(packet)
                raise
            fmt = ''.join(('>', fmt))
            size = struct.calcsize(fmt)
            if len(data) > size:
                args = struct.unpack(fmt, data[1:1 + size])
                name = self.packets.num_names[packet]
                self.d('>', name, args)
                self.recv_callback(name, args)
                data = data[1 + size:]
            else:
                break
        self.data = data

    def d(self, rw, packet, args):
        if packet in ('space_object', 'ship_stats'):
            return
        sys.stderr.write(' '.join((rw, packet, repr(args), '\n')))
        sys.stderr.flush()
import sys
