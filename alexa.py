import boto3
import sys
import os
import json
import time
from subprocess import Popen, PIPE, STDOUT

import secrets as s

uesess = boto3.Session(
        aws_access_key_id=s.AWS_ACCESS_KEY,
        aws_secret_access_key=s.AWS_SECRET_KEY,
        region_name=s.AWS_REGION
)

cmd=["/usr/bin/sudo","/usr/bin/python","screen.py"]

p=Popen(cmd,stdout=PIPE,stdin=PIPE,stderr=PIPE)

polly=uesess.client('polly')
sqs=uesess.client('sqs')
s3=uesess.client('s3')
rekog=uesess.client('rekognition')

def screen(cmd):
    print("Screen:"+json.dumps(cmd))
    p.stdin.write(json.dumps(cmd)+'\n')
    p.stdin.flush()

def speak(text):
    resp=polly.synthesize_speech(OutputFormat='mp3',Text=text,VoiceId='Salli')
    mp3file=open('test.mp3','w')
    mp3file.write(resp['AudioStream'].read())
    mp3file.close()
    os.system("/usr/bin/mpg123 -q test.mp3")

def snap():
    os.system("/usr/bin/raspistill -t 1 -w 640 -h 480 -o snap.jpg")
    show_image("snap.jpg")

def make_collection(name):
    resp=rekog.create_collection(CollectionId=name)
    print(resp)

def delete_collection(name):
    resp=rekog.delete_collection(CollectionId=name)
    print(resp)

def index_face(name,obj):
    photoName=obj['S3Object']['Name']
    extName=":"+name+":"+(photoName.replace('/','_'))
    resp=rekog.index_faces(CollectionId='home',Image=obj,ExternalImageId=extName,DetectionAttributes=['ALL'])
    if 'FaceDetails' in resp:
        fd=resp['FaceDetails']
        if len(fd)>0:
            bb=fd[0]['BoundingBox']
            iw=640
            ih=480
            fw=int(bb['Width']*iw)
            fh=int(bb['Height']*ih)
            fl=int(bb['Left']*iw)
            ft=int(bb['Top']*ih)
            show_subimage("snap.jpg",fl,ft,fw,fh)
    print(resp)

def search_faces(obj):
    try:
        resp=rekog.search_faces_by_image(CollectionId='home',Image=obj)
        if 'FaceMatches' in resp:
            fm=resp['FaceMatches']
            for match in fm:
                print(match)
                extName=match['Face']['ExternalImageId']
                label=None
                if (extName.startswith(":")):
                    parts=extName.split(':')
                    label=parts[1]
                else:
                    label=extName
                speak("That's "+label)
                break
    except:
        speak("I didn't see a face to recognize")
        resp="No Face"
    return(resp)

def push_photo():
    ltime=time.localtime()
    filename=time.strftime("photo/%Y/%m/%d/%H:%M:%S.jpg")
    s3.put_object(Bucket=s.BUCKET_NAME,Key=filename,Body=open('snap.jpg','rb'))
    print(filename)
    return({'S3Object':{'Bucket':s.BUCKET_NAME,'Name':filename}})

def get_photo(key):
    resp=s3.get_object(Bucket=s.BUCKET_NAME,Key=key)
    f=open('snap.jpg','wb')
    f.write(resp['Body'].read())
    f.close()

faceindex=[]    

def list_faces():
    global faceindex
    resp=rekog.list_faces(CollectionId='home',MaxResults=100)
    print(resp)
    if 'Faces' in resp:
        fcnt=1
        faceindex=[]
        for face in resp['Faces']:
            extName=face['ExternalImageId']
            faceindex.append(face['ImageId'])
            extName=extName.replace('_','/')
            print(extName)
            if extName.startswith(':'):
                cnt=2
                i=0
                while cnt>0:
                    if extName[i]==':':
                        cnt=cnt-1
                    i=i+1
                key=extName[i:]
                parts=extName.split(':')
                #print("Key:<"+key+">")
                get_photo(key)
                bb=face['BoundingBox']
                iw=640
                ih=480
                fw=int(bb['Width']*iw)
                fh=int(bb['Height']*ih)
                fl=int(bb['Left']*iw)
                ft=int(bb['Top']*ih)
                show_subimage("snap.jpg",fl,ft,fw,fh,str(fcnt)+': '+parts[1])
                time.sleep(2)
            else:
                print(str(fcnt)+': '+extName)
            fcnt=fcnt+1

def remove_face(index):
    print("Deleting ImageId:<"+faceindex[index-1]+">")
    faces=[]
    faces.append(faceindex[index-1])
    resp=rekog.delete_faces(CollectionId='home',FaceIds=faces)
    print(resp)
    

def detect_faces(obj):
    resp=rekog.detect_faces(Image=obj,Attributes=['ALL'])
    if 'FaceDetails' in resp:
        fd=resp['FaceDetails']
        if len(fd)>0:
            bb=fd[0]['BoundingBox']
            iw=640
            ih=480
            fw=int(bb['Width']*iw)
            fh=int(bb['Height']*ih)
            fl=int(bb['Left']*iw)
            ft=int(bb['Top']*ih)
            show_subimage("snap.jpg",fl,ft,fw,fh)
    print(resp)

def clear_screen():
    screen({"cmd":"clear"})

def show_image(filename):
    screen({"cmd":"image","file":filename})
    
def show_subimage(filename,x,y,w,h,label=None):
    cmd={"cmd":"image","file":filename,"crop":{"x":x,"y":y,"w":w,"h":h}}
    if label!=None:
        cmd['label']=label
    screen(cmd)

speak("Welcome to the Alexa companion -- listening for commands")
clear_screen()
queue=s.SQS_QUEUE
while True:
    resp=sqs.receive_message(QueueUrl=queue,WaitTimeSeconds=20)
    print(resp)
    if 'Messages' in resp:
        for msg in resp['Messages']:
            cmd=json.loads(msg['Body'])
            c=cmd['cmd']
            if c=='speak':
                if 'delay' in cmd:
                    print("delay by "+str(cmd['delay'])+" seconds")
                    time.sleep(cmd['delay'])
                    print("delay is done")
                speak(cmd['text'])
                print("speech is done")
            elif c=='snap':
                snap()
            elif c=='detect_faces':
                snap()
                obj=push_photo()
                detect_faces(obj)
            elif c=='make_collection':
                make_collection(cmd['name'])
            elif c=='delete_collection':
                delete_collection(cmd['name'])
            elif c=='index_face':
                snap()
                obj=push_photo()
                index_face(cmd['name'],obj)
                speak("I indexed that face as "+cmd['name'])
            elif c=='search_faces':
                snap()
                obj=push_photo()
                resp=search_faces(obj)
            elif c=='clear_screen':
                clear_screen()
            elif c=='show_faces':
                list_faces()
            elif c=='remove_face':
               remove_face(cmd['index'])
                
            sqs.delete_message(QueueUrl=queue,ReceiptHandle=msg['ReceiptHandle'])
                
