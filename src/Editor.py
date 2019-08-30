import sys

import pygame

from src.entity.Space import Space
from src.entity.Stock import Stock
from src.game import Global
from src.game.Camera import Camera
from src.game.Group import Group
from src.game.Turn import Turn
from src.tools.Data import Data


class Editor:
    scroll = 2

    def __init__(self, loc, control):
        self.backup = Turn.update
        Turn.update = self.update
        Group.effects.append(self)
        control.set_keymap('data/editor_keymap.txt')
        self.control = control
        self.location = loc
        self.visible = 1
        self.mouse = [0, 0]
        self.tool = ToolTerrain(self.location)
        self.display_text = ''
        self.display_subtext = ''
        self.enter = 0
        self.prev_mouse = [0, 0]
        self.prev_action = None
        self.prev_command = None
        self.fog_update = True
        self.selection = None
        Stock.make('Force', Global.player.character.pos).center_camera()
        Camera.target.location.remove(Camera.target)

    def update(self):
        self.control.turn()
        if self.fog_update:
            self.location.update_fog()
            self.fog_update = False

    def remove(self):
        self.tool.cancel()
        Camera.target.remove()
        Turn.remove(self)
        Group.remove(self)
        Turn.update = self.backup

    def input(self, action, target):
        m = Camera.target.pos + target
        self.prev_mouse = m
        self.display_subtext = 'X:' + str(m.x) + ' Y:' + str(m.y)
        if action == 'idle':
            self.tool.input(0, self.location.get_tile(m))
            self.tool.last = None
        elif action == 'use':
            self.tool.input(1, self.location.get_tile(m))
        elif action == 'special':
            self.tool.input(4, self.location.get_tile(m))
        elif action == 'delete':
            self.tool.input(2, self.location.get_tile(m))
        elif action == 'prev':
            if action != self.prev_action:
                self.display_text = self.tool.cycle(-1)
        elif action == 'next':
            if action != self.prev_action:
                self.display_text = self.tool.cycle(1)
        elif action == 's_prev':
            if action != self.prev_action:
                self.display_text = self.tool.cycle(-1, specific=True)
        elif action == 's_next':
            if action != self.prev_action:
                self.display_text = self.tool.cycle(1, specific=True)
        elif action == 'up':
            Camera.target.move(0, -1, Editor.scroll, [])
            self.fog_update = True
        elif action == 'down':
            Camera.target.move(0, 1, Editor.scroll, [])
            self.fog_update = True
        elif action == 'left':
            Camera.target.move(-1, 0, Editor.scroll, [])
            self.fog_update = True
        elif action == 'right':
            Camera.target.move(1, 0, Editor.scroll, [])
            self.fog_update = True
        elif action == 'sample':
            if action != self.prev_action:
                self.tool.cancel()
                objs = self.location.get_tile(m).things
                if objs:
                    self.tool = ToolObject(self.location, 'props')
                    obj = objs.copy().pop()
                    self.tool.select(obj.name)
                    self.display_text = obj.__str__()
                else:
                    self.tool = ToolTerrain(self.location)
                    terrain = self.location.get_tile(m).terrain
                    if terrain:
                        self.tool.select(terrain.name)
        elif action == 'select':
            objs = self.location.get_tile(m).things
            if objs:
                self.display_text = 'Selected ID ' + str(objs[0].id)
                self.tool = ToolObject(self.location, 'props')
                self.tool.cancel()
                self.tool.selection = objs[0]
        elif action == 'player':
            Global.player.character.relocate(m.x, m.y)
        elif action == 'tiles':
            self.tool.cancel()
            self.tool = ToolTerrain(self.location)
            self.display_text = 'Terrain Tool'
        elif action == 'props':
            self.tool.cancel()
            self.tool = ToolObject(self.location, action)
            self.display_text = 'Props Tool'
        elif action == 'items':
            self.tool.cancel()
            self.tool = ToolObject(self.location, action)
            self.display_text = 'Items Tool'
        elif action == 'units':
            self.tool.cancel()
            self.tool = ToolObject(self.location, action)
            self.display_text = 'Units Tool'
        elif action == 'weapons':
            self.tool.cancel()
            self.tool = ToolObject(self.location, action)
            self.display_text = 'Weapons Tool'
        elif action == 'armors':
            self.tool.cancel()
            self.tool = ToolObject(self.location, action)
            self.display_text = 'Armors Tool'
        elif action == 'headgears':
            self.tool.cancel()
            self.tool = ToolObject(self.location, action)
            self.display_text = 'Headgears Tool'
        elif action == 'spells':
            self.tool.cancel()
            self.tool = ToolObject(self.location, action)
            self.display_text = 'Spells Tool'
        elif action == 'miscellaneous':
            self.tool.cancel()
            self.tool = ToolObject(self.location, action)
            self.display_text = 'Miscellaneous Tool'
        elif action == 'repeat':
            Global.main.textbox.display_text = self.prev_command
            self.command()
        elif action == 'command':
            self.command()
        elif action == 'save':
            self.tool.cancel()
            self.location.save()
            self.display_text = 'saved to ' + self.location.name
        elif action == 'quit':
            self.tool.cancel()
            pygame.quit()
            sys.exit()
        self.prev_action = action
        return 0

    def command(self):
        self.prev_command = Global.main.textbox.display_text
        params = Global.main.textbox.display_text.split(' ')
        if params[0] == 'set':
            if isinstance(self.tool, ToolObject):
                if self.tool.selection.name == 'Beacon':
                    self.tool.selection.var = params[1]
                elif self.tool.selection.name == 'Interactive':
                    self.tool.selection.argument = params[1].split(',')
                self.display_text = '[' + params[1] + '] Applied'
        elif params[0] == 'loot':
            if isinstance(self.tool, ToolObject):
                self.tool.selection.loot = params[1].split(',')
        elif params[0] == 'image':
            if isinstance(self.tool, ToolObject):
                self.tool.selection.set_form(params[1])
        elif params[0] == 'make':
            self.location.construct_map(params[1])
            Global.player.switch()
            Global.player.travel('current', Space())
            Global.player.switch()
        elif params[0] == 'background':
            self.location.header[2] = params[1]
        elif params[0] == 'camera':
            pos = params[1].split(',')
            Camera.target.relocate(int(pos[0]), int(pos[1]), force=1)
        elif params[0] == 'merchant':
            r = Stock.make('Merchant', self.location.get_tile(self.prev_mouse))
            r.var = params[1].split(',')
        elif params[0] == 'moveall':
            pos = params[1].split(',')
            self.location.tiles = {}
            self.location.record.clear()
            map_data = list(Data.process_raw(Data.read('save/' + self.location.name + '.map')))
            self.location.load_map(map_data, offset=(int(pos[0]), int(pos[1])))
        elif params[0] == 'moveobj':
            pos = params[1].split(',')
            for i in self.location.record:
                i.move(int(pos[0]), int(pos[1]), distance=9999, flag=[])
        elif params[0] == 'new':
            from src.map.Location import Location
            new = Location(params[1], ['0,[0,0,0,1],field', '', ''])
            new.save()
            Global.player.switch()
            Global.player.travel(params[1], Space())
            Global.player.switch()
        elif params[0] == 'load':
            maps = Data.get_files('save', lambda x: x.endswith('.map'))
            if params[1] + '.map' in maps:
                Global.player.switch()
                Global.player.travel(params[1], Space())
                Global.player.switch()
        elif params[0] == 'loadraw':
            Global.player.switch()
            Global.player.travel('../data/map/' + params[1], Space())
            Global.player.switch()
        elif params[0] == 'save':
            self.tool.cancel()
            self.location.name = params[1]
            self.location.save()
            self.display_text = 'saved to ' + params[1]
        Global.main.textbox.display_text = ''

    def draw(self, surface):
        if self.display_text:
            surface.blit(Global.font.render(self.display_text, 1, (255, 255, 255)), (16, 16))
            surface.blit(Global.font.render(self.display_subtext, 1, (255, 255, 255)), (500, 16))


