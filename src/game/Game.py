from src.entity.Particle import Particle
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
    def __init__(self, mode=False):
        Turn.add(Global.menu.turn)
        Turn.fast_queue.append(Global.map_view.update)
        Turn.add(self.turn)
        Turn.hour_change.append(self.on_hour_change)
        from src.interface.Control import Control
        self.control = Control(self.input)
        self.companions = []
        if Data.is_file('save/player.char'):
            player_data = Data.read('save/player.char')
            data = Data.process_raw(player_data)
            for companion in player_data.split('\n')[3:]:
                self.companions.append(companion)
        else:
            data = Data.process_raw(Data.read('data/map/template.char'))
        self.tags = Tag()
        self.tags.load(data[0][0])
        self.player = None
        self.dead = -1
        self.days = self.tags.get('time')
        Turn.frame = self.tags.get('frame')
        self.editor_mode = mode
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
            Global.world.initialize(data3[2], data3[3])
            self.npc.make()
            from src.entity.Stock import Stock
            self.character = Stock.get(self.temporary[1][1], data=self.temporary[1]).add()
            self.character.relocate(x=data3[0], y=data3[1], force=True)
            class_data = Data.get_line('raw.txt', 'class')[1]
            self.set_class(Global.r.rand_list(class_data))
        else:
            self.npc.load(self.temporary[2])
            Global.world.initialize(self.tags.get('c_x'), self.tags.get('c_y'))
            from src.entity.Stock import Stock
            self.character = Stock.get(self.temporary[1][1], data=self.temporary[1]).add()
        self.temporary = self.character.sight
        self.character.relocate(to=self.character.pos.get_neighbor(World.CHUNK, World.CHUNK), force=True)
        self.set_player(self.character)
        self.initialize_mode()
        Global.world.location.sound.initialize()
        if is_new:
            Script.execute_code('birth')

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
            r += self.character.save() + '\n'
            r += self.npc.__str__() + '\n'
            r += '\n'.join(self.companions)
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
            self.character.tags.set('classg', Global.r.rand_list(Data.get_line('raw.txt', 'revenge')[1]))
        elif arg == 'gourmet':
            self.character.tags.set('classg', Global.r.rand_list(Data.get_line('raw.txt', 'favorite')[1]))
        elif arg == 'agent':
            mission = Global.r.rand_list(Data.get_line('raw.txt', 'mission')[1])
            self.character.tags.set('classg', '&'.join(mission))

    def set_player(self, player):
        player.tags.set('hunger', player.tags.get('hunger', 0))
        player.center_camera()
        player.is_save = False
        self.character = player
        self.player = player
        Script.var['game'] = self
        Script.var['player'] = player
        self.set_darkness()
        return player

    def is_daytime(self):
        return 5 < self.days % 24 < 20

    def on_hour_change(self):
        self.sleep(-1, blackout=False)

    def sleep(self, time, blackout=True):
        if time != 0:
            self.save()
            self.character.progress_level(time, mode='survive')
            Global.world.location.on_sleep(time)
            event = Global.r.rand_list(Data.get_line('raw.txt', 'event')[1])
            if event:
                Script.var['host'] = self
                Script.execute_code(event)
            if time > 0:
                self.days += time
                investment = self.tags.get('invest', 0)
                if investment:
                    time = self.tags.increment('investt', time)
                    if time >= 24:
                        Global.player.character.tags.increment('money', max(1, int(investment / 10)) * int(time / 24))
                        self.tags.set('investt', self.days % 24)
        if blackout:
            Global.map_view.overlay.blackout()
        else:
            Global.map_view.overlay.fading = True
        self.set_darkness()
        return True

    def try_sleep(self, arg):
        if not self.character.is_hungry():
            self.sleep(arg)
            return True
        else:
            Global.main.monologue.set(Dialog.get('!eat'))

    def set_darkness(self):
        time = self.days % 24
        Global.map_view.overlay.set_time(time)
        Global.map_view.set_sight_range(Global.SIGHT)
        if self.character.get_skill('nocturnal') or self.character.states.get('Vision'):
            Global.map_view.set_view_range(Global.map_view.sight_range)
        else:
            Global.map_view.set_view_range(self.character.tags.get('view', 3))

    def input(self, command):
        if self.player:
            self.player.input(command)

    def initialize_mode(self):
        Global.menu.display(-1)
        if self.editor_mode:
            self.control.set_keymap('editor_keymap.txt')
            self.player = Editor(self)
            self.temporary = self.character.sight
            self.character.sight = []
        else:
            self.editor_mode = False
            self.control.set_keymap('keymap.txt')
            self.player = self.character
            self.character.center_camera()
            self.character.sight = self.temporary
            self.sleep(0)
        Global.map_view.on_sight_change()

    def switch(self):
        if not self.editor_mode:
            self.editor_mode = True
        else:
            self.player.remove()
            self.editor_mode = False
        self.initialize_mode()

    def turn(self):
        if self.character.removed:
            if self.dead == 10:
                Script.execute_code('death')
            elif self.dead == 11:
                Global.menu.display(1)
            else:
                self.dead += 1
        elif self.character.action.delay > 0:
            self.character.tags.increment('hunger', 1)
        elif self.character.action.current_action == 'idle':
            if self.character.is_hungry():
                self.character.form.set_state('hunger')
            if self.character.tags.get('p', 0) == 1 and self.character.tags.get('P'):
                Particle.make('blood', self.character.pos, offset=8)
        if Global.world.recenter(self.character.pos.x, self.character.pos.y):
            Global.map_view.turn()
            Camera.update()
            Global.map_view.update_region()
        else:
            Global.map_view.update_region()
            Global.map_view.turn()

    def is_safe(self):
        for unit in self.character.get_team(ally=False):
            if unit.tags.get('ai'):
                diff = (unit.pos - self.character.pos).difference()
                if diff <= 2:
                    Global.main.monologue.set(Dialog.get('!safe'))
                    return False
                elif diff <= 13 and unit.pilot.task == unit.pilot.attack and unit.pilot.task.target == self.character:
                    Global.main.monologue.set(Dialog.get('!safe'))
                    return False
        return True

    def pay(self, amount):
        if amount <= 0 or self.character.tags.require('money', amount):
            return True
        Global.main.monologue.set(Dialog.get('!pay', [amount]))

    def is_sociable(self, arg, notice=True):
        count = len(self.companions) * 2
        for i in Global.world.location.population.get_team(self.character.tags.get('team', 0)):
            if i.tags.get('summon', 0) == 1:
                count += 1
        if count + arg <= self.character.tags.get('cha', 0):
            return True
        if notice:
            Global.main.monologue.set(Dialog.get('!sociable', [count, self.character.tags.get('cha', 0)]))

    def is_bright(self):
        if self.character.pos.light > 0:
            return True
        Global.main.monologue.set(Dialog.get('!bright'))

    def is_learnable(self):
        intelligence = self.character.tags.get('int', 0)
        current = len(self.character.skills)
        if self.character.tags.get('ab1'):
            current += 1
        if self.character.tags.get('ab2'):
            current += 1
        if self.character.tags.get('ab3'):
            current += 1
        if intelligence > current:
            return True
        Global.main.monologue.set(Dialog.get('!learn_int'))

    def describe_class(self):
        persona = self.character.tags.get('class', 'classless')
        if persona == 'avenger':
            arg = self.character.tags.get('classg')
            return Dialog.get(':' + persona, [arg])
        elif persona == 'gourmet':
            arg = self.character.tags.get('classg')
            return Dialog.get(':' + persona, [arg])
        elif persona == 'agent':
            arg = ', '.join(self.character.tags.get('classg').split('&'))
            return Dialog.get(':' + persona, [arg])
        return Dialog.get(':' + persona)
