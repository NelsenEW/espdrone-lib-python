# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2017 Bitcraze AB
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
Simple example that connects to the first Espdrone found, and then sends the
reboot signals to 6 anchors ID from 0 to 5. The reset signals is sent
10 times in a row to make sure all anchors are reset to bootloader.
"""
import logging
import time
from threading import Thread

import edlib
from edlib.espdrone import Espdrone
from lpslib.lopoanchor import LoPoAnchor

logging.basicConfig(level=logging.ERROR)


class LpsRebootToBootloader:
    """Example that connects to a Espdrone and ramps the motors up/down and
    the disconnects"""

    def __init__(self, link_uri):
        """ Initialize and run the example with the specified link_uri """

        self._ed = Espdrone()

        self._ed.connected.add_callback(self._connected)
        self._ed.disconnected.add_callback(self._disconnected)
        self._ed.connection_failed.add_callback(self._connection_failed)
        self._ed.connection_lost.add_callback(self._connection_lost)

        self._ed.open_link(link_uri)

        print('Connecting to %s' % link_uri)

    def _connected(self, link_uri):
        """ This callback is called form the Espdrone API when a Espdrone
        has been connected and the TOCs have been downloaded."""

        # Start a separate thread to do the motor test.
        # Do not hijack the calling thread!
        Thread(target=self._reboot_thread).start()

    def _connection_failed(self, link_uri, msg):
        """Callback when connection initial connection fails (i.e no Espdrone
        at the specified address)"""
        print('Connection to %s failed: %s' % (link_uri, msg))

    def _connection_lost(self, link_uri, msg):
        """Callback when disconnected after a connection has been made (i.e
        Espdrone moves out of range)"""
        print('Connection to %s lost: %s' % (link_uri, msg))

    def _disconnected(self, link_uri):
        """Callback when the Espdrone is disconnected (called in all cases)"""
        print('Disconnected from %s' % link_uri)

    def _reboot_thread(self):

        anchors = LoPoAnchor(self._ed)

        print('Sending reboot signal to all anchors 10 times in a row ...')
        for retry in range(10):
            for anchor_id in range(6):
                anchors.reboot(anchor_id, anchors.REBOOT_TO_BOOTLOADER)
                time.sleep(0.1)

        self._ed.close_link()


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
        le = LpsRebootToBootloader(available[0][0])
    else:
        print('No Espdrones found, cannot run example')
