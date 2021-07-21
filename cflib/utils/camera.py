#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   _   _ _    _            _               ____   _____ 
#  | \ | | |  | |          | |        /\   |  _ \ / ____|
#  |  \| | |__| |  ______  | |       /  \  | |_) | (___  
#  | . ` |  __  | |______| | |      / /\ \ |  _ < \___ \ 
#  | |\  | |  | |          | |____ / ____ \| |_) |____) |
#  |_| \_|_|  |_|          |______/_/    \_\____/|_____/ 
#
#  Copyright (C) 2021 NH - LABS
#
#  ESP-DRONE NH
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
Subsystem handling camera-related data communication
"""

import struct
import time
import numpy as np
import cv2
import sys
if sys.version_info[0] < 3:
    from urllib2 import urlopen
else:
    from urllib.request import urlopen
import threading
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie




class Camera():
    """
    Handle camera-related data communication with the Crazyflie
    """
    CAMERA_BUFFER_SIZE = 4096
    def __init__(self, crazyflie):
        """
        Initialize the camera object.
        """
        if isinstance(crazyflie, SyncCrazyflie):
            self._cf = crazyflie.cf
        else:
            self._cf = crazyflie
        self._url = self._cf.link_uri.replace('udp', 'http')
        self._image = None
        self._fps = -1

    def _capture_frames(self):
        bts = b''
        while self._stream:
            try:
                start_time = time.time()
                bts+= self._file_stream.read(self.CAMERA_BUFFER_SIZE)
                jpghead=bts.find(b'\xff\xd8')
                jpgend=bts.find(b'\xff\xd9')
                if jpghead>-1 and jpgend>-1:
                    jpg=bts[jpghead:jpgend+2]
                    bts=bts[jpgend+2:]
                    self._image=cv2.imdecode(np.frombuffer(jpg,dtype=np.uint8),cv2.IMREAD_UNCHANGED)
                    self._fps = 1 / (time.time() - start_time)
            except Exception as e:
                print("Error:" + str(e))
                bts=b''
                self._file_stream = urlopen(self._url)
                continue

    def _is_streaming(self):
        return (hasattr(self, '_thread') and self._thread.isAlive())

    def start(self):
        try:
            self._file_stream = urlopen(self._url + "/stream.jpg")
            if not self._is_streaming():
                self._stream = True
                self._thread = threading.Thread(target=self._capture_frames)
                self._thread.start()
        except Exception as e:
            print(e)      

    def stop(self):
        if hasattr(self, '_thread'):
            self._stream = False
            self._thread.join()
    
    @property
    def image(self):
        if self._is_streaming():
            return self._image

    @property
    def fps(self):
        return self._fps
        
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()