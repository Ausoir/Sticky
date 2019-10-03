from src.Editor import Editor
from src.entity.Particle import Particle
from src.game import Global
from src.game.Group import Group
from src.game.Interaction import Interaction
from src.game.Turn import Turn
from src.map.Location import Location
from src.map.Tile import Tile
from src.tools.Data import Data


class Player:
    def __init__(self):
        Group.init()
        Turn.init()
        Turn.add(self.turn)
        self.control = None
        data = Data.process_raw(Data.read('save/player.char'))
        if not data:
            data = Data.process_raw(Data.read('map/template.char'))
        map_data = list(Data.process_raw(Data.read('save/' + data[0][0] + '.map')))
        self.location = Location(data[0][0], map_data)
        self.dead = 0
        self.background = None
        self.days = data[1][0]
        Turn.frame = data[1][1]
        self.depart = data[1][2]
        self.editor = None
        self.editor_mode = False
        self.knowledge = data[3]
        self.temporary = None
        self.character = self.load_player(self.location, data[2])
        self.set_power(self.character.var['power'])
        self.turn()
        self.sleep(0)

    def load_player(self, loc, data):
        from src.interface.MenuAll import MenuAll
        from src.interface.Control import Control
        from src.entity.unit.Character import Character
        player = Character(loc)
        player.load(data)
        Global.menu = MenuAll(player)
        self.control = Control(player)
        player.center_camera()
        player.add()
        player.delay = 4
        loc.record.remove(player)
        return player

    def is_daytime(self):
        return self.days % 2 == 0

    def get_spell_list(self):
        spells = []
        for i in self.knowledge:
            if Player.is_spell(i):
                spells.append(i)
        return spells

    def get_craft_list(self):
        crafts = []
        for i in self.knowledge:
            if not Player.is_spell(i):
                crafts.append(i)
        return crafts

    @staticmethod
    def is_spell(knowledge):
        spell = Data.get_line('data/raw/spells.txt', knowledge)
        if spell:
            return True

    def set_power(self, passive):
        if passive == 'Warrior':
            self.character.fist.weight = 0

    def sleep(self, time):
        self.days += time
        if Global.player and time >= 1:
            self.character.attributes.rest()
            self.character.var['protein'] = max(0, self.character.var['protein'] - 1)
            self.character.var['calories'] = max(0, self.character.var['calories'] - 1)
            for i in self.character.get_possessions():
                i.on_sleep(time)
            for i in self.character.states.buffs:
                i.trigger(['time', time])
        for i in self.location.draw_tiles.values():
            i.light = 0
        Global.main.colorize(0, [0, 0, 0, 255], fade=2)
        self.set_darkness()

    def set_darkness(self):
        if self.is_daytime():
            Global.main.colorize(1, [0, 0, 0, 0])
            self.location.sight_range = 12
            self.location.view_range = 12
            self.location.resize()
            self.background = Data.run_cache('data/image/background/' + self.location.header[2])
            self.background.resize(Global.DISPLAY)
        else:
            Global.main.colorize(1, [10, 0, 30, 160])
            self.location.sight_range = 8
            self.location.view_range = 5
            self.location.resize()
            name = 'data/image/background/' + self.location.header[2] + '_night'
            if Data.is_file(name + '.png'):
                self.background = Data.run_cache(name)
            else:
                self.background = Data.run_cache(name[:-6])
            self.background.resize(Global.DISPLAY)

    def travel(self, to_map, to_pos):
        Global.main.colorize(0, [0, 0, 0, 255], fade=2)
        self.depart = self.character.location.name
        self.character.location.save()
        self.character.action.set('idle')
        self.character.form.set('interact')
        self.character.relocate(to_pos.x, to_pos.y, force=1)
        if to_map == 'home':
            to_map = Global.player.character.var['home']
        Global.player.location.name = to_map
        Global.player.turn()
        Global.player = Player()
        Global.main.resize(Global.DISPLAY[0], Global.DISPLAY[1])

    def switch(self):
        if not self.editor_mode:
            Global.menu.display(-1)
            self.editor_mode = True
            self.editor = Editor(self.location, self.control)
            self.control.player = self.editor
            self.temporary = self.location.sight_block
            self.location.sight_block = []
            self.location.save()
        else:
            self.editor_mode = False
            self.editor.remove()
            self.control.set_keymap('data/keymap.txt')
            self.control.player = self.character
            self.character.center_camera()
            self.location.sight_block = self.temporary
            self.location.save()

    def click(self, command, mouse):
        if command == 'use':
            if self.character == self.control.player:
                self.character.next_target = mouse
                tile = self.character.get_target_tile()
                if (tile - self.character.pos).distance() <= 1:
                    return Interaction.trigger(tile)

    def turn(self):
        if self.character.removed:
            if self.dead == 2:
                revive = self.character.states.get('Foresee')
                if revive:
                    self.dead = 0
                    self.character.add()
                    revive.trigger(['death'])
            if self.dead == 10:
                self.character.var['money'] = 0
                self.character.var['protein'] = 0
                self.character.var['calories'] = 0
                death = 'Accident'
                if 'sign' in self.character.var:
                    death = self.character.var['sign']
                elif self.character.durability > 0:
                    death = 'Illness'
                insurance = self.character.states.get('Insured')
                if insurance:
                    if insurance.trigger(['death', death]):
                        self.character.states.get('Insured').end()
                        self.dead = 0
                        self.character.removed = 0
                        Global.main.colorize(0, [0, 0, 0, 255], fade=1)
                        from src.entity.Space import Space
                        self.travel('home', Space(0, 0))
                        Global.menu.var = [1]
                        Global.menu.state = Global.menu.menu_dead
                        Global.menu.display(1)
                    else:
                        Global.menu.var = [2, death, insurance.var.split('/')[0]]
                        Global.menu.state = Global.menu.menu_dead
                        Global.menu.display(1)
                else:
                    Global.menu.var = [0, death]
                    Global.menu.state = Global.menu.menu_dead
                    Global.menu.display(1)
            else:
                self.dead += 1
        else:
            if self.character.var['power'] == 'Rogue':
                for x in range(-6, 7):
                    for y in range(-6, 7):
                        tile = self.character.get_offset_tile(x, y)
                        if tile.is_land([Tile.COLLIDE_UNIT]):
                            pos = str(self.character.pos.x + x) + ',' + str(self.character.pos.y + y)
                            if pos not in self.location.draw_tiles:
                                Particle.make('sonic', tile.get_center())
            r = self.location.name + '\n'
            r += str(self.days) + ',' + str(Turn.frame) + ',' + str(self.depart) + '\n'
            r += self.character.__str__() + '\n'
            r += ','.join(self.knowledge) + '\n'
            Data.write('save/player.char', r)

    def is_safe(self):
        from src.entity.unit.Unit import Unit
        for unit in self.location.record:
            if isinstance(unit, Unit):
                if self.character.faction != unit.faction and unit.pilot.var == self.character:
                    self.character.say('Not safe!')
                    return False
        return True

    def menu(self, menu):
        self.control.clear_press()
        Global.menu.state = menu
        Global.menu.display(1)

    def drink(self):
        items = self.character.get_accessibles()
        from src.game.Tags import Tags
        for i in items:
            if Tags.drinkable in i.tags:
                i.hit(1)
                return True
        thirst = self.character.states.get('Thirst')
        if thirst:
            self.character.say('Too thirsty!')
            return False
        self.character.states.add('Thirst', -1, 0)
        return True

    def memorize(self):
        if self.character.attributes.intelligence > len(self.knowledge):
            return True
        else:
            self.character.say('Knowledge count exceeds Intelligence!')
            return False
