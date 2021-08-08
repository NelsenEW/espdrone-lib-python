#!/usr/bin/env python
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
Subsytem handling localization-related data communication
"""
import collections
import logging
import struct
import math

from typing import List
from edlib.crtp.crtpstack import CRTPPacket
from edlib.crtp.crtpstack import CRTPPort
from edlib.utils.callbacks import Caller

__author__ = 'Bitcraze AB'
__all__ = ['Localization', 'LocalizationPacket']

logger = logging.getLogger(__name__)

# A generic location packet contains type and data. When received the data
# may be decoded by the lib.
LocalizationPacket = collections.namedtuple('localizationPacket',
                                            ['type', 'raw_data', 'data'])


class Localization():
    """
    Handle localization-related data communication with the Espdrone
    """

    # Implemented channels
    POSITION_CH = 0
    GENERIC_CH = 1

    # Location message types for generig channel
    RANGE_STREAM_REPORT = 0
    RANGE_STREAM_REPORT_FP16 = 1
    LPS_SHORT_LPP_PACKET = 2
    EMERGENCY_STOP = 3
    EMERGENCY_STOP_WATCHDOG = 4
    COMM_GNSS_NMEA = 6
    COMM_GNSS_PROPRIETARY = 7
    EXT_POSE = 8
    EXT_POSE_PACKED = 9
    EMERGENCY_RESET = 10

    def __init__(self, espdrone=None):
        """
        Initialize the Extpos object.
        """
        self._ed = espdrone

        self.receivedLocationPacket = Caller()
        self._ed.add_port_callback(CRTPPort.LOCALIZATION, self._incoming)

    def _incoming(self, packet):
        """
        Callback for data received from the copter.
        """
        if len(packet.data) < 1:
            logger.warning('Localization packet received with incorrect' +
                           'length (length is {})'.format(len(packet.data)))
            return

        pk_type = struct.unpack('<B', packet.data[:1])[0]
        data = packet.data[1:]

        # Decoding the known packet types
        # TODO: more generic decoding scheme?
        decoded_data = None
        if pk_type == self.RANGE_STREAM_REPORT:
            if len(data) % 5 != 0:
                logger.error('Wrong range stream report data lenght')
                return
            decoded_data = {}
            raw_data = data
            for i in range(int(len(data) / 5)):
                anchor_id, distance = struct.unpack('<Bf', raw_data[:5])
                decoded_data[anchor_id] = distance
                raw_data = raw_data[5:]
        elif pk_type == self.LH_PERSIST_DATA:
            decoded_data = bool(data[0])
        elif pk_type == self.LH_ANGLE_STREAM:
            decoded_data = self._decode_lh_angle(data)

        pk = LocalizationPacket(pk_type, data, decoded_data)
        self.receivedLocationPacket.call(pk)

    def send_extpos(self, pos):
        """
        Send the current Espdrone X, Y, Z position. This is going to be
        forwarded to the Espdrone's position estimator.
        """

        pk = CRTPPacket()
        pk.port = CRTPPort.LOCALIZATION
        pk.channel = self.POSITION_CH
        pk.data = struct.pack('<fff', pos[0], pos[1], pos[2])
        self._ed.send_packet(pk)

    def send_extpose(self, pos, quat):
        """
        Send the current Espdrone pose (position [x, y, z] and
        attitude quaternion [qx, qy, qz, qw]). This is going to be forwarded
        to the Espdrone's position estimator.
        """

        pk = CRTPPacket()
        pk.port = CRTPPort.LOCALIZATION
        pk.channel = self.GENERIC_CH
        pk.data = struct.pack('<Bfffffff',
                              self.EXT_POSE,
                              pos[0], pos[1], pos[2],
                              quat[0], quat[1], quat[2], quat[3])
        self._ed.send_packet(pk)

    def send_short_lpp_packet(self, dest_id, data):
        """
        Send ultra-wide-band LPP packet to dest_id
        """

        pk = CRTPPacket()
        pk.port = CRTPPort.LOCALIZATION
        pk.channel = self.GENERIC_CH
        pk.data = struct.pack('<BB', self.LPS_SHORT_LPP_PACKET, dest_id) + data
        self._ed.send_packet(pk)

    def send_emergency_stop(self):
        """
        Send emergency stop
        """

        pk = CRTPPacket()
        pk.port = CRTPPort.LOCALIZATION
        pk.channel = self.GENERIC_CH
        pk.data = struct.pack('<B', self.EMERGENCY_STOP)
        self._ed.send_packet(pk)

    def send_emergency_reset(self):
        """
        Send emergency reset
        """

        pk = CRTPPacket()
        pk.port = CRTPPort.LOCALIZATION
        pk.channel = self.GENERIC_CH
        pk.data = struct.pack('<B', self.EMERGENCY_RESET)
        self._ed.send_packet(pk)  

    def send_emergency_stop_watchdog(self):
        """
        Send emergency stop watchdog
        """

        pk = CRTPPacket()
        pk.port = CRTPPort.LOCALIZATION
        pk.channel = self.GENERIC_CH
        pk.data = struct.pack('<B', self.EMERGENCY_STOP_WATCHDOG)
        self._ed.send_packet(pk)

    
    @staticmethod
    def quatdecompress(comp: int):
        q= [0] * 4
        sqrt1_2 = 0.70710678118654752440
        mask = (1 << 9) - 1
        i_largest = comp >> 30
        sum_squares = 0
        for i in range(3, -1, -1):
            if (i != i_largest):
                mag = comp & mask
                negbit = (comp >> 9) & 0x1
                comp = comp >> 10
                q[i] = sqrt1_2 * mag / mask
                if (negbit == 1):
                    q[i] = - q[i]
                sum_squares += q[i] * q[i]
                
        q[i_largest] = math.sqrt(1 - sum_squares)
        return q
    
    @staticmethod
    def quatcompress(q: List[float]):
        sqrt1_2 = 0.70710678118654752440
        i_largest = 0
        for i in range(1,4):
            if (math.fabs(q[i]) > math.fabs(q[i_largest])):
                i_largest = i
        negate = q[i_largest] < 0
        comp = i_largest
        for i in range(4):
            if i != i_largest:
                negbit = (q[i] < 0) ^ negate
                mag = int(((1 << 9) - 1) * math.fabs(q[i])/ sqrt1_2 + 0.5)
                comp = (comp << 10) | (negbit << 9) | mag
        
        return comp

