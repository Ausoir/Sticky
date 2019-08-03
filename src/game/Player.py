from src.Editor import Editor
from src.game import Global
from src.game.Group import Group
from src.game.Interaction import Interaction
from src.game.Turn import Turn
from src.interface.Textbox import Textbox
from src.map.Location import Location
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
        self.background = None
        self.days = data[1][0]
        self.experience = data[1][1]
        self.sleep(0)
        self.character = self.load_player(self.location, data[2])
        self.editor = None
        self.knowledge = data[3]
        self.temporary = None
        self.turn()

    def load_player(self, loc, data):
        from src.interface.MenuAll import MenuAll
        from src.interface.Control import Control
        from src.entity.Stock import Stock
        player = Stock.units(data)
        Global.menu = MenuAll(player)
        self.control = Control(player)
        player.center_camera()
        player.add()
        player.delay = 4
        loc.record.remove(player)
        return player

    def sleep(self, time):
        self.days += time
        if self.days % 2 == 0:
            self.location.sight_range = 7
            self.location.resize()
            self.background = Data.run_cache('data/image/background/' + self.location.header[2])
        else:
            Global.main.weather = (10, 0, 30, 220)
            self.location.sight_range = 5
            self.location.resize()
            name = 'data/image/background/' + self.location.header[2] + '_night'
            if Data.is_file(name + '.png'):
                self.background = Data.run_cache(name)
            else:
                self.background = Data.run_cache(name[:-6])

    def travel(self, to_map, to_pos):
        self.character.location.save()
        self.character.action.set('idle')
        self.character.form.set('interact')
        self.character.relocate(to_pos.x, to_pos.y, force=1)
        Global.main.player.location.name = to_map
        Global.main.player.turn()
        Global.main.player = Player()
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
                if (tile - self.character.pos[0]).distance() <= 1:
                    return Interaction.trigger(tile)

    def turn(self):
        r = self.location.name + '\n'
        r += str(self.days) + ',[' + ','.join(str(x) for x in self.experience) + ']\n'
        r += self.character.__str__() + '\n'
        r += ','.join(self.knowledge) + '\n'
        Data.write('save/player.char', r)
