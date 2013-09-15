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

from collections import namedtuple
import logging
import socket
import struct
from threading import RLock

HANDSHAKE = '\x69\x83\x82\xe2\xf4\x63\x22\x3b\x13\x91\xba\x28\x9b\x6f\x3d\x1d'

PACKETS = [
    0x00, 'ping', 'x',                      # () c <-> s
    0x01, 'handshake', '16s',               # (handshake, ) c -> s
    0x02, 'login', 'BB32p16s',              # (version,, name, authkey) c -> s
    0x03, 'login_confirm', 'x',             # () s -> c
    
    0x10, 'client_info', 'BBB',             # (color,,, ) c -> s
    0x11, 'viewpoint', 'I',                 # (id, ) s -> c
    0x12, 'flash_ui', 'BBBB',               # (what, color,,,) s -> c
    
    0x20, 'space_object', 'Iddf',           # (id, pos,, direction) s -> c
    0x21, 'space_object_dead', 'I',         # (id, ) s -> c
    0x22, 'space_object_render', 'I10pB8f', # (id, cmd, num_args, args,,,,,,,,)
    0x23, 'space_object_name', 'I15pH',     # (id, name, operations) s -> c
    
    0x30, 'set_dest', 'dd',                 # (x, y) c -> s
    0x31, 'edit_ship', 'x',                 # () c -> s
    0x32, 'full_grid', '32p121H121B',       # (title, items, damage) s -> c
    0x33, 'small_grid', 'x',                # not implemented
    0x34, 'cargo_clear', 'x',               # () s <-> c (also, req)
    0x35, 'cargo_item', 'HB',               # (item, damage) s -> c
    0x36, 'do_edit', 'bbHB',                # (pos,, replacewith)
    0x37, 'engineering_clear', 'x',         # () s <-> c (also, req)
    0x38, 'engineering_option', 'H',        # (item,) s -> c
    0x39, 'engineer_item', 'H',             # (item,) c -> s
    
    0x40, 'operate', 'IH',                  # (target, operation) c -> s
    
    0xff, 'disconnect', '32p',              # (reason, ) c <-> s
]

def parse_packets():
    num_names = dict()
    name_nums = dict()
    num_fmts = dict()
    for i in range(0, len(PACKETS), 3):
        num, name, fmt = PACKETS[i:i+3]
        num_names[num] = name
        name_nums[name] = num
        num_fmts[num] = fmt
    Packets = namedtuple('Packets', ['num_names', 'name_nums', 'num_fmts'])
    return Packets(num_names, name_nums, num_fmts)

def server_connection(port):
    sock = None
    for res in socket.getaddrinfo(None, port, socket.AF_UNSPEC,
                                  socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
        af, socktype, proto, canonname, sa = res
        try:
            sock = socket.socket(af, socktype, proto)
        except socket.error:
            sock = None
            continue
        try:
            sock.bind(sa)
            sock.listen(1)
        except socket.error:
            sock.close()
            sock = None
            continue
        break
    return sock


def str_to_floats(text):
    '''Function to convert string to floats, for render text'''
    text += '   ' # 3 spaces
    floats = list()
    for i in range(0, min(len(text), 32), 4):
        sub_text = text[i:i+4]
        f = struct.unpack('>f', struct.pack('>4s', sub_text))[0]
        floats.append(f)
    return floats

def floats_to_str(floats):
    '''Function to convert floats to string, for render text'''
    text = str()
    for f in floats:
        text += struct.unpack('>4s', struct.pack('>f', f))[0]
    return text.rstrip()

class NetworkReciever(object):
    '''Custom socket interface, n.b.: passing `None` as `address` will create
    a listening socket (for servers)'''
    def __init__(self, address=None, port=None, sock=None):
        self.packets = parse_packets()
        self.addr = address
        self.conn = None
        if sock is not None:
            self.conn = sock
        elif address is None:
            self.conn = server_connection(port)
        else:
            self.conn = socket.create_connection((address, port))
        self.print_lock = RLock()
    def __getattr__(self, name):
        return getattr(self.conn, name)
    def accept(self):
        conn, addr = self.conn.accept()
        return NetworkReciever(address=addr, sock=conn)
    def send(self, packet_name, *args, **kwargs):
#        with self.print_lock:
#            print '@ >>>', packet_name, args
        num = self.packets.name_nums[packet_name]
        if kwargs.get('raw', False):
            data = args[0]
        else:
            fmt = self.packets.num_fmts[num]
            data = struct.pack('>' + fmt, *args)
        head = struct.pack('>B', num)
        to_send = ''.join((head, data))
        sent_len = self.conn.send(to_send)
        if sent_len != len(to_send):
            logging.error('Packet may not have been delivered')
    def recv(self):
        packet_id = self.conn.recv(1)
        if not packet_id:
            self.close('socket died')
        num = struct.unpack('>B', packet_id)[0]
        fmt = '>' + self.packets.num_fmts[num]
        size = struct.calcsize(fmt)
        data = self.conn.recv(size)
        res = struct.unpack(fmt, data)
        packet_name = self.packets.num_names[num]
#        with self.print_lock:
#            if packet_name != 'space_object':
#                print '@ <<<', packet_name, res
        return (packet_name,) + res
    def close(self, reason):
        try:
            self.send('disconnect', reason)
        except socket.error:
            pass
        self.conn.close()
        self.conn = None
    def __del__(self):
        if self.conn is not None and self.addr is not None:
            self.close('NR object deleted')
    
