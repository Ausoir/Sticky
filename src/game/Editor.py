import sys

from src.entity.Space import Space
from src.entity.Stock import Stock
from src.game import Global
from src.game.Camera import Camera
from src.game.Turn import Turn
from src.map.Tile import Tile
from src.tools.Data import Data


class Editor:
    def __init__(self, control):
        self.backup = Turn.update
        Turn.update = self.update
        Global.draw_group.other.append(self)
        control.set_keymap('editor_keymap.txt')
        self.control = control
        self.visible = 1
        self.tool = ToolTerrain()
        self.display_text = Global.land.name
        self.display_subtext = ''
        self.enter = 0
        self.moving = [0, 0]
        self.prev_mouse = [0, 0]
        self.prev_action = None
        self.prev_command = None
        self.selection = None
        center = Stock.make('Force', Global.player.character.pos)
        center.center_camera()
        Global.land.population.remove(center)
        Global.land.population.remove(Camera.target)
        Global.overlay.fade.remove_batch()

    def update(self):
        self.control.turn()
        Camera.target.move(self.moving[0], self.moving[1], 1, flag=[])
        Global.map_view.update_region()
        Global.map_view.update_fog()
        self.moving = [0, 0]

    def remove(self):
        self.tool.cancel()
        Camera.target.remove()
        Turn.update = self.backup

    def input(self, action):
        m = self.control.cursor_tile
        self.prev_mouse = m
        self.display_subtext = 'X:' + str(m[0]) + ' Y:' + str(m[1])
        if action == 'idle':
            self.tool.input(0, Global.land.get_tile(m[0], m[1], limit=True))
            self.tool.last = None
        elif action == 'use':
            self.tool.input(1, Global.land.get_tile(m[0], m[1], limit=True))
        elif action == 'special':
            self.tool.input(4, Global.land.get_tile(m[0], m[1], limit=True))
        elif action == 'delete':
            self.tool.input(2, Global.land.get_tile(m[0], m[1], limit=True))
        elif action == 'prev':
            if action != self.prev_action:
                self.display_text = self.tool.cycle(-1)
        elif action == 'next':
            if action != self.prev_action:
                self.display_text = self.tool.cycle(1)
        elif action == 's_prev':
            if action != self.prev_action:
                self.display_text = self.tool.cycle(-10)
        elif action == 's_next':
            if action != self.prev_action:
                self.display_text = self.tool.cycle(10)
        elif action == 'up':
            self.moving = [0, -1]
        elif action == 'down':
            self.moving = [0, 1]
        elif action == 'left':
            self.moving = [-1, 0]
        elif action == 'right':
            self.moving = [1, 0]
        elif action == 'sample':
            if action != self.prev_action:
                self.tool.cancel()
                objs = Global.land.get_tile(m[0], m[1], limit=True).things.copy()
                if objs:
                    self.tool = ToolObject('props')
                    obj = objs.pop()
                    while objs and obj not in Global.land.population.get_all():
                        obj = objs.pop()
                    self.display_text = obj.__str__()
                    self.tool.select(obj.name, data=Data.process_raw(self.display_text))
                else:
                    self.tool = ToolTerrain()
                    tile = Global.land.get_tile(m[0], m[1], limit=True)
                    if tile:
                        self.tool.select(tile.terrain)
                        self.display_text = self.tool.text
        elif action == 'select':
            objs = Global.land.get_tile(m[0], m[1], limit=True).things
            if objs:
                self.display_text = 'Selected ID ' + str(objs[0].id)
                self.tool = ToolObject('props')
                self.tool.cancel()
                self.tool.selection = objs[0]
        elif action == 'player':
            Global.player.character.relocate(m[0], m[1])
        elif action == 'tiles':
            self.tool.cancel()
            self.tool = ToolTerrain()
            self.display_text = 'Terrain Tool'
        elif action == 'props':
            self.tool.cancel()
            self.tool = ToolObject(action)
            self.display_text = 'Props Tool'
        elif action == 'items':
            self.tool.cancel()
            self.tool = ToolObject(action)
            self.display_text = 'Items Tool'
        elif action == 'units':
            self.tool.cancel()
            self.tool = ToolObject(action)
            self.display_text = 'Units Tool'
        elif action == 'weapons':
            self.tool.cancel()
            self.tool = ToolObject(action)
            self.display_text = 'Weapons Tool'
        elif action == 'armors':
            self.tool.cancel()
            self.tool = ToolObject(action)
            self.display_text = 'Armors Tool'
        elif action == 'headgears':
            self.tool.cancel()
            self.tool = ToolObject(action)
            self.display_text = 'Headgears Tool'
        elif action == 'spells':
            self.tool.cancel()
            self.tool = ToolObject(action)
            self.display_text = 'Spells Tool'
        elif action == 'miscellaneous':
            self.tool.cancel()
            self.tool = ToolObject(action)
            self.display_text = 'Miscellaneous Tool'
        elif action == 'repeat':
            self.display_text = self.prev_command
            self.command()
        elif action == 'command':
            self.command()
        elif action == 'save':
            self.tool.cancel()
            Global.land.save()
            self.display_text = 'saved to ' + Global.land.name
        elif action == 'quit':
            self.tool.cancel()
            sys.exit()
        self.prev_action = action
        if self.display_text != '':
            Global.main.monologue.set(self.display_text + ' @ ' + self.display_subtext)
            self.display_text = ''
        return 0

    def command(self):
        self.prev_command = Global.main.monologue.label.text
        params = Global.main.monologue.label.text.split(' ')
        arg1 = ' '.join(params[1:])
        if params[0] == 'set':
            if isinstance(self.tool, ToolObject):
                if self.tool.selection.name == 'Scripter':
                    script = Data.process_raw(params[1])
                    self.tool.selection.condition = script[0]
                    self.tool.selection.mechanism = script[1]
                    self.display_text = self.tool.selection.__str__()
                    self.tool.last_data = Data.process_raw(self.display_text)
                self.display_text = '[' + params[1] + '] Applied'
        elif params[0] == 'setc':
            from src.entity.Other import Scripter
            if isinstance(self.tool, ToolObject):
                if isinstance(self.tool.selection, Scripter):
                    self.tool.selection.condition = Data.process_raw(arg1)
                    self.display_text = self.tool.selection.__str__()
                    self.tool.last_data = Data.process_raw(self.display_text)
            self.display_text = 'Applied condition'
        elif params[0] == 'setm':
            from src.entity.Other import Scripter
            if isinstance(self.tool, ToolObject):
                if isinstance(self.tool.selection, Scripter):
                    self.tool.selection.mechanism = Data.process_raw(arg1)
                    self.display_text = self.tool.selection.__str__()
                    self.tool.last_data = Data.process_raw(self.display_text)
            self.display_text = 'Applied mechanics'
        elif params[0] == 'setc@':
            from src.entity.Other import Scripter
            if isinstance(self.tool, ToolObject):
                if isinstance(self.tool.selection, Scripter):
                    self.tool.selection.condition[int(params[1])] = Data.process_raw(' '.join(params[2:]))
                    self.display_text = self.tool.selection.__str__()
                    self.tool.last_data = Data.process_raw(self.display_text)
            self.display_text = '[' + params[2] + '] Applied'
        elif params[0] == 'setm@':
            from src.entity.Other import Scripter
            if isinstance(self.tool, ToolObject):
                if isinstance(self.tool.selection, Scripter):
                    self.tool.selection.mechanism[int(params[1])] = Data.process_raw(' '.join(params[2:]))
                    self.display_text = self.tool.selection.__str__()
                    self.tool.last_data = Data.process_raw(self.display_text)
            self.display_text = '[' + params[2] + '] Applied'
        elif params[0] == 'addc':
            from src.entity.Other import Scripter
            if isinstance(self.tool, ToolObject):
                if isinstance(self.tool.selection, Scripter):
                    self.tool.selection.condition.append(Data.process_raw(arg1))
                    self.display_text = self.tool.selection.__str__()
                    self.tool.last_data = Data.process_raw(self.display_text)
        elif params[0] == 'addm':
            from src.entity.Other import Scripter
            if isinstance(self.tool, ToolObject):
                if isinstance(self.tool.selection, Scripter):
                    self.tool.selection.mechanism.append(Data.process_raw(arg1))
                    self.display_text = self.tool.selection.__str__()
                    self.tool.last_data = Data.process_raw(self.display_text)
        elif params[0] == 'loot':
            if isinstance(self.tool, ToolObject):
                self.tool.selection.loot = arg1.split(',')
        elif params[0] == 'image':
            if isinstance(self.tool, ToolObject):
                self.tool.selection.set_form(arg1)
        elif params[0] == 'make':
            from src.map.Location import Location
            from src.entity.Other import Scripter
            r = Location(params[2], list(Data.process_raw(Data.read('data/map/' + params[1] + '.map'))))
            r.save()
            Global.player.switch()
            Global.player.travel(params[2], Space())
            Global.player.switch()
        elif params[0] == 'create':
            self.input('props')
            self.tool.select('Force', data=Data.parse('#-1,[0,0],' + arg1))
        elif params[0] == 'background':
            Global.land.header[2] = arg1
        elif params[0] == 'camera':
            pos = params[1].split(',')
            Camera.target.relocate(int(pos[0]), int(pos[1]), force=1)
        elif params[0] == 'merchant':
            r = Stock.make('Merchant', Global.land.get_tile(self.prev_mouse[0], self.prev_mouse[1]))
            r.var = params[1].split(',')
        elif params[0] == 'moveall':
            pos = params[1].split(',')
            Global.land.tiles = {}
            Global.land.record.clear()
            map_data = list(Data.process_raw(Data.read('save/' + Global.land.name + '.map')))
            Global.land.load_map(map_data, offset=(int(pos[0]), int(pos[1])))
        elif params[0] == 'moveobj':
            pos = params[1].split(',')
            for i in Global.land.record:
                i.move(int(pos[0]), int(pos[1]), distance=9999, flag=[])
        elif params[0] == 'new':
            from src.map.Location import Location
            new = Location(params[1], Data.process_raw('0,[0,0,0,1],field\n\n'))
            new.save()
            Global.player.switch()
            Global.player.travel(params[1], Space())
            Global.player.switch()
        elif params[0] == 'load':
            maps = Data.get_files('save', lambda x: x.endswith('.map'))
            if arg1 + '.map' in maps:
                Global.player.switch()
                Global.player.travel(arg1, Space())
                Global.player.switch()
        elif params[0] == 'loadraw':
            if Data.is_file('data/map/' + arg1 + '.map'):
                Global.player.switch()
                Global.player.travel('../data/map/' + arg1, Space())
                Global.player.switch()
        elif params[0] == 'save':
            self.tool.cancel()
            Global.land.name = arg1
            Global.land.save()
            self.display_text = 'saved to ' + arg1
        elif params[0] == 'time':
            Global.player.days = int(params[1])
            Global.player.sleep(0)


