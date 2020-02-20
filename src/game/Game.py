from src.game.Editor import Editor
from src.game import Global
from src.game.Turn import Turn
from src.map.Location import Location
from src.map.Tile import Tile
from src.entity.unit.Inventory import Inventory
from src.tools.Data import Data
from src.tools.Dialog import Dialog


class Game:
    def __init__(self):
        Turn.add(self.turn)
        from src.interface.Control import Control
        self.control = Control()
        data = Data.process_raw(Data.read('../save/player.char'))
        if not data:
            data = Data.process_raw(Data.read('map/template.char'))
        map_data = list(Data.process_raw(Data.read('../save/' + data[0][0] + '.map')))
        Global.land = Location(data[0][0], map_data)
        from src.entity.Stock import Stock
        self.character = None
        self.set_player(Stock.get(Global.land, data[2][2], data=data[2]).add())
        self.dead = 0
        self.days = data[1][0]
        Turn.frame = data[1][1]
        self.depart = data[1][2]
        self.editor = None
        self.editor_mode = False
        self.temporary = None
        self.set_ability(self.character.tags.get('talent'))
        self.inventory = Inventory(self.character)
        self.turn()
        self.sleep(0)

    def set_player(self, player):
        player.tags.remove('ai')
        self.control.player = player
        player.center_camera()
        player.action.delay = 4
        player.save = False
        self.character = player
        return player

    def is_daytime(self):
        return 5 < self.days % 24 < 18

    def set_ability(self, passive):
        if passive == 'Brawler':
            self.character.fist.damage += 1

    def sleep(self, time):
        if time > 0:
            if self.character.tags.get('full') <= 0:
                nutrition = self.eat()
                if nutrition:
                    self.character.tags.increment('full', nutrition)
                    self.days += time
                    if Global.player:
                        self.character.tags.increment('full', -time)
                        for i in self.character.get_possessions():
                            i.on_sleep(time)
                        for i in self.character.states.buffs:
                            i.trigger(['time', time])
                else:
                    return False
        Global.overlay.blackout()
        self.set_darkness()
        return True

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
        self.depart = Global.land.name
        if Global.land.name != to_map:
            Global.land.save()
        self.character.action.set('idle')
        self.character.form.set_state('interact')
        self.character.relocate(to_pos.x, to_pos.y, force=1)
        if to_map == 'home':
            to_map = Global.player.character.tags.get('home')
        Global.land.name = to_map
        Global.player.turn()
        Turn.init()
        Global.player = Game()
        Global.main.resize(Global.DISPLAY[0], Global.DISPLAY[1])

    def switch(self):
        if not self.editor_mode:
            Global.menu.display(-1)
            self.editor_mode = True
            self.editor = Editor(self.control)
            self.control.player = self.editor
            self.temporary = Global.map_view.sight_block
            Global.map_view.sight_block = []
            Global.land.save()
        else:
            self.editor_mode = False
            self.editor.remove()
            self.control.set_keymap('keymap.txt')
            self.control.player = self.character
            self.character.center_camera()
            Global.map_view.sight_block = self.temporary
            Global.land.save()

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
                    text = Dialog.get('insurerevive', [Dialog.date(coma)])
                    Global.menu.get_message(text + '\n' + Dialog.get('sign', [death]))(None)
                else:
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
            r = Global.land.name + '\n'
            r += str(self.days) + ',' + str(Turn.frame) + ',' + str(self.depart) + '\n'
            r += self.character.__str__() + '\n'
            Data.write('../save/player.char', r)

    def is_safe(self):
        for unit in Global.land.population.bad:
            if unit.pilot.var == self.character:
                Global.main.monologue.set(Dialog.get('!safe'))
                return False
        return True

    def eat(self):
        items = self.character.get_accessibles()
        from src.entity.Other import Food
        for i in items:
            if isinstance(i, Food):
                if i.nutrition[1] > 0:
                    nutrition = i.nutrition[1]
                    i.decay(1)
                    return nutrition
        Global.main.monologue.set(Dialog.get('!eat'))

    def pay(self, amount):
        if self.character.tags.require('money', amount):
            return True
        Global.main.monologue.set(Dialog.get('!pay'))

    def is_bright(self):
        if self.is_daytime() or self.character.pos.light > 1:
            return True
        Global.main.monologue.set(Dialog.get('!bright'))
