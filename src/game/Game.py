from src.game import Global
from src.game.Camera import Camera
from src.game.Editor import Editor
from src.game.Mercenary import Mercenary
from src.game.Script import Script
from src.game.Turn import Turn
from src.map.World import World
from src.tools.Data import Data
from src.tools.Dialog import Dialog
from src.tools.Tag import Tag


class Game:
    def __init__(self):
        Turn.add(Global.menu.turn)
        Turn.fast_queue.append(Global.map_view.update)
        Turn.add(self.turn)
        Turn.hour_change.append(self.on_hour_change)
        from src.interface.Control import Control
        self.control = Control(self.input)
        if Data.is_file('save/player.char'):
            data = Data.process_raw(Data.read('save/player.char'))
        else:
            data = Data.process_raw(Data.read('data/map/template.char'))
        self.tags = Tag()
        self.tags.load(data[0][0])
        self.player = None
        self.dead = -1
        self.days = self.tags.get('time')
        Turn.frame = self.tags.get('frame')
        self.player_mode = 1
        self.character = None
        self.temporary = data
        self.npc = Mercenary()

    def initialize(self):
        if not self.tags.get('seed'):
            self.tags.set('seed', Global.r.rand_int(0, 99999))
        Global.world.set_seed(self.tags.get('seed'))
        is_new = False
        if not self.tags.get('c_x') or not self.tags.get('c_y'):
            is_new = True
            spawns = []
            count = 0
            while not spawns:
                spawns = self.get_biomes(count)
                count += 1
            data3 = Global.r.rand_list(spawns)
            self.tags.set('c_x', data3[2])
            self.tags.set('c_y', data3[3])
            self.npc.make()
            Global.world.initialize(data3[2], data3[3])
            from src.entity.Stock import Stock
            self.character = Stock.get(Global.world.location, self.temporary[1][1], data=self.temporary[1]).add()
            self.character.pos.load(data3[0], data3[1])
            class_data = Data.get_line('raw.txt', 'class')[1]
            self.set_class(Global.r.rand_list(class_data))
        else:
            self.npc.load(self.temporary[2:], self.tags.get('c_x'), self.tags.get('c_y'))
            Global.world.initialize(self.tags.get('c_x'), self.tags.get('c_y'))
            from src.entity.Stock import Stock
            self.character = Stock.get(Global.world.location, self.temporary[1][1], data=self.temporary[1]).add()
        self.temporary = self.character.sight
        self.character.relocate(to=self.character.pos.get_neighbor(World.CHUNK, World.CHUNK), force=True)
        self.set_player(self.character)
        self.initialize_mode()
        bgm = []
        Global.r_t.reset(self.tags.get('seed'))
        for i in [1, 2, 0, 0, 3, 4, 5, 6, 0, 0, 0]:
            if i != 0:
                bgm.append(Global.r_t.rand_list(['k_[', 'k_1', 'k_3', 'k_o']))
        self.character.location.sound.set_bgm(bgm, 2)
        if is_new:
            Script.execute_code('!birth')

    def save(self):
        if not self.character.removed:
            self.tags.set('time', self.days)
            self.tags.set('frame', Turn.frame)
            chunk = Global.world.get_camera_pos(self.character.pos.x, self.character.pos.y)
            start_coord = World.get_chunk_coord(chunk)
            self.character.pos_offset = start_coord
            self.tags.set('c_x', Global.world.cells[chunk][0])
            self.tags.set('c_y', Global.world.cells[chunk][1])
            r = self.tags.__str__() + '\n'
            r += self.character.__str__() + '\n'
            r += self.npc.__str__()
            Data.write('save/player.char', r)

    def get_biomes(self, level):
        spawns = []
        for i in Data.get_line('raw.txt', 'spawn')[1]:
            data3 = Global.world.get_true_pos_tile(i[0], i[1])
            if Global.world.get_biome(data3[2], data3[3]) == level:
                spawns.append(data3)
        return spawns

    def set_class(self, arg):
        self.character.tags.set('class', arg)
        if arg == 'avenger':
            self.character.tags.set('revenge', Global.r.rand_list(Data.get_line('raw.txt', 'revenge')[1]))
        elif arg == 'gourmet':
            self.character.tags.set('favorite', Global.r.rand_list(Data.get_line('raw.txt', 'favorite')[1]))
        elif arg == 'agent':
            mission = Global.r.rand_list(Data.get_line('raw.txt', 'mission')[1])
            self.character.tags.set('mission', '&'.join(mission))

    def set_player(self, player):
        player.tags.set('hunger', player.tags.get('hunger', 0))
        player.center_camera()
        player.save = False
        self.character = player
        self.player = player
        Script.var['game'] = self
        Script.var['player'] = player
        self.set_darkness()
        return player

    def is_daytime(self):
        return 5 < self.days % 24 < 20

    def sleep(self, time, blackout=True):
        if time > 0:
            self.character.progress_level(time, mode='survive')
            self.character.tags.increment('hunger', 1000 * time)
            self.days += time
            self.character.location.on_sleep(time)
            self.npc.update(0, 0, force=True)
            event = Global.r.rand_list(Data.get_line('raw.txt', 'event')[1])
            if event:
                Script.var['host'] = self
                Script.execute_code(event)
            investment = Global.player.character.tags.get('invest', 0)
            if investment:
                time = self.character.tags.increment('investt', time)
                if time >= 24:
                    Global.player.character.tags.increment('money', max(1, int(investment / 10)) * int(time / 24))
                    self.character.tags.set('investt', self.days % 24)
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
        if self.character.get_skill('nocturnal'):
            Global.map_view.set_view_range(Global.map_view.sight_range)
        else:
            Global.map_view.set_view_range(self.character.tags.get('view', 3))

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
        elif self.player_mode == 0:
            self.player.remove()
            self.player_mode = 1
        self.initialize_mode()

    def turn(self):
        if self.character.removed:
            if self.dead == 10:
                revive = self.character.states.get('Revive')
                if revive:
                    revive.end()
                    args = [int(x) for x in revive.var.split('&')]
                    self.character.add()
                    self.character.tags.set('money', 0)
                    self.character.tags.set('hunger', 0)
                    if self.character.tags.get('P', 0) <= 0:
                        Script.execute_code('death')
                    else:
                        Global.world.travel(args[0], args[1])
                else:
                    Script.execute_code('death')
            elif self.dead == 20:
                Global.menu.direct(Global.menu.menu_victory)
            else:
                self.dead += 1
        elif self.character.action.delay > 0:
            self.character.tags.increment('hunger', 5)
            if Global.r.rand_int(0, 16) == 0 and self.is_hungry():
                self.character.action.knockdown(self.character, Global.r.rand_int(2, 16))
        self.character.location.sound.update_bgm()
        if Global.world.recenter(self.character.pos.x, self.character.pos.y):
            Global.map_view.turn()
            Camera.update()
            Global.map_view.update_region()
        else:
            Global.map_view.update_region()
            Global.map_view.turn()

    def on_hour_change(self):
        self.sleep(1, blackout=False)

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
        items = self.character.get_possessions()
        from src.entity.Other import Food
        for i in items:
            if isinstance(i, Food):
                if i.tags.get('hunger') > 0:
                    return i.eat()
        Global.main.monologue.set(Dialog.get('!eat'))

    def is_hungry(self):
        return self.character.tags.get('hunger') >= 10000

    def pay(self, amount):
        if self.character.tags.require('money', amount):
            return True
        Global.main.monologue.set(Dialog.get('!pay', [amount]))

    def is_sociable(self):
        count = 0
        for i in self.character.location.population.get_team(self.character.tags.get('team', 0)):
            if i.tags.get('ai', '') == 'ally' and i.pilot.task.target == self.character:
                count += 1
        if count < self.character.tags.get('cha', 0):
            return True
        Global.main.monologue.set(Dialog.get('!sociable', [count, self.character.tags.get('cha', 0)]))

    def is_bright(self):
        if self.is_daytime() or self.character.pos.light >= Turn.rounds:
            return True
        Global.main.monologue.set(Dialog.get('!bright'))

    def describe_class(self):
        persona = self.character.tags.get('class', 'classless')
        if persona == 'avenger':
            arg = self.character.tags.get('revenge')
            return Dialog.get(persona, [arg])
        elif persona == 'gourmet':
            arg = self.character.tags.get('favorite')
            return Dialog.get(persona, [arg])
        elif persona == 'agent':
            arg = ', '.join(self.character.tags.get('mission').split('&'))
            return Dialog.get(persona, [arg])
        return Dialog.get(persona)
