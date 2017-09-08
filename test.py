import os
import time
from datetime import datetime
print('time:' + str(datetime.now()))
media_file = "test.wav"
timestr = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
print "play back %s now [%s]"%(media_file,timestr)
