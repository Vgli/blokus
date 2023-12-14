import src.events as e
import src.objects as o
import numpy as n
import pygame
import src.menu as m
from pygame import display, Surface, font, image, surfarray, Rect
from os.path import join
import pygame_menu

class PygameView:
    def __init__(self, evManager, fullscreen = False, menu = True):
        self.evManager = evManager
        self.evManager.RegisterListener(self)
        self.fullscreen = fullscreen
        self.menu = menu
        self.score = False
        if fullscreen:
            self.window = display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.window = display.set_mode((720,420))

        if self.menu:
            self.drawMenu(self.window)

        else:

            self.winsize = self.window.get_size()
            display.set_caption("Blokus")
            self.background = Surface( self.window.get_size() )
            self.background.fill( (255,255,255) )
            self.window.blit( self.background, (0,0) )
            sbLoc = (int(self.winsize[1]) , 0)
            self.scorebox = {"surf": Surface((100,200)), "loc": sbLoc }
            self.scorebox["surf"].fill((255,255,255))
            self.font = font.Font(None, 40)
            pbLoc = (int(self.winsize[1]) + 100, 0)
            self.piecebox = self.window.subsurface(Rect(pbLoc,(200,420)))
            self.piecebox.fill((255,255,255))
            self.drawBoard()
            self.drawPiece()
            self.drawScores()
            self.drawPlayerPieces()
            display.flip()

    def toggleGameState(self, new_state):
        self.game_state = new_state
        if new_state == e.GameState.MENU:
            self.drawMenu()
        elif new_state == e.GameState.PLAYING:
            o.players.update_pygameViewer(self)  # Update the PygameViewer for playing mode
            # Add other logic for playing mode if needed

        

        # Update the display
        pygame.display.flip()


    def drawMenu(self, window):
        config = m.config()
        print('printing menu')
        menu = pygame_menu.Menu('Welcome', 400, 300, theme=pygame_menu.themes.THEME_BLUE)
        menu.add.selector('Difficulty :', [('Level 1', 1), ('Level 2', 2), ('Level 3', 3), ('Level 4', 4), ('Level 5', 5)], onchange = config.set_difficulty)
        menu.add.selector('Human Players :', [('1', 1), ('2', 2), ('3', 3),('4', 4)], onchange = config.set_num_players)
        menu.add.button('Play', config.start_the_game, menu, accept_kwargs=True)
        menu.add.button('Quit', pygame_menu.events.EXIT)
        while self.menu:
            menu.mainloop(window)


    def updateView(self, fullscreen = False):
        print('menu: ', self.menu)
        if fullscreen:
            self.window = display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.window = display.set_mode((720,420))

        if self.menu:
            self.drawMenu(self.window)
        
        if self.score:
            self.drawScores()

        else:
            self.winsize = self.window.get_size()
            display.set_caption("Blokus")
            self.background = Surface( self.window.get_size() )
            self.background.fill( (255,255,255) )
            self.window.blit( self.background, (0,0) )
            sbLoc = (int(self.winsize[1]) , 0)
            self.scorebox = {"surf": Surface((100,200)), "loc": sbLoc }
            self.scorebox["surf"].fill((255,255,255))
            self.font = font.Font(None, 40)
            pbLoc = (int(self.winsize[1]) + 100, 0)
            self.piecebox = self.window.subsurface(Rect(pbLoc,(200,420)))
            self.piecebox.fill((255,255,255))
            self.drawBoard()
            self.drawPiece()
            self.drawScores()
            self.drawPlayerPieces()
            display.flip()

    def drawBoard(self):
        csize_x = self.winsize[0] / len(o.board.matrix[0])
        csize_y = self.winsize[1] / len(o.board.matrix)
        csize = min(csize_x, csize_y)
        #update board cell size
        o.board.csize = csize
        space = image.load(join("sprites", "space.png"))
        pieceImg = image.load(join("sprites", "piece.jpg"))

        # Scale the background image to match the cell size
        space = pygame.transform.scale(space, (int(csize), int(csize)))
        pieceImg = pygame.transform.scale(pieceImg, (int(csize), int(csize)))

        pieceArray = surfarray.array3d(pieceImg)

        for row in o.board.matrix:
            for cell in row:
                x_pos = int(cell.x * csize)
                y_pos = int(cell.y * csize)
                self.window.blit(space, (x_pos, y_pos))
                if cell.color:
                    piece = n.array(pieceArray)
                    if cell.color == "r":
                        piece[:,:,1:] = 0
                    elif cell.color == "g":
                        piece[:,:,[0,2]] = 0
                    elif cell.color == "b":
                        piece[:,:,:2] = 0
                    elif cell.color == "y":
                        piece[:,:,2] = 0
                    surfarray.blit_array(pieceImg, piece)

                    x_piece_pos = int(cell.x * csize + 1)
                    y_piece_pos = int(cell.y * csize + 1)
                    self.window.blit(pieceImg,(x_piece_pos, y_piece_pos))
    

    def drawPiece(self):
        csize = o.board.csize
        pieceImg = image.load(join("sprites", "piece.jpg"))
        pieceImg = pygame.transform.scale(pieceImg, (int(csize), int(csize)))
        p = o.players.cur
        pieceArray = surfarray.array3d(pieceImg)
        if p.c == "r":
            pieceArray[:,:,1:] = 0
        elif p.c == "g":
            pieceArray[:,:,[0,2]] = 0
        elif p.c == "b":
            pieceArray[:,:,:2] = 0
        elif p.c == "y":
            pieceArray[:,:,2] = 0
        surfarray.blit_array(pieceImg, pieceArray)
        pieceImg.set_alpha(175)
        bpos = n.array((p.pos[0]*csize+1, p.pos[1]*csize+1))
        for r in range(len(p.curPiece.m)):
            for c in range(len(p.curPiece.m[0])):
                if p.curPiece.m[r][c] == 1:
                    pos = n.array((c*csize,r*csize))
                    self.window.blit(pieceImg, bpos+pos)


    def drawTrophy(self, color, x, y):
        window_width, window_height = self.window.get_size()
        trophyImg = image.load(join("sprites", "trophy.png"))
        trophyImg = pygame.transform.scale(trophyImg, (window_height/30*8, window_height/30*9))
        trophyArray = surfarray.array3d(trophyImg)
        if color == "r":
            trophyArray[:,:,1:] = 0
        elif color == "g":
            trophyArray[:,:,[0,2]] = 0
        elif color == "b":
            trophyArray[:,:,:2] = 0
        elif color == "y":
            trophyArray[:,:,2] = 0
        else:
            trophyArray[:, :, [0, 1, 2]] = 128 #grey if more than one winner
        surfarray.blit_array(trophyImg, trophyArray)
        self.window.blit(trophyImg, (x, y))

    def drawScores(self):
        if self.score:
            white = (255, 255, 255)
            black = (0, 0, 0)
            self.window.fill(white)
            window_width, window_height = self.window.get_size()
            pygame.draw.rect(self.window, black, (window_height,0,window_width-window_height, window_height))  # The last argument (2) is the thickness of the border

            scores = []
            spacing_between_text = 10  # Spacing between consecutive text surfaces
            current_y = 0 + 100
            winner = self.find_winner(o.players.players)

            for player in o.players.players:
                player_info = f"{player.c}: {player.score}"
                text_surface = self.font.render(player_info, True, white)
                scores.append(text_surface)

            for text_surface in scores:
                text_rect = text_surface.get_rect()
                text_rect.midtop = ((window_width-window_height)*3/2, current_y)
                self.window.blit(text_surface, text_rect)
                current_y += text_rect.height + spacing_between_text
            #print and the winner is    
            text_rect.midtop = ((window_width-window_height)*3/2, current_y)
            self.window.blit(self.font.render('And the whinner is...', True, white), text_rect)
            current_y += text_rect.height + spacing_between_text
            if winner == 'grey':
                text_rect.midtop = ((window_width-window_height)*3/2, current_y)
                self.window.blit(self.font.render('it is a tie!', True, white), text_rect)
                current_y += text_rect.height + spacing_between_text
                
            self.drawTrophy(winner,window_height + 50, current_y + 50)
            
            


            self.drawBoard()
            pygame.display.flip()

        else:
            self.scorebox["surf"].fill((255,255,255))
            scores = []
            for player in o.players.players:
                if player.is_bot:
                    color = (0,0,0)
                else:
                    color = (50,100,255)
                scores.append(self.font.render(player.c+": "+str(player.score), True, color))
            for s in range(len(scores)):
                self.scorebox["surf"].blit(scores[s],(0,s*50))
            self.window.blit(self.scorebox["surf"],self.scorebox["loc"])

    def find_winner(self, players):
        players_dict = {}
        for player in players:
            players_dict[player.c] = player.score

        max_value = max(players_dict.values())
        max_keys = [key for key in players_dict if players_dict[key]==max_value]

        if len(max_keys) == 1:
            return max_keys[0]
        else:
            return 'grey'
        
    def drawPlayerPieces(self):
        self.piecebox.fill((255,255,255))
        pieceImg = image.load(join("sprites", "piecesmall.jpg"))
        
        pieceArrays = {"r": surfarray.array3d(pieceImg),
                       "g": surfarray.array3d(pieceImg),
                       "b": surfarray.array3d(pieceImg),
                       "y": surfarray.array3d(pieceImg)}
        pieceArrays["r"][:,:,1:] = 0
        pieceArrays["g"][:,:,[0,2]] = 0
        pieceArrays["b"][:,:,:2] = 0
        pieceArrays["y"][:,:,2] = 0

        bpos = n.array((0,0))
        for player in o.players.players:
            surfarray.blit_array(pieceImg, pieceArrays[player.c])
            for size in player.pieces.keys():
                for p in player.pieces[size]:
                    if len(p.m) < len(p.m[0]):
                        isTaller = True
                        h = len(p.m)
                        psize = (9*len(p.m[0]), 9*len(p.m))
                    else:
                        isTaller = False
                        h = len(p.m[0])
                        psize = (9*len(p.m), 9*len(p.m[0]))
                    pieceImg.set_alpha(100)
                    if player is o.players.cur:
                        pieceRect = self.piecebox.subsurface(Rect(bpos,psize))
                        o.players.pieces.append((pieceRect, size, p))
                        if p is player.curPiece:
                            pieceImg.set_alpha(255)
                    for r in range(len(p.m)):
                        for c in range(len(p.m[0])):
                            if isTaller:
                                x = c
                                y = r
                            else:
                                x = r
                                y = c
                            if p.m[r][c] == 1:
                                pos = n.array((x*9,y*9))
                                if player.c == o.players.cur.c:
                                    pieceRect.blit(pieceImg, pos)
                                else:
                                    self.piecebox.blit(pieceImg, bpos+pos)
                    bpos[1] += h*9 + 1
            bpos[0] += 50
            bpos[1] = 0
    def Notify(self, event):
        if isinstance(event, (e.GetPiece, e.RotPiece, e.NextPiece, e.MovePiece, e.SwitchPiece)):
            if not self.menu:
                self.drawBoard()
                self.drawPiece()
                if isinstance(event, (e.GetPiece, e.NextPiece, e.SwitchPiece)):
                    self.drawPlayerPieces()
                display.update()
        if isinstance(event, e.NextTurn):
            if not self.menu:
                self.drawBoard()
                self.drawPiece()
                self.drawPlayerPieces()
                self.drawScores()
                display.update()
        if isinstance(event, (e.ToggleFullscreen, e.ShowMenu, e.ShowScore)):
            if isinstance(event, e.ToggleFullscreen):
                self.fullscreen = not self.fullscreen
                self.updateView(self.fullscreen)
            if isinstance(event, e.ShowMenu):
                self.menu = not self.menu
                self.updateView(self.fullscreen)
            if isinstance(event, e.ShowScore):
                print('showScore')
                self.score = not self.score
                self.updateView(self.fullscreen)
        if isinstance(event, e.StartGameEvent):
            self.updateView(self.fullscreen)
