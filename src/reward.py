import numpy as np
import random
import copy
import json
import src.bot as bot

def choose_move_strategy(matrix, possible_places, possible_pieces, color, players, weights = [10,10,1], strategy = None):
    
    if strategy == 'greedy':
         choice = len(possible_places)-1 # will return a move for the biggest piece
    elif strategy == 'oc':
         choice = choose_move_oc(matrix, possible_places, color)
    elif strategy == 'bcocap':
         choice = choose_move_bcocap(matrix, possible_places, color, weights = [10,10,1,5])
    elif strategy == 'bcocap_depth1':
         choice = choose_move_bcocap_depth1(matrix, possible_places,possible_pieces,color, players)
    elif strategy == 'minimize__opponent_moves': #sucks
         choice = choose_move_minimize_opponent_moves(matrix, possible_places, possible_pieces, color, players)
    elif strategy == 'minmax':
         choice = choose_move_min_max(matrix, possible_places, players, color, depth = 4)
    else:
         choice = bot.random_choice(possible_places)

    return choice

def choose_move_oc(matrix, possible_places, color):
    best = 0
    choice = 0
    corners = {}
    for c in range(1,5):
        corners[c]= set(bot.get_playable_conditions(matrix,color, only_corners= True))  
    for i in range(len(possible_places)):
        reward = bot.get_number_of_corners(matrix, possible_places[i], color, corners) # negative value for own color. you want to add some.
        if reward > best:
            choice = i
            best = reward
    return choice

def choose_move_bcocap(matrix, possible_places, color, weights = [10,10,1,5]):
    '''takes in 4 weights'''
    best = [0,()]
    choice = 0
    old_square = []
    corners = get_corners_for_all_players(matrix) 
    for i in range(len(possible_places)):
        reward = []
        reward.append(bot.get_number_of_blocked_corners(corners, possible_places[i], color))
        reward.append(bot.get_number_of_corners(matrix, possible_places[i], color, corners)) # negative value for own color. you want to add some.
        area, new_square = bot.get_area_change(old_square, possible_places[i])
        reward.append(area)
        reward.append(len([coord for coord in possible_places[i] if coord is not None]))
        current_sum = sum([x * y for x, y in zip(weights, reward)])
        if current_sum > best[0]:
            choice = i
            best = (current_sum, new_square)
    return choice

def choose_move_bcocap_depth1(matrix, possible_places, possible_pieces, color, players, weights = [10,10,5,15,5]):
    '''takes in 4 weights'''
    if len(players[color-1].available_pieces) > 16:
        weights = [10,5,5,10]
    elif len(players[color-1].available_pieces) > 11:
        weights = [10,10,5,5]
    else:
        weights = [10,10,10,2,10]
    best = [0,()]
    choice = 0
    old_square = []
    corners = get_corners_for_all_players(matrix) 
    for i in range(len(possible_places)):
        reward = []
        reward.append(bot.get_number_of_blocked_corners(corners, possible_places[i], color))
        reward.append(bot.get_number_of_corners(matrix, possible_places[i], color, corners)) # negative value for own color. you want to add some.
        area, new_square = bot.get_area_change(old_square, possible_places[i])
        reward.append(area)
        reward.append(len([coord for coord in possible_places[i] if coord is not None]))
        if len(players[color-1].available_pieces) <= 10:
            new_matrix = make_move(matrix, possible_places[i],color)
            depth1possible_places = bot.get_available_actions(new_matrix, players[color-1], auto_update=False, available_pieces= [p for p in players[color-1].available_pieces if p != possible_pieces[i]])[0]
            reward.append(len(depth1possible_places))
        current_sum = sum([x * y for x, y in zip(weights, reward)])
        if current_sum > best[0]:
            choice = i
            best = (current_sum, new_square)
    return choice


def choose_move_minimize_opponent_moves(matrix, possible_places, possible_pieces, color, players):
    '''
    
    need to fix human player all playable moves otherwise you get a crash
    
    '''
    choice = 0
    corners = get_corners_for_all_players(matrix) 
    old_square = []
    best = 0
    weights = [5,10,5] #area, points, opponent moves
    for i in range(len(possible_places)):
        if len(players[color-1].available_pieces) > 16: #ignore small pieces at start of game
            if len([coord for coord in possible_places[i] if coord is not None]) <5:
                pass
            else:
                reward = []
                area, new_square = bot.get_area_change(old_square, possible_places[i])
                reward.append(area)
                reward.append(len([coord for coord in possible_places[i] if coord is not None]))#points
                new_matrix = make_move(matrix, possible_places[i],color)
                for p in range(len(players)):
                    opponent_moves = 0
                    if p != color:
                        a,b,c = bot.get_available_actions(matrix, players[p], auto_update = False)
                        opponent_moves+= len(a)
                reward.append(opponent_moves)
                current_sum = sum([x * y for x, y in zip(weights, reward)])
                if current_sum > best:
                    choice = i
                    best = current_sum




    return choice


def choose_move_min_max(matrix, possible_places, players, player, depth = 4, alpha = float('-inf'), beta = float('inf')):
    player = player
    maximizing_player = player
    eval, choice, piece = minimax_alpha_beta(matrix, possible_places, depth, alpha, beta, players, player, maximizing_player)

    return choice

