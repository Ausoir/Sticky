from src.entity.Stock import Stock
from src.game import Global
from src.game.Camera import Camera
from src.game.Turn import Turn
from src.map.Tile import Tile
from src.tools.Data import Data


class Editor:
    def __init__(self, player):
        self.backup = Turn.update
        Turn.update = self.update
        self.control = player.control
        self.visible = 1
        self.tool = ToolTerrain()
        self.display_text = 'Map'
        self.display_subtext = ''
        self.enter = 0
        self.moving = [0, 0]
        self.prev_mouse = [0, 0]
        self.prev_action = None
        self.prev_command = None
        self.selection = None
        Global.map_view.overlay.clear()
        for i in Global.world.location.population.get_all():
            if i.states.get('Invisible'):
                i.show(True)

    def update(self):
        self.control.turn()
        Camera.target.relocate(to=Camera.target.pos.get_neighbor(self.moving[0], self.moving[1], limit=True))
        for tile in Camera.target.pos.get_area(8, 6):
            tile.light = 4
        self.moving = [0, 0]
        time = Global.player.days
        Global.player.days = -1
        offset = Global.world.recenter(Camera.target.pos.x, Camera.target.pos.y)
        Global.player.days = time
        if not offset:
            Global.map_view.update_region()
            Global.map_view.update_fog()
            Global.map_view.update()
            Global.map_view.update_region_editor()
        else:
            self.tool.cancel()

    def remove(self):
        self.tool.cancel()
        Turn.update = self.backup

    def input(self, action):
        m = self.control.cursor_tile
        self.prev_mouse = m
        self.display_subtext = str(Global.world.get_tile_true_pos(m[0], m[1])) + ' / '
        self.display_subtext += str(Global.world.get_coordinates(m[0], m[1]))
        if action == 'idle':
            self.tool.input(0, Global.world.location.get_tile(m[0], m[1], limit=True))
            self.tool.last = None
        elif action == 'use':
            self.tool.input(1, Global.world.location.get_tile(m[0], m[1], limit=True))
        elif action == 'special':
            self.tool.input(4, Global.world.location.get_tile(m[0], m[1], limit=True))
        elif action == 'delete':
            self.tool.input(2, Global.world.location.get_tile(m[0], m[1], limit=True))
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
        elif action == 'fill':
            tile = Global.world.location.get_tile(m[0], m[1], limit=True)
            self.tool.fill(tile)
            Global.world.dirty = True
            self.control.clear_press()
        elif action == 'sample':
            if action != self.prev_action:
                self.tool.cancel()
                objs = Global.world.location.get_tile(m[0], m[1], limit=True).things.copy()
                highest = [None, -1]
                population = Global.world.location.population.get_all()
                for obj in objs:
                    if obj in population and obj.obstruct_type > highest[1]:
                        highest = [obj, obj.obstruct_type]
                if highest[0]:
                    self.tool = ToolObject('props')
                    self.display_text = highest[0].__str__()
                    self.tool.select(highest[0].name, data=Data.process_raw(self.display_text))
                else:
                    self.tool = ToolTerrain()
                    tile = Global.world.location.get_tile(m[0], m[1], limit=True)
                    if tile:
                        self.tool.select(tile.index)
                        self.display_text = self.tool.text
        elif action == 'select':
            objs = Global.world.location.get_tile(m[0], m[1], limit=True).things
            if objs:
                self.display_text = 'Selected ID ' + str(objs[0].id)
                self.tool = ToolObject('props')
                self.tool.cancel()
                self.tool.selection = objs[0]
        elif action == 'player':
            Global.player.character.relocate(x=m[0], y=m[1])
        elif action == 'tiles':
            self.tool.cancel()
            self.tool = ToolTerrain()
            self.display_text = 'Terrain Tool'
        elif action == 'roofs':
            self.tool.cancel()
            self.tool = ToolRoof()
            self.display_text = 'Roof Tool'
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
            Global.world.dirty = True
            self.tool.cancel()
            Global.world.save()
            self.display_text = 'saved map'
        self.prev_action = action
        if self.display_text != '':
            Global.main.monologue.set(self.display_text + ' @ ' + self.display_subtext)
            self.display_text = ''
        return 0

    def command(self):
        self.prev_command = Global.main.monologue.text.text
        params = Global.main.monologue.text.text.split(',')
        arg1 = ' '.join(params[1:])
        if params[0] == 'to':
            Global.world.travel(int(params[1]) * Global.world.CHUNK, int(params[2]) * Global.world.CHUNK)
        elif params[0] == 'set':
            if isinstance(self.tool, ToolObject):
                if self.tool.selection.name == 'Scripter':
                    script = Data.process_raw(params[1])
                    self.tool.selection.load(script)
                    self.display_text = self.tool.selection.__str__()
                    self.tool.last_data = Data.process_raw(self.display_text)
                self.display_text = '[' + params[1] + '] Applied'
        elif params[0] == 'prop':
            for tool_type in Data.registry_list:
                self.tool.cancel()
                self.tool = ToolObject(tool_type)
                for i in self.tool.object_list:
                    if i[0] == params[1]:
                        self.tool.select(i[0])
                        return
        elif params[0] == 'dest':
            self.tool.cancel()
            self.tool = ToolObject('miscellaneous')
            self.tool.select(params[1])
            to = Global.world.get_tile_true_pos(self.control.cursor_tile[0], self.control.cursor_tile[1])
            self.tool.selection.tags.set('tox', to[0])
            self.tool.selection.tags.set('toy', to[1])
        elif params[0] == 'tag':
            if isinstance(self.tool, ToolObject):
                self.tool.selection.tags.set(params[1], Data.parse(params[2])[0])
        elif params[0] == 'deltag':
            if isinstance(self.tool, ToolObject):
                self.tool.selection.tags.remove(params[1])
        elif params[0] == 'image':
            if isinstance(self.tool, ToolObject):
                self.tool.selection.set_form(arg1)
        elif params[0] == 'camera':
            pos = params[1].split(',')
            Camera.target.relocate(x=int(pos[0]), y=int(pos[1]), force=True)
        elif params[0] == 'move':
            map_data = list(Data.process_raw(Global.world.location.__str__()))
            Global.world.location.load(map_data, make=False, offset=(int(params[1]), int(params[2])))
        elif params[0] == 'fill':
            for y in range(Global.world.location.get_height()):
                for x in range(Global.world.location.get_width()):
                    Global.world.location.get_tile(x, y).set_terrain(params[1])
            Global.world.location.process_terrain()
        elif params[0] == 'resize':
            Global.world.location.resize(int(params[1]), int(params[2]))
        elif params[0] == 'script':
            Global.player.switch()
            from src.game.Script import Script
            Script.execute_code(params[1])
        elif params[0] == 'scriptraw':
            Global.player.switch()
            from src.game.Script import Script
            Script.execute_string(Data.process_raw('1,[],[' + params[1] + '],[]'))
        elif params[0] == 'save':
            self.tool.cancel()
            Global.world.save()
            Global.player.save()
            self.display_text = 'saved to ' + arg1
        elif params[0] == 'time':
            Global.player.days = int(params[1])
            Global.player.sleep(0)


