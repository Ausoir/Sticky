from src.Editor import Editor
from src.game.Camera import Camera
from src.game.Turn import Turn
from src.map.Location import Location
from src.tools.Data import Data


class World:
    def __init__(self):
        Turn.add(self)
        self.control = None
        data = Data.process_raw(Data.read('save/player'))
        if not data:
            data = Data.process_raw(Data.read('save/template'))
        self.map = Location(data[0])
        self.player = self.load_player(self.map, data[1])
        self.delay = 0
        self.editor = None

    def load_player(self, loc, data):
        from src.entity.unit.Humanoid import Humanoid
        from src.interface.Menu import Menu
        from src.interface.Control import Control
        from src.game.Group import Group
        player = Humanoid('unit/Man', 0, loc)
        self.control = Control(Menu(player), player)
        Camera.target = player.animation_move_from
        Group.interface.append(self.control)
        player.durability = 8
        player.load(data)
        player.add()
        loc.record.remove(player)
        return player

    def switch(self):
        if self.player == self.control.player:
            self.editor = Editor(self.map, self.control)
        else:
            self.editor.remove()
            self.control.set_keymap('data/keymap.txt')
            self.control.player = self.player
            Camera.target = self.player.animation_move_from

    def turn(self):
        r = self.map.name + '\n'
        r += self.player.__str__() + '\n'
        Data.write('save/player', r)
