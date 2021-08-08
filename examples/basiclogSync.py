# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2016 Bitcraze AB
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

This example utilizes the SyncEspdrone and SyncLogger classes.
"""
import logging
import time
import argparse

import edlib.crtp
from edlib.espdrone import Espdrone
from edlib.espdrone.log import LogConfig
from edlib.espdrone.syncEspdrone import SyncEspdrone
from edlib.espdrone.syncLogger import SyncLogger

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)


if __name__ == '__main__':
    # Initialize the low-level drivers (don't list the debug drivers)
    edlib.crtp.init_drivers(enable_debug_driver=False)
    parser = argparse.ArgumentParser()
    parser.add_argument("--uri", help='The ip address of the drone, e.g. "192.168.0.102"')
    args = parser.parse_args()
    if args.uri:
        uri = args.uri
    else:
        uri = '192.168.43.42'
   
    lg_stab = LogConfig(name='Stabilizer', period_in_ms=10)
    lg_stab.add_variable('stabilizer.roll', 'float')
    lg_stab.add_variable('stabilizer.pitch', 'float')
    lg_stab.add_variable('stabilizer.yaw', 'float')

    ed = Espdrone(rw_cache='./cache')
    with SyncEspdrone(uri, ed=ed) as sed:
        with SyncLogger(sed, lg_stab) as logger:
            endTime = time.time() + 10

            for log_entry in logger:
                timestamp = log_entry[0]
                data = log_entry[1]
                logconf_name = log_entry[2]

                print('[%d][%s]: %s' % (timestamp, logconf_name, data))

                if time.time() > endTime:
                    break
