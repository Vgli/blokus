import numpy as np
import random

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
    for abs_coord in absolute_coords:
            if abs_coord is not None:
                if 0 <= abs_coord[0] < rows and 0 <= abs_coord[1] < cols:
                    if matrix[abs_coord[0]][abs_coord[1]] > 0:
                        return False  # Found a non-empty cell at the specified position
                else:
                    return False  # Coordinates are out of the board range
    return True  # All specified positions are empty

def get_playable_conditions(matrix, color):
    rows, cols = len(matrix), len(matrix[0])
    playable_pos = []
    playable_matrix = np.zeros((rows,cols))

    # Check diagonally adjacent positions
    diagonals = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    for i in range(rows):
        for j in range(cols):
            if matrix[i][j].color == color:

                ## playable matrix
                # Set the current position to 1 # Check left, right, top, and bottom positions
                playable_matrix[i][j] = 1
                for x, y in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                    new_i, new_j = i + x, j + y
                    if 0 <= new_i < rows and 0 <= new_j < cols:
                        playable_matrix[new_i][new_j] = 1
                        
                ## playable pos
                for x, y in diagonals:
                    new_i, new_j = i + x, j + y
                    if 0 <= new_i < rows and 0 <= new_j < cols:
                        if matrix[new_i][new_j].color is None:
                            # Check for valid corners
                            if (
                                0 <= new_i + x < rows
                                and 0 <= new_j + y < cols
                                and matrix[new_i + x][new_j + y].color != color
                                and matrix[new_i][new_j + y].color != color
                            ):
                                playable_pos.append((new_i, new_j))

            if matrix[i][j].color is not None:
               playable_matrix[i][j] = 1
    # Check board corners if no valid corners found
    if not playable_pos:
        corners = [(0, 0), (0, cols - 1), (rows - 1, 0), (rows - 1, cols - 1)]
        for i, j in corners:
            if matrix[i][j].color is None:
                playable_pos.append((i, j))
                break
    
    return playable_matrix, playable_pos


def get_playable_pos(matrix, color):
    """
    Finds playable positions for the given player color on the game board.

    Parameters:
    - matrix (list of lists): The game board represented as a matrix of Cell objects.
    - color (int): The color identifier of the player for whom playable positions are being determined.

    Returns:
    - list of tuples: A list of (row, column) tuples representing valid positions where the player can place their pieces.
    """

    rows, cols = len(matrix), len(matrix[0])
    playable_pos = []

    # Check diagonally adjacent positions
    diagonals = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    for i in range(rows):
        for j in range(cols):
            if matrix[i][j].color == color:
                for x, y in diagonals:
                    new_i, new_j = i + x, j + y
                    if 0 <= new_i < rows and 0 <= new_j < cols:
                        if matrix[new_i][new_j].color is None:
                            # Check for valid corners
                            if (
                                0 <= new_i + x < rows
                                and 0 <= new_j + y < cols
                                and matrix[new_i + x][new_j + y].color != color
                                and matrix[new_i][new_j + y].color != color
                            ):
                                playable_pos.append((new_i, new_j))
    
    # Check board corners if no valid corners found
    if not playable_pos:
        corners = [(0, 0), (0, cols - 1), (rows - 1, 0), (rows - 1, cols - 1)]
        for i, j in corners:
            if matrix[i][j].color is None:
                playable_pos.append((i, j))
                break
    
    return playable_pos

def get_number_of_blocked_corners(old_matrix, new_matrix, color):
    """Returns the number of blocked corners for a player after a given move is played"""
    return len(get_playable_pos(old_matrix,color))-len(get_playable_pos(new_matrix,color))

def matrix_with_placed_piece(matrix, absolute_coords, color):
    for abs_coord in absolute_coords:
        if abs_coord is not None:
                matrix[abs_coord[0]][abs_coord[1]].color = color
    return matrix

def get_available_actions(board, player):
    # Return a list of valid moves as a form of coordinates to play and piece indices
    possible_pieces = []
    possible_places = []
    possible_plays_indices = []
    playable_board, playable_pos = get_playable_conditions(board.matrix,player.c)
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
                                if check_absolute_coordinates(playable_board, absolute_coords):
                                    possible_pieces.append(p)
                                    possible_places.append(absolute_coords)
                                    possible_plays_indices.append((pkey,pindex))
                                    
    return possible_pieces, possible_places, possible_plays_indices

def potential_board(matrix, absolute_coords, color):
    rows, cols = np.shape(matrix)
    potential_matrix = np.zeros((rows,cols))             

    for i in range(rows):
        for j in range(cols):
            if matrix[i][j].color == color or (i,j) in absolute_coords: 
                for x, y in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                    new_i, new_j = i + x, j + y
                    if 0 <= new_i < rows and 0 <= new_j < cols:
                        if matrix[new_i][new_j].color is None:
                            potential_matrix[new_i][new_j] = 1
                        elif matrix[new_i][new_j].color == color:
                            potential_matrix[new_i][new_j] = 1
                        else:
                            potential_matrix[new_i][new_j] = 9
    return np.sum(potential_matrix == 1)#right now only returns the number of potential covered tiles

def play_coordinates(pkey,pindex,absolute_coords, player, board):
    for abs_coord in absolute_coords:
        if abs_coord is not None:
            board.matrix[abs_coord[0]][abs_coord[1]].colorize(player.c)
    player.removePiece(pkey,pindex)

def check_center_occupancy(board, player, number_of_moves):
    """Goal is to check whether or not the player has reach the center area within a given number of moves."""
    center = [8,9,10,11]
    colors_center = [board.matrix[i][j].color for i in center for j in center] # center square of 4x4
    num_of_pieces = sum(len(player.pieces[key]) for key in player.pieces.keys())
    if player.c in colors_center and num_of_pieces > 21-number_of_moves:
        return True
    else:
        return False

def random_index(my_list):
    return random.randint(0, len(my_list) - 1)

def selectBotMove(board, player):
    possible_pieces, possible_places, possible_plays_indices = get_available_actions(board, player)

    #random play right now.
    rand_index = random_index(possible_plays_indices)
    pkey,pindex = possible_plays_indices[rand_index]
    absolute_coords = possible_places[rand_index]
    play_coordinates(pkey,pindex,absolute_coords,player,board)
                
                                                    