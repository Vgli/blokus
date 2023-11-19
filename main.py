#MVC framework adapted from http://ezide.com/games/writing-games.html

import sys
import pygame
import src.events as e
import src.controllers as c
import src.views as v
import src.objects as o

def init(evManager):
    o.createBoard()
    o.createPlayers(1,3, evManager)

def main():
    pygame.init()
    evManager = e.EventManager()
    keyb = c.KeyboardController(evManager)
    mouse = c.MouseController(evManager)
    tick = c.TickController(evManager)
    init(evManager)
    pygameView = v.PygameView(evManager, fullscreen=True)

    tick.run()

    pygame.quit()
    sys.exit()



main()
