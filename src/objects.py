import numpy as np
from src import events as e
from src import bot

class LinkedGridNode:
    def __init__(self, u, l, pos):
        self.up = u
        self.left = l
        if u:
            self.up.down = self
        if l:
            self.left.right = self
        self.down = None
        self.right = None
        self.color = None
        self.x = pos[0]
        self.y = pos[1]
        self.pos = pos
    def colorize(self, c):
        self.color = c

class LinkedGrid:
    def __init__(self, width, height, cellSize):
        self.matrix = []
        self.w = width
        self.h = height
        self.csize = cellSize
        for h in range(height):
            self.matrix.append([])
            for w in range(width):
                if h != 0:
                    nodeUp = self.matrix[h-1][w]
                else:
                    nodeUp = None
                if w!= 0:
                    nodeLeft = self.matrix[h][w-1]
                else:
                    nodeLeft = None
                pos = (w,h)
                self.matrix[h].append(LinkedGridNode(nodeUp,nodeLeft,pos))

class Piece:
    def __init__(self, matrix, player):
        self.player = player
        self.c = player.c
        self.m = np.array(matrix)
    def fixPos(self):
        #add player position to piece array dimensions
        botright = self.player.pos + self.m.shape[::-1]
        #check if this goes off the board...
        while botright[0] > 20:#hardcoding size for now, fix for variable board size
            self.player.pos -= (1,0)
            botright -= (1,0)
        while botright[1] > 20:
            self.player.pos -= (0,1)
            botright -= (0,1)
        while self.player.pos[0] < 0:
            self.player.pos += (1,0)
        while self.player.pos[1] < 0:
            self.player.pos += (0,1)
    def rotflip(self,rottype):
        if rottype == "rotCW":
            self.m = np.rot90(self.m,3)
        elif rottype == "rotCCW":
            self.m = np.rot90(self.m)
        elif rottype == "flip":
            self.m = np.fliplr(self.m)
        self.fixPos()
    def place(self):
        bpos = board.matrix[self.player.pos[0]][self.player.pos[1]]
        for r in range(len(self.m)):
            for c in range(len(self.m[r])):
                if self.m[r][c] == 1:
                    cell = board.matrix[r+bpos.x][c+bpos.y]
                    if cell.color:
                        break
                    #if piece overlaps another piece, we shouldn't place it!
                    for adjCell in [cell.up,cell.left,cell.down,cell.right]:
                        if adjCell and adjCell.color == self.c:
                            break
                    else:
                        continue
                    break
            else:   #if we didn't break...
                continue
            break   #if we did break, break outer loop
                    
        else:
            for r in range(len(self.m)):
                for c in range(len(self.m[r])):
                    if self.m[r][c] == 1:
                        board.matrix[r+bpos.x][c+bpos.y].colorize(self.c)
            self.player.delPiece()
            return True #we placed the piece, so delete it and return true
        return False #we didn't place the piece =(
    
    def placeFirst(self):#check if in corner
        bpos = board.matrix[self.player.pos[0]][self.player.pos[1]]
        if self.m[0][0] == 1 and np.array_equal(self.player.pos,np.array([0,0])):
            #this piece is in the top-left corner!
            ret = self.place()
        elif self.m[-1][-1] == 1 and np.array_equal(self.player.pos+self.m.shape, np.array(board.matrix).shape):
            #this piece is in the bottom-right corner!
            ret = self.place()
        elif len(players.players) > 2:
            #if there are only two players, orthagonally adjacent corners are disallowed
            if self.m[-1][0] == 1 and self.player.pos[1]+len(self.m) == len(board.matrix):
                #this piece is in the bottom-left corner!
                ret = self.place()
            elif self.m[0][-1] == 1 and self.player.pos[0]+len(self.m[0]) == len(board.matrix[0]):
                #this piece is in the top-right corner!
                ret = self.place()
            else:
                return False
        else:
            return False
        if ret:
            self.player.hasntPlayed = False
            return ret
    def placeRest(self): #check if diagonal to one of your pieces
        bpos = board.matrix[self.player.pos[0]][self.player.pos[1]]
        for r in range(len(self.m)):
            for c in range(len(self.m[r])):
                if self.m[r][c] == 1:
                    cell = board.matrix[r+bpos.x][c+bpos.y]
                    for ud in [cell.up, cell.down]:
                        if ud:
                            for dAdjCell in [ud.left, ud.right]:
                                if dAdjCell and dAdjCell.color == self.c:
                                    return self.place()
        return False

