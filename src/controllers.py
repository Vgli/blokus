import pygame
from pygame.key import *
from src import events as e
from src import objects as o

class MouseController:
    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.RegisterListener(self)
    def Notify(self, event):
        if isinstance(event, e.PygameEvent):
            event = event.ev
            ev = None
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mpos = pygame.mouse.get_pos()
                    csize = o.board.csize
                    if mpos <= (o.board.w*csize, o.board.h*csize):
                    #needs to be in bounds both x and y, so tuple compare works here
                        pos = (mpos[0]/csize,mpos[1]/csize)
                        ev = e.MovePiece(None, pos)
                    else:
                        for p in o.players.pieces:
                            r = p[0].get_rect()
                            r.move_ip(p[0].get_abs_offset())
                            if r.collidepoint(mpos):
                                ev = e.SwitchPiece(p[1],p[2])
                                break
                elif event.button == 2:
                    self.evManager.Post(e.RotPiece("flip"))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.evManager.Post(e.RotPiece("rotCW"))
                elif event.button == 5:
                    self.evManager.Post(e.RotPiece("rotCCW"))
            if ev:
                self.evManager.Post(ev)
class KeyboardController:
    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.RegisterListener(self)
    def Notify(self, event):
        if isinstance(event, e.PygameEvent):
            event = event.ev
            ev = None
            if event.type == pygame.KEYDOWN:
                if event.key in { pygame.K_1, pygame.K_KP2 }:
                    ev = e.GetPiece(1)
                elif event.key in { pygame.K_2, pygame.K_KP2 }:
                    ev = e.GetPiece(2)
                elif event.key in { pygame.K_3, pygame.K_KP3 }:
                    ev = e.GetPiece(3)
                elif event.key in { pygame.K_4, pygame.K_KP4 }:
                    ev = e.GetPiece(4)
                elif event.key in { pygame.K_5, pygame.K_KP5 }:
                    ev = e.GetPiece(5)
                elif event.key == pygame.K_z:
                    ev = e.RotPiece("rotCCW")
                elif event.key == pygame.K_x:
                    ev = e.RotPiece("rotCW")
                elif event.key == pygame.K_LSHIFT:
                    ev = e.RotPiece("flip")
                elif event.key in { pygame.K_COMMA, pygame.K_LESS }:
                    ev = e.NextPiece("b")
                elif event.key in { pygame.K_PERIOD, pygame.K_GREATER }:
                    ev = e.NextPiece("f")
                elif event.key == pygame.K_UP:
                    ev = e.MovePiece("up")
                elif event.key == pygame.K_DOWN:
                    ev = e.MovePiece("down")
                elif event.key == pygame.K_LEFT:
                    ev = e.MovePiece("left")
                elif event.key == pygame.K_RIGHT:
                    ev = e.MovePiece("right")
                elif event.key in { pygame.K_KP_ENTER, pygame.K_RETURN }:
                    ev = e.PlacePiece()
                elif event.key == pygame.K_ESCAPE:
                    ev = e.ResignEvent()
            if ev:
                self.evManager.Post(ev)

class TickController:
    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.RegisterListener(self)
        self.on = True

    def run(self):
        while self.on:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.evManager.Post(e.QuitEvent())
                else:
                    self.evManager.Post(e.PygameEvent(event))
            self.evManager.Post(e.TickEvent())
    def Notify(self, event):
        if isinstance(event, e.QuitEvent):
            self.on = False
