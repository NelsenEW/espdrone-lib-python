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
Espdrone console is used to receive characters printed using printf
from the firmware.
"""
from espdlib.crtp.crtpstack import CRTPPort
from espdlib.utils.callbacks import Caller

__author__ = 'Bitcraze AB'
__all__ = ['Console']


class Console:
    """
    Espdrone console is used to receive characters printed using printf
    from the firmware.
    """

    def __init__(self, espdrone):
        """
        Initialize the console and register it to receive data from the copter.
        """

        self.receivedChar = Caller()

        self.ed = espdrone
        self.ed.add_port_callback(CRTPPort.CONSOLE, self.incoming)

    def incoming(self, packet):
        """
        Callback for data received from the copter.
        """
        # This might be done prettier ;-)
        console_text = packet.data.decode('UTF-8')

        self.receivedChar.call(console_text)
