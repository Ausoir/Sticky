from src.Editor import Editor
from src.game.Group import Group
from src.game.Turn import Turn
from src.map.Location import Location
from src.tools.Data import Data


class Player:
    def __init__(self):
        Group.init()
        Turn.init()
        Turn.add(self)
        self.control = None
        data = Data.process_raw(Data.read('save/player'))
        if not data:
            data = Data.process_raw(Data.read('save/template'))

        maps = Data.get_files('save', lambda x: x.endswith('.map'))
        map_name = data[0][0] + '.map'
        if map_name in maps:
            map_data = list(Data.process_raw(Data.read('save/'+map_name)))
            self.map = Location(data[0][0], map_data)
        else:
            map_data = list(Data.process_raw(Data.read('data/map/'+map_name)))
            self.map = Location('map', map_data)
        self.character = self.load_player(self.map, data[1])
        self.editor = None
        self.knowledge = data[2]
        self.temporary = None
        self.turn()

    def load_player(self, loc, data):
        from src.entity.unit.Humanoid import Humanoid
        from src.interface.Menu import Menu
        from src.interface.Control import Control
        player = Humanoid(loc)
        self.control = Control(Menu(player), player)
        player.center_camera()
        player.durability = 8
        player.load(data)
        player.add()
        player.delay = 4
        loc.record.remove(player)
        return player

    def switch(self):
        if self.character == self.control.player:
            self.editor = Editor(self.map, self.control)
            self.control.player = self.editor
            self.temporary = self.map.sight_block
            self.map.sight_block = []
            self.map.turn()
        else:
            self.editor.remove()
            self.control.set_keymap('data/keymap.txt')
            self.control.player = self.character
            self.character.center_camera()
            self.map.sight_block = self.temporary
            self.map.turn()

    def turn(self):
        r = self.map.name + '\n'
        r += self.character.__str__() + '\n'
        r += ','.join(self.knowledge) + '\n'
        Data.write('save/player', r)
