import time
import sys
import pjsua as pj
import re
from subprocess import Popen, PIPE, call
import time
import os
import json
import signal
import os

if len(sys.argv) > 1:
    call_num = sys.argv[1]

timestr = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))

targetdir = "%s-%s"%(call_num, timestr)
print targetdir

call(["mkdir", "-p", "./wav/"+targetdir])
call(["cp", "*.wav", "./wav/"+targetdir+"/"])
