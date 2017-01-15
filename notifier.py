#
# Simple Alexa Spoken Notification Demo
# Scott Bennett, 1/17
#

import boto3
import sys
import os
import json
import time

import secrets as s #import our keys and such

#set up an AWS session
uesess = boto3.Session(
        aws_access_key_id=s.AWS_ACCESS_KEY,
        aws_secret_access_key=s.AWS_SECRET_KEY,
        region_name=s.AWS_REGION
)

polly=uesess.client('polly') #for our speech synthesis
sqs=uesess.client('sqs') #for receiving commands

#speak some text (on Alexa)
def speak(text):
    resp=polly.synthesize_speech(OutputFormat='mp3',Text=text,VoiceId='Salli')
    mp3file=open('notify.mp3','w')
    mp3file.write(resp['AudioStream'].read())
    mp3file.close()
    os.system("/usr/bin/mpg123 -q notify.mp3")

speak("Welcome to the Alexa Notifier -- listening for commands")
#set the queue we get commands from
queue=s.SQS_QUEUE2
#our main control loop
while True:
    #get messages containing JSON from SQS (20 second long poll)
    resp=sqs.receive_message(QueueUrl=queue,WaitTimeSeconds=20)
    print(resp)
    if 'Messages' in resp:
        for msg in resp['Messages']:
            try:
                #parse the json of the message
                try:
                    cmd=json.loads(msg['Body']) #illustrating use of json for more complex commands
                    #get the command
                    c=cmd['cmd']
                    #handle the command
                    if c=='speak':
                        speak(cmd['text'])
                except:
                    speak(msg['Body']) #if not in json, just speak it
            except:
                None
            finally:
                #delete the message from the queue
                sqs.delete_message(QueueUrl=queue,ReceiptHandle=msg['ReceiptHandle'])
                
