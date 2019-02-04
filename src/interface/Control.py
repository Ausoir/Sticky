import sys

import pygame

from src.game import Global
from src.game.Turn import Turn
from src.tools.Data import Data


class Control:
    def __init__(self, menu, player):
        Turn.add(self)
        self.menu = menu
        self.player = player
        self.keymap = {}
        self.mouse = [0, 0]
        self.delay = 0
        self.command = 'idle'
        self.idle = 0
        control = Data.process_raw(Data.read("Data/Keymap.txt"))
        for k, v in control:
            self.keymap[k] = v

    def input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            button = event.button + 500
            if button in self.keymap:
                self.perform(self.keymap[button])
        elif event.type == pygame.MOUSEBUTTONUP:
            self.idle = 1
        elif event.type == pygame.KEYDOWN:
            if event.key in self.keymap:
                self.perform(self.keymap[event.key])
        elif event.type == pygame.KEYUP:
            self.idle = 1
        return 0

    def turn(self):
        self.mouse = pygame.mouse.get_pos()
        self.mouse = Global.get_relative_tile_pos(self.mouse[0], self.mouse[1])
        self.player.input(self.command, self.mouse)
        if self.idle:
            self.command = 'idle'
            self.idle = 0

    def perform(self, arg):
        if arg == 'quit':
            pygame.quit()
            sys.exit()
        elif arg == 'menu':
            self.menu.toggle()
        else:
            self.command = arg
