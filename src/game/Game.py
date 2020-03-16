from src.game import Global
from src.game.Editor import Editor
from src.game.Traveller import Traveller
from src.game.Turn import Turn
from src.map.Location import Location
from src.tools.Data import Data
from src.tools.Dialog import Dialog
from src.tools.Tag import Tag


class Game:
    def __init__(self):
        Turn.add(Global.menu.turn)
        Turn.add(Global.map_view.turn)
        Turn.add(Global.map_view.update_region)
        Turn.add(self.turn)
        from src.interface.Control import Control
        self.control = Control(self.input)
        data = Data.process_raw(Data.read('save/player.char'))
        if not data:
            data = Data.process_raw(Data.read('data/map/template.char'))
        self.tags = Tag()
        self.tags.load(data[0][0])
        map_name = self.tags.get('map')
        map_data = list(Data.process_raw(Data.read('save/' + map_name + '.map')))
        Global.land = Location(map_name, map_data)
        from src.entity.Stock import Stock
        self.character = None
        self.set_player(Stock.get(Global.land, data[1][2], data=data[1]).add())
        Global.map_view.old_camera = self.character.pos
        self.dead = -1
        self.days = self.tags.get('time')
        Turn.frame = self.tags.get('frame')
        self.player_mode = 1
        self.temporary = self.character.sight
        self.player = None
        self.daytime = True
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
        Global.player.character.relocate(x, y, force=1)
        Global.map_view.on_sight_change()

    def set_player(self, player):
        if player.tags.get('hunger') is None:
            player.tags.set('hunger', 0, add=True)
        self.control.player = player
        player.center_camera()
        player.action.delay = 4
        player.save = False
        self.character = player
        return player

    def is_daytime(self):
        return 5 < self.days % 24 < 18

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
        self.daytime = self.is_daytime()
        if blackout:
            Global.map_view.overlay.blackout()
        else:
            Global.map_view.overlay.fading = True
        self.set_darkness()
        return True

    def set_darkness(self):
        if self.daytime:
            Global.map_view.overlay.colorize(None)
            Global.map_view.sight_range = 13
            Global.map_view.view_range = 13
        else:
            Global.map_view.overlay.colorize([10, 0, 30, 160])
            Global.map_view.sight_range = 13
            Global.map_view.view_range = 3
        Global.map_view.on_sight_change()
        
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
            if self.character.location.name == 'worldmap':
                self.player_mode = 2
                self.control.set_keymap('travel_keymap.txt')
                self.character.center_camera()
                self.character.sight = self.temporary
                self.player = Traveller(self)
            else:
                self.player_mode = 1
                self.control.set_keymap('keymap.txt')
                self.player = self.character
                self.character.center_camera()
                self.character.sight = self.temporary
            self.sleep(0)
        Global.land.save()

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
                self.death()
            else:
                self.dead += 1
        elif self.dead == -1:
            self.dead = 0
            on_load = self.character.location.tags.get('load')
            if on_load:
                from src.game.Script import Script
                Script.execute_code(on_load)

    def death(self):
        self.character.tags.set('money', 0)
        self.character.tags.set('protein', 0)
        self.character.tags.set('calories', 0)
        insurance = self.character.states.get('Revive')
        if insurance:
            self.character.states.get('Revive').end()
            coma = Global.r.rand_int(3, 60)
            self.sleep(coma)
            self.dead = 0
            self.character.removed = 0
            Global.map_view.overlay.blackout()
            self.travel('home', 0, 0)
            Global.menu.var = [1, coma]
            text = Dialog.get('insurerevive', [Dialog.date(coma)])
            Global.menu.get_message(text + '\n' + Dialog.get('sign', ['Death']))(None)
        else:
            Global.menu.get_message(Dialog.get('youdie') + '\n' + Dialog.get('sign', ['Death']))(None)

    def save(self):
        self.tags.set('map', self.character.location.name)
        self.tags.set('time', self.days)
        self.tags.set('frame', Turn.frame)
        r = self.tags.__str__() + '\n'
        r += self.character.__str__() + '\n'
        Data.write('save/player.char', r)

    def is_safe(self):
        for unit in self.character.get_team(ally=False):
            if (unit.pos - self.character.pos).difference() < 8:
                Global.main.monologue.set(Dialog.get('!safe'))
                return False
            if unit.pilot.task == unit.pilot.attack and unit.pilot.task.target == self.character:
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
        if self.daytime or self.character.pos.light > 1:
            return True
        Global.main.monologue.set(Dialog.get('!bright'))
