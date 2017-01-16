#
# Set Up Audio Pairing with Alexa from a Pi
#

import os
import sys
import secrets as s
from pulsectl import Pulse

def run(cmd):
    print("Executing:"+cmd)
    os.system(cmd)

def btctl(cmd):
    print("Sending "+cmd+" to bluetoothctl...")
    os.system('echo -e "'+cmd+'\nquit\n"|bluetoothctl')

try:
    p=Pulse()
except:
    print("Couldn't find pulseaudio running ... trying to fix that...")
    run("pulseaudio --start &")
    try:
        p=Pulse()
        btctl("connect "+s.ECHO_BT_ADDRESS)
    except:
        print("Sorry, couldn't get pulseaudio running")
        sys.exit(0)
print("We've verified pulse is running")
cards=p.card_list()
for card in p.card_list():
    if card.name.startswith("bluez_card"):
        idx=card.index
        print("Found a bluetooth audio source as card #"+str(idx))
        run("pactl set-card-profile "+str(idx)+" a2dp")
        print("I've ensured that the bluetooth card is using a2dp profile")
        for sink in p.sink_list():
            if sink.description.startswith("Echo"):
                print("Found "+sink.description+" as sink #"+str(sink.index))
                run("pactl set-default-sink "+str(sink.index))
                print("I've set the Echo is the default sink")
