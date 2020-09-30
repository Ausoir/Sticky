import pyglet

from src.game import Global
from src.game.Camera import Camera
from src.game.Turn import Turn
from src.tools.Data import Data


class Control:
    def __init__(self, output):
        Turn.fast_queue.append(self.turn)
        self.cursor = [0, 0]
        self.cursor_tile = None
        self.keypress = []
        self.keyrelease = []
        self.keymap = {}
        self.text_mode = False
        self.target_mark = self.make_mark()
        self.target_mark_frame = 0
        self.next_action = None
        self.output = output

    def set_keymap(self, fdir):
        self.keymap.clear()
        control = Data.process_raw(Data.read('data/' + fdir))
        for k, v in control:
            self.keymap[Control.get_key_code(k)] = v

    @staticmethod
    def make_mark():
        from src.entity.Image import Image
        mark = Image()
        mark.form = Data.get_form('_g_9_0')
        mark.form.z = 900
        mark.form.bound(True)
        mark.vec += Global.HALF_BLOCK
        return mark

    def get_key(self, value):
        for k, v in self.keymap.items():
            if v == value:
                return k

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
            Global.text.set(Global.text.text.text + key)

    def input(self, code):
        if self.text_mode:
            self.clear_press(code)
            if code in self.keymap and self.keymap[code] == 'text':
                self.text_mode = False
                self.output('command')
                Global.text.set('')
            elif code > 5:
                if code == pyglet.window.key.BACKSPACE:
                    Global.text.set(Global.text.text.text[:-1])
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
                self.target_mark_frame = 0
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

    def turn(self):
        self.target_mark_frame += 1
        self.target_mark.update()
        self.cursor_tile = Camera.get_relative_tile_pos(self.cursor[0], self.cursor[1])
        self.cursor_tile[0] += Camera.target.pos.x
        self.cursor_tile[1] += Camera.target.pos.y
        length = self.keypress.__len__()
        if length > 0:
            code = self.keypress[length - 1]
            if code in self.keymap:
                command = self.keymap[code]
                if command.startswith('#'):
                    self.clear_press(code)
                    from src.game.Script import Script
                    Script.var['host'] = Global.player.character
                    Script.execute_code(command[1:])
                elif command == 'fullscreen':
                    if Global.main.fullscreen:
                        Global.main.set_fullscreen(False)
                    else:
                        Global.main.set_fullscreen(True)
                elif Global.menu.visible == 1 and command == 'grab':
                    self.clear_press(code)
                    Global.menu.previous()
                elif command == 'switch':
                    self.clear_press(code)
                    Global.player.switch()
                elif command == 'text':
                    self.clear_press(code)
                    Global.text.set('')
                    self.text_mode = True
                elif Global.menu.visible != 1:
                    if command == 'left2':
                        self.move_mark_toward(1)
                    elif command == 'up2':
                        self.move_mark_toward(2)
                    elif command == 'right2':
                        self.move_mark_toward(3)
                    elif command == 'down2':
                        self.move_mark_toward(4)
                    else:
                        self.target_mark.form.show(False)
                        self.output(command)
        else:
            self.output('idle')
        for i in self.keyrelease:
            self.keyrelease.remove(i)
            if i in self.keypress:
                self.keypress.remove(i)
            if i > 100000:
                realkey = i - 100000
                if realkey in self.keypress:
                    self.keypress.remove(realkey)

    def move_mark_toward(self, direction):
        self.next_action = direction
        self.move_mark(Camera.target.pos.to_list())
        if self.target_mark_frame > 3 and self.next_action > 0:
            if self.next_action == 1:
                self.target_mark.vec.x -= Global.BLOCK
            elif self.next_action == 2:
                self.target_mark.vec.y -= Global.BLOCK
            elif self.next_action == 3:
                self.target_mark.vec.x += Global.BLOCK
            elif self.next_action == 4:
                self.target_mark.vec.y += Global.BLOCK
            self.target_mark_frame = 0
            self.next_action = 0

    def move_mark(self, pos):
        if not self.target_mark.form.visible:
            x = pos[0] * Global.BLOCK + Global.HALF_BLOCK
            y = pos[1] * Global.BLOCK + Global.HALF_BLOCK
            self.target_mark.vec.load(x, y)
            self.target_mark.form.show(True)
            self.target_mark.update()

    def get_mark(self):
        vec = self.target_mark.vec
        tile = Global.world.location.get_tile_from_vec(vec.x, vec.y)
        if tile and tile.is_seen():
            return tile
