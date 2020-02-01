from src.game.Editor import Editor
from src.game import Global
from src.game.Turn import Turn
from src.map.Location import Location
from src.map.Tile import Tile
from src.player.Inventory import Inventory
from src.tools.Data import Data


class Player:
    def __init__(self):
        Turn.add(self.turn)
        self.control = None
        data = Data.process_raw(Data.read('../save/player.char'))
        if not data:
            data = Data.process_raw(Data.read('map/template.char'))
        map_data = list(Data.process_raw(Data.read('../save/' + data[0][0] + '.map')))
        self.location = Location(data[0][0], map_data)
        self.dead = 0
        self.days = data[1][0]
        Turn.frame = data[1][1]
        self.depart = data[1][2]
        self.editor = None
        self.editor_mode = False
        self.knowledge = data[3]
        self.temporary = None
        self.character = self.load_player(self.location, data[2])
        self.set_ability(self.character.tags.get('talent'))
        self.inventory = Inventory(self.character)
        self.turn()
        self.sleep(0)

    def draw(self):
        pass

    def on_resize(self):
        pass

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
        return 5 < self.days % 24 < 18

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
        spell = Data.get_line('raw/spells.txt', knowledge)
        if spell:
            return True

    def set_ability(self, passive):
        if passive == 'Brawler':
            self.character.fist.weight = 0

    def sleep(self, time):
        self.days += time
        if Global.player and time >= 1:
            self.character.tags.add('full', -1)
            for i in self.character.get_possessions():
                i.on_sleep(time)
            for i in self.character.states.buffs:
                i.trigger(['time', time])
        Global.overlay.blackout()
        self.set_darkness()

    def set_darkness(self):
        if self.is_daytime():
            Global.overlay.colorize(None)
            Global.map_view.sight_range = 13
            Global.map_view.view_range = 13
        else:
            Global.overlay.colorize([10, 0, 30, 160])
            Global.map_view.sight_range = 10
            Global.map_view.view_range = 3
        Global.map_view.on_sight_change()

    def travel(self, to_map, to_pos):
        Global.overlay.blackout()
        self.depart = self.character.location.name
        if self.character.location.name != to_map:
            self.character.location.save()
        self.character.action.set('idle')
        self.character.form.set_state('interact')
        self.character.relocate(to_pos.x, to_pos.y, force=1)
        if to_map == 'home':
            to_map = Global.player.character.tags.get('home')
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
            self.temporary = Global.map_view.sight_block
            Global.map_view.sight_block = []
            self.location.save()
        else:
            self.editor_mode = False
            self.editor.remove()
            self.control.set_keymap('keymap.txt')
            self.control.player = self.character
            self.character.center_camera()
            Global.map_view.sight_block = self.temporary
            self.location.save()

    def turn(self):
        if self.character.removed:
            if self.dead == 2:
                revive = self.character.states.get('Foresee')
                if revive:
                    self.dead = 0
                    self.character.add()
                    revive.trigger(['death'])
            if self.dead == 10:
                self.character.tags.set('money', 0)
                self.character.tags.set('protein', 0)
                self.character.tags.set('calories', 0)
                death = self.character.tags.get('sign')
                insurance = self.character.states.get('Revive')
                if insurance:
                    self.character.states.get('Revive').end()
                    coma = Global.r.rand_int(3, 60)
                    self.sleep(coma)
                    self.dead = 0
                    self.character.removed = 0
                    Global.overlay.blackout()
                    from src.entity.Space import Space
                    self.travel('home', Space())
                    Global.menu.var = [1, coma]
                    from src.tools.Dialog import Dialog
                    text = Dialog.get('insurerevive', [Dialog.date(coma)])
                    Global.menu.get_message(text + '\n' + Dialog.get('sign', [death]))(None)
                else:
                    from src.tools.Dialog import Dialog
                    Global.menu.get_message(Dialog.get('youdie') + '\n' + Dialog.get('sign', [death]))(None)
            else:
                self.dead += 1
        else:
            if self.character.tags.get('talent') == 'Rogue':
                for x in range(-5, 6):
                    for y in range(-5, 6):
                        tile = self.character.pos.get_neighbor(x, y)
                        if tile.is_land([Tile.COLLIDE_UNIT]):
                            pos = str(self.character.pos.x + x) + ',' + str(self.character.pos.y + y)
                            if pos not in Global.map_view.draw_tiles:
                                Global.map_view.draw_tiles[pos] = self.character.pos.get_neighbor(x, y)
            r = self.location.name + '\n'
            r += str(self.days) + ',' + str(Turn.frame) + ',' + str(self.depart) + '\n'
            r += self.character.__str__() + '\n'
            r += ','.join(self.knowledge) + '\n'
            Data.write('../save/player.char', r)

    def is_safe(self):
        from src.entity.unit.Unit import Unit
        for unit in self.location.record:
            if isinstance(unit, Unit):
                if self.character.faction != unit.faction and unit.pilot.var == self.character:
                    self.character.say('Not safe!')
                    return False
        return True

    def eat(self):
        items = self.character.get_accessibles()
        from src.entity.Other import Food
        for i in items:
            if isinstance(i, Food):
                i.hit(1)
                return True
        hunger = self.character.states.get('Hunger')
        if hunger:
            self.character.say('Too hungry!')
            return False
        self.character.states.add('Hunger', -1, 0)
        return True

    def memorize(self):
        if self.character.tags.get('intelligence') > len(self.knowledge):
            return True
        else:
            self.character.say('Knowledge count exceeds Intelligence!')
            return False
