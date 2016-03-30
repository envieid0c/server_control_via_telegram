#!/usr/bin/env python
# -*- coding: utf-8 -*-

import httplib
import urllib
import json
import logging
import subprocess
import threading

from enum import Enum

logging.basicConfig(level=logging.DEBUG)

class Methods(str, Enum):
    getMe = 'getMe'
    sendMessage = 'sendMessage'
    getUpdates = 'getUpdates'

token = "token here"

def message_processing(str_command, sender):
    command = str_command.split(' ')
    p = subprocess.Popen(command, stdout=subprocess.PIPE)
    p.wait()
    out = p.communicate()[0]
    # logging.warning(out)

    send_request(Methods.sendMessage, {'chat_id': sender, 'text': '*YOUR COMMAND WAS:*\n*{}*\n`{}`'.format(str_command, out), 'parse_mode': 'Markdown'})

def send_request(method, data_to_send):
    c = httplib.HTTPSConnection('api.telegram.org')
    data_to_send = urllib.urlencode(data_to_send)
    c.request('GET', '/bot{}/{}?{}'.format(token, method, data_to_send))
    r = c.getresponse()
    answer = r.read()
    if json.loads(answer).get('ok'):
        value = json.loads(answer).get('result')
        c.close()
    else:
        print answer
        raise

    return value

offset = -1
while True:

    messages = send_request(Methods.getUpdates, {'offset': offset + 1})
    for m in messages:
        # logging.info(m)
        offset = m.get('update_id')
        sender = m.get('message').get('from').get('id')
        # logging.info('From: {}'.format(sender))

        if m.get('message').get('text'):
            # logging.info('Received a message ')
            text = m.get('message').get('text').encode('utf-8')
            # send_request(Methods.sendMessage, {'chat_id': sender, 'text': text})
            t = threading.Thread(target=message_processing, args=(text, sender))
            t.start()

        else:
            send_request(Methods.sendMessage, {'chat_id': sender, 'text': 'Send only text messages!'})
