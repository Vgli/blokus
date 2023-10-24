import bot
import objects as o
from src.objects import Player, Piece
from pygame import display, Surface, font, image, surfarray, Rect
import pygame
import src.events as e
import views as v
from os.path import join
import controllers as c
import sys
import time
import reward as r

# Initialize game
board = o.LinkedGrid(20,20, 20)
players = []
colors = ["r", "g", "b", "y"]
weights = [[10,10,1],[10,10,1],[10,10,1],[3,2,1]]
all_playable_moves = bot.get_all_playable_moves('data/all_playable_moves.json')
for p in range(4):
    players.append(Player(colors[p], preload = False, all_playable_moves = {**all_playable_moves}))

#Initialize player strategies for comparison
for p in range(4):
    players[p].weights = weights[p]

#Initialize openings
piece_opening = []
for key in players[0].pieces.keys():
    for i,piece in enumerate(players[0].pieces[key]):
        piece_opening.append(piece.m)
piece_opening.pop() #remove last element as it is the cross and it is not a valid start piece.

players_scores = [0,0,0,0]
for opening in piece_opening: #will do a loop of all pieces to start with to benchmark the bot for different openings
    # Initialize game
    board = o.LinkedGrid(20,20, 20)
    players = []
    colors = ["r", "g", "b", "y"]
    weights = [[10,10,1],[10,10,1],[10,10,1],[3,2,1]]
    strategies = ['random','greedy','oc','bcoca']
    for p in range(4):
        players.append(Player(colors[p],preload = False, all_playable_moves = {**all_playable_moves}))

#Initialize player strategies for comparison
    for p in range(4):
        players[p].weights = weights[p]
        players[p].strategy = strategies[p]

    run = True
    turn = 0
    start_time = time.time()
    while run:
        print(turn)
        turn +=1

        for player in players:
            if False not in [player.isDone for player in players]: # when all players are done, game stops.
                run = False
                break

            if not player.isDone:
                matrix = bot.convert_matrix_to_nparray(board.matrix)
                possible_places, possible_plays_indices, possible_pieces = bot.get_available_actions(matrix, player)
                
                
                if turn == 1: # choose the opening
                    choice = possible_pieces.index(opening.tolist())
                    pkey, pindex = possible_plays_indices[choice]
                    absolute_coords = possible_places[choice]
                    piece_played = possible_pieces[choice]
                    bot.play_coordinates(pkey, pindex, absolute_coords, piece_played, player, board)
                elif len(possible_plays_indices) == 0:
                    player.isDone = True
                else:
                    '''Change choice function here. return should be an index to choose from
                    in the possible_places, possible_plays_index, possible_pieces'''
                
                    choice = r.choose_move_strategy(matrix,possible_places, bot.convert_color_to_number(player.c),strategy = player.strategy)

                    ''' End of change'''
                    pkey, pindex = possible_plays_indices[choice]
                    absolute_coords = possible_places[choice]
                    piece_played = possible_pieces[choice]

                    bot.play_coordinates(pkey, pindex, absolute_coords, piece_played, player, board)
                    if len(player.pieces) == 0:
                        player.isDone = True

    end_time = time.time()
    execution_time = end_time - start_time
    print("Execution time: {:.6f} seconds".format(execution_time))

    for p in players:
        print(p.c, p.score)

    for i in range(len(players)):
        players_scores[i]+= players[i].score

for i in range(len(players)):
    print(players[i].c, players_scores[i])

import pygame
import sys

# Define constants
SCREEN_SIZE = (400, 400)  # Adjusted to match the matrix size
CELL_SIZE = 20
WHITE = (255, 255, 255)

# Sample colored matrix (0 for empty cell, 1 for red, 2 for green, 3 for blue)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Colored Matrix Renderer")

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Clear the screen
    screen.fill(WHITE)

    # Render colored matrix with cell objects
    for row in range(len(board.matrix)):
        for col in range(len(board.matrix[0])):
            color = board.matrix[row][col].color
            pygame.draw.rect(screen, (255, 0, 0) if color == 'r' else (0, 255, 0) if color == 'g' else (0, 0, 255) if color == 'b' else (255,255,0) if color == 'y' else (255,255,255),
                             (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Update the display
    pygame.display.flip()

    # Limit frames per second
    pygame.time.Clock().tick(60)

    


