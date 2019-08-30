from src.Editor import Editor
from src.entity.Effect import Effect
from src.game import Global
from src.game.Group import Group
from src.game.Interaction import Interaction
from src.game.Turn import Turn
from src.interface.Textbox import Textbox
from src.map.Location import Location
from src.map.Tile import Tile
from src.tools.Data import Data


class Player:
    def __init__(self):
        Group.init()
        Turn.init()
        Turn.add(self)
        self.control = None
        self.monologue = Textbox(self, Global.CENTER[0] - 100, Global.CENTER[1] - 80)
        data = Data.process_raw(Data.read('save/player.char'))
        if not data:
            data = Data.process_raw(Data.read('save/template.char'))
            self.monologue.text('Press [TAB] for help', time=300)
        map_name = 'save/' + data[0][0] + '.map'
        if not Data.is_file(map_name):
            self.location = Location.construct_map(data[0][0])
        else:
            map_data = list(Data.process_raw(Data.read(map_name)))
            self.location = Location(data[0][0], map_data)
        self.dead = 0
        self.background = None
        self.days = data[1][0]
        self.depart = data[1][1]
        self.character = self.load_player(self.location, data[2])
        self.set_passive(self.character.var['passive'])
        self.editor = None
        self.knowledge = data[3]
        self.temporary = None
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

    def set_passive(self, passive):
        if passive == 'Monk':
            self.character.fist.weight = 0

    def sleep(self, time):
        self.days += time
        if Global.player:
            if self.character.var['passive'] == 'Ranger':
                self.character.attributes.rest()
            insurance = self.character.states.get('Insured')
            if insurance:
                insurance.trigger(['time', 1])
        Global.main.colorize(0, [0, 0, 0, 255], fade=2)
        self.set_darkness()

    def set_darkness(self):
        if self.days % 2 == 0:
            Global.main.colorize(1, [0, 0, 0, 0])
            self.location.sight_range = 12
            self.location.resize()
            self.background = Data.run_cache('data/image/background/' + self.location.header[2])
        else:
            Global.main.colorize(1, [10, 0, 30, 160])
            self.location.sight_range = 6
            self.location.resize()
            name = 'data/image/background/' + self.location.header[2] + '_night'
            if Data.is_file(name + '.png'):
                self.background = Data.run_cache(name)
            else:
                self.background = Data.run_cache(name[:-6])

    def travel(self, to_map, to_pos):
        self.depart = self.character.location.name
        self.character.location.save()
        self.character.action.set('idle')
        self.character.form.set('interact')
        self.character.relocate(to_pos.x, to_pos.y, force=1)
        Global.player.location.name = to_map
        Global.player.turn()
        Global.player = Player()
        Global.main.resize(Global.DISPLAY[0], Global.DISPLAY[1])

    def switch(self):
        if self.character == self.control.player:
            self.editor = Editor(self.location, self.control)
            self.control.player = self.editor
            self.temporary = self.location.sight_block
            self.location.sight_block = []
            self.location.save()
        else:
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
            if self.dead == 10:
                if self.character.states.get('Insured'):
                    self.character.states.get('Insured').end()
                    self.dead = 0
                    self.character.removed = 0
                    Global.main.colorize(0, [0, 0, 0, 255], fade=1)
                    from src.entity.Space import Space
                    self.travel('town', Space(0, 0))
                    Global.menu.var = 1
                    Global.menu.state = Global.menu.menu_dead
                    Global.menu.display(1)
                else:
                    Global.menu.var = 0
                    Global.menu.state = Global.menu.menu_dead
                    Global.menu.display(1)
            else:
                self.dead += 1
        else:
            if self.character.var['passive'] == 'Rogue':
                for x in range(-4, 5):
                    for y in range(-4, 5):
                        tile = self.character.get_offset_tile(x, y)
                        if tile.is_land(Tile.CHECK_BREAKABLE):
                            pos = str(self.character.pos.x + x) + ',' + str(self.character.pos.y + y)
                            if pos not in self.location.draw_tiles:
                                Effect.make('sonic', tile.get_center())
            r = self.location.name + '\n'
            r += str(self.days) + ',' + str(self.depart) + '\n'
            r += self.character.__str__() + '\n'
            r += ','.join(self.knowledge) + '\n'
            Data.write('save/player.char', r)

    def is_safe(self):
        from src.entity.unit.Unit import Unit
        for unit in self.location.record:
            if isinstance(unit, Unit):
                if self.character.faction != unit.faction and unit.pilot.var == self.character:
                    self.monologue.text('Not safe!')
                    return False
        return True

    def pay(self, gold):
        if self.character.get_gold() >= gold:
            self.character.modify_gold(-gold)
            return True
        else:
            self.monologue.text('Not enough gold!')
            return False

    def eat(self):
        items = self.character.get_accessibles()
        for i in items:
            if i.name == 'Food':
                i.hit(1)
                return True
        hunger = self.character.states.get('Hunger')
        if hunger:
            self.monologue.text('Too hungry!')
            return False
        self.character.states.add('Hunger', -1, 0)
        return True

    def stamina(self, mag):
        if self.character.attributes.breath >= mag:
            self.character.attributes.breath -= mag
            return True
        else:
            self.monologue.text('Not enough stamina!')
            return False
