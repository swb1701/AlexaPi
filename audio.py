#
# Set Up Audio Pairing with Alexa from a Pi
#

import os
import sys
import time
import secrets as s
from subprocess import Popen, PIPE

from pulsectl import Pulse

def run(cmd):
    print("Executing:"+cmd)
    os.system(cmd)

def btctl(cmd):
    print("Sending "+cmd+" to bluetoothctl...")
    p=Popen("/usr/bin/bluetoothctl",stdout=PIPE,stdin=PIPE,stderr=PIPE)
    p.stdin.write(cmd+"\n")
    p.stdin.flush()
    time.sleep(4)
    p.stdin.write("quit\n")
    p.stdin.flush()
    #btcmd="echo -e '"+cmd+"\\nquit\\n'|sed 's/-e //'|bluetoothctl"
    #print("Executing:"+btcmd)
    #os.system(btcmd)

try:
    p=Pulse()
except:
    print("Couldn't find pulseaudio running ... trying to fix that...")
    run("pulseaudio --start &")
    time.sleep(5)
    try:
        p=Pulse()
    except:
        print("Sorry, couldn't get pulseaudio running")
        print(sys.exc_info()[0])
        sys.exit(0)
    try:
        btctl("connect "+s.ECHO_BT_ADDRESS)
    except:
        print("Sorry, was unable to connect to Echo after starting pulseaudio...")
        print(sys.exc_info()[0])
        sys.exit(0)
print("We've verified pulse is running")
cards=p.card_list()
found=False
for card in p.card_list():
    if card.name.startswith("bluez_card"):
        found=True
        idx=card.index
        print("Found a bluetooth audio source as card #"+str(idx))
        run("pactl set-card-profile "+str(idx)+" a2dp")
        print("I've ensured that the bluetooth card is using a2dp profile")
        for sink in p.sink_list():
            if sink.description.startswith("Echo"):
                print("Found "+sink.description+" as sink #"+str(sink.index))
                run("pactl set-default-sink "+str(sink.index))
                print("I've set the Echo is the default sink")
if not found:
    print("Sorry you probably need to connect to bluetooth on the Echo")
