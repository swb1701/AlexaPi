#
# Demonstration of Voice Interaction with a Raspberry Pi 3, Camera, and PiTFT Shield Doing Face Recognition
# Scott Bennett, 1/17
#

import pygame
import os
import time
import json
import sys

#set up some common colors
blue=(0,0,255)
black=(0,0,0)

#set up our PiTFT 320x240
os.putenv('SDL_FBDEV','/dev/fb1')
pygame.init()
screen=pygame.display.set_mode((320,240))
screen.fill(blue)
pygame.display.update()
pygame.mouse.set_visible(False)

#clear the screen
def clear_screen():
    screen.fill(black)
    pygame.display.update()

#from www.pygame.org/pcr/transform_scale/    
def aspect_scale(img,(bx,by)):
    ix,iy = img.get_size()
    if ix > iy: # fit to width
        scale_factor = bx/float(ix)
        sy = scale_factor * iy
        if sy > by:
            scale_factor = by/float(iy)
            sx = scale_factor * ix
            sy = by
        else:
            sx = bx
    else: # fit to height
        scale_factor = by/float(iy)
        sx = scale_factor * ix
        if sx > bx:
            scale_factor = bx/float(ix)
            sx = bx
            sy = scale_factor * iy
        else:
            sy = by
    return pygame.transform.scale(img,(int(sx),int(sy)))

#our command loop
while True:
    #read a line from the pipe
    line=sys.stdin.readline()
    #parse the json
    map=json.loads(line)
    #get the command
    cmd=map['cmd']
    #handle the command
    if cmd=="clear":
        clear_screen()
    elif cmd=="fill":
        screen.fill(blue)
        pygame.display.update()
    elif cmd=="image":
        img=pygame.image.load(map['file']).convert()
        if 'crop' in map:
            crop=map['crop']
            img=img.subsurface((crop['x'],crop['y'],crop['w'],crop['h']))
        aspect_scale(img,(320,240))
        size=img.get_rect().size
        offx=(320-size[0])/2
        offy=(240-size[1])/2
        #img=pygame.transform.scale(img,(320,240))
        screen.fill(black)
        screen.blit(img,(offx,offy))
        if 'label' in map:
            myfont = pygame.font.SysFont("monospace",30, bold=True)
            label=myfont.render(map['label'],1,(0,0,255))
            screen.blit(label,(0,200))
        pygame.display.update()
    elif cmd=="exit":
        clear_screen()
        sys.exit(0)


