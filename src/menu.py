import src.objects as o
import src.events as e
from typing import Tuple, Any
import src.controllers as c
import src.views as v
import src.bot as bot
import marshal


class config:
    def __init__(self):
        self.num_players = 1
        self.difficulty = 'random'
        self.all_playable_moves_starter = bot.get_all_playable_moves('data/all_playable_moves.json')



    def set_difficulty(self, value: Tuple[Any, Any], difficulty: int):
        print(difficulty)
        if difficulty == 1:
            self.difficulty = 'random'
        elif difficulty == 2:
            self.difficulty = 'greedy'
        elif difficulty == 3:
            self.difficulty = 'oc'
        elif difficulty == 4:
            self.difficulty = 'bcocap'
        elif difficulty == 5:
            self.difficulty = 'bcocap_depth1'
    # Do the job here !

    def set_num_players(self, value:Tuple[Any, Any], num_players: int):
        self.num_players = num_players

# Add menu items and functions

    def start_the_game(self, menu):
        menu.full_reset()
        menu.disable()
        evManager = e.EventManager()
        o.createBoard()

        #init players
        p_list = []
        colors = ["r", "g", "b", "y"]
        for p in range(self.num_players):
            p_list.append(o.Player(colors[p], preload=False, all_playable_moves= [], strategy= self.difficulty))
        for p in range(self.num_players, 4):
            p_list.append(o.Player(colors[p], preload=False, all_playable_moves= marshal.loads(marshal.dumps(self.all_playable_moves_starter,-1)), strategy= self.difficulty, is_bot=True))

        o.createPlayers(0,0,evManager,pre_init=False, p_list=p_list)
        pygameView = v.PygameView(evManager, fullscreen=True, menu = False)
        pygameView.updateView(fullscreen=pygameView.fullscreen)  
        keyb = c.KeyboardController(evManager)
        mouse = c.MouseController(evManager)
        tick = c.TickController(evManager)
        tick.run()

   