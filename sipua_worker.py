import sys
import pjsua as pj
import re
from subprocess import Popen, PIPE, call
import time
from datetime import datetime
import os
import json
import signal
import os
import wave

LOG_LEVEL=2
CONSOLE_LEVEL=2
ua_info = None
ua_status = None
acc = None
current_call = None
ua_buddy = None
buddy_uri = ""
username = "91021"
password = "1234"
domain = "27.223.110.114:5060"
register_expires = 86400
current_callid = None
exit_flag = False
output = None
call_slot = None
current_recv_id = None
lan_source = ""
lan_target = ""
lan_cur = ""

# Logging callback
def log_cb(level, str, len):
    #matchObj = re.search(r'Response msg 200/INVITE', str)
    pass
    #global current_callid
    #if current_callid :
    #    matchObj =  re.search( current_callid, str )
    #    if matchObj:
    #        if re.search('m=audio ', str):
    #            print str.split('m=audio ')[1].split(' ')[0]
            #print str,

class MyAccountCallback(pj.AccountCallback):
    global ua_status
    global ua_buddy
    global buddy_uri
    global acc
    global lan_source
    global lan_target

    def __init__(self, account=None):
        pj.AccountCallback.__init__(self, account)

    def on_reg_state(self):
        global ua_status
        if self.account.info().reg_status == 200:
            print self.account.info().uri, "register ok", self.account.info().reg_expires
            #ua_status = "register succ"
        elif self.account.info().reg_status > 200:
            print self.account.info().uri, "register fail :", self.account.info().reg_status,
            print self.account.info().reg_reason, self.account.info().reg_active, self.account.info().reg_expires
            #ua_status = "register fail"

    def on_incoming_call(self, call):
        global current_call
        global current_callid
        global acc
        global ua_buddy
        global buddy_uri
        global lan_source
        global lan_target
        if current_call:
            call.answer(486, "Busy")
            return

        print "Incoming call from: ", call.info().remote_uri
        lan_array = call.info().remote_uri.split('"')[1].split('_')
        if len(lan_array) > 2:
            lan_source = lan_array[1]
            lan_target = lan_array[2]
            print "Incoming call language: ", lan_source, lan_target
        else:
            print "Incoming call language: ", "No Language Info"
        from_addr = call.info().remote_uri.split('<')[1].split('>')[0]
        print from_addr
        print "Incoming call contact: ", call.info().remote_contact
        #print "Incoming call req url: ", call.info().contact
        print "Incoming call callid: ", call.info().sip_call_id
        current_callid = call.info().sip_call_id
        current_call = call

        call_cb = MyCallCallback(current_call)
        current_call.set_callback(call_cb)

        current_call.answer(200)

        #buddy_uri = call.info().remote_contact
        buddy_uri = from_addr
        ua_buddy = acc.add_buddy(buddy_uri, cb=MyBuddyCallback())
        ua_buddy.subscribe()

    def on_incoming_subscribe(self, buddy, from_uri, contact_uri, pres):
        global acc
        global ua_buddy
        # Allow buddy to subscribe to our presence
        if buddy:
            return (200, None)
        print 'Incoming SUBSCRIBE request from', from_uri

        acc.pres_notify(pres, pj.SubscriptionState.ACTIVE)
        ua_buddy = acc.add_buddy(from_uri, cb=MyBuddyCallback())
        ua_buddy.subscribe()
        return (202, None)