class ToolTerrain:
    def __init__(self):
        self.terrain = '.'
        self.text = 'Dirt'
        self.tile = Global.land.get_tile(0, 0)
        self.prev_tile = self.tile
        self.current = 0

    def cancel(self):
        pass

    def cycle(self, inc):
        self.current += inc
        if self.current >= Tile.DICTIONARY.__len__():
            self.current = 0
        elif self.current < 0:
            self.current = Tile.DICTIONARY.__len__() - 1
        self.select(list(Tile.DICTIONARY)[self.current])
        return self.text

    def select(self, terrain, data=None):
        self.terrain = terrain
        self.text = Tile.DICTIONARY[self.terrain][0]

    def input(self, button, tile):
        if button == 2:
            self.tile.set_terrain(self.prev_tile.terrain)
        elif button == 1:
            if tile != self.tile:
                self.tile = tile
                self.prev_tile = self.tile
                self.tile.set_terrain(self.terrain)
                from src.tools import Direction
                for i in Direction.coord.values():
                    neighbor = self.tile.get_neighbor(i[0], i[1])
                    if neighbor:
                        neighbor.connect()
                self.tile.connect()


class ToolObject:
    def __init__(self, object_type):
        self.text = 'Door'
        self.selection = Stock.get(Global.land, 'Door').add()
        self.tile = Global.land.get_tile(0, 0)
        self.object_list = list(Data.process_raw(Data.read('raw/' + object_type + '.txt')))
        self.current = 0
        self.last_data = None
        self.last = None
        self.select(self.object_list[self.current][0])

    def cancel(self):
        self.selection.remove()

    def cycle(self, inc):
        self.current += inc
        if self.current >= self.object_list.__len__():
            self.current = 0
        if self.current < 0:
            self.current = self.object_list.__len__() - 1
        self.select(self.object_list[self.current][0])
        return self.text

    def select(self, text, data=None):
        self.text = text
        self.last_data = data
        self.selection.remove()
        self.selection = Stock.get(Global.land, self.text, data=data)
        if self.selection:
            self.selection.relocate(Global.player.control.cursor_tile[0], Global.player.control.cursor_tile[1])
            self.selection.add()

    def input(self, button, tile):
        if not button:
            self.selection.relocate(tile.x, tile.y)
        elif button == 1:
            self.selection.relocate(tile.x, tile.y, force=1)
            preexisting = 0
            for i in tile.things:
                if i != self.selection and i.name == self.text and (not self.last_data or i.id == self.last_data[0]):
                    preexisting = 1
                    break
            if not preexisting:
                self.selection = Stock.get(Global.land, self.text, self.last_data)
                if not self.selection:
                    self.selection = Stock.get(Global.land, 'Crate')
                self.selection.add()
                self.selection.relocate(tile.x, tile.y, force=1)
        else:
            if self.last != tile:
                if tile.things:
                    for i in reversed(tile.things):
                        if i != self.selection:
                            i.remove()
                            break
                self.last = tile
