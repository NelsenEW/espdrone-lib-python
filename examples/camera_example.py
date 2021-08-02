#!/usr/bin/env python3
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
#  Espdrone Python Library
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
Example scipts that allows a user to see images from the camera of the drone

This examples uses camera feature of the drone to stream images
The demo is ended by either pressing Ctrl-C

For the example to run the following hardware is needed:
 * ESP Drone - NH
 * Camera
"""
import logging
import argparse

import edlib.crtp  # noqa
from edlib.espdrone import Espdrone
from edlib.espdrone.syncEspdrone import SyncEspdrone
from edlib.utils.camera import Camera
import cv2


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

    ed = Espdrone(rw_cache='./cache')
    with SyncEspdrone(uri, ed=ed) as sed:
        with Camera(sed) as camera:
            while True:
                if camera.image is not None:
                    cv2.imshow('unique_window_identifier',camera.image)
                    cv2.setWindowTitle("unique_window_identifier", f"fps= {camera.fps}")
                    if cv2.waitKey(1) == ord('q'):
                        break
            cv2.destroyAllWindows()