import numpy as np
import src.events as e # Import events module
import src.bot as bot # Import bot module

class LinkedGridNode:
    """
    Initialize a node in the LinkedGrid, representing a cell on the game board.

    Parameters:
    - u (LinkedGridNode): Reference to the node above this node.
    - l (LinkedGridNode): Reference to the node to the left of this node.
    - pos (tuple): Position (x, y) of the node on the game board grid.

    Attributes:
    - up (LinkedGridNode): Reference to the node above this node.
    - left (LinkedGridNode): Reference to the node to the left of this node.
    - down (LinkedGridNode): Reference to the node below this node.
    - right (LinkedGridNode): Reference to the node to the right of this node.
    - color (str): Color of the cell, representing ownership or state.
    - x (int): X-coordinate of the cell's position on the game board grid.
    - y (int): Y-coordinate of the cell's position on the game board grid.
    - pos (tuple): Position (x, y) of the node on the game board grid.
    """
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
        """
        Set the color of the cell to indicate ownership.

        Parameters:
        - c (str): Color to assign to the cell.
        """
        self.color = c

class LinkedGrid:
    """
        Initialize a grid structure for the Blokus game board.

        Parameters:
        - width (int): Width of the game board.
        - height (int): Height of the game board.
        - cellSize (int): Size of each cell in the grid in terms of pixels.

        Attributes:
        - matrix (list): 2D list to represent the grid structure.
        - w (int): Width of the game board.
        - h (int): Height of the game board.
        - csize (int): Size of each cell in pixels.
    """
        
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
    """
    Represents a game piece in Blokus.

    Parameters:
    - matrix (list): 2D array representing the piece's shape.
    - player (Player): The player who owns this piece.

    Attributes:
    - player (Player): The player who owns this piece.
    - c (str): Color of the player who owns the piece.
    - m (numpy.ndarray): Numpy array representing the piece's shape.

    Methods:
    - fixPos(self): Adjusts the piece's position based on player's position and ensures it fits on the board.
    - rotflip(self, rottype): Rotates or flips the piece according to the specified type.
    - place(self): Attempts to place the piece on the board and checks for valid placement.
    - placeFirst(self): Checks if the piece can be placed in a corner on the board.
    - placeRest(self): Checks if the piece can be placed diagonally adjacent to another piece.

    """

    def __init__(self, matrix, player):
        self.player = player
        self.c = player.c
        self.m = np.array(matrix)

    def fixPos(self):
        """
        Adjusts the piece's position based on the player's position and ensures it fits on the board.
        """
        # Add player position to piece array dimensions
        botright = self.player.pos + self.m.shape[::-1]
        # Check if this goes off the board...
        while botright[0] > 20: # Hardcoding size for now, fix for variable board size
            self.player.pos -= (1, 0)
            botright -= (1, 0)
        while botright[1] > 20: # Hardcoding size for now, fix for variable board size
            self.player.pos -= (0, 1)
            botright -= (0, 1)
        while self.player.pos[0] < 0:
            self.player.pos += (1, 0)
        while self.player.pos[1] < 0:
            self.player.pos += (0, 1)

    def rotflip(self, rottype):
        """
        Rotates or flips the piece according to the specified type.

        Parameters:
        - rottype (str): Type of rotation or flip ("rotCW", "rotCCW", or "flip").
        """
        if rottype == "rotCW": # Rotate clockwise or three times counterclockwise
            self.m = np.rot90(self.m, 3)
        elif rottype == "rotCCW":
            self.m = np.rot90(self.m)
        elif rottype == "flip": # Reverse the order of elements along axis 1 (left/right)
            self.m = np.fliplr(self.m)
        self.fixPos()

    def place(self):
        """
        Attempts to place the piece on the board and checks for valid placement.

        Returns:
        - bool: True if the piece was successfully placed, False otherwise.
        """
        bpos = board.matrix[self.player.pos[0]][self.player.pos[1]]
        for r in range(len(self.m)):
            for c in range(len(self.m[r])):
                if self.m[r][c] == 1:
                    cell = board.matrix[r + bpos.x][c + bpos.y]
                    if cell.color:
                        break
                    # If the piece overlaps another piece, we shouldn't place it!
                    for adjCell in [cell.up, cell.left, cell.down, cell.right]:
                        if adjCell and adjCell.color == self.c:
                            break
                    else:
                        continue
                    break
            else:  # If we didn't break...
                continue
            break  # If we did break, break the outer loop

        else:
            for r in range(len(self.m)):
                for c in range(len(self.m[r])):
                    if self.m[r][c] == 1:
                        board.matrix[r + bpos.x][c + bpos.y].colorize(self.c)
            self.player.delPiece()
            return True  # We placed the piece, so delete it and return True
        return False  # We didn't place the piece =(
    
    def placeFirst(self):
        """
        Checks if the piece can be placed in a corner on the board.

        Returns:
        - bool: True if the piece can be placed in a corner, False otherwise.
        """
       
        if self.m[0][0] == 1 and np.array_equal(self.player.pos, np.array([0, 0])):
            # This piece is in the top-left corner!
            ret = self.place()
        elif self.m[-1][-1] == 1 and np.array_equal(self.player.pos + self.m.shape, np.array(board.matrix).shape):
            # This piece is in the bottom-right corner!
            ret = self.place()
        elif len(players.players) > 2:
            # If there are only two players, orthogonally adjacent corners are disallowed
            if self.m[-1][0] == 1 and self.player.pos[1] + len(self.m) == len(board.matrix):
                # This piece is in the bottom-left corner!
                ret = self.place()
            elif self.m[0][-1] == 1 and self.player.pos[0] + len(self.m[0]) == len(board.matrix[0]):
                # This piece is in the top-right corner!
                ret = self.place()
            else:
                return False
        else:
            return False
        if ret:
            self.player.hasntPlayed = False
            return ret

    def placeRest(self):
        """
        Checks if the piece can be placed diagonally adjacent to another piece.

        Returns:
        - bool: True if the piece can be placed diagonally adjacent, False otherwise.
        """
        bpos = board.matrix[self.player.pos[0]][self.player.pos[1]]
        for r in range(len(self.m)):
            for c in range(len(self.m[r])):
                if self.m[r][c] == 1:
                    cell = board.matrix[r + bpos.x][c + bpos.y]
                    for ud in [cell.up, cell.down]:
                        if ud:
                            for dAdjCell in [ud.left, ud.right]:
                                if dAdjCell and dAdjCell.color == self.c:
                                    return self.place()
        return False


