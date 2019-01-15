import sys
import pygame

from src.interface.Menu import Menu
from src.other.Data import Data


class Control:
    def __init__(self):
        self.keymap = {}
        control = Data.process_raw(Data.read("Keymap.txt"))
        for k, v in control:
            self.keymap[k] = v

    def input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in self.keymap:
                self.perform(self.keymap[event.key])

    @staticmethod
    def perform(arg):
        if arg == 'quit':
            pygame.quit()
            sys.exit()
        if arg == 'menu':
            Menu.display()