class MyCallCallback(pj.CallCallback):

    def __init__(self, call=None):
        pj.CallCallback.__init__(self, call)

    def on_dtmf_digit(self, digits):
        global username
        global lan_source
        global lan_target
        global lan_cur
        global output
        global ua_status
        global call_slot
        global current_recv_id
        print "MyCall %s: receiving dtmf [%s]"%(username, digits)
        lan_cur = lan_target
        pj.Lib.instance().recorder_destroy(self.rec_id)

        if output:
            os.killpg(os.getpgid(output.pid), signal.SIGKILL)
            print "kill sclice [", output.pid, "]"

        #pj.Lib.instance().recorder_destroy(self.rec_id)

        recv_name = username + ".wav"
        call('rm %s'%(recv_name), shell=True)
        call('rm %s*.wav'%(username), shell=True)
        call('rm %s*.mp3'%(username), shell=True)
        call('rm %s*.log'%(username), shell=True)

        self.rec_id = pj.Lib.instance().create_recorder(recv_name)
        rec_slot = pj.Lib.instance().recorder_get_slot(self.rec_id)
        pj.Lib.instance().conf_connect(call_slot, rec_slot)
        current_recv_id = self.rec_id

        ua_status = "Switch"

    # Notification when call state has changed
    def on_state(self):
        global current_call
        global current_callid
        global ua_status
        global exit_flag
        global output
        global username
        print "Call with", self.call.info().remote_contact,
        print "is", self.call.info().state_text,
        print "last code =", self.call.info().last_code,
        print "(" + self.call.info().last_reason + ")"

        if self.call.info().state == pj.CallState.DISCONNECTED:
            current_call = None
            current_callid = None
            print 'DISCONNECTED call is', current_call
            ua_status = "call disconnected"
            pj.Lib.instance().recorder_destroy(self.rec_id)
            #exit_flag = True
            timestr = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
            targetdir = "%s-%s"%(username, timestr)
            call(["mkdir", "-p", "./wav/"+targetdir])
            src = "./"+username+"*"
            dst = "./wav/"+targetdir+"/"
            call('cp -r %s %s'%(src, dst), shell=True)
            if output:
                os.killpg(os.getpgid(output.pid), signal.SIGKILL)
                print "kill sclice [", output.pid, "]"

    # Notification when call's media state has changed.
    def on_media_state(self):
        global username
        global ua_status
        global call_slot
        global current_recv_id

        if self.call.info().media_state == pj.MediaState.ACTIVE:
            # Connect the call to sound device
            call_slot = self.call.info().conf_slot

            recv_name = username + ".wav"
            self.rec_id = pj.Lib.instance().create_recorder(recv_name)
            rec_slot = pj.Lib.instance().recorder_get_slot(self.rec_id)
            pj.Lib.instance().conf_connect(call_slot, rec_slot)
            current_recv_id = self.rec_id

            #play_name = "input.wav"
            #play_id = pj.Lib.instance().create_player(play_name, True)
            #play_slot = pj.Lib.instance().player_get_slot(play_id)
            #pj.Lib.instance().conf_connect(play_slot, call_slot)

            #pj.Lib.instance().conf_connect(call_slot, 0)
            #pj.Lib.instance().conf_connect(0, call_slot)
            print "Media is now active"
            #ua_status = "Start"
            ua_status = "Prepare"

        else:
            print "Media is inactive"
            ua_status = "Media inactive"

class MyBuddyCallback(pj.BuddyCallback):
    def __init__(self, buddy=None):
        pj.BuddyCallback.__init__(self, buddy)

    def on_state(self):
        pass
        #print "Buddy", self.buddy.info().uri, "is",
        #print self.buddy.info().online_text

    def on_pager(self, mime_type, body):
        print "Instant message from", self.buddy.info().uri,
        print "(", mime_type, "):"
        print body

    def on_pager_status(self, body, im_id, code, reason):
        if code >= 300:
            print "Message delivery failed for message",
            print body, "to", self.buddy.info().uri, ":", reason

    def on_typing(self, is_typing):
        if is_typing:
            print self.buddy.info().uri, "is typing"
        else:
            print self.buddy.info().uri, "stops typing"

