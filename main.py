#MVC framework adapted from http://ezide.com/games/writing-games.html

import sys
import pygame
import src.events as e
import src.controllers as c
import src.views as v
import src.objects as o

def init(evManager):
    o.createBoard()
    o.createPlayers(3,1, evManager)

def main():
    pygame.init()
    evManager = e.EventManager()
    pygameView = v.PygameView(evManager, fullscreen=True)

    pygame.quit()
    sys.exit()



main()
