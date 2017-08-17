from subprocess import Popen
from subprocess import PIPE
import time
import sys
import signal
import os
import ConfigParser

conf = ConfigParser.ConfigParser()
conf.read("ua.cfg")

ua_list = conf.sections()

threads = []
for ua_item in ua_list:
    username = conf.get(ua_item, "username")
    lan_source = conf.get(ua_item, "source")
    lan_target = conf.get(ua_item, "target")
    #t = Popen("python sipua_worker.py %s"%username, shell=True, preexec_fn=os.setsid)
    t = Popen("python sipua_worker.py %s %s %s"%(username, lan_source, lan_target), shell=True, preexec_fn=os.setsid)
    threads.append(t)

try:
    while True:
        print "Menu: q=quit"
        input = sys.stdin.readline().rstrip("\r\n")
        if input == "q":
            print "Wait for SIPUA Quit..."
            for t in threads:
                os.killpg(os.getpgid(t.pid), signal.SIGKILL)
                print "kill [", t.pid, "]"
            break

except KeyboardInterrupt:
    print "Killing SIPUA..."
    for t in threads:
        os.kill(t.pid, signal.SIGTERM)