def ua_register():
    global ua_status
    global ua_info
    global acc
    global lib
    global username
    global domain
    global register_expires
    global password

    try:
        sip_uri = pj.SIPUri()
        sip_uri.scheme = "sip"
        sip_uri.user = username
        sip_uri.host = domain
        acc_cfg = pj.AccountConfig()
        acc_cfg.id = sip_uri.encode()
        acc_cfg.reg_uri = acc_cfg.id
        acc_cfg.reg_timeout = register_expires
        #acc_cfg.proxy = [ "sip:pjsip.org;lr" ]
        acc_cfg.auth_cred = [pj.AuthCred("*", username, password)]

        ua_info = acc_cfg.id

        acc_cb = MyAccountCallback()
        acc = lib.create_account(acc_cfg, cb=acc_cb)

        ua_status = "ua register start..."

    except pj.Error, err:
        ua_status = "ua register error"
        print 'Error creating account:', err

    print ua_info, ", status[", ua_status, "]"

def getDst(line):
    str_line =  line.rstrip('\r\n')
    decode_json = json.loads(str_line)
    return decode_json['dst']

def getSrc(line):
    str_line =  line.rstrip('\r\n')
    decode_json = json.loads(str_line)
    return decode_json['src']

def getWav(line):
    str_line =  line.rstrip('\r\n')
    decode_json = json.loads(str_line)
    return decode_json['tran_wav_file']

def getPreSrc(line):
    str_line =  line.rstrip('\r\n')
    decode_json = json.loads(str_line)
    return decode_json['src']

def getPreWav(line):
    str_line =  line.rstrip('\r\n')
    decode_json = json.loads(str_line)
    return './tts_tones/%s'%(decode_json['wav'])

def getModeFlag(line):
    str_line =  line.rstrip('\r\n')
    decode_json = json.loads(str_line)
    return decode_json['fastReturn']

def ua_sendmsg(text):
    global ua_status
    global ua_info
    global ua_buddy

    msg = text.encode('utf-8')
    timestr = str(datetime.now())
    print "send back message at [%s]:"%(timestr), msg

    if ua_buddy:
        ua_buddy.send_pager(msg)
    else :
        print "ua_buddy is none"

def ua_newwav():
    global lib
    global call_slot
    global username
    global current_recv_id

    if current_recv_id != None:
        lib.instance().recorder_destroy(current_recv_id)

    recv_name = username + ".wav"
    Popen("rm %s"%(recv_name), shell=True)

    time.sleep(0.2)

    recv_id = lib.instance().create_recorder(recv_name)
    rec_slot = lib.instance().recorder_get_slot(recv_id)
    lib.instance().conf_connect(call_slot, rec_slot)

    current_recv_id = recv_id

def ua_playback(text):
    global lib
    global call_slot
    media_file = text.encode('utf-8')

    if os.path.exists(media_file) == True:
        wfile = wave.open(media_file)
        wtime = (1.0 * wfile.getnframes()) / wfile.getframerate()
        print wtime, media_file
        wfile.close()
        #avoid too short wav
        if wtime > 0.2:
            #timestr = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
            timestr = str(datetime.now())
            print "play back %s now [%s]"%(media_file,timestr)
            wav_player_id=lib.instance().create_player(media_file, False)
            wav_slot=lib.instance().player_get_slot(wav_player_id)
            lib.instance().conf_connect(wav_slot, call_slot)
            time.sleep(wtime)
            lib.instance().player_destroy(wav_player_id)
    else:
        print "[Error] no such translated file:", media_file

def onsignal_term(a, b):
    global output
    global exit_flag
    global username
    print username, ': receive SIGTERM'
    if output:
        os.killpg(os.getpgid(output.pid), signal.SIGTERM)
        print "kill sclice"
    ua_status = "End"
    print ua_status
    exit_flag = True


lib = pj.Lib()

