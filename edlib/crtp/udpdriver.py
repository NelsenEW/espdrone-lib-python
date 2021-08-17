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

import logging
import ipaddress
from queue import Queue
import sys
from socket import *
import threading
import time

from .crtpdriver import CRTPDriver
from .crtpstack import CRTPPacket
from .exceptions import WrongUriType
if sys.version_info < (3,):
    import Queue as queue
else:
    import queue

__author__ = 'Bitcraze AB'
__all__ = ['UdpDriver']

logger = logging.getLogger(__name__)

class UdpDriver(CRTPDriver):
    """ Esp UDP link driver"""
    def __init__(self):
        """ Create the link driver """
        CRTPDriver.__init__(self)
        self.link_error_callback = None
        self.link_quality_callback = None
        self.in_queue = None
        self.out_queue = None
        self._thread = None

    def connect(self, uri, link_quality_callback, link_error_callback):
        """
        Connect the link driver to a specific IP address:

        The callback for linkQuality is not yet available (RSSI is not yet implemented),
        The callback from linkError will be called when an error occures with an error message.
        """
        
        # check if the URI is a radio URI
        try:
            ipaddress.ip_address(uri)
        except ValueError:
            raise WrongUriType('Not an IP URI')
        
        self.queue = queue.Queue()
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.addr = (uri, 2390)
        allocated_port = False
        i = 0
        while not allocated_port:
            try:
                self.socket.bind(('', 2390 + i))
                allocated_port = True
            except OSError as e: # Unable to allocate port, try a different one
                i += 1
        self.socket.connect(self.addr)
        self.connected = True

        # Prepare the inter-thread communication queue
        self.in_queue = queue.Queue()
        
        #Launch the comm thread
        self._thread = _UdpDriverThread(self.socket,
                                        self.addr,
                                        self.in_queue,
                                        link_quality_callback,
                                        link_error_callback)

        self._thread.start()
        
        self.link_error_callback = link_error_callback

    def receive_packet(self, time=0):
        try:
            if time == 0:
                return self.in_queue.get(False)
            elif time < 0:
                return self.in_queue.get(True)
            else:
                return self.in_queue.get(True, time)
        except queue.Empty:
            return None

    def send_packet(self, pk: CRTPPacket):
        """ Send the packet pk through the link """
        raw = (pk.header,) + pk.datat
        cksum = 0
        for i in raw:
            cksum += i
        cksum %= 256
        raw = raw + (cksum,)
        data = ''.join(chr(v) for v in raw )
        if self.connected:
            self.socket.sendto(data.encode('latin'), self.addr)

    def pause(self):
        self._thread.stop()
        self._thread = None
    
    def restart(self):
        if self._thread:
            return
        self.socket.connect(self.addr)
        self._thread = _UdpDriverThread(self.socket,
                                self.addr,
                                self.in_queue,
                                self.link_quality_callback,
                                self.link_error_callback)
        


    def close(self):
        self.connected = False
        # Stop the comm thread
        self._thread.stop()
        # Clear callbacks
        self.link_error_callback = None
        self.link_quality_callback = None


    def get_name(self):
        return 'udp'

    def scan_interface(self, address):
        return [[address, ""]]

# Transmit/receive udp thread

class _UdpDriverThread(threading.Thread):
    """
    Udp link receiver thread used to read data from the
    Udp driver. """

    KEEP_ALIVE_MAX_COUNT = 10

    def __init__(self, socket: socket, addr, in_queue: Queue,
                 link_quality_callback, link_error_callback):
        """ Create the object """
        threading.Thread.__init__(self)
        self._socket = socket
        self._addr = addr
        self._in_queue = in_queue
        self._sp = False
        self._link_error_callback = link_error_callback
        self._link_quality_callback = link_quality_callback
        self._keep_alive_bytearray = b'\xFF\x01\x01\x01'
        self.link_keep_alive = 0 #keep alive when no input device
        # Add this to the server clients list
        self._socket.sendto(self._keep_alive_bytearray,self._addr)
        self._socket.settimeout(3)
        self.daemon = True

    def stop(self):
        """ Stop the thread """
        self._sp = True
        self._socket.sendto(self._keep_alive_bytearray, self._addr)
        self._socket.close()
        try:
            self.join()
        except Exception as e:
            import traceback
            print(e, traceback.format_exc())
    
    def run(self):
        """ Run the receiver thread """
        while not self._sp:
            try:
                data = self._socket.recv(1024)
                if data:
                    self.link_keep_alive +=1
                    pk = CRTPPacket(data[0], list(data[1:(len(data)-1)]))
                    self._in_queue.put(pk)
                    if (self.link_keep_alive > self.KEEP_ALIVE_MAX_COUNT) and not self._sp:
                        self._socket.sendto(self._keep_alive_bytearray, self._addr)
            except timeout:
                self._link_error_callback(
                    'Connection timeout!'
                )
            except OSError:
                pass # When socket has been closed, it causes bad file descriptor.