class Tool:
    def cancel(self):
        pass

    def cycle(self, inc):
        pass

    def fill(self, tile):
        pass


class ToolTerrain(Tool):
    def __init__(self):
        self.terrain = 0
        self.text = 'Dirt'
        self.tile = Global.world.location.get_tile(0, 0)
        self.prev_tile = self.tile

    def cycle(self, inc):
        self.terrain += inc
        if self.terrain >= Tile.DATA.__len__():
            self.terrain = 0
        elif self.terrain < 0:
            self.terrain = Tile.DATA.__len__() - 1
        self.select(self.terrain)
        return self.text

    def select(self, terrain, data=None):
        self.terrain = terrain
        self.text = Tile.DATA[self.terrain][1]

    def input(self, button, tile):
        if button == 4:
            Global.world.dirty = True
            for y in range(-2, 3):
                for x in range(-2, 3):
                    neighbor = tile.get_neighbor(x, y)
                    if neighbor:
                        self.input(1, neighbor)
        elif button == 2:
            Global.world.dirty = True
            self.tile.set_terrain(self.prev_tile.get_icon())
            self.tile.update_update_shader()
        elif button == 1:
            if tile != self.tile:
                Global.world.dirty = True
                self.tile = tile
                self.prev_tile = self.tile
                self.tile.set_index(self.terrain)
                self.tile.connect_connect()
                self.tile.update_update_shader()

    def fill(self, tile):
        self.fill_recurse(tile, tile.index)
        Global.world.location.process_terrain()

    def fill_recurse(self, tile, target):
        if tile and tile.index != self.terrain and tile.index == target and tile.is_seen():
            tile.set_index(self.terrain)
            self.fill_recurse(tile.get_neighbor(1, 0), target)
            self.fill_recurse(tile.get_neighbor(-1, 0), target)
            self.fill_recurse(tile.get_neighbor(0, 1), target)
            self.fill_recurse(tile.get_neighbor(0, -1), target)


class ToolRoof(Tool):
    def input(self, button, tile):
        Global.world.dirty = True
        if button == 4:
            for y in range(-2, 3):
                for x in range(-2, 3):
                    neighbor = tile.get_neighbor(x, y)
                    if neighbor:
                        self.input(1, neighbor)
        elif button == 1:
            tile.roof = 1
        elif button == 2:
            tile.roof = 0

    def fill(self, tile):
        self.fill_recurse(tile, tile.roof)
        Global.world.location.process_terrain()

    def fill_recurse(self, tile, target):
        if tile and tile.roof == target and tile.is_seen():
            if tile.roof == 1:
                tile.roof = 0
            else:
                tile.roof = 1
            self.fill_recurse(tile.get_neighbor(1, 0), target)
            self.fill_recurse(tile.get_neighbor(-1, 0), target)
            self.fill_recurse(tile.get_neighbor(0, 1), target)
            self.fill_recurse(tile.get_neighbor(0, -1), target)


class ToolObject(Tool):
    def __init__(self, object_type):
        self.text = 'Door'
        self.selection = Stock.get('Door').add()
        self.selection.is_save = False
        self.tile = Global.world.location.get_tile(0, 0)
        self.object_list = list(Data.process_raw(Data.read('data/raw/' + object_type + '.txt')))
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
        self.selection = Stock.get(self.text, data=data)
        if self.selection:
            self.selection.relocate(x=Global.player.control.cursor_tile[0], y=Global.player.control.cursor_tile[1])
            self.selection.add()
            self.selection.is_save = False

    def input(self, button, tile):
        if not button:
            self.selection.relocate(to=tile)
        elif button == 1:
            self.selection.is_save = True
            self.selection.relocate(to=tile, force=1)
            preexisting = 0
            for i in tile.things:
                if i != self.selection and i.name == self.text:
                    preexisting = 1
                    break
            if not preexisting:
                self.selection = Stock.get(self.text, self.last_data)
                if not self.selection:
                    self.selection = Stock.get('Crate')
                self.selection.add()
                self.selection.relocate(to=tile, force=1)
        else:
            if self.last != tile:
                if tile.things:
                    for i in reversed(tile.things):
                        if i != self.selection:
                            i.remove()
                            break
                self.last = tile
