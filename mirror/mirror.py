#!/usr/bin/python
# -*- coding: utf-8 -*-

import binascii #pour convertir l'hexa en string
import requests
import signal
import sys
import time
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG, filename='/var/log/rabsberry/mirror.log')
  


def call_rabsberry_event_api(rfid_id, action):
    # TODO manque url from conf
    url = "http://localhost/api/event"
    payload = { 'actor_type':'RFID_READER', 'actor_id':'mir:ror', 'rfid_id': rfid_id, 'action': action}
    # print payload
    r = requests.post(url, json=payload)
    #print(r.text)

<<<<<<< HEAD:mirr:ror/mirror.py

=======
def signal_term_handler(signal, frame):
    logging.info('Terminating Mirror')
    mirror.close()
    sys.exit(0)
	
	
>>>>>>> 375ad999e3343a2b914a06ff3c6ef77d998722b9:mirror/mirror.py
# TODO verrifier quel /dev/hidrawx est le bon
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
mirror = open("/dev/hidraw0", "rb")

signal.signal(signal.SIGTERM, signal_term_handler)
signal.signal(signal.SIGINT, signal_term_handler)
erreur_generale = False
logging.info('Starting Mirror')
while erreur_generale == False:
  #on lit les données envoyées par le mir:ror
  try:
    donnee = mirror.read(16)
  except Exception as e:
    logging.error("Erreur inconnue (lecture du  mir:ror) : %s" % e)
    erreur_generale = True

  #on test les données renvoyées par le mir:ror
  if donnee != '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00':
    try:
      rfid_id = binascii.hexlify(donnee)[4:]
    except Exception as e:
      logging.error("Erreur inconnue (conversion binaire-string) : %s" % e)

    #on test les 2 premiers octets pour savoir si une puce RFID est posée ou retirée
    if donnee[0:2] == '\x02\x01': #puce posée
      logging.debug("Puce %s posée" % rfid_id)
      call_rabsberry_event_api(rfid_id, "IN")

    elif donnee[0:2] == '\x02\x02': #puce retirée
      logging.debug("Puce %s retirée." % rfid_id)
      call_rabsberry_event_api(rfid_id, "OUT")

    #on test le ler octet, s'il vaut 1, alors une action à été faite sur le mir:ror
    if donnee[0] == '\x01':
      if donnee[1] == '\x04':
        logging.info("Le mir:ror est retourné face vers le haut")
        call_rabsberry_event_api("0", "ON")
      if donnee[1] == '\x05':
        logging.info("Le mir:ror est retourné face vers le bas")
        call_rabsberry_event_api("0", "OFF")
