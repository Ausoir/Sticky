import sys

import pygame

from src.tools.Data import Data


class Control:
    def __init__(self, menu, player):
        self.menu = menu
        self.player = player
        self.keymap = {}
        self.mouse = [0, 0]
        control = Data.process_raw(Data.read("Keymap.txt"))
        for k, v in control:
            self.keymap[k] = v

    def input(self, event):
        self.mouse = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            button = event.button + 500
            if button in self.keymap:
                self.perform(self.keymap[button])
        elif event.type == pygame.KEYDOWN:
            if event.key in self.keymap:
                self.perform(self.keymap[event.key])
        elif event.type == pygame.KEYUP:
            if -event.key in self.keymap:
                self.perform(self.keymap[-event.key])
        return 0

    def perform(self, arg):
        if arg == 'quit':
            pygame.quit()
            sys.exit()
        elif arg == 'menu':
            self.menu.toggle()
        else:
            self.player.input(arg, self.mouse)