try:
    signal.signal(signal.SIGTERM,onsignal_term)

    media_cfg = pj.MediaConfig()
    log_cfg = pj.LogConfig(console_level=CONSOLE_LEVEL, level=LOG_LEVEL, callback=log_cb, filename='./logs/master.log')
    lib.init(log_cfg = log_cfg, media_cfg=media_cfg)

    transport = lib.create_transport(pj.TransportType.UDP, pj.TransportConfig(0))
    print "sip:" + transport.info().host + ":" + str(transport.info().port)

    lib.start()

    lib.set_null_snd_dev()

    if len(sys.argv) > 3:
        username = sys.argv[1]
        lan_source = sys.argv[2]
        lan_target = sys.argv[3]
        print username, lan_source, lan_target

    ua_register()
    #main loop of SIPUA
    output = None
    while True:
        time.sleep(0.1)
        if exit_flag == True:
            print ua_info, "Destory and Exit"
            if output:
                os.killpg(os.getpgid(output.pid), signal.SIGTERM)
                print "kill sclice"
            ua_status = "End"
            print ua_status
            break
        elif ua_status == "Prepare":
            infofile = "./tts_tones/%s.log"%(lan_source)
            print "send back prepared info from %s"%infofile
            if os.path.exists(infofile) == True:
                h_file = open(infofile)
                ua_playback(getPreWav(h_file.readlines()[0]))
                #for line in h_file.readlines():
                    #ua_sendmsg(getSrc(line))
                #    ua_playback(getPreWav(line))
                h_file.close()
            ua_status = "Start"
        elif ua_status == "Switch":
            switchfile = "./tts_tones/%s.log"%(lan_cur)
            print "send back switch info from %s"%switchfile
            if os.path.exists(switchfile) == True:
                s_file = open(switchfile)
                ua_playback(getPreWav(s_file.readlines()[1]))
                s_file.close()
            lan_target = lan_source
            lan_source = lan_cur
            ua_status = "Start"
        elif ua_status == "Start":
            print "start to translate..."
            #ua_status = "test"
            #output = Popen("./sclice.sh %s"%(username), shell=True, preexec_fn=os.setsid)
            print "prepare sclice:", lan_source, lan_target
            binfile = "%s_result.log"%(username)
            if os.path.exists(binfile) == True:
                h_file = open(binfile, "r+")
                h_file.truncate()
                h_file.close()

            output = Popen("./sclice.sh %s %s %s %s"%(username, lan_source, lan_target,'1'), shell=True, preexec_fn=os.setsid)
            ua_status = "Translate"
        elif ua_status == "Translate":
            binfile = "%s_result.log"%(username)
            #fsize = os.stat(binfile).st_size
            #print "current size:", fsize

            fsize = 0
            #if os.path.exists(binfile) == True:
            #    h_file = open(binfile, "r+")
            #    h_file.truncate()
            #    h_file.close()

            #for line in h_file.readlines():
            #    ua_sendmsg(getSrc(line))
            #    time.sleep(0.1)
            #    ua_sendmsg(getDst(line))
            #    time.sleep(0.1)
            #    ua_playback(getWav(line))
            #h_file.close()
            while ua_status == "Translate":
                if os.path.exists(binfile) == True:
                    current_fsize = os.stat(binfile).st_size
                    if current_fsize > fsize:
                        print "current size:", current_fsize, "old size:", fsize
                        h_file = open(binfile)
                        h_file.seek(fsize)
                        for line in h_file.readlines():
                            if(getModeFlag(line)==1):
                                ua_sendmsg(getSrc(line))
                                time.sleep(0.1)
                                ua_sendmsg(getDst(line))
                            else:
                                ua_playback(getWav(line))
                        h_file.close()
                        fsize = current_fsize
                time.sleep(0.2)

    #clean up
    if ua_buddy:
        ua_buddy = None

    if current_call:
        current_call.hangup()
        current_call = None

    if acc:
        acc.delete()
    acc = None

    transport = None

    log_cfg = None
    media_cfg = None

    lib.destroy()
    lib = None

except pj.Error, e:
    print "Exception: " + str(e)
    lib.destroy()
    lib = None
