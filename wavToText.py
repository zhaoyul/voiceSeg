# -*- coding: utf-8 -*-
import sys
import re
import json
import urllib
import random
import hashlib
import requests
from websocket import create_connection
from subprocess import call
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from aip import AipSpeech
import logging


from tts_tones import tts

def ms_reg(wav_file, lang, rate):
    internal_lang = tts.lang_mapping(lang)
    auth_code = tts.getToken()
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
                "Content-type": "audio/wav; codec=\"audio/pcm\"; samplerate=" + rate,
            },
            files = {'file': open(wav_file, 'rb')},
        )
        if (response.ok):
            rsp_dict = response.json()
            if(rsp_dict["Duration"] > 0):
                return rsp_dict["DisplayText"]
            else:
                log.debug('%s 微软识别没结果，exit', wav_file)
                sys.exit(0)

    except requests.exceptions.RequestException:
        print('HTTP Request failed')

def getBaiduAipSpeech():
    APP_ID = '9909545'
    API_KEY = 'BtgyKlo673yQ5olb2QX5GXZn'
    SECRET_KEY = 'zhs41IHDIxGDdAnaEnw5xu18FC6Xr4Lq'
    return AipSpeech(APP_ID, API_KEY, SECRET_KEY)

def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

def baidu_rec(current_wav_file, lang, rate):
    # TODO: should parameterize the languages.
    aipSpeech = getBaiduAipSpeech()
    result_dict = aipSpeech.asr(get_file_content(current_wav_file), 'wav', int(rate), {
        'lan': lang,
    })
    #if result_dict is None or len(result_dict["result"]) == 0:
    #  print ("baidu 解析没有结果, 退出")
    #  sys.exit(0)
    try:
        first_result =  result_dict["result"][0]#.decode("UTF-8")
    except Exception as e:
        log.debug('%s 百度识别没有结果，exit', current_wav_file)
        sys.exit(0)
    log.debug('%s 百度识别结果是:%s', current_wav_file, first_result)
    return first_result

def speech_synthesis(text, lang, output_file_name):
    if(lang == 'en' or lang == 'ch'):
        log.debug('%s 百度tts开始', wav_file)
        aipSpeech = getBaiduAipSpeech()
        text2WavResult  = aipSpeech.synthesis(text, 'zh', 1, {
            'vol': 1,
        })

        # 识别正确返回语音二进制 错误则返回dict 参照下面错误码
        mp3_file = output_file_name.replace('.wav', '.mp3')
        if not isinstance(text2WavResult, dict):
            with open(mp3_file, 'wb') as f:
                f.write(text2WavResult)
            call(["ffmpeg",'-loglevel', '-8',"-i", mp3_file, output_file_name] )
            log.debug('%s 百度tts结束', wav_file)
        else:
           print (text2WavResult)
    else:
        internal_lang = tts.lang_mapping(lang)

        log.debug('%s 微软tts开始', wav_file)
        #call(["java","-jar", "TTSSample.jar", text, internal_lang,  output_file_name] )
        auth_code = tts.getToken()
        tts.genWav(auth_code, internal_lang, text, output_file_name)
        log.debug('%s 微软tts结束', wav_file)

def getAppLogger():
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    logging.getLogger('requests').setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    log = logging.getLogger(__name__)
    return log

def getWs():
    ws = None
    if rate == '16000':
        return ws

    try:
        ws = create_connection("ws://localhost:5000//websocket")
    except Exception as e:
        pass
    return ws

def send_ws_msg(ws,call_id, msg_type, msg):
    if not ws is None and ws.connected:
        ws.send('{0}|{1}|{2}|{3}'.format('kevin', call_id, msg_type, msg))

if __name__ == '__main__':

    log = getAppLogger()

    wav_file=''
    tran_wav_file=''

    fromLang = 'zh'
    toLang = 'en'
    rate='16000'


    if len(sys.argv) <= 4:
        log.error('必须指定1.要处理的已经切片好的wav文件名称  2.输入语言 3.输出语言 4. 采样频率')
        sys.exit(1)
    else:
        print(sys.argv)
        wav_file = sys.argv[1].strip('\r');
        tran_wav_file = wav_file.replace('.wav', '_tran.wav')
        fromLang = sys.argv[2]
        toLang = sys.argv[3]
        rate = sys.argv[4]
        log.debug('%s 开始切片', wav_file)

    call_id = wav_file.split('_')[0]

    q = None
    if(fromLang == 'en' or fromLang == 'zh'):
        log.debug('%s 百度识别开始:%s', wav_file, fromLang)
        q = baidu_rec(wav_file, fromLang, rate)
        log.debug('%s 百度识别结束', wav_file)
    else:
        log.debug('%s 微软识别开始', wav_file)
        q = ms_reg(wav_file, fromLang, rate)
        log.debug('%s 微软识别结束', wav_file)

    call_translate = call_id + "_result.log"
    file_object = open(call_translate, "a")

    log.debug("%s 返回识别文本:%s", wav_file, q)

    ws = getWs()
    # send out the asr result
    send_ws_msg(ws, call_id, 'asr', q)


    salt = random.randint(32768, 65536)

    appid = '20170721000065533'
    secretKey = 'xfI4YwH9Hh8jhobg1qjV'
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
    log.debug('%s 百度翻译参数%s', wav_file, str(payload))
    trans_result=''
    try:
        log.debug('%s 百度翻译开始', wav_file)
        response  = requests.get('https://fanyi-api.baidu.com/api/trans/vip/translate',payload)
        if response.status_code == 200:
            src = response.json()["trans_result"][0]["src"]
            dst = response.json()["trans_result"][0]["dst"]
            try:
                fast_return_dict = {'fastReturn':1,
                                    'src':src,
                                    'dst':dst}
                file_object.writelines([json.dumps(fast_return_dict),'\n'] )
                file_object.flush()
            finally:
                pass
            log.debug('%s baidu result:', dst)
            # send out the asr result
            #send_ws_msg(ws, call_id, 'tran', dst)
            trans_result = response.json()["trans_result"][0]
            log.debug('%s 百度翻译结束', wav_file)
            speech_synthesis(dst, toLang, tran_wav_file)
            # send out the tts file name
            #send_ws_msg(ws, call_id, 'tts', tran_wav_file)
    except Exception as e:
        log.error('百度翻译异常:%s', e)
    try:
       trans_result["tran_wav_file"] = tran_wav_file
       trans_result["fastReturn"] = 0
       file_object.writelines([json.dumps(trans_result),'\n'] )
    finally:
       file_object.close( )

    if ws:
        ws.close()
