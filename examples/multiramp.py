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
Simple example that connects 2 Espdrones, ramp up-down the motors and
disconnects.
"""
import logging
import time
from threading import Thread
import argparse
import edlib
from edlib.espdrone import Espdrone

logging.basicConfig(level=logging.ERROR)


class MotorRampExample:
    """Example that connects to a Espdrone and ramps the motors up/down and
    the disconnects"""

    def __init__(self, link_uri):
        """ Initialize and run the example with the specified link_uri """

        self._ed = Espdrone(rw_cache='./cache')

        self._ed.connected.add_callback(self._connected)
        self._ed.disconnected.add_callback(self._disconnected)
        self._ed.connection_failed.add_callback(self._connection_failed)
        self._ed.connection_lost.add_callback(self._connection_lost)

        self._ed.open_link(link_uri)

        self.connected = True

        print('Connecting to %s' % link_uri)

    def _connected(self, link_uri):
        """ This callback is called form the Espdrone API when a Espdrone
        has been connected and the TOCs have been downloaded."""

        # Start a separate thread to do the motor test.
        # Do not hijack the calling thread!
        Thread(target=self._ramp_motors).start()

    def _connection_failed(self, link_uri, msg):
        """Callback when connection initial connection fails (i.e no Espdrone
        at the specified address)"""
        print('Connection to %s failed: %s' % (link_uri, msg))
        self.connected = False

    def _connection_lost(self, link_uri, msg):
        """Callback when disconnected after a connection has been made (i.e
        Espdrone moves out of range)"""
        print('Connection to %s lost: %s' % (link_uri, msg))
        self.connected = False

    def _disconnected(self, link_uri):
        """Callback when the Espdrone is disconnected (called in all cases)"""
        print('Disconnected from %s' % link_uri)
        self.connected = False

    def _ramp_motors(self):
        thrust_mult = 1
        thrust_step = 500
        thrust = 5000
        pitch = 0
        roll = 0
        yawrate = 0

        # Unlock startup thrust protection
        self._ed.commander.send_setpoint(0, 0, 0, 0)

        while thrust >= 5000:
            self._ed.commander.send_setpoint(roll, pitch, yawrate, thrust)
            time.sleep(0.1)
            if thrust >= 10000:
                thrust_mult = -1
            thrust += thrust_step * thrust_mult
        self._ed.commander.send_setpoint(0, 0, 0, 0)
        # Make sure that the last packet leaves before the link is closed
        # since the message queue is not flushed before closing
        time.sleep(0.1)
        self._ed.close_link()


if __name__ == '__main__':
    # Initialize the low-level drivers (don't list the debug drivers)
    edlib.crtp.init_drivers(enable_debug_driver=False)
    parser = argparse.ArgumentParser()
    parser.add_argument("--uri",  nargs='+', help='The ip addresses of the drone, e.g. "192.168.0.102 192.168.0.103"', required=True)
    args = parser.parse_args()
    multiple_le = [MotorRampExample(uri) for uri in args.uri]

    # The Espdrone lib doesn't contain anything to keep the application alive,
    # so this is where your application should do something. In our case we
    # are just waiting until all of them are disconnected
    connected = True

    # Connect the two espdrones and ramps them up-down
    while(any([le.connected for le in multiple_le])):
        time.sleep(0.1)
