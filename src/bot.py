import numpy as np
import random
import copy
import json
try:
    import src.reward as r
except:
    pass

################################################## UTILS ###
def convert_color_to_number(color):
    colors = {"r":1, "g":2, "b":3, "y":4}
    return colors[color]


def convert_matrix_to_nparray(matrix):
    colors = {"r":1, "g":2, "b":3, "y":4} 
    rows, cols = np.shape(matrix)
    array = np.zeros((rows,cols), dtype=int)
    for i in range(rows):
        for j in range(cols):
            c = matrix[i][j].color
            if c != None:
                array[i][j] = colors[c]

    return array


def random_index(my_list):
    return random.randint(0, len(my_list) - 1)

def generate_all_playable_moves(matrix,player,path = 'data/all_playable_moves.json'):
    playable_board, playable_pos = get_playable_conditions((matrix),convert_color_to_number(player.c))
    playable_pos = [(i,j) for i in range(20) for j in range(20)]

    all_pos_play = {}
    for pkey in player.pieces.keys():
        for pindex in range(len(player.pieces[pkey])):
            piece = player.pieces[pkey][pindex].m
            piece_permutations = [piece, np.rot90(piece,1), np.rot90(piece,2), np.rot90(piece,3), np.fliplr(piece), np.rot90(np.fliplr(piece),1), np.rot90(np.fliplr(piece),2), np.rot90(np.fliplr(piece),3)]  
            for p in piece_permutations:
                for position in playable_pos:
                    for i in range(len(p)):
                        for j in range(len(p[0])):
                            relative_coords = get_piece_relative_coordinates(p, i,j)
                            absolute_coords = get_absolute_coordinates(position, relative_coords)
                            if position in absolute_coords:
                                if position not in all_pos_play.keys():
                                    all_pos_play[position] = []
                                    
                                if check_absolute_coordinates(playable_board, absolute_coords):
                                    if [(pkey,pindex),absolute_coords] not in all_pos_play[position]:
                                        all_pos_play[position].append([(pkey,pindex),absolute_coords,piece])
    string_keys_dict = {str(key): value for key, value in all_pos_play.items()}
    # Open the file in write mode and use json.dump() to save the list as a JSON file
    with open(path, 'w') as json_file:
        json.dump(string_keys_dict, json_file)

def get_all_playable_moves(file_path = 'data/all_playable_moves.json'):
    with open(file_path, 'r') as json_file:
        string_keys_dict = json.load(json_file)
    # Convert string keys back to tuples
    loaded_dict = {tuple(eval(key)): value for key, value in string_keys_dict.items()}
    return loaded_dict

################################################### PIECE Handling ###

def get_piece_coordinates(piece, position):
    coordinates = []
    for r in range(len(piece)):
        for c in range(len(piece[0])):
            if piece[r][c] == 1:
                relative_coord = (r - position[0], c - position[1])
                coordinates.append(relative_coord)
    return coordinates

def get_piece_relative_coordinates(piece, r, c):
    relative_coordinates = [[None] * len(piece[0]) for _ in range(len(piece))]
    for i in range(len(piece)):
        for j in range(len(piece[0])):
            relative_coordinates[i][j] = (i - r, j - c) if piece[i][j] == 1 else None
    return relative_coordinates

def get_absolute_coordinates(position, relative_coords):
    r, c = position
    absolute_coords = []
    for row in relative_coords:
        for rel_coord in row:
            if rel_coord is not None:
                abs_coord = (r + rel_coord[0], c + rel_coord[1])
                absolute_coords.append(abs_coord)
            else:
                absolute_coords.append(None)
    return absolute_coords

def check_absolute_coordinates(matrix, absolute_coords):
    rows, cols = np.shape(matrix)
    playable = True
    for abs_coord in absolute_coords:
            if abs_coord is not None:
                if 0 <= abs_coord[0] < rows and 0 <= abs_coord[1] < cols:
                    if matrix[abs_coord[0]][abs_coord[1]] > 0:
                        playable = False
                        break  # Found a non-empty cell at the specified position
                else:
                    playable = False
                    break   # Coordinates are out of the board range
    return playable  # All specified positions are empty


################################################# GENERATE Play

