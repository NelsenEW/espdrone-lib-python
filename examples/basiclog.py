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
Simple example that connects to the first Espdrone found, logs the Stabilizer
and prints it to the console. After 10s the application disconnects and exits.
"""
import logging
import time
from threading import Timer
import argparse
import edlib.crtp  # noqa
from edlib.espdrone import Espdrone
from edlib.espdrone.log import LogConfig

# Only output errors from the logging framework
logging.basicConfig(level = logging.ERROR,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class LoggingExample:
    """
    Simple logging example class that logs the Stabilizer from a supplied
    link uri and disconnects after 10s.
    """

    def __init__(self, link_uri):
        """ Initialize and run the example with the specified link_uri """

        self._ed = Espdrone(rw_cache='./cache')

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

    def _connected(self, link_uri):
        """ This callback is called form the Espdrone API when a Espdrone
        has been connected and the TOCs have been downloaded."""
        print('Connected to %s' % link_uri)

        # The definition of the logconfig can be made before connecting
        self._lg_stab = LogConfig(name='Stabilizer', period_in_ms=10)
        self._lg_stab.add_variable('stabilizer.roll', 'float')
        self._lg_stab.add_variable('stabilizer.pitch', 'float')
        self._lg_stab.add_variable('stabilizer.yaw', 'float')

        # Adding the configuration cannot be done until a Espdrone is
        # connected, since we need to check that the variables we
        # would like to log are in the TOC.
        try:
            self._ed.log.add_config(self._lg_stab)
            # This callback will receive the data
            self._lg_stab.data_received_cb.add_callback(self._stab_log_data)
            # This callback will be called on errors
            self._lg_stab.error_cb.add_callback(self._stab_log_error)
            # Start the logging
            self._lg_stab.start()
        except KeyError as e:
            print('Could not start log configuration,'
                  '{} not found in TOC'.format(str(e)))
        except AttributeError:
            print('Could not add Stabilizer log config, bad configuration.')

        # Start a timer to disconnect in 10s
        t = Timer(10, self._ed.close_link)
        t.start()

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
    parser = argparse.ArgumentParser()
    parser.add_argument("--uri", help='The ip address of the drone, e.g. "192.168.0.102"')
    args = parser.parse_args()
    if args.uri:
        le = LoggingExample(args.uri)
    else:
        available = edlib.crtp.scan_interfaces()
        print('Espdrones found:')
        if available:
            print(available[0])
            le = LoggingExample(available[0][0])
        else:
            quit()
   
    # The Espdrone lib doesn't contain anything to keep the application alive,
    # so this is where your application should do something. In our case we
    # are just waiting until we are disconnected.
    while le.is_connected:
        time.sleep(1)