class ToolTerrain:
    def __init__(self, loc):
        self.tile_list = Data.get_cache('tiles')
        self.text = 'dirt'
        self.location = loc
        self.tile = loc.get_tile(0)
        self.prev_tile = loc.get_tile(0).terrain
        self.current = 0
        self.last = None  # unused

    def cancel(self):
        self.tile.terrain = self.prev_tile

    def cycle(self, inc, specific=False):
        self.current += inc
        if self.current >= self.tile_list.__len__():
            self.current = 0
        elif self.current < 0:
            self.current = self.tile_list.__len__() - 1
        elif not specific and self.tile_list[self.current][0].find(' ') >= 0:
            return self.cycle(inc)
        self.select(self.tile_list[self.current][0])
        return self.text

    def select(self, text):
        self.text = text

    def enter(self, text):
        self.text = text

    def input(self, button, tile):
        text = self.text
        if not button:
            self.cancel()
        elif button == 2:
            self.tile.set_terrain('')
        self.tile = tile
        self.prev_tile = tile.terrain
        self.tile.set_terrain(text)
        if button == 1:
            self.update(self.tile.x - 1, self.tile.y)
            self.update(self.tile.x + 1, self.tile.y)
            self.update(self.tile.x, self.tile.y - 1)
            self.update(self.tile.x, self.tile.y + 1)
            self.update(self.tile.x, self.tile.y)

    def is_terrain(self, x, y, terrain):
        r = self.location.get_tile([x, y]).terrain
        if r:
            return 1 if r.name.split(' ')[0] == terrain else 0
        return 0

    def update(self, x, y):
        tile = self.location.get_tile([x, y])
        if tile.terrain:
            name_type = tile.terrain.name.split(' ')[0]
            if name_type in ['dirt', 'rock', 'bush', 'sand']:
                grid = [self.is_terrain(x, y - 1, name_type), self.is_terrain(x - 1, y, name_type),
                        self.is_terrain(x + 1, y, name_type), self.is_terrain(x, y + 1, name_type)]
                if grid in [[0, 1, 1, 1], [0, 1, 1, 0]] and tile.set_terrain(name_type + ' top'):
                    return
                elif grid in [[1, 1, 1, 0], [0, 1, 1, 0]] and tile.set_terrain(name_type + ' bottom'):
                    return
                elif grid in [[0, 1, 0, 1]] and tile.set_terrain(name_type + ' left'):
                    return
                elif grid in [[0, 0, 1, 1]] and tile.set_terrain(name_type + ' right'):
                    return
                elif grid in [[1, 1, 0, 1], [1, 1, 0, 0]] and tile.set_terrain(name_type + ' side left'):
                    return
                elif grid in [[1, 0, 1, 1], [1, 0, 1, 0]] and tile.set_terrain(name_type + ' side right'):
                    return
                elif grid in [[0, 1, 0, 0]] and tile.set_terrain(name_type + ' edge left'):
                    return
                elif grid in [[0, 0, 1, 0]] and tile.set_terrain(name_type + ' edge right'):
                    return
                elif grid in [[1, 1, 0, 0]] and tile.set_terrain(name_type + ' corner left'):
                    return
                elif grid in [[1, 0, 1, 0]] and tile.set_terrain(name_type + ' corner right'):
                    return
                else:
                    tile.set_terrain(name_type)


