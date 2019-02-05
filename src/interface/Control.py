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
        self.keypress = []
        self.keyrelease = []
        self.keymap = {}
        self.mouse = [0, 0]
        self.delay = 0
        self.set_keymap('data/keymap.txt')

    def set_keymap(self, fdir):
        control = Data.process_raw(Data.read(fdir))
        for k, v in control:
            self.keymap[k] = v

    def input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            button = event.button + 500
            if button not in self.keypress:
                self.keypress.append(button)
        elif event.type == pygame.MOUSEBUTTONUP:
            button = event.button + 500
            if button not in self.keyrelease:
                self.keyrelease.append(button)
        elif event.type == pygame.KEYDOWN:
            if event.key not in self.keypress:
                self.keypress.append(event.key)
        elif event.type == pygame.KEYUP:
            if event.key not in self.keyrelease:
                self.keyrelease.append(event.key)
        return 0

    def turn(self):
        mouse = pygame.mouse.get_pos()
        mouse = Global.get_relative_tile_pos(mouse[0], mouse[1])
        length = self.keypress.__len__()
        if length > 0:
            code = self.keypress[length - 1]
            if code in self.keymap:
                command = self.keymap[code]
                if command == 'quit':
                    pygame.quit()
                    sys.exit()
                elif command == 'menu':
                    if code in self.keyrelease:
                        self.keyrelease.remove(code)
                    if code in self.keypress:
                        self.keypress.remove(code)
                    if self.menu:
                        self.menu.toggle()
                else:
                    self.player.input(command, mouse)
        else:
            self.player.input('idle', mouse)
        for i in self.keyrelease:
            self.keyrelease.remove(i)
            if i in self.keypress:
                self.keypress.remove(i)
