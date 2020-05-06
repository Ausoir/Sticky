from src.game import Global
from src.game.Camera import Camera
from src.game.Editor import Editor
from src.game.Script import Script
from src.game.Turn import Turn
from src.map.World import World
from src.tools.Data import Data
from src.tools.Dialog import Dialog
from src.tools.Tag import Tag


class Game:
    def __init__(self):
        Turn.add(Global.map_view.update_region)
        Turn.add(Global.menu.turn)
        Turn.add(Global.map_view.turn)
        Turn.fast_queue.append(Global.map_view.update)
        Turn.add(self.turn)
        from src.interface.Control import Control
        self.control = Control(self.input)
        data = Data.process_raw(Data.read('save/player.char'))
        if not data:
            data = Data.process_raw(Data.read('data/map/template.char'))
        self.tags = Tag()
        self.tags.load(data[0][0])
        # map_data = list(Data.process_raw(Data.read('save/' + map_name + '.map')))
        # Global.land = Location(map_name, map_data)
        self.world = World(self.tags.get('map'), self.tags.get('coord_x'), self.tags.get('coord_y'))
        Global.land = self.world.location
        from src.entity.Stock import Stock
        self.character = Stock.get(Global.land, data[1][1], data=data[1]).add()
        self.character.relocate(to=self.character.pos.get_neighbor(World.CHUNK, World.CHUNK), force=True)
        self.player = None
        self.set_player(self.character)
        self.dead = -1
        self.days = self.tags.get('time')
        Turn.frame = self.tags.get('frame')
        self.player_mode = 1
        self.temporary = self.character.sight
        self.initialize_mode()

    def travel(self, to_map, x=None, y=None):
        if self.character.location.name != to_map:
            self.character.location.save()
        self.character.action.set('idle')
        self.character.form.set_state('interact')
        self.character.location.name = to_map
        Global.player.save()
        Turn.init()
        self.character.remove()
        Global.player = Game()
        if x is None:
            x = Global.player.character.location.tags.get('enterx', 0)
        if y is None:
            y = Global.player.character.location.tags.get('entery', 0)
        Global.player.character.relocate(x=x, y=y, force=True)

    def set_player(self, player):
        if player.tags.get('hunger') is None:
            player.tags.set('hunger', 0)
        player.center_camera()
        player.action.delay = 4
        player.save = False
        self.character = player
        self.player = player
        Script.var['game'] = self
        Script.var['player'] = player
        return player

    def is_daytime(self):
        return 5 < self.days % 24 < 20

    def sleep(self, time, force=False, blackout=True):
        if time > 0:
            if not force:
                hunger = self.character.tags.get('hunger')
                if hunger + (time * 4) > 100:
                    nutrition = self.eat()
                    if not nutrition:
                        return False
            self.character.tags.increment('hunger', time * 4)
            self.character.decay(-time)
            self.days += time
            self.character.location.on_sleep(time)
        if blackout:
            Global.map_view.overlay.blackout()
        else:
            Global.map_view.overlay.fading = True
        self.set_darkness()
        return True

    def set_darkness(self):
        time = self.days % 24
        Global.map_view.overlay.set_time(time)
        Global.map_view.set_sight_range(Global.SIGHT)
        Global.map_view.set_view_range(3)

    def input(self, command):
        if self.player:
            self.player.input(command)

    def initialize_mode(self):
        Global.menu.display(-1)
        if self.player_mode == 0:
            self.control.set_keymap('editor_keymap.txt')
            self.player = Editor(self)
            self.temporary = self.character.sight
            self.character.sight = []
        else:
            self.player_mode = 1
            self.control.set_keymap('keymap.txt')
            self.player = self.character
            self.character.center_camera()
            self.character.sight = self.temporary
            self.sleep(0)
        Global.map_view.on_sight_change()

    def switch(self):
        if self.player_mode == 1:
            self.player_mode = 0
        elif self.player_mode == 2:
            self.player.remove()
            self.player_mode = 0
        elif self.player_mode == 0:
            self.player.remove()
            self.player_mode = 1
        self.initialize_mode()

    def turn(self):
        if self.character.removed:
            if self.dead == 10:
                Script.execute_code('death')
            else:
                self.dead += 1
        elif self.dead == -1:
            self.dead = 0
            on_load = self.character.location.tags.get('load')
            if on_load:
                Script.execute_code(on_load)
        # if self.player_mode == 1:
        old_x = self.character.pos.x
        old_y = self.character.pos.y
        if self.world.recenter(self.character.pos.x, self.character.pos.y):
            self.character.location.process_terrain()
            self.character.vec.x += Camera.pos[0] - old_x * Global.BLOCK - Global.HALF_BLOCK
            self.character.vec.y += Camera.pos[1] - old_y * Global.BLOCK - Global.HALF_BLOCK
            Global.map_view.update_fog()
            Camera.update()
            Global.map_view.update_region()

    def save(self):
        self.tags.set('map', self.character.location.name)
        self.tags.set('time', self.days)
        self.tags.set('frame', Turn.frame)
        if self.tags.get('map') == 'world':
            actual = self.world.get_camera_pos(self.character.pos.x, self.character.pos.y)
            temp = self.character.pos
            self.character.pos = self.character.pos - actual[1]
            self.tags.set('coord_x', self.world.cells[actual[0]][0])
            self.tags.set('coord_y', self.world.cells[actual[0]][1])
            r = self.tags.__str__() + '\n'
            r += self.character.__str__() + '\n'
            self.character.pos = temp
        else:
            r = self.tags.__str__() + '\n'
            r += self.character.__str__() + '\n'
        Data.write('save/player.char', r)

    def is_safe(self):
        for unit in self.character.get_team(ally=False):
            if unit.tags.get('ai'):
                diff = (unit.pos - self.character.pos).difference()
                if diff <= 3:
                    Global.main.monologue.set(Dialog.get('!safe'))
                    return False
                elif diff <= 13 and unit.pilot.task == unit.pilot.attack and unit.pilot.task.target == self.character:
                    Global.main.monologue.set(Dialog.get('!safe'))
                    return False
        return True

    def eat(self):
        items = self.character.get_accessibles()
        from src.entity.Other import Food
        for i in items:
            if isinstance(i, Food):
                if i.nutrition[1] > 0:
                    return i.eat()
        Global.main.monologue.set(Dialog.get('!eat'))

    def is_hungry(self):
        return self.character.tags.get('hunger') >= 100

    def pay(self, amount):
        if self.character.tags.require('money', amount):
            return True
        Global.main.monologue.set(Dialog.get('!pay'))

    def is_bright(self):
        if self.is_daytime() or self.character.pos.light > 1:
            return True
        Global.main.monologue.set(Dialog.get('!bright'))

    def get_brightness(self):
        return Global.map_view.overlay.LIGHT[self.days % 24]
