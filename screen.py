import pygame
import os
import time
import sys

blue=(0,0,255)
black=(0,0,0)

os.putenv('SDL_FBDEV','/dev/fb1')
pygame.init()
screen=pygame.display.set_mode((320,240))
screen.fill(blue)
pygame.display.update()
pygame.mouse.set_visible(False)

def clear_screen():
    screen.fill(black)
    pygame.display.update()

while True:
    line=sys.stdin.readline()
    if line.startswith("clear"):
        clear_screen()
    elif line.startswith("fill"):
        screen.fill(blue)
        pygame.display.update()
    elif line.startswith("exit"):
        clear_screen()
        sys.exit(0)


