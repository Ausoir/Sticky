from src.Editor import Editor
from src.game import Global
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
        data = Data.process_raw(Data.read('save/player.char'))
        if not data:
            data = Data.process_raw(Data.read('save/template'))
        map_data = list(Data.process_raw(Data.read('save/' + data[0][0] + '.map')))
        self.map = Location(data[0][0], map_data)
        self.background = None
        self.days = data[1][0]
        self.experience = data[1][1]
        self.sleep(0)
        self.character = self.load_player(self.map, data[2])
        self.editor = None
        self.knowledge = data[3]
        self.temporary = None
        self.turn()

    def load_player(self, loc, data):
        from src.entity.unit.Humanoid import Humanoid
        from src.interface.MenuAll import MenuAll
        from src.interface.Control import Control
        player = Humanoid(loc)
        Global.menu = MenuAll(player)
        self.control = Control(player)
        player.center_camera()
        player.durability = 8
        player.load(data)
        player.add()
        player.delay = 4
        loc.record.remove(player)
        return player

    def sleep(self, time):
        self.days += time
        if self.days % 2 == 0:
            self.background = Data.run_cache('data/image/background/desert')
        else:
            self.background = Data.run_cache('data/image/background/desert_night')

    def travel(self, to_map, to_pos):
        self.character.location.save()
        self.character.action.set('idle')
        self.character.form.set('interact')
        self.character.relocate(to_pos.x, to_pos.y, force=1)
        Global.main.player.map.name = to_map
        Global.main.player.turn()
        Global.main.player = Player()
        Global.main.resize(Global.DISPLAY[0], Global.DISPLAY[1])

    def switch(self):
        if self.character == self.control.player:
            self.editor = Editor(self.map, self.control)
            self.control.player = self.editor
            self.temporary = self.map.sight_block
            self.map.sight_block = []
            self.map.save()
        else:
            self.editor.remove()
            self.control.set_keymap('data/keymap.txt')
            self.control.player = self.character
            self.character.center_camera()
            self.map.sight_block = self.temporary
            self.map.save()

    def turn(self):
        r = self.map.name + '\n'
        r += str(self.days) + ',[' + ','.join(str(x) for x in self.experience) + ']\n'
        r += self.character.__str__() + '\n'
        r += ','.join(self.knowledge) + '\n'
        Data.write('save/player.char', r)
