import sys

import pyglet

from src.game import Global
from src.game.Camera import Camera
from src.game.Turn import Turn
from src.tools.Data import Data


class Control:
    def __init__(self, player):
        Turn.fast_queue.append(self.turn)
        self.player = player
        self.cursor = [0, 0]
        self.cursor_tile = None
        self.keypress = []
        self.keyrelease = []
        self.keymap = {}
        self.text_mode = False
        self.directory = 'keymap.txt'
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

    @staticmethod
    def get_key_code(name):
        if name == 'DRAG':
            return 0
        elif name == 'LMB':
            return 1
        elif name == 'MMB':
            return 2
        elif name == 'RMB':
            return 4
        elif name == 'Wheel+':
            return 504
        elif name == 'Wheel-':
            return 505
        elif str(name).startswith('LS+'):
            return 100000 + Control.get_key_code(name[3:])
        return getattr(pyglet.window.key, str(name))

    @staticmethod
    def get_key_name(key):
        if key == 0:
            return 'DRAG'
        elif key == 1:
            return 'LMB'
        elif key == 2:
            return 'MMB'
        elif key == 4:
            return 'RMB'
        elif key == 504:
            return 'Wheel+'
        elif key == 505:
            return 'Wheel-'
        elif key > 100000:
            return 'LS+' + Control.get_key_name(key - 100000)
        r = pyglet.window.key.symbol_string(key)
        if r.startswith('_'):
            return r[1:]
        return r

    def on_text(self, key):
        if self.text_mode:
            Global.main.monologue.set(Global.main.monologue.label.text + key)

    def input(self, code):
        if self.text_mode:
            if code in self.keymap and self.keymap[code] == 'text':
                self.text_mode = False
                self.player.input('command')
                Global.main.monologue.set('')
            elif code > 5:
                if code == pyglet.window.key.BACKSPACE:
                    Global.main.monologue.set(Global.main.monologue.label.text[:-1])
        else:
            if Global.menu.visible == 1:
                if Global.menu.input(code):
                    return 1
            if code > 0:
                if code not in self.keypress:
                    if code == 65505:
                        for k, v in enumerate(self.keypress):
                            if self.keypress[k] not in self.keyrelease:
                                self.keypress[k] = 100000 + v
                        self.keypress.insert(0, 65505)
                    else:
                        if 65505 in self.keypress:
                            self.keypress.append(100000 + code)
                        else:
                            self.keypress.append(code)
            elif code < 0:
                if -code not in self.keyrelease:
                    if 65505 in self.keypress:
                        if (100000 - code) in self.keypress:
                            self.keypress.remove(100000 - code)
                        if -code == 65505:
                            self.keypress.remove(-code)
                            for k, v in enumerate(self.keypress):
                                if v > 100000:
                                    self.keypress[k] = v - 100000
                    else:
                        self.keyrelease.append(-code)
        return 0

    def clear_press(self, code=None):
        if code:
            if code in self.keyrelease:
                self.keyrelease.remove(code)
            if code in self.keypress:
                self.keypress.remove(code)
        else:
            self.keyrelease.clear()
            self.keypress.clear()

    def quit(self):
        self.player.input('quit')
        self.player.location.delay = 0
        self.player.location.turn()
        sys.exit()

    def turn(self):
        self.cursor_tile = Camera.get_relative_tile_pos(self.cursor[0], self.cursor[1])
        self.cursor_tile[0] += Camera.target.pos.x
        self.cursor_tile[1] += Camera.target.pos.y
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
                    Global.main.monologue.set('')
                    self.text_mode = True
                elif command == 'switch':
                    self.clear_press(code)
                    Global.player.switch()
                elif command == 'help':
                    self.clear_press(code)
                    if Global.menu.visible == 1:
                        Global.menu.toggle()
                    else:
                        Global.menu.var = [None, 'Ask']
                        Global.menu.topic('Ask')
                elif Global.menu.visible != 1:
                    self.player.input(command)
        else:
            self.player.input('idle')
        for i in self.keyrelease:
            self.keyrelease.remove(i)
            if i in self.keypress:
                self.keypress.remove(i)
            if i > 100000:
                realkey = i - 100000
                if realkey in self.keypress:
                    self.keypress.remove(realkey)
