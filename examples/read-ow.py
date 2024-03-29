# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2014 Bitcraze AB
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
"""
Simple example that connects to the first Espdrone found, looks for
1-wire memories and lists its contents.
"""
import logging
import sys
import time

import edlib.crtp  # noqa
from edlib.espdrone import Espdrone
from edlib.espdrone.mem import MemoryElement

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)


class OWExample:
    """
    Simple example listing the 1-wire memories found and lists its contents.
    """

    def __init__(self, link_uri):
        """ Initialize and run the example with the specified link_uri """

        # Create a Espdrone object without specifying any cache dirs
        self._ed = Espdrone()

        # Connect some callbacks from the Espdrone API
        self._ed.connected.add_callback(self._connected)
        self._ed.disconnected.add_callback(self._disconnected)
        self._ed.connection_failed.add_callback(self._connection_failed)
        self._ed.connection_lost.add_callback(self._connection_lost)

        print('Connecting to %s' % link_uri)

        # Try to connect to the Espdrone
        self._ed.open_link(link_uri)

        # Variable used to keep main loop occupied until disconnect
        self.is_connected = True
        self._mems_to_update = 0

    def _connected(self, link_uri):
        """ This callback is called form the Espdrone API when a Espdrone
        has been connected and the TOCs have been downloaded."""
        print('Connected to %s' % link_uri)

        mems = self._ed.mem.get_mems(MemoryElement.TYPE_1W)
        self._mems_to_update = len(mems)
        print('Found {} 1-wire memories'.format(len(mems)))
        for m in mems:
            print('Updating id={}'.format(m.id))
            m.update(self._data_updated)

    def _data_updated(self, mem):
        print('Updated id={}'.format(mem.id))
        print('\tAddr      : {}'.format(mem.addr))
        print('\tType      : {}'.format(mem.type))
        print('\tSize      : {}'.format(mem.size))
        print('\tValid     : {}'.format(mem.valid))
        print('\tName      : {}'.format(mem.name))
        print('\tVID       : 0x{:02X}'.format(mem.vid))
        print('\tPID       : 0x{:02X}'.format(mem.pid))
        print('\tPins      : 0x{:02X}'.format(mem.pins))
        print('\tElements  : ')

        for key in mem.elements:
            print('\t\t{}={}'.format(key, mem.elements[key]))

        self._mems_to_update -= 1
        if self._mems_to_update == 0:
            self._ed.close_link()

    def _stab_log_error(self, logconf, msg):
        """Callback from the log API when an error occurs"""
        print('Error when logging %s: %s' % (logconf.name, msg))

    def _stab_log_data(self, timestamp, data, logconf):
        """Callback froma the log API when data arrives"""
        print('[%d][%s]: %s' % (timestamp, logconf.name, data))

    def _connection_failed(self, link_uri, msg):
        """Callback when connection initial connection fails (i.e no Espdrone
        at the speficied address)"""
        print('Connection to %s failed: %s' % (link_uri, msg))
        self.is_connected = False

    def _connection_lost(self, link_uri, msg):
        """Callback when disconnected after a connection has been made (i.e
        Espdrone moves out of range)"""
        print('Connection to %s lost: %s' % (link_uri, msg))

    def _disconnected(self, link_uri):
        """Callback when the Espdrone is disconnected (called in all cases)"""
        print('Disconnected from %s' % link_uri)
        self.is_connected = False


if __name__ == '__main__':
    # Initialize the low-level drivers (don't list the debug drivers)
    edlib.crtp.init_drivers(enable_debug_driver=False)
    # Scan for Espdrones and use the first one found
    print('Scanning interfaces for Espdrones...')
    available = edlib.crtp.scan_interfaces()
    print('Espdrones found:')
    for i in available:
        print(i[0])

    if len(available) > 0:
        le = OWExample(available[0][0])
    else:
        print('No Espdrones found, cannot run example')

    # The Espdrone lib doesn't contain anything to keep the application alive,
    # so this is where your application should do something. In our case we
    # are just waiting until we are disconnected.
    try:
        while le.is_connected:
            time.sleep(1)
    except KeyboardInterrupt:
        sys.exit(1)
