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
Used for sending control setpoints to the Espdrone
"""
from edlib.espdrone.localization import Localization
import struct

from edlib.crtp.crtpstack import CRTPPacket
from edlib.crtp.crtpstack import CRTPPort

__author__ = 'Bitcraze AB'
__all__ = ['Commander']

TYPE_STOP = 0
TYPE_VELOCITY_WORLD = 1
TYPE_ZDISTANCE = 2
TYPE_HOVER = 5
TYPE_POSITION = 7
TYPE_FULL_STATE = 6


class Commander():
    """
    Used for sending control setpoints to the Espdrone
    """

    def __init__(self, espdrone=None):
        """
        Initialize the commander object. By default the commander is in
        +-mode (not x-mode).
        """
        self._ed = espdrone
        self._x_mode = False

    def set_client_xmode(self, enabled):
        """
        Enable/disable the client side X-mode. When enabled this recalculates
        the setpoints before sending them to the Espdrone.
        """
        self._x_mode = enabled

    def send_setpoint(self, roll, pitch, yaw, thrust):
        """
        Send a new control setpoint for roll/pitch/yaw/thrust to the copter

        The arguments roll/pitch/yaw/trust is the new setpoints that should
        be sent to the copter
        """
        if thrust > 0xFFFF or thrust < 0:
            raise ValueError('Thrust must be between 0 and 0xFFFF')

        if self._x_mode:
            roll, pitch = 0.707 * (roll - pitch), 0.707 * (roll + pitch)

        pk = CRTPPacket()
        pk.port = CRTPPort.COMMANDER
        pk.data = struct.pack('<fffH', roll, -pitch, yaw, thrust)
        self._ed.send_packet(pk)

    def send_stop_setpoint(self):
        """
        Send STOP setpoing, stopping the motors and (potentially) falling.
        """
        pk = CRTPPacket()
        pk.port = CRTPPort.COMMANDER_GENERIC
        pk.data = struct.pack('<B', TYPE_STOP)
        self._ed.send_packet(pk)

    def send_velocity_world_setpoint(self, vx, vy, vz, yawrate):
        """
        Send Velocity in the world frame of reference setpoint.

        vx, vy, vz are in m/s
        yawrate is in degrees/s
        """
        pk = CRTPPacket()
        pk.port = CRTPPort.COMMANDER_GENERIC
        pk.data = struct.pack('<Bffff', TYPE_VELOCITY_WORLD,
                              vx, vy, vz, yawrate)
        self._ed.send_packet(pk)

    def send_zdistance_setpoint(self, roll, pitch, yawrate, zdistance):
        """
        Control mode where the height is send as an absolute setpoint (intended
        to be the distance to the surface under the Crazflie).

        Roll, pitch, yawrate are defined as degrees, degrees, degrees/s
        """
        pk = CRTPPacket()
        pk.port = CRTPPort.COMMANDER_GENERIC
        pk.data = struct.pack('<Bffff', TYPE_ZDISTANCE,
                              roll, pitch, yawrate, zdistance)
        self._ed.send_packet(pk)

    def send_hover_setpoint(self, vx, vy, yawrate, zdistance):
        """
        Control mode where the height is send as an absolute setpoint (intended
        to be the distance to the surface under the Crazflie).

        vx and vy are in m/s
        yawrate is in degrees/s
        """
        pk = CRTPPacket()
        pk.port = CRTPPort.COMMANDER_GENERIC
        pk.data = struct.pack('<Bffff', TYPE_HOVER,
                              vx, vy, yawrate, zdistance)
        self._ed.send_packet(pk)

    def send_full_state_setpoint(self, x, y, z, vx, vy, vz, ax, ay, az, quat_x, quat_y, quat_z, quat_w, rate_roll, rate_pitch, rate_yaw):
        """
        Full state control!
        """
        pk = CRTPPacket()
        pk.port = CRTPPort.COMMANDER_GENERIC
        pk.data = struct.pack('<Bhhhhhhhhhihhh', TYPE_POSITION,
                            x * 1000, y * 1000, z * 1000,
                            vx * 1000, vy * 1000, vz * 1000,
                            ax * 1000, ay * 1000, az * 1000,
                            Localization.quatcompress([quat_x, quat_y, quat_z, quat_w]),
                            rate_roll * 1000, rate_pitch * 1000, rate_yaw * 1000)
        self._ed.send_packet(pk)


    def send_position_setpoint(self, x, y, z, yaw):
        """
        Control mode where the position is sent as absolute x,y,z coordinate in
        meter and the yaw is the absolute orientation.

        x and y are in m
        yaw is in degrees
        """
        pk = CRTPPacket()
        pk.port = CRTPPort.COMMANDER_GENERIC
        pk.data = struct.pack('<Bffff', TYPE_POSITION,
                              x, y, z, yaw)
        self._ed.send_packet(pk)
