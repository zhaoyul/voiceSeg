# -*- coding: utf-8 -*-
import sys
import requests
from subprocess import call

from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

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

wav_file=''
tran_wav_file=''

fromLang = 'zh'
toLang = 'en'

if len(sys.argv) <= 3:
  print ("必须指定1.要处理的已经切片好的wav文件名称  2.输入语言 3.输出语言")
  sys.exit(1)
else:
  wav_file = sys.argv[1].strip('\r');
  tran_wav_file = wav_file.replace('.wav', '_tran.wav')
  fromLang = sys.argv[2]
  toLang = sys.argv[3]
  # use ffmpeg to boost the volume
  #call(["ffmpeg","-loglevel","16", "-i", wav_file, "-af", "volume=5", "bigger"+wav_file] )
  #call(["mv", "bigger"+wav_file, wav_file])

import requests
################################
def getToken():
    # Request
    # POST https://api.cognitive.microsoft.com/sts/v1.0/issueToken

    try:
        response = requests.post(
            url="https://api.cognitive.microsoft.com/sts/v1.0/issueToken",
            headers={
                "Ocp-Apim-Subscription-Key": "006f1cd905e3457a8c565c50f9147a41",
                "Content-type": "application/x-www-form-urlencoded",
            },
            data={
            },
        )
#         print('Response HTTP Status Code: {status_code}'.format(
#             status_code=response.status_code))
#         print('Response HTTP Response Body: {content}'.format(
#             content=response.content))
        return response.content
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


# 	ko-KR	Korean (Korea)
#       ja-JP	Japanese (Japan)
#       zh-CN	Chinese (Mandarin, simplified)
#       en-US	English (United States)


def ms_reg(wav_file, lang):

    internal_lang = lang_mapping(lang)


    auth_code = getToken()

    try:
        response = requests.post(
            url="https://speech.platform.bing.com/speech/recognition/interactive/cognitiveservices/v1",
            params={
                "language": internal_lang,
                "locale": "your_locale",
                "format": "your_format",
                "requestid": "your_guid",
            },
            headers={
                "Authorization": auth_code,
                "Content-type": "audio/wav; codec=\"audio/pcm\"; samplerate=16000",
            },
            files = {'file': open(wav_file, 'rb')},
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        print('Response HTTP Response Body: {content}'.format(
            content=response.content))
        if (response.ok):
            rsp_dict = response.json()
            if(rsp_dict["Duration"] > 0):
                return rsp_dict["DisplayText"]
            else:
                print ("ms 解析:(%s)没有结果, 退出!" %(current_wav_file))
                sys.exit(0)

    except requests.exceptions.RequestException:
        print('HTTP Request failed')

from aip import AipSpeech
APP_ID = '9909545'
API_KEY = 'BtgyKlo673yQ5olb2QX5GXZn'
SECRET_KEY = 'zhs41IHDIxGDdAnaEnw5xu18FC6Xr4Lq'

aipSpeech = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

def baidu_rec(current_wav_file, lang):
    # TODO: should parameterize the languages.
    result_dict = aipSpeech.asr(get_file_content(current_wav_file), 'wav', 16000, {
        'lan': lang,
    })

    #if result_dict is None or len(result_dict["result"]) == 0:
    #  print ("baidu 解析没有结果, 退出")
    #  sys.exit(0)

    try:
        first_result =  result_dict["result"][0]#.decode("UTF-8")
    except Exception as e:
        print ("baidu 解析:(%s)没有结果, 退出!" %(current_wav_file))
        sys.exit(0)


    print (first_result)
    return first_result



################################j译
#import sys
#reload(sys)
#sys.setdefaultencoding('utf8')

import urllib
import random
import hashlib

appid = '20170721000065533'
secretKey = 'xfI4YwH9Hh8jhobg1qjV'

def speech_synthesis(text, lang, output_file_name):
    if(lang == 'en' or lang == 'ch'):
        #print("------------")
        #print(text + " " + lang + " " + output_file_name)
        text2WavResult  = aipSpeech.synthesis(text, 'zh', 1, {
            'vol': 1,
        })

        # 识别正确返回语音二进制 错误则返回dict 参照下面错误码
        mp3_file = output_file_name.replace('.wav', '.mp3')
        if not isinstance(text2WavResult, dict):
            with open(mp3_file, 'wb') as f:
                f.write(text2WavResult)
            call(["ffmpeg","-i", mp3_file, output_file_name] )
        else:
           print (text2WavResult)
    else:
        internal_lang = lang_mapping(lang)

        print(["java","-jar", "TTSSample.jar", text, internal_lang,  output_file_name])
        call(["java","-jar", "TTSSample.jar", text, internal_lang,  output_file_name] )


q = None
if(fromLang == 'en' or fromLang == 'zh'):
    q = baidu_rec(wav_file, fromLang)
else:
    q = ms_reg(wav_file, fromLang)
salt = random.randint(32768, 65536)

sign = (appid+q+str(salt)+secretKey).encode('utf-8')
m = hashlib.md5()
m.update(sign)
sign = m.hexdigest()

payload = {'appid': appid,
               'q': q,
            'from':fromLang,
              'to':toLang,
            'salt':str(salt),
            'sign':sign
          }

src=''
dst=''
trans_result=''
try:
    response  = requests.get('https://fanyi-api.baidu.com/api/trans/vip/translate',payload)
    print (response.content)
    if response.status_code == 200:
        src = response.json()["trans_result"][0]["src"]
        dst = response.json()["trans_result"][0]["dst"]
        trans_result = response.json()["trans_result"][0]
        speech_synthesis(dst, toLang, tran_wav_file)
        #call(["pico2wave","--wave="+tran_wav_file, dst] )
        #call(["ffmpeg","-loglevel","16", "-i", tran_wav_file, "-af", "volume=5", "bigger"+tran_wav_file] )
        #call(["mv", "bigger"+tran_wav_file, tran_wav_file])
        #print (src)
except Exception as e:
    print (e)


import re
call_translate = re.split("_", wav_file)[0] + "_result.log"
file_object = open(call_translate, "a")
import json
try:
   #file_object.writelines([src,' ',dst] )
   trans_result["tran_wav_file"] = tran_wav_file
   file_object.writelines([json.dumps(trans_result),'\n'] )
finally:
   file_object.close( )
