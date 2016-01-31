#!/usr/bin/python
# -*- coding: utf-8 -*-

import binascii #pour convertir l'hexa en string
from urllib2 import Request, urlopen, URLError, HTTPError #pour pouvoir appeler une url
import socket #pour afficher gérer les sockets (utilisé ici que pour afficher une erreur de timeout)

import usb.core
import usb.util
import sys
import time

def show_result(bytes):
    sys.stdout.write("Result:")
    sys.stdout.write(''.join(['%d ' % abyte for abyte in bytes]))

# show all devices
# print usb.core.show_devices(verbose=True)
# exit(0)

# find mir:ror
dev = usb.core.find( idVendor=0x1da8, idProduct=0x1301)
print dev

reattach = False
if dev.is_kernel_driver_active(0):
    reattach = True
    dev.detach_kernel_driver(0)

dev.set_configuration()

endpoint_in = dev[0][(0,0)][0]
endpoint_out = dev[0][(0,0)][1]

print ("endpoint_out",endpoint_out)
print ("endpoint_in",endpoint_in)

msg = b'\x81'

while 1:

        #endpoint_out.write(msg)

        # reading
        print ("Waiting to read...")
        print (endpoint_in.bEndpointAddress)
        bytes = dev.read(endpoint_in.bEndpointAddress, 64, 1000)
        show_result(bytes)
        time.sleep(100)

    # end while


# This is needed to release interface, otherwise attach_kernel_driver fails
# due to "Resource busy"
usb.util.dispose_resources(dev)

# It may raise USBError if there's e.g. no kernel driver loaded at all
if reattach:
    dev.attach_kernel_driver(0)

exit(0)
