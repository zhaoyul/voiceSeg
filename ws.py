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
from subprocess import Popen
import signal

sockets_dict = {}

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

    #def parse_msg(self, msg):
    #    call_id = msg.split(' ')[1]
    #    return call_id

    def check_origin(self, origin):
        return True

    def open(self):
        print ("open")
        self.call_id = None
        self.sclice_process = None
        self.out_wave_file = None
    def on_close(self):
        print ("close")

    def get_sclice_process(self, call_id, lan_source, lan_target):
        if not self.sclice_process is None :
            pass
        else:
            self.sclice_process =  Popen("./sclice.sh %s %s %s %s"%(call_id, lan_source, lan_target, '2'), shell=True, preexec_fn=os.setsid)

    def clean_resource(self):
        if self.call_id in sockets_dict:
            older_self = sockets_dict[self.call_id]
            if older_self and older_self.sclice_process:
                os.killpg(os.getpgid(older_self.sclice_process.pid), signal.SIGKILL)
                older_self.sclice_process = None
        else:
            pass

    def on_message(self, message):

        if type(message) != str:
            self.process_wave(message)
        elif message.startswith("start"):
            self.call_id = None
            #self.call_id = self.parse_msg(message)
            _, self.call_id, lan_source, lan_target = message.split(' ')
            self.clean_resource()
            self.out_wave_file = init_wave(self.call_id)
            self.get_sclice_process(self.call_id, lan_source, lan_target)
            print ("now start call:", self.call_id)
            sockets_dict[self.call_id] = self
        elif message.startswith("stop"):
            print ("now close call:", self.call_id)
            self.out_wave_file.close()
            if self.sclice_process:
                os.killpg(os.getpgid(self.sclice_process.pid), signal.SIGKILL)
                self.sclice_process = None
        elif message.startswith("kevin"):
            print("recv local msg:", message)
            _, call_id, sub_type, msg = message.split("|")
            if call_id in sockets_dict:
                sender = sockets_dict[call_id]
                if sub_type == "asr":
                    sender.write_message(msg)
                elif sub_type == "tran" :
                    sender.write_message("{'tran':'" + msg + "'}")
                elif sub_type == "tts":
                    try:
                        with open(msg, 'rb') as f:
                            data = f.read()
                            sender.write_message(data, binary=True)
                            print('send binary file:'+msg)
                    except Exception as e:
                        pass
        else:
            pass

    def process_wave(self, message):
        #print(message)
        if self.out_wave_file is None:
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
