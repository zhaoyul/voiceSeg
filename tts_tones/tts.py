#! /usr/bin/env python3

# -*- coding: utf-8 -*-

import http.client, urllib.parse, json
from xml.etree import ElementTree
import sys


def lang_mapping(baidu_lang):
   internal_lang = 'zh-CN'
   if(baidu_lang == 'kor'):
     internal_lang = 'ko-KR'
   if(baidu_lang == 'jp'):
     internal_lang = 'ja-JP'
   if(baidu_lang == 'cn'):
     internal_lang = 'zh-CN'
   if(baidu_lang == 'en'):
     internal_lang = 'en-US'
   if(baidu_lang == 'de'):
     internal_lang = 'de-DE'
   if(baidu_lang == 'fr'):
     internal_lang = 'fr-FR'
   if(baidu_lang == 'spa'):
     internal_lang = 'es-ES'
   if(baidu_lang == 'ru'):
     internal_lang = 'ru-RU'
   if(baidu_lang == 'it'):
     internal_lang = 'it-IT'
   return internal_lang

def getToken():
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": '006f1cd905e3457a8c565c50f9147a41'}

    #AccessTokenUri = "https://api.cognitive.microsoft.com/sts/v1.0/issueToken";
    AccessTokenHost = "api.cognitive.microsoft.com"
    path = "/sts/v1.0/issueToken"

    # Connect to server to get the Access Token
    #print ("Connect to ms server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)

    data = response.read()
    conn.close()

    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)
    return accesstoken

def genWav(accesstoken, lang, text, file_name):
    body = ElementTree.Element('speak', version='1.0')
    body.set('{http://www.w3.org/XML/1998/namespace}lang', lang)
    #body.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-us')
    voice = ElementTree.SubElement(body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', lang)
    #voice.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-US')
    voice.set('{http://www.w3.org/XML/1998/namespace}gender', 'Female')
    if lang == 'zh-CN':
        voice.set('name', 'Microsoft Server Speech Text to Speech Voice (zh-CN, HuihuiRUS)')
    if lang == 'en-US':
        voice.set('name', 'Microsoft Server Speech Text to Speech Voice (en-US, ZiraRUS)')
    if lang == 'ja-JP':
        voice.set('name', 'Microsoft Server Speech Text to Speech Voice (ja-JP, HarukaRUS)')
    if lang == 'ko-KR':
        voice.set('name', 'Microsoft Server Speech Text to Speech Voice (ko-KR, HeamiRUS)')
    if lang == 'de-DE':
        voice.set('name', 'Microsoft Server Speech Text to Speech Voice (de-DE, HeddaRUS)')
    if lang == 'fr-FR':
        voice.set('name', 'Microsoft Server Speech Text to Speech Voice (fr-FR, HortenseRUS)')
    if lang == 'es-ES':
        voice.set('name', 'Microsoft Server Speech Text to Speech Voice (es-ES, HelenaRUS)')
    if lang == 'ru-RU':
        voice.set('name', 'Microsoft Server Speech Text to Speech Voice (ru-RU, Irina, Apollo)')
    if lang == 'it-IT':
        voice.set('name', 'Microsoft Server Speech Text to Speech Voice (it-IT, Cosimo, Apollo)')
    voice.text = text
    #voice.text = 'This is a demo to call microsoft text to speech service in Python.'

    headers = {"Content-type": "application/ssml+xml",
                "X-Microsoft-OutputFormat": "riff-16khz-16bit-mono-pcm",
                "Authorization": "Bearer " + accesstoken,
                "X-Search-AppId": "07D3234E49CE426DAA29772419F436CA",
                "X-Search-ClientID": "1ECFAE91408841A480F00935DC390960",
                "User-Agent": "TTSForPython"}

    #Connect to server to synthesize the wave
    print ("\nConnect to server to synthesize the wave")
    conn = http.client.HTTPSConnection("speech.platform.bing.com")
    conn.request("POST", "/synthesize", ElementTree.tostring(body), headers)
    response = conn.getresponse()
    print(response.status, response.reason)

    data = response.read()
    #file_name = 'output.wav'
    with open(file_name, 'wb') as f:
        f.write(data)

    conn.close()
    print("The synthesized wave length: %d" %(len(data)))
if __name__ == '__main__':
    lang=sys.argv[1]
    text=sys.argv[2]
    file_name=sys.argv[3]
    accesstoken = getToken()
    genWav(accesstoken, lang, text, file_name)