def choose_candidate_moves(matrix, possible_places, color, weights = [10,10,1], num_of_candidates = 5, max_places = 100):
    '''takes in 4 weights'''
    best = []
    choice = []
    corners = get_corners_for_all_players(matrix)
    possible_places = possible_places[len(possible_places)-max_places:len(possible_places)]
    for i in range(len(possible_places)):
        reward = []
        reward.append(bot.get_number_of_blocked_corners(corners, possible_places[i], color))
        reward.append(bot.get_number_of_corners(matrix, possible_places[i], color, corners)) # negative value for own color. you want to add some.
        reward.append(len([coord for coord in possible_places[i] if coord is not None]))
        current_sum = sum([x * y for x, y in zip(weights, reward)])
        if len(best) < num_of_candidates:
            best.append(current_sum)
            choice.append(i)
        elif current_sum > min(best):
            index_to_replace = best.index(min(best))
            best[index_to_replace] = current_sum
            choice[index_to_replace] = i
    return choice

    
def check_corner_on_pos(matrix,i,j):
    if i > 0 and j > 0 and i <19 and j <19:
        s = matrix[i-1:i+2,j-1:j+2]
        d = {s[0][0],s[0][2],s[2][0],s[2][2]}
        l = {s[1,0],s[1,2],s[0,1],s[2,1]}
        corner_to = d.difference(l).difference({0})
    elif i == 0 and j >0 and j<19:
        s = matrix[i:i+2,j-1:j+2]
        d = {s[1][0],s[1][2]}
        l = {s[0,0],s[0,2],s[1,1]}
        corner_to = d.difference(l).difference({0})
    elif i == 19 and j > 0 and j < 19:
        s = matrix[i-1:i+1,j-1:j+2]
        d = {s[0][0],s[0][2]}
        l = {s[1,0],s[1,2],s[0,1]}
        corner_to = d.difference(l).difference({0})
    elif  j == 0 and i >0 and i<19:
        s = matrix[i-1:i+2,j:j+2]
        d = {s[0][1],s[2][1]}
        l = {s[0,0],s[1,1],s[2,0]}
        corner_to = d.difference(l).difference({0})
    elif  j == 19 and i >0 and i<19:
        s = matrix[i-1:i+2,j-1:j+1]
        d = {s[0][0],s[2][0]}
        l = {s[0,1],s[1,0],s[2,1]}
        corner_to = d.difference(l).difference({0})
    else:
        corner_to = set()
    return corner_to

def get_corners_for_all_players(matrix):
    corners = {1:[],2:[],3:[],4:[]}
    for i,j in np.argwhere(matrix == 0):
        c = check_corner_on_pos(matrix,i,j)
        if len(c) > 0:
            for p in c:
                corners[p].append((i,j))
    return corners

def get_number_of_blocked_corners_player(corners, absolute_coords, color):
    '''This function calculates the number of corners blocked for a player after a given move is played.

    Parameters:
    corners (dictionary): A dictionary containing corner coordinates for each player color.
    absolute_coords (list of tuples): Absolute coordinates where a piece is being placed on the board.
    color (int): The color code of the player making the move.

    Returns:
    int: The number of opponent corners blocked for that move.'''

    blocked_corners = 0
    for coord in absolute_coords:
            if  coord is not None and tuple(coord) in corners[color]:
                blocked_corners+=1
    return blocked_corners

def evaluate_board(matrix, p_color):
    weight_corner = 3
    score = 0
    corners = get_corners_for_all_players(matrix)
    unique_colors, counts = np.unique(matrix,return_counts=True)
    for color, count in zip(unique_colors, counts):
        if color > 0:
            if color == p_color:
                score+= count + len(corners[color])*weight_corner
            else:
                score-= count - len(corners[color])*weight_corner


    return score

def is_game_over(players):
    return False not in [player.isDone for player in players] #means all players have isDone True

def next_player(current_player):
    # Function to determine the next player in the sequence. current_player is an int between 1 and 4
    return (current_player + 1) % 4 +1 # will go from 1 to 4

def minimax_alpha_beta(state, possible_places, depth, alpha, beta, players, current_player, maximizing_player):
    active_player_max_move = 30
    passive_player_max_move = 10
    if depth == 0 or is_game_over(players):
        return evaluate_board(state, maximizing_player), None, None
    
    if current_player == maximizing_player:
        max_eval = float('-inf')
        best_move = None
        piece_to_remove = None
                
        for move in range(max(0,len(possible_places)-active_player_max_move), len(possible_places)):
            new_state = make_move(state, possible_places[move], current_player)  # Apply the move to get the new state
            op_possible_places, op_possible_plays_indices, op_possible_pieces = bot.get_available_actions(state, players[next_player(current_player)-1], auto_update=False)
            eval, _, _ = minimax_alpha_beta(new_state, op_possible_places, depth - 1, alpha, beta, players, next_player(current_player), maximizing_player)
            if eval > max_eval:
                max_eval = eval
                best_move = move
                piece_to_remove = 3#possible_pieces[move]
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Beta pruning
        return max_eval, best_move, piece_to_remove
    else:
        min_eval = float('inf')
        best_move = None
        for move in range(max(0,len(possible_places)-passive_player_max_move), len(possible_places)):
            new_state = make_move(state, possible_places[move], current_player)  # Apply the move to get the new state
            op_possible_places, op_possible_plays_indices, op_possible_pieces = bot.get_available_actions(state, players[next_player(current_player)-1], auto_update=False)
            eval, _, _ = minimax_alpha_beta(new_state, op_possible_places, depth - 1, alpha, beta, players, next_player(current_player), maximizing_player)
            if eval < min_eval:
                min_eval = eval
                best_move = move
                piece_to_remove = 3#possible_pieces[move]
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Alpha pruning
        return min_eval, best_move, piece_to_remove

def get_last_n(lst, n):
    return lst[len(lst)-n:len(lst)]

def make_move(matrix, absolute_coords, color):
    new_matrix = np.array(matrix, copy = True)
    for abs_coord in absolute_coords:
        if abs_coord is not None:
                new_matrix[abs_coord[0]][abs_coord[1]] = color
    return new_matrix


def select_corners(matrix, corners):
    pass

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