import sys

import pygame

from src.entity.Space import Space
from src.game import Global
from src.game.Camera import Camera
from src.game.Turn import Turn
from src.tools.Data import Data


class Control:
    def __init__(self, player):
        Turn.add(self)
        self.player = player
        self.keypress = []
        self.keyrelease = []
        self.keymap = {}
        self.directory = 'data/keymap.txt'
        self.set_keymap(self.directory)

    def set_keymap(self, fdir):
        self.directory = fdir
        control = Data.process_raw(Data.read(fdir))
        for k, v in control:
            self.keymap[Control.get_key_code(k)] = v

    def get_key(self, value):
        for k, v in self.keymap.items():
            if v == value:
                return k

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
        elif str(name).startswith('LS+'):
            return 2000 + Control.get_key_code(name[3:])
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
        elif key > 2000:
            return 'LS+' + Control.get_key_name(key - 2000)
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
        if Global.menu.visible == 1:
            if Global.menu.input(event):
                return 1
        code = Control.get_event_code(event)
        if code > 0:
            if code not in self.keypress:
                if code == 304:
                    for k, v in enumerate(self.keypress):
                        if self.keypress[k] not in self.keyrelease:
                            self.keypress[k] = 2000 + v
                    self.keypress.insert(0, 304)
                else:
                    if 304 in self.keypress:
                        self.keypress.append(2000 + code)
                    else:
                        self.keypress.append(code)
        elif code < 0:
            if -code not in self.keyrelease:
                if 304 in self.keypress:
                    if (2000 - code) in self.keypress:
                        self.keypress.remove(2000 - code)
                else:
                    self.keyrelease.append(-code)
                if -code == 304:
                    self.keypress.remove(-code)
                    for k, v in enumerate(self.keypress):
                        if v > 2000:
                            self.keypress[k] = v - 2000
        return 0

    def clear_press(self, code):
        if code in self.keyrelease:
            self.keyrelease.remove(code)
        if code in self.keypress:
            self.keypress.remove(code)

    def quit(self):
        mouse = pygame.mouse.get_pos()
        mouse = Space(Camera.get_relative_tile_pos(mouse[0], mouse[1]))
        self.player.input('quit', mouse)
        self.player.location.delay = 0
        self.player.location.turn()
        pygame.quit()
        sys.exit()

    def turn(self):
        mouse = pygame.mouse.get_pos()
        mouse = Space(Camera.get_relative_tile_pos(mouse[0], mouse[1]))
        length = self.keypress.__len__()
        if length > 0:
            code = self.keypress[length - 1]
            if code in self.keymap:
                command = self.keymap[code]
                if command == 'quit':
                    self.quit()
                elif command == 'menu':
                    self.clear_press(code)
                    Global.menu.toggle()
                elif command == 'text':
                    self.clear_press(code)
                    Global.main.textbox.display_text = ''
                    Global.main.text_mode = True
                elif command == 'switch':
                    self.clear_press(code)
                    Global.player.switch()
                else:
                    if not Global.player.click(command, mouse):
                        self.player.input(command, mouse)
        else:
            self.player.input('idle', mouse)
        for i in self.keyrelease:
            self.keyrelease.remove(i)
            if i in self.keypress:
                self.keypress.remove(i)
            if i > 2000:
                realkey = i - 2000
                if realkey in self.keypress:
                    self.keypress.remove(realkey)
