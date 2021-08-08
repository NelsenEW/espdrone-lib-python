#!/bin/bash
# Install the Espdrone PC client and set up permissions so that it can be used
# by the current user immediately
# Caution! This installs the Espdrone PC client as root to your Python
# site-packages directory. If you wish to install it as a normal user, use the
# instructions on the Wiki at
# http://wiki.bitcraze.se/projects:espdrone:pc_utils:install
# After installation, the Espdrone PC client can be started with `edclient`.
# @author Daniel Lee 2013

# Allow user to use USB radio without root permission
groupadd plugdev
usermod -a -G plugdev $USER
echo SUBSYSTEM==\"usb\", ATTRS{idVendor}==\"1915\", ATTRS{idProduct}==\"7777\", \
MODE=\"0664\", GROUP=\"plugdev\" > /etc/udev/rules.d/99-crazyradio.rules
echo SUBSYSTEM==\"usb\", ATTRS{idVendor}==\"0483\", ATTRS{idProduct}==\"5740\", \
MODE=\"0664\", GROUP=\"plugdev\" > /etc/udev/rules.d/99-espdrone.rules

# Install Espdrone PC client
python3 setup.py install