def get_playable_conditions(matrix, color, only_corners = False ):
    #will compute playable matrix if only corner is false otherwise will only return the corners. saves half the compute time
    rows, cols = len(matrix), len(matrix[0])
    playable_pos = []

    if not only_corners:
        playable_matrix = np.zeros((rows,cols))

    # Check diagonally adjacent positions
    diagonals = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    up_and_downs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    for i in range(rows):
        for j in range(cols):
            if matrix[i][j] == color:

                ## playable matrix
                # Set the current position to 1 # Check left, right, top, and bottom positions
                if not only_corners:
                    playable_matrix[i][j] = 1
                    for a, b in up_and_downs:
                        new_i, new_j = i + a, j + b
                        if 0 <= new_i < rows and 0 <= new_j < cols:
                            playable_matrix[new_i][new_j] = 1
                        
                ## playable pos
                for x, y in diagonals:
                    new_i, new_j = i + x, j + y
                    if 0 <= new_i < rows and 0 <= new_j < cols:
                        if matrix[new_i][new_j] == 0:
                            append = True
                            for a, b in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                            # Check for valid corners
                                if 0 <= new_i+a < rows and 0 <= new_j+b < cols:
                                    if matrix[new_i+a][new_j+b] == color:
                                        append = False
                                        break

                            if append:
                                playable_pos.append((new_i, new_j))
            if not only_corners:
                if matrix[i][j] != 0:
                    playable_matrix[i][j] = 1
    # Check board corners if no valid corners found
    if not playable_pos:
        corners = [(0, 0), (0, cols - 1), (rows - 1, 0), (rows - 1, cols - 1)]
        for i, j in corners:
            if matrix[i][j] == 0:
                playable_pos.append((i, j))
                break
    
    if not only_corners:
        return playable_matrix, playable_pos
    else:
        return playable_pos
    
    

def get_available_actions(matrix, player):
    # Return a list of valid moves as a form of coordinates to play and piece indices
    possible_plays_indices = []
    possible_places = []
    possible_pieces = []
    playable_board, playable_pos = get_playable_conditions(matrix,convert_color_to_number(player.c))
    for position in playable_pos:
        to_pop = []
        for i, move in enumerate(player.all_playable_moves[position]):
            absolute_coords = move[1]
            if check_absolute_coordinates(playable_board, absolute_coords):
                possible_places.append(absolute_coords)
                possible_plays_indices.append(move[0])
                possible_pieces.append(move[2])
            else:
                to_pop.append(i)
        for i in reversed(to_pop):
            player.all_playable_moves[position].pop(i)
                                    
    return possible_places, possible_plays_indices, possible_pieces


####################################################### REWARDS

def get_number_of_corners(matrix, absolute_coords, color, corners):
    '''This function calculates the change in the number of corners occupied after a move is played by a player of a specific color.

    Parameters:
    matrix (2D list): The game board matrix.
    absolute_coords (list of tuples): Absolute coordinates where a piece is being placed on the board.
    color (int): The color code of the player making the move.
    corners (dictionary): A dictionary containing corner coordinates for each player color.

    Returns:
    int: The difference in the number of corners occupied after the move.'''

    rows, cols = len(matrix), len(matrix[0])
    added_corners = 0
    removed_corners = 0
    diagonals = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    laterals = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    
    for coord in absolute_coords:
        if coord is not None:
            i,j = coord
            for x, y in diagonals:
                    new_i, new_j = i + x, j + y
                    if 0 <= new_i < rows and 0 <= new_j < cols:
                        if matrix[new_i][new_j] == 0:
                            append = True
                            for a, b in laterals:    
                            # Check for valid corners
                                if 0 <= new_i+a < rows and 0 <= new_j+b < cols:
                                    if (matrix[new_i+a][new_j+b] == color) or ([new_i+a,new_j+b] in absolute_coords):
                                        append = False
                                        break
                            #Check if corner already exists
                            if (new_i,new_j) in corners[color]:
                                 append = False

                            if append:
                                added_corners += 1

    for coord in corners[color]:
        i,j = coord
        remove = False
        #Check if a corner has been occupied
        if [i,j] in absolute_coords:
            remove = True
        
            
        for a, b in laterals:
        # Check if squares surrounding corner have been occupied
                if [i+a,j+b] in absolute_coords:
                    remove = True
                    break
        if remove:
            removed_corners += 1


    return added_corners - removed_corners
    