class Player:
    """
    Represents a player in the Blokus game.

    Parameters:
    - color (str): The color associated with the player.
    - is_bot (bool): Indicates if the player is controlled by a bot (default is False).

    Attributes:
    - c (str): The color of the player.
    - is_bot (bool): True if the player is controlled by a bot, False otherwise.
    - pieces (dict): A dictionary that stores the player's game pieces.
    - score (int): The player's current score.
    - pos (numpy.ndarray): The player's current position on the game board.
    - curPiece (Piece): The player's current selected game piece.
    - curPieceIndex (int): The index of the current game piece in the list.
    - curPieceKey (int): The key representing the current game piece.
    - hasntPlayed (bool): Indicates if the player has made a move yet (True by default).
    - isDone (bool): Indicates if the player has finished their turn (False by default).

    Methods:
    - setPos(self, pos): Set the player's position on the game board.
    - getPiece(self, num): Select a game piece by its number.
    - nextPiece(self, direction): Navigate to the next or previous game piece in the list.
    - move(self, direction, pos): Move the player's piece in a specific direction or to a specified position.
    - delPiece(self): Delete the player's current game piece and get the next one.
    - removePiece(self, pKey, pIn): Remove a specific game piece from the player's collection.
    - performBotAction(self): Perform a bot action for the player (if the player is controlled by a bot).
    """

    def __init__(self, color, is_bot=False):
        self.c = color
        self.is_bot = is_bot
        self.pieces = dict()
        self.score = 0
        self.pos = np.array([0, 0])

        # Load game pieces from a file
        with open("data/pieces.blok", "r") as f:
            for line in f:
                l = eval(line.rstrip())
                if isinstance(l, int):
                    s = l
                    if s not in self.pieces:
                        self.pieces[s] = []
                elif isinstance(l, list):
                    l = Piece(l, self)
                    self.pieces[s].append(l)
                    self.score -= s

        # Initialize the player's current piece and position
        self.curPiece = self.pieces[1][0]
        self.curPieceIndex = 0
        self.curPieceKey = 1
        self.hasntPlayed = True
        self.isDone = False

    def setPos(self, pos):
        """
        Set the player's position on the game board.

        Parameters:
        - pos (numpy.ndarray): The new position to set for the player.
        """
        self.pos = pos

    def getPiece(self, num):
        """
        Select a game piece by its number.

        Parameters:
        - num (int): The number of the game piece to select.
        """
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
        """
        Navigate to the next or previous game piece in the list.

        Parameters:
        - direction (str): The direction to navigate ("f" for next, "b" for previous).
        """
        pKey = self.curPieceKey
        if direction == "f":
            self.curPieceIndex += 1
            if self.curPieceIndex >= len(self.pieces[pKey]):
                self.curPieceIndex = 0
        if direction == "b":
            self.curPieceIndex -= 1
            if self.curPieceIndex < 0:
                self.curPieceIndex = len(self.pieces[pKey]) - 1
        self.curPiece = self.pieces[pKey][self.curPieceIndex]
        self.curPiece.fixPos()

    def move(self, direction, pos):
        """
        Move the player's piece in a specific direction or to a specified position.

        Parameters:
        - direction (str): The direction to move the piece (e.g., "up", "down", "left", "right").
        - pos (numpy.ndarray): The new position to move the piece to.
        """
        if direction:
            if direction == "up":
                self.pos -= (0, 1)
            elif direction == "down":
                self.pos += (0, 1)
            elif direction == "left":
                self.pos -= (1, 0)
            elif direction == "right":
                self.pos += (1, 0)
            self.curPiece.fixPos()
        elif pos:
            prev = self.pos
            self.pos = np.floor(np.array(pos)).astype(int)
            self.curPiece.fixPos()
            if (self.pos == prev).all():
                players.evManager.Post(e.PlacePiece())
                
    def delPiece(self):
        """
        Delete the player's current game piece and select the next one.
        """
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
        """
        Remove a specific game piece from the player's collection.

        Parameters:
        - pKey (int): The key of the game piece to remove.
        - pIn (int): The index of the game piece to remove in the list.
        """
        self.score += pKey
        del self.pieces[pKey][pIn]
        if self.pieces[pKey]:
            self.nextPiece("b")
        else:
            del self.pieces[pKey]
            self.getPiece(1)

    def performBotAction(self):
        """
        Perform a bot action for the player (if the player is controlled by a bot).
        """
        bot.selectBotMove(board, self)

