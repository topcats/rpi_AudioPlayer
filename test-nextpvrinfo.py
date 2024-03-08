#!/usr/bin/python3
import sys
if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

import json

print("TEST - NextPvr Info")

from nextpvrinfo import *


nAction = NextpvrInfo(hostip="localhost", hostport=8866, pin=1234)

currentinfo = nAction.GetChannelCurrent(channel_id=8560)


print(nAction.sid)

print (currentinfo)



print()
print("TEST - NextPvr SID")

sAction = NextpvrSid(hostip="localhost", hostport=8866)

oldsid = sAction.GetSid()
print('oldsid', oldsid)

bsaved = sAction.SaveSid(nAction.sid)
print('bsaved', bsaved)