class Player:
    def __init__(self, color, is_bot=False, preload = True, all_playable_moves = {}):
        self.c = color
        self.is_bot = is_bot
        self.pieces = dict()
        self.score = 0
        self.pos = np.array([0,0])
        self.start_pos = tuple()
        with open("data/pieces.blok", "r") as f:
            for line in f:
                l = eval(line.rstrip())
                if isinstance(l,int):
                    s = l
                    if s not in self.pieces:
                        self.pieces[s] = []
                elif isinstance(l,list):
                    l = Piece(l, self)
                    self.pieces[s].append(l)
                    self.score -= s
        self.curPiece = self.pieces[1][0]
        self.curPieceIndex = 0
        self.curPieceKey = 1
        self.hasntPlayed = True
        self.isDone = False
        if preload:
            self.all_playable_moves = bot.get_all_playable_moves('data/all_playable_moves.json')
        else:
            self.all_playable_moves = all_playable_moves
    def setPos(self, pos):
        self.pos = pos
    def getPiece(self, num):
        if num in self.pieces:
            if self.pieces[num]:
                self.curPiece = self.pieces[num][0]
                self.curPieceKey = num
                self.curPieceIndex = 0
            else:
                self.curPieceKey = next(iter(self.pieces))
                self.curPieceIndex = 0
                self.curPiece = self.pieces[self.curPieceKey][0]
        else:
            self.curPieceKey = next(iter(self.pieces))
            self.curPieceIndex = 0
            self.curPiece = self.pieces[self.curPieceKey][0]
        self.curPiece.fixPos()
    def nextPiece(self, direction):
        pKey = self.curPieceKey
        if direction == "f":
            self.curPieceIndex += 1
            if self.curPieceIndex >= len(self.pieces[pKey]):
                self.curPieceIndex = 0
        if direction == "b":
            self.curPieceIndex -= 1
            if self.curPieceIndex < 0:
                self.curPieceIndex = len(self.pieces[pKey])-1
        self.curPiece = self.pieces[pKey][self.curPieceIndex]
        self.curPiece.fixPos()
    def move(self, direction, pos):
        if direction:
            if direction == "up":
                self.pos -= (0,1)
            elif direction == "down":
                self.pos += (0,1)
            elif direction == "left":
                self.pos -= (1,0)
            elif direction == "right":
                self.pos += (1,0)
            self.curPiece.fixPos()
        elif pos:
            prev = self.pos
            self.pos = np.floor(np.array(pos)).astype(int)
            self.curPiece.fixPos()
            if (self.pos == prev).all():
                players.evManager.Post(e.PlacePiece())
            
    def delPiece(self):
        pKey = self.curPieceKey
        pIn = self.curPieceIndex
        self.score += pKey
        del self.pieces[pKey][pIn]
        if self.pieces[pKey]:
            self.nextPiece("b")
        else:
            del self.pieces[pKey]
            self.getPiece(1)
    
    def removePiece(self, pKey, pIn):
        self.score += pKey
        del self.pieces[pKey][pIn]
        if self.pieces[pKey]:
            self.nextPiece("b")
        else:
            del self.pieces[pKey]
            if len(self.pieces) > 0:
                self.getPiece(1)

    def updateAllMoves(self,tuple_piece_to_remove):
        for key in self.all_playable_moves.keys():
            self.all_playable_moves[key] = [sublist for sublist in self.all_playable_moves[key] if sublist[0] != list(tuple_piece_to_remove)]

    def performBotAction(self):
        bot.selectBotMove(board, self)
        

class Players:
    def __init__(self, num_human_players, num_bot_players, evManager):
        self.evManager = evManager
        self.evManager.RegisterListener(self)
        colors = ["r", "g", "b", "y"]
        remaining_colors = colors[num_human_players:]
        self.players = []
        for p in range(num_human_players):
            self.players.append(Player(colors[p]))
        for _ in range(num_bot_players):
            bot_color = remaining_colors.pop(0)  # Get the first remaining color for the bot
            self.players.append(Player(bot_color, is_bot=True))
        self.activePlayers = list(self.players)
        self.curI = 0
        self.cur = self.activePlayers[self.curI]
        self.pieces = []
        self.res = 0

    def nextTurn(self):
        self.curI += 1
        if self.curI >= len(self.activePlayers):
            self.curI = 0
        self.cur = self.activePlayers[self.curI]

        if self.cur.is_bot:  # Check if the current player is a bot
            # Call bot logic function to get the bot's move
            bot.selectBotMove(board, self.cur)  # Get position and piece from bot
            self.evManager.Post(e.NextTurn())  # Continue the game after the bot's move
        else:
            self.pieces = []  # Reset the pieces list for human players
    def resign(self):
        self.res += 1
        if self.res >= 2:
            del self.activePlayers[self.curI]
            self.curI -= 1
            self.evManager.Post(e.NextTurn())
    def Notify(self, event):
        if isinstance(event, e.NextTurn):
            self.nextTurn()
            self.res = 0
        elif isinstance(event, e.GetPiece):
            self.cur.getPiece(event.num)
            self.res = 0
        elif isinstance(event, e.SwitchPiece):
            self.cur.getPiece(event.s)
            while self.cur.curPiece is not event.p:
                self.cur.nextPiece("f")
            self.res = 0
        elif isinstance(event, e.NextPiece):
            self.cur.nextPiece(event.direction)
            self.res = 0
        elif isinstance(event, e.RotPiece):
            self.cur.curPiece.rotflip(event.rottype)
            self.res = 0
        elif isinstance(event, e.MovePiece):
            self.cur.move(event.direction, event.pos)
            self.res = 0
        elif isinstance(event, e.PlacePiece):
            if self.cur.hasntPlayed:
                if self.cur.curPiece.placeFirst():
                    self.evManager.Post(e.NextTurn())
            elif self.cur.curPiece.placeRest():
                self.evManager.Post(e.NextTurn())
            self.res = 0
        elif isinstance(event, e.ResignEvent):
            self.resign()
            print (self.res)
                
            

def createBoard(w=20,h=20, c=20):
    global board
    board = LinkedGrid(w,h,c)
def createPlayers(num_human_players, num_bot_players, evManager):
    global players
    players = Players(num_human_players, num_bot_players, evManager)