class ToolObject:
    def __init__(self, loc, object_type):
        self.location = loc
        self.text = 'Crate'
        self.selection = Stock.get('Crate').add()
        self.tile = loc.get_tile(0)
        self.object_list = list(Data.get_cache(object_type))
        self.current = 0
        self.last = None

    def cancel(self):
        self.selection.remove()

    def cycle(self, inc, specific=False):
        self.current += inc
        if self.current >= self.object_list.__len__():
            self.current = 0
        if self.current < 0:
            self.current = self.object_list.__len__() - 1
        self.select(self.object_list[self.current][0])
        return self.text

    def select(self, text):
        self.text = text
        self.selection.remove()
        self.selection = Stock.get(self.text)
        if self.selection:
            self.selection.add()

    def input(self, button, tile):
        if not button:
            self.selection.relocate(tile.x, tile.y)
        elif button == 1:
            self.selection.relocate(tile.x, tile.y, force=1)
            preexisting = 0
            for i in tile.things:
                if i != self.selection and i.name == self.text:
                    preexisting = 1
                    break
            if not preexisting:
                self.selection = Stock.get(self.text).add()
                self.selection.relocate(tile.x, tile.y, force=1)
        else:
            if self.last != tile:
                if tile.things:
                    for i in reversed(tile.things):
                        if i != self.selection:
                            i.remove()
                            break
                self.last = tile
