#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2011-2013 Bitcraze AB
#
#  Espdrone Nano Quadcopter Client
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA  02110-1301, USA.
""" CRTP UDP Driver. Work either with the UDP server or with an UDP device
See udpserver.py for the protocol"""
import re
import struct
import sys
import binascii
import ipaddress
from socket import *

from .crtpdriver import CRTPDriver
from .crtpstack import CRTPPacket
from .exceptions import WrongUriType
if sys.version_info < (3,):
    import Queue as queue
else:
    import queue

__author__ = 'Bitcraze AB'
__all__ = ['UdpDriver']


class UdpDriver(CRTPDriver):

    def __init__(self):
        self.link_error_callback = None
        self.link_quality_callback = None
        self.in_queue = None
        self.out_queue = None
        self._thread = None
        self.needs_resending = False
        self.link_keep_alive = 0 #keep alive when no input device
        None

    def connect(self, uri, linkQualityCallback, linkErrorCallback):
        # check if the URI is a radio URI
        try:
            ipaddress.ip_address(uri)
        except ValueError:
            raise WrongUriType('Not an IP URI')
        
        self.queue = queue.Queue()
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.addr = (uri, 2390)
        self.connected = False
        i = 0
        while not self.connected:
            try:
                self.socket.bind(('', 2390 + i))
                self.connected = True
            except OSError:
                i += 1
    
        self.socket.connect(self.addr)
        str1=b'\xFF\x01\x01\x01'
        self.socket.sendto(str1,self.addr)

    def receive_packet(self, time=0):
        data, addr = self.socket.recvfrom(1024)
        if data:
            pk = CRTPPacket(data[0], list(data[1:(len(data)-1)]))
            self.link_keep_alive += 1
            if self.link_keep_alive > 10:
                str1 = b'\xFF\x01\x01\x01'
                self.socket.sendto(str1, self.addr)
                self.link_keep_alive = 0
            return pk

        try:
            if time == 0:
                return self.rxqueue.get(False)
            elif time < 0:
                while True:
                    return self.rxqueue.get(True, 10)
            else:
                return self.rxqueue.get(True, time)
        except queue.Empty:
            return None

    def send_packet(self, pk):
        raw = (pk.header,) + pk.datat
        cksum = 0
        for i in raw:
            cksum += i
        cksum %= 256
        raw = raw + (cksum,)
        data = ''.join(chr(v) for v in raw )
        self.socket.sendto(data.encode('latin'), self.addr)
        self.link_keep_alive = 0

    def close(self):
        str1=b'\xFF\x01\x01\x01'
        self.socket.sendto(str1, self.addr)
        self.socket.close()

    def get_name(self):
        return 'udp'

    def scan_interface(self, address):
        return [[address, ""]]
