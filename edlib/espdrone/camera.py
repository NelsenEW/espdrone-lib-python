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


from edlib.utils.callbacks import Caller

import gc
import time
import numpy as np
import cv2
from urllib.request import urlopen
import threading
import requests

class Camera():
    """
    Handle camera-related data communication with the Espdrone
    """
    CAMERA_BUFFER_SIZE = 4096
    def __init__(self, espdrone = None):
        """
        Initialize the camera object.
        """
        self._ed = espdrone
        self.image_received_cb = Caller()
        self._stream = False
        
    def _capture_frames(self):
        bts = b''
        while self._stream and self._ed.link:
            try:
                start_time = time.time()
                bts+= self._file_stream.read(self.CAMERA_BUFFER_SIZE)
                jpghead=bts.find(b'\xff\xd8')
                jpgend=bts.find(b'\xff\xd9')
                if jpghead>-1 and jpgend>-1:
                    jpg=bts[jpghead:jpgend+2]
                    bts=bts[jpgend+2:]
                    image=cv2.imdecode(np.frombuffer(jpg,dtype=np.uint8),cv2.IMREAD_UNCHANGED)
                    fps = 1 / (time.time() - start_time)
                    if self._stream:
                        self.image_received_cb.call(image, fps)
                    

            except Exception as e:
                print("Error:" + str(e))
                bts=b''
                self._file_stream = urlopen(self._url)
                continue
        self._file_stream.close()
        self._stream = False

    def _is_streaming(self):
        return (hasattr(self, '_thread') and self._thread.isAlive())

    def start(self):
        try:
            self._url = 'http://' + self._ed.link_uri + "/stream.jpg"
            self._file_stream = urlopen(self._url)
            if not self._is_streaming():
                self._stream = True
                self._thread = threading.Thread(target=self._capture_frames, daemon=True)
                self._thread.start()
        except Exception as e:
            print(e)      

    def stop(self):
        if hasattr(self, '_thread'):
            self._file_stream.close()
            self._stream = False
            self._thread.join()
    
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()