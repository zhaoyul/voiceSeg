#! /usr/bin/env python3

# -*- coding: utf-8 -*-

import json
import sys
import tts

config_dict = {
        'kor': ['이폰（YeePhone） 자동번역 서비스를 이용해 주셔서 감사합니다. 발신자를 교체하려면 샵 버튼을 눌러주십시오.',
                  '지금부터 한국어로 말씀하십시오.'],
        'spa': ['Bienvenido al servicio de traducción automática de Yeephone, para cambiar de altavoz marque por favor el signo numeral.  ',
                  'Por favor hable ahora en español.'],
        'en': ['Thank you for using the interpreting services provided by YeePhone. Press the pound key to switch the speaker.  ',
                  'Now please speak in English.  '],
        'fra': ['Bienvenue chez Yeephone avec ses services de traduction !  Appuyez sur la touche dièse pour changer de porte-parole ',
                  'Maintenant prenez votre parole en français s\'il vous plaît !  '],
        'jp': ['YeePhone機械翻訳サービスをご利用いただきありがとうございます。 ',
                  '日本語をお話ください。 '],
        'it': ['Benvenuti ad usare il servizio di traduzione automatica YeePhone, per cambiare il portavoce si prega di premere il tasto stemma ',
                  'Ora si prega di parlare in italiano '],
        'de': ['Herzlich wilkommen in YeePhone Interpretation, bitte sprechen Sie und dann drücken Sie bitte die Reset-Taste.',
                  'Jetzt spechen Sie bitte auf Deutsch.'],
        'ru': ['Добро пожаловать пользоваться переводной услугой YeePhone. Чтобы переходить на следующего выступающего, нажмите Знак решётки.',
                  'Расскажите по-русски.'],
        'zh': ['欢迎使用译呼百应机器翻译服务，切换发言人请按井号键.',
                  '现在请使用中文发言.'],
        }

def genLangArray(lang):
    results = []
    filtered_dict = {k:v for k,v in config_dict.items() if lang == k}
    for lang, announce_array in filtered_dict.items():
        for num, announce in enumerate(announce_array, start=1):
            result_map = {}
            result_map['src'] = announce
            result_map['wav'] = lang+str(num)+'.wav'
            results.append(result_map)
    return results

def writeLog(lang):
    announce_array = genLangArray(lang)
    file_object = open(lang+'.log', "w")
    for announce in announce_array:
        file_object.writelines([json.dumps(announce),'\n'] )

if __name__ == '__main__':
    accesstoken = tts.getToken()
    for lang, announce_array in config_dict.items():
        for num, announce in enumerate(announce_array, start=1):
            print(accesstoken, lang, announce, lang+str(num)+'.wav')
            ms_lang = tts.lang_mapping(lang)
            tts.genWav(accesstoken, ms_lang, announce, lang+str(num)+'.wav')
    for lang, announce_array in config_dict.items():
        writeLog(lang)

