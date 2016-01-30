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

'''
cat /sys/class/hidraw/hidraw2/device/uevent
DRIVER=hid-generic
HID_ID=0003:00001DA8:00001301
HID_NAME=Violet Mirror
HID_PHYS=usb-0000:00:1d.0-1.7/input0
HID_UNIQ=67BFEFFF
MODALIAS=hid:b0003g0001v00001DA8p00001301
'''


#ouverture du port hidraw0 (port du mir:ror) en mode lecture octet par octet (rb)
mirror = open("/dev/hidraw2", "rb")

erreur_generale = False
while erreur_generale == False:
  #on lit les données envoyées par le mir:ror
  try:
    donnee = mirror.read(16)
  except Exception as e:
    print "Erreur inconnue (lecture du  mir:ror) : %s" % e
    erreur_generale = True

  #on test les données renvoyées par le mir:ror
  if donnee != '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00':
    try:
      rfid_id = binascii.hexlify(donnee)[4:]
    except Exception as e:
      print "Erreur inconnue (conversion binaire-string) : %s" % e

    #on test les 2 premiers octets pour savoir si une puce RFID est posée ou retirée
    if donnee[0:2] == '\x02\x01': #puce posée
      print "Puce %s posée" % rfid_id

    elif donnee[0:2] == '\x02\x02': #puce retirée
      print "Puce %s retirée." % rfid_id

    #on test le ler octet, s'il vaut 1, alors une action à été faite sur le mir:ror
    if donnee[0] == '\x01':
      if donnee[1] == '\x04':
        print "Le mir:ror est retourné face vers le haut"
      if donnee[1] == '\x05':
        print "Le mir:ror est retourné face vers le bas"