def get_number_of_blocked_corners(corners, absolute_coords, color):
    '''This function calculates the number of corners blocked for a player after a given move is played.

    Parameters:
    corners (dictionary): A dictionary containing corner coordinates for each player color.
    absolute_coords (list of tuples): Absolute coordinates where a piece is being placed on the board.
    color (int): The color code of the player making the move.

    Returns:
    int: The number of opponent corners blocked for that move.'''

    blocked_corners = 0
    for c in range(1,5):
        if c!= color:
                for coord in absolute_coords:
                        if  coord is not None and tuple(coord) in corners[c]:
                            blocked_corners+=1
                            break
    return blocked_corners

def matrix_with_placed_piece(matrix, absolute_coords, color):

    new_matrix = copy.deepcopy(matrix)
    
    for abs_coord in absolute_coords:
        if abs_coord is not None:
                new_matrix[abs_coord[0]][abs_coord[1]] = color
    return new_matrix

def get_area_change(old_square, absolute_coords):
    '''This function calculates the change in area on the game board occupied by a player's pieces after a move is played.

    Parameters:
    old_square (tuple): A tuple representing the previous area occupied by the player on the game board.
    absolute_coords (list of tuples): Absolute coordinates where a piece is being placed on the board.

    Returns:
    int: The difference in area occupied by the player's pieces after the move.
    tuple: Updated square area occupied by the player on the game board.'''

    xs = [sublist[0] for sublist in absolute_coords if sublist is not None]
    ys = [sublist[1] for sublist in absolute_coords if sublist is not None]

    if len(old_square) == 0:
        old_area = 0
        x = (min(xs),max(xs))
        y = (min(ys),max(ys))
        new_area = np.abs((x[0]-x[1])*(y[0]-y[1]))

    else:
        x,y = old_square
        old_area = np.abs((x[0]-x[1])*(y[0]-y[1]))
        #update the square
        if min(xs)<x[0]:
            x[0] = min(xs)
        if max(xs)>x[1]:
            x[1] = max(xs)
        if min(ys)<y[0]:
            y[0] = min(ys)
        if max(ys)>y[1]:
            y[1] = max(ys)
        
        new_area = np.abs((x[0]-x[1])*(y[0]-y[1]))

    return new_area - old_area, (x,y)

############################################# PLAY

def play_coordinates(pkey,pindex,absolute_coords, piece_played, player, board):
    for abs_coord in absolute_coords:
        if abs_coord is not None:
            board.matrix[abs_coord[0]][abs_coord[1]].colorize(player.c)
    
    player.updateAllMoves((pkey,pindex))

    #find matching piece index of piece_played to remove
        #retrieve piece shape
    for i, piece in enumerate(player.pieces[pkey]):
        if piece.m.tolist() == piece_played:
            break
 
    player.removePiece(pkey,i)

def random_choice(possible_places):
    choice = random_index(possible_places)
    return choice


def selectBotMove(board, player, players = []):
    
    if not player.isDone:
        matrix = convert_matrix_to_nparray(board.matrix)
        possible_places, possible_plays_indices, possible_pieces = get_available_actions(matrix, player)
        if len(possible_plays_indices) == 0:
            player.isDone = True
        else:
            '''Change choice function here. return should be an index to choose from
            in the possible_places, possible_plays_index, possible_pieces'''
            
            choice = random_choice(possible_places)# Random play right now.

            ''' End of change'''

            pkey, pindex = possible_plays_indices[choice]
            absolute_coords = possible_places[choice]
            piece_played = possible_pieces[choice]
            play_coordinates(pkey, pindex, absolute_coords, piece_played, player, board)
            if len(player.pieces) == 0:
                player.isDone = True


                

def selectBotMoveTemplate(board, player): 
    
    weights = [10,10,1]
    
    if not player.isDone:
        matrix = convert_matrix_to_nparray(board.matrix)
        possible_places, possible_plays_indices, possible_pieces = get_available_actions(matrix, player)
        if len(possible_plays_indices) == 0:
            player.isDone = True
        else:
            #here you implement the algo that will choose the right move by picking the index.
            #the input is the matrix, the player and the get available action output.

            choice = 0

            pkey, pindex = possible_plays_indices[choice]
            absolute_coords = possible_places[choice]
            piece_played = possible_pieces[choice]
            play_coordinates(pkey, pindex, absolute_coords, piece_played, player, board)
            if len(player.pieces) == 0:
                player.isDone = True                                                   