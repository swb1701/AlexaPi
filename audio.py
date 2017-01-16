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
    p.stdin.write("version\n")
    p.stdin.flush()
    lines=[]
    done=False
    while not done:
        line=p.stdout.readline()
        if line.startswith("Version"):
            break;
        else:
            lines.append(line)
    p.stdin.write("quit\n")
    p.stdin.flush()
    return(lines)

def isConnected(device):
    con=False
    for line in btctl("info "+device):
        if line.find("Connected: yes")>-1:
            con=True
            break
    return(con)

def ensureConnected(device):
    if isConnected(device):
        print("Echo is already connected -- we're good")
        return(True)
    else:
        retry=5
        while retry>0:
            print("Attempting to connect to the Echo...")
            btctl("connect "+device)
            print("Waiting to see if the connection (if established) is stable...")
            time.sleep(10)
            if isConnected(device):
                print("OK, we're still connected -- things must be OK")
                return(True)
            retry=retry-1
            print("We're going to try to connect again...")
        return(False)

#
# this assumes you've already paired but potentially pulse audio is not running or the device is not connected
# if requires you to put the BT address of your echo in the secrets.py file
#
    
def setup():    
    try:
        p=Pulse()
        ensureConnected(s.ECHO_BT_ADDRESS)
    except:
        print("Couldn't find pulseaudio running ... trying to fix that...")
        run("pulseaudio --start &")
        time.sleep(5)
        try:
            p=Pulse()
        except:
            print("Sorry, couldn't get pulseaudio running")
            print(sys.exc_info()[0])
            return(False)
        try:
            ensureConnected(s.ECHO_BT_ADDRESS)
        except:
            print("Sorry, was unable to connect to Echo after starting pulseaudio...")
            print(sys.exc_info()[0])
            return(False)
    print("We've verified pulse is running")
    cards=p.card_list()
    found=False
    for card in p.card_list():
        if card.name.startswith("bluez_card"):
            found=True
            idx=card.index
            print("Found a bluetooth audio source as card #"+str(idx))
            time.sleep(2)
            run("pactl set-card-profile "+str(idx)+" a2dp")
            print("I've ensured that the bluetooth card is using a2dp profile")
            time.sleep(2)
            foundSink=False
            for sink in p.sink_list():
                if sink.description.startswith("Echo"):
                    foundSink=True
                    print("Found "+sink.description+" as sink #"+str(sink.index))
                    run("pactl set-default-sink "+str(sink.index))
                    print("I've set the Echo is the default sink")
                    return(True)
            if not foundSink:
                print("Despite having set the a2dp profile for #"+str(idx)+" we still can't find the Echo sink")
                return(False)
    if not found:
        print("Sorry you probably need to connect to bluetooth on the Echo")
        return(False)
    return(True)

#print(setup())
