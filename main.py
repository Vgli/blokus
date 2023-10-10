#MVC framework adapted from http://ezide.com/games/writing-games.html

import sys
import pygame
import events as e
import controllers as c
import views as v
import objects as o

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
    pygameView = v.PygameView(evManager)

    tick.run()

    pygame.quit()
    sys.exit()



main()
