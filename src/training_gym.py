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

board = o.LinkedGrid(20,20, 20)
players = []
colors = ["r", "g", "b", "y"]
for p in range(4):
    players.append(Player(colors[p]))


run = True
weights = [1,1,10]
turn = 0
while run:
    print(turn)
    turn +=1

    for player in players:
        if False not in [player.isDone for player in players]: # when all players are done, game stops.
            run = False
            break

        if not player.isDone:
            matrix = bot.convert_matrix_to_nparray(board.matrix)
            possible_pieces, possible_places, possible_plays_indices = bot.get_available_actions(matrix, player)
            if len(possible_plays_indices) == 0:
                player.isDone = True
            else:
                # Random play right now.
                best = 0
                choice = 0
                best_reward = None

                for i in range(len(possible_places)):
                    reward = bot.estimate_rewards(matrix, possible_places[i], bot.convert_color_to_number(player.c))
                    current_sum = sum([x * y for x, y in zip(weights, reward)])
                    if current_sum > best:
                        choice = i
                        best = current_sum
                        best_reward = reward

                # rand_index = bot.random_index(possible_plays_indices)
                pkey, pindex = possible_plays_indices[choice]
                absolute_coords = possible_places[choice]

                bot.play_coordinates(pkey, pindex, absolute_coords, player, board)
                if len(player.pieces) == 0:
                    player.isDone = True

        

for p in players:
    print(p.c, p.score)

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

    


