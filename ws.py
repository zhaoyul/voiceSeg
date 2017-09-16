#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import partial
import threading
import wave
import struct
import numpy as np
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import os
import sys
import time
from datetime import datetime
try:
    import simplejson as json
except ImportError:
    import json
import shutil

def init_wave(call_id):
    if call_id:
        wave_file = wave.open(call_id+'.wav', 'wb')
        sample_rate = 8000
        bit_width = 16
        chanels = 1
        wave_file.setparams((chanels, bit_width//8, sample_rate, 0, 'NONE', 'not compressed'))
        return wave_file
    else:
        return None



class RealtimeHandler(tornado.websocket.WebSocketHandler):

    def parse_msg(self, msg):
        call_id = msg.replace("start ", "")
        return call_id

    def check_origin(self, origin):
        return True

    def open(self):
        print ("open")


    def on_message(self, message):

        if type(message) != str:
            self.process_wave(message)
        elif message.startswith("start"):
            self.call_id = self.parse_msg(message)
            self.out_wave_file = init_wave(self.call_id)
            print ("now start call:", self.call_id)
        elif message.startswith("stop"):
            print ("now close call:", self.call_id)
            self.out_wave_file.close()
        else :
            pass

    def process_wave(self, message):
        #print(message)
        if not hasattr(self, 'out_wave_file'):
            self.out_wave_file = init_wave('xxxxxx')

        self.out_wave_file.writeframes(message)
        #audio_as_int_array = np.frombuffer(message, 'i2')
        #print(audio_as_int_array)
        #for i in audio_as_int_array:
        #    value = struct.pack('h', i)
        #    print("------------:", i)
        #    self.out_wave_file.writeframes(value)
        #    #print(value)


settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    'auto_reload': True,
    }

application = tornado.web.Application(
    [('//websocket',RealtimeHandler),],
    **settings)


#usage from http://stackoverflow.com/questions/8045698/https-python-client
#openssl genrsa -out privatekey.pem 2048
#openssl req -new -key privatekey.pem -out certrequest.csr
#openssl x509 -req -in certrequest.csr -signkey privatekey.pem -out certificate.pem
http_server = tornado.httpserver.HTTPServer(
            application,
        )
http_server.listen(5000)
tornado.ioloop.IOLoop.instance().start()
