import sys

import pygame

from src.entity.Space import Space
from src.game import Global
from src.game.Camera import Camera
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
        self.delay = 0
        self.directory = 'data/keymap.txt'
        self.set_keymap(self.directory)

    def set_keymap(self, fdir):
        self.directory = fdir
        control = Data.process_raw(Data.read(fdir))
        for k, v in control:
            self.keymap[Control.get_key_code(k)] = v

    def change_key(self, key, action):
        self.keymap[key] = action
        data = Data.process_raw(Data.read(self.directory))
        new_data = []
        for k, v in data:
            if k != key and v != action:
                new_data.append(str(k) + ',' + v)
        new_data.append(str(key) + ',' + action)
        Data.write(self.directory, '\n'.join(new_data))

    def get_key_name_from_action(self, action):
        for k, v in self.keymap.items():
            if v == action:
                return self.get_key_name(k)
        return 0

    @staticmethod
    def get_key_code(name):
        if name == 'LMB':
            return 501
        elif name == 'MMB':
            return 502
        elif name == 'RMB':
            return 503
        elif name == 'Wheel+':
            return 504
        elif name == 'Wheel-':
            return 505
        return getattr(pygame, 'K_' + str(name))

    @staticmethod
    def get_key_name(key):
        if key == 501:
            return 'LMB'
        elif key == 502:
            return 'MMB'
        elif key == 503:
            return 'RMB'
        elif key == 504:
            return 'Wheel+'
        elif key == 505:
            return 'Wheel-'
        return pygame.key.name(key)

    @staticmethod
    def get_event_code(event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            return event.button + 500
        elif event.type == pygame.MOUSEBUTTONUP:
            return -(event.button + 500)
        elif event.type == pygame.KEYDOWN:
            return event.key
        elif event.type == pygame.KEYUP:
            return -event.key
        return 0

    def input(self, event):
        if self.menu:
            if self.menu.input(event):
                return 1
        code = Control.get_event_code(event)
        if code > 0:
            if code not in self.keypress:
                self.keypress.append(code)
        elif code < 0:
            if -code not in self.keyrelease:
                self.keyrelease.append(-code)
        return 0

    def clear_press(self, code):
        if code in self.keyrelease:
            self.keyrelease.remove(code)
        if code in self.keypress:
            self.keypress.remove(code)

    def turn(self):
        mouse = pygame.mouse.get_pos()
        mouse = Space(Camera.get_relative_tile_pos(mouse[0], mouse[1]))
        length = self.keypress.__len__()
        if length > 0:
            code = self.keypress[length - 1]
            if code in self.keymap:
                command = self.keymap[code]
                if command == 'quit':
                    pygame.quit()
                    sys.exit()
                elif command == 'menu':
                    self.clear_press(code)
                    self.menu.toggle()
                elif command == 'character':
                    self.clear_press(code)
                    self.menu.state = self.menu.menu_character
                    self.menu.display(1)
                elif command == 'skills':
                    self.clear_press(code)
                    self.menu.state = self.menu.menu_skills
                    self.menu.display(1)
                elif command == 'equipment':
                    self.clear_press(code)
                    self.menu.state = self.menu.menu_equipment
                    self.menu.display(1)
                elif command == 'switch':
                    self.clear_press(code)
                    self.player.input(command, mouse)
                    Global.main.world.switch()
                else:
                    self.player.input(command, mouse)
        else:
            self.player.input('idle', mouse)
        for i in self.keyrelease:
            self.keyrelease.remove(i)
            if i in self.keypress:
                self.keypress.remove(i)