class Players:
    def __init__(self, num_human_players, num_bot_players, evManager):
        """
        Initialize the Players object with human and bot players.

        Parameters:
        - num_human_players (int): Number of human players in the game.
        - num_bot_players (int): Number of bot players in the game.
        - evManager: Event manager for game events.

        Attributes:
        - evManager: Event manager for handling game events.
        - players (list): List of Player objects representing all players in the game.
        - activePlayers (list): List of active players (human and bot) in the current game.
        - curI (int): Index of the current active player.
        - cur: The current active player.
        - pieces (list): List to store game pieces for human players.
        - res (int): Counter for player resignations.
        """
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
        """
        Switch to the next player's turn.

        If the current player is a bot, perform the bot's move.
        """
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
        """
        Handle player resignation.

        If at least two players have resigned, continue the game by switching to the next turn.
        """
        self.res += 1
        if self.res >= 2:
            del self.activePlayers[self.curI]
            self.curI -= 1
            self.evManager.Post(e.NextTurn())

    def Notify(self, event):
        """
        Handle game events and perform actions accordingly.

        Parameters:
        - event: The game event to handle.
        """
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


def createBoard(w=20, h=20, c=20):
    """
    Create the game board with the specified dimensions and cell size.

    Parameters:
    - w (int): Width of the game board.
    - h (int): Height of the game board.
    - c (int): Size of each cell in the grid.

    This function initializes the global 'board' object as a LinkedGrid with the specified dimensions and cell size.
    """
    global board
    board = LinkedGrid(w, h, c)

def createPlayers(num_human_players, num_bot_players, evManager):
    """
    Create the players for the game.

    Parameters:
    - num_human_players (int): Number of human players in the game.
    - num_bot_players (int): Number of bot players in the game.
    - evManager: Event manager for game events.

    This function initializes the global 'players' object as a Players instance with the specified number of human and bot players and links it to the provided event manager.
    """
    global players
    players = Players(num_human_players, num_bot_players, evManager)

