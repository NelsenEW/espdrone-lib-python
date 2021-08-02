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
"""
The Espdrone Micro Quadcopter library API used to communicate with the
Espdrone Micro Quadcopter via a communication link.

The API takes care of scanning, opening and closing the communication link
as well as sending/receiving data from the Espdrone.

A link is described using an URI of the following format:
    <interface>://<interface defined data>.
See each link for the data that can be included in the URI for that interface.

The two main uses-cases are scanning for Espdrones available on a
communication link and opening a communication link to a Espdrone.

Example of scanning for available Espdrones on all communication links:
edlib.crtp.init_drivers()
available = edlib.crtp.scan_interfaces()
for i in available:
    print "Found Espdrone on URI [%s] with comment [%s]"
            % (available[0], available[1])

Example of connecting to a Espdrone with know URI (radio dongle 0 and
radio channel 125):
ed = Espdrone()
ed.open_link("radio://0/125")
...
ed.close_link()
"""
