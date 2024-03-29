#!/usr/bin/env python
"""
Bridge a Espdrone connected to a Crazyradio to a local MAVLink port
Requires 'pip install edlib'

As the ESB protocol works using PTX and PRX (Primary Transmitter/Reciever)
modes. Thus, data is only recieved as a response to a sent packet.
So, we need to constantly poll the receivers for bidirectional communication.

@author: Dennis Shtatnov (densht@gmail.com)

Based off example code from espdrone-lib-python/examples/read-eeprom.py
"""
# import struct
import logging
import socket
import sys
import threading
import time

import edlib.crtp
from edlib.espdrone import Espdrone
from edlib.crtp.crtpstack import CRTPPacket
# from edlib.crtp.crtpstack import CRTPPort

CRTP_PORT_MAVLINK = 8


# Only output errors from the logging framework
logging.basicConfig(level=logging.DEBUG)


class RadioBridge:
    def __init__(self, link_uri):
        """ Initialize and run the example with the specified link_uri """

        # UDP socket for interfacing with GCS
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind(('127.0.0.1', 14551))

        # Create a Espdrone object without specifying any cache dirs
        self._ed = Espdrone()

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

        threading.Thread(target=self._server).start()

    def _connected(self, link_uri):
        """ This callback is called form the Espdrone API when a Espdrone
        has been connected and the TOCs have been downloaded."""
        print('Connected to %s' % link_uri)

        self._ed.packet_received.add_callback(self._got_packet)

    def _got_packet(self, pk):
        if pk.port == CRTP_PORT_MAVLINK:
            self._sock.sendto(pk.data, ('127.0.0.1', 14550))

    def _forward(self, data):
        pk = CRTPPacket()
        pk.port = CRTP_PORT_MAVLINK  # CRTPPort.COMMANDER
        pk.data = data  # struct.pack('<fffH', roll, -pitch, yaw, thrust)
        self._ed.send_packet(pk)

    def _server(self):
        while True:
            print('\nwaiting to receive message')

            # Only receive what can be sent in one message
            data, address = self._sock.recvfrom(256)

            print('received %s bytes from %s' % (len(data), address))

            for i in range(0, len(data), 30):
                self._forward(data[i:(i+30)])

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
    edlib.crtp.radiodriver.set_retries_before_disconnect(1500)
    edlib.crtp.radiodriver.set_retries(3)
    edlib.crtp.init_drivers(enable_debug_driver=False)
    # Scan for Espdrones and use the first one found
    print('Scanning interfaces for Espdrones...')
    if len(sys.argv) > 2:
        address = int(sys.argv[2], 16)  # address=0xE7E7E7E7E7
    else:
        address = None

    available = edlib.crtp.scan_interfaces(address)
    print('Espdrones found:')
    for i in available:
        print(i[0])

    if len(available) > 0:
        if len(sys.argv) > 1:
            channel = str(sys.argv[1])
        else:
            channel = 80

        link_uri = 'radio://0/' + str(channel) + '/2M'
        le = RadioBridge(link_uri)  # (available[0][0])

    # The Espdrone lib doesn't contain anything to keep the application alive,
    # so this is where your application should do something. In our case we
    # are just waiting until we are disconnected.
    try:
        while le.is_connected:
            time.sleep(1)
    except KeyboardInterrupt:
        sys.exit(1)
