from src.entity.Particle import Particle
from src.entity.Prop import Prop
from src.entity.unit.Unit import Unit
from src.entity.unit.item.Item import Item
from src.game import Global
from src.game.Script import Script
from src.map.Tile import Tile
from src.tools.Data import Data
from src.tools.Dialog import Dialog


class Scripter(Prop):
    def __init__(self, location):
        super().__init__(location)
        self.script = Script()

    def __str__(self):
        return super().__str__() + ',[' + self.script.__str__() + ']'

    def load(self, arg):
        index = super().load(arg)
        self.script.load(arg[index])
        return index + 1

    def add(self):
        super().add()
        Script.var['host'] = self
        if self.tags.get('trigger') == 'load':
            self.script.run()

    def set_row(self, row):
        self.form.z = 800

    def on_sleep(self, time):
        super().on_sleep(time)
        if time > 0 and self.tags.get('trigger') == 'time':
            self.script.run()

    def turn(self):
        super().turn()
        if self.tags.get('trigger') == 'always':
            Script.var['host'] = self
            self.script.run()


class Force(Prop):
    def __init__(self, location):
        super().__init__(location)
        self.obstruct_type = 0
        self.save = False

    def add(self):
        self.removed = 0
        self.relocate(to=self.pos, force=True)
        return self

    def remove(self):
        self.removed = 1
        del self

    def relocate(self, to=None, x=None, y=None, force=0):
        if to is None:
            to = self.location.get_tile(x, y, limit=True)
        self.pos = to
        self.update_vec()


class Door(Prop):
    def __init__(self, location):
        super().__init__(location)
        self.form1 = None
        self.form2 = None
        self.orig_obstruct_type = None

    def load(self, arg):
        index = super().load(arg)
        self.form1 = self.form
        self.form2 = Data.get_form(self.tags.get('alt'))
        self.form2.show(True)
        self.orig_obstruct_type = self.obstruct_type
        return index

    def set_row(self, row):
        self.form.z = row * 20 + 100
        self.form1.z = self.form.z
        self.form2.z = self.form.z

    def turn(self):
        super().turn()
        if self.form.inbound:
            if len(self.pos.things) > 1:
                if self.obstruct_type != Tile.COLLIDE_ITEM:
                    self.form2.show(True)
                    self.form = self.form2
                    self.form1.show(False)
                    self.obstruct_type = Tile.COLLIDE_ITEM
            else:
                if self.obstruct_type != self.orig_obstruct_type:
                    self.form1.show(True)
                    self.form = self.form1
                    self.form2.show(False)
                    self.obstruct_type = self.orig_obstruct_type


class Container(Prop):
    def __init__(self, location):
        super().__init__(location)
        from src.entity.unit.Inventory import Inventory
        self.inventory = Inventory(self)

    def __str__(self):
        return super().__str__() + ',' + self.inventory.__str__()

    def load(self, arg):
        index = super().load(arg)
        self.inventory.load(arg[index])
        return index + 1

    def is_vacant(self, weight):
        return self.tags.get('space', 0) >= self.inventory.get_weight() + weight


class Specie(Item):
    def load(self, arg):
        r = super().load(arg)
        if self.form_name is None:
            cell_coord = Global.world.get_current_chunk(self.pos.x, self.pos.y)
            seed = int(Global.world.map_biome.get_noise(cell_coord[0], cell_coord[1]) * 12500)
            self.tags.set('seed', seed)
            cue = Data.get_line('raw.txt', self.name.lower())[1]
            arg = cue[seed % len(cue)]
            self.set_form(arg)
            luminance = seed % 240
            if luminance < 3:
                self.states.add('Glow', -1, luminance + 1)
            fuel = seed % 64
            if fuel <= 8:
                self.tags.set('fuel', fuel)
        return r

    def set_form(self, arg):
        if arg != 0:
            super().set_form(arg)

    def get_display_name(self):
        cue = Data.get_line('raw.txt', 'cue')[1]
        return cue[self.get_seed() % len(cue)].title() + ' ' + self.name

    def get_description(self):
        r = super().get_description()
        if Global.player.character.get_skill('alchemy'):
            r += '\n' + Dialog.get('Density') + ': ' + str(self.get_seed() % 100)
        return r

    def on_unwield(self):
        super().on_unwield()
        if Global.player.character.get_skill('herbalism'):
            self.tags.set('$', 1)

    def on_sleep(self, time):
        if time >= 12:
            if self.pos.get_icon() == '*':
                from src.entity.Stock import Stock
                for i in Global.cardinal_coord:
                    tile = self.pos.get_neighbor(i[0], i[1])
                    if tile.get_icon() == '*' and not tile.things:
                        clone = Stock.get(self.location, self.name, data=Data.parse(self.__str__()))
                        clone.pos = tile
                        clone.add()


class Marker(Prop):
    @staticmethod
    def check_connection(marked_tile):
        if marked_tile:
            for tile_marker in marked_tile.things:
                if tile_marker.name == 'Marker':
                    return True
        return False

    def connect_connect(self):
        for i in Global.cardinal_coord:
            tile = self.pos.get_neighbor(i[0], i[1])
            for thing in tile.things:
                if isinstance(thing, Marker):
                    thing.connect()
        self.connect()

    def connect(self):
        r = False
        connection, direction = self.pos.get_connection(self.pos, Marker.check_connection)
        forms = self.tags.get('forms').split('&')
        if connection > 1:
            connection -= 2
        elif connection == 1:
            connection = 0
        else:
            connection = 3
        if forms[connection] != self.form_name:
            self.set_form(forms[connection])
            self.form.show(True)
            r = True
        self.tags.set('dir', direction)
        self.tags.set('way', connection)
        world_seed = Global.player.tags.get('seed') + ord(self.pos.get_icon())
        one_way = int(connection <= 1)
        if world_seed % 4 == connection:
            self.tags.set('ohm', -1)
        elif (world_seed + one_way) % 2:
            self.tags.set('ohm', 1)
        else:
            self.tags.set('ohm', 0)
        self.face(direction)
        return r

    def trigger(self):
        signal = False
        for i in self.pos.things.copy():
            if isinstance(i, Marker) and i != self:
                i.remove()
                signal = True
        if signal:
            self.remove()
        self.connect_connect()

    def get_routes(self):
        r = []
        way = self.tags.get('way')
        if way == 0:
            r.append(self.pos.get_cardinal(self.direction))
            r.append(self.pos.get_cardinal(self.direction + 2))
        elif way == 1:
            r.append(self.pos.get_cardinal(self.direction))
            r.append(self.pos.get_cardinal(self.direction - 1))
        elif way == 2:
            r.append(self.pos.get_cardinal(self.direction + 2))
            r.append(self.pos.get_cardinal(self.direction - 1))
            r.append(self.pos.get_cardinal(self.direction + 1))
        elif way == 3:
            r.append(self.pos.get_cardinal(self.direction))
            r.append(self.pos.get_cardinal(self.direction - 1))
            r.append(self.pos.get_cardinal(self.direction + 1))
            r.append(self.pos.get_cardinal(self.direction + 2))
        return r

    def turn(self):
        glow = self.states.get('Glow')
        if not glow:
            if self.pos.light_source > 0:
                self.states.add('Glow', 7, 4)
        elif glow.duration == 1:
            routes = self.get_routes()
            for tile in routes:
                interrupt = True
                for thing in tile.things.copy():
                    if isinstance(thing, Marker) and len(tile.things) == 1:
                        if len(thing.states.buffs) == 0:
                            Particle.make('fire', tile)
                            thing.states.add('Glow', 1, glow.var - thing.tags.get('ohm', 0))
                        elif glow.var >= 8:
                            thing_glow = thing.states.get('Glow')
                            if thing_glow:
                                power = abs(thing_glow.var - glow.var)
                                self.tags.set('fuel', power)
                                self.states.add('Burn', 12)
                                Particle.make('portal', self.pos)
                                self.cast(glow.var, power + 1)
                                thing.remove()
                                self.remove()
                        interrupt = False
                if interrupt:
                    self.states.add('Burn', 12)
        super().turn()

    def cast(self, intensity, collision):
        data = Data.get_line('raw.txt', 'portals')[1]
        from src.entity.unit.item.Spell import Spell
        category = data[max(0, len(data) - collision)]
        seed = self.get_seed() * self.tags.get('way', 0)
        Spell.get(category[seed % len(category)], power=intensity * 6).cast_on(self.pos)
        # print('spell ' + category[seed % len(category)] + ' intensity ' + str(intensity * 6))


class Food(Item):
    def load(self, arg):
        index = super().load(arg)
        time = self.tags.get('time', 0)
        if time < 0:
            self.tags.set('time', Global.player.days + -time)
        return index + 1

    def get_value(self):
        expire = self.get_expiration()
        if expire <= 0:
            return 0
        return super().get_value()

    def describe(self):
        r = super().describe()
        r += '\n' + Dialog.get('Nutrition') + ': ' + str(self.tags.get('hunger', 0)) + '%'
        expire = self.get_expiration()
        if expire:
            r += '\n' + Dialog.get('food_expire', [Dialog.hours(expire)])
        else:
            r += '\n' + Dialog.get('food_expired')
        return r

    def get_expiration(self):
        left = max(0, self.tags.get('time', 0) - Global.player.days)
        return left

    def use(self):
        if self.get_expiration():
            hunger = self.host.tags.get('hunger', 0)
            if hunger >= self.tags.get('hunger', 0):
                self.host.action.act('eat', 8)
                self.host.action.on_finish = self.eat
            else:
                Global.main.monologue.set(Dialog.get('!hungry'))
        else:
            Global.main.monologue.set(Dialog.get('!expire'))
            self.die()

    def eat(self):
        for i in self.states.buffs:
            self.host.states.add(i.name, i.duration, i.var)
        nutrition = -(self.tags.get('hunger', 0) + self.host.get_skill('asceticism', stacks=True))
        self.location.sound.register(self.pos, 0, file='eat')
        self.host.tags.increment('hunger', nutrition)
        self.decay(1)
        return nutrition


class Corpse(Prop):
    def __init__(self, location):
        super().__init__(location)
        self.direction = 1
        self.obstruct_type = Tile.COLLIDE_ITEM
        self.form = None
        self.has_host = False

    def load(self, arg):
        r = super().load(arg)
        self.form = Data.get_form(self.form_name)
        return r

    def invalid(self, state):
        pass

    def set_form(self, arg):
        self.form_name = arg

    def set_row(self, row):
        if self.has_host:
            self.form.set_row(row)
        else:
            super().set_row(row)

    def set(self, form):
        self.has_host = True
        self.form = form
        dead = 'dead'
        self.form.randomize_clip(dead, 8)
        self.form.set_state(dead)
        self.form.set_state = self.invalid
        self.show(True)
        return self

    def update(self):
        super().update()
        if self.has_host:
            from src.game.Camera import Camera
            bound_x, bound_y = Camera.get_relative_pos(self.vec.x, self.vec.y)
            self.form.place(bound_x, bound_y)

    def hit(self, damage, hitter=None):
        r = super().hit(damage, hitter)
        if r != 2:
            if self.has_host:
                self.form.randomize_once(4)
        return r

    def die(self):
        self.remove()


class Manual(Item):
    def __init__(self, location):
        super().__init__(location)
        self.skill = None

    def __str__(self):
        return super().__str__() + ',' + self.skill

    def load(self, arg):
        index = super().load(arg)
        self.skill = arg[index]
        if not self.skill:
            data = [x[0] for x in Data.get_line('raw.txt', 'stacking skill')[1]]
            data += Data.get_line('raw.txt', 'unique skill')[1]
            self.skill = Global.r.rand_list(data)
        return index + 1

    def get_display_name(self):
        return '<' + self.skill.title() + '> ' + self.name

    def describe(self):
        r = super().describe() + '\n' + Dialog.get('manual_skill', [self.skill.title()])
        data = Data.get_line('descriptions.txt', 'sk.' + self.skill)
        if data:
            r += '\n' + data[1]
        return r

    def use(self):
        if self.host == Global.player.character:
            self.host.action.act('eat', 8)
            self.host.action.on_finish = self.learn

    def learn(self):
        if self.host:
            skill = self.skill.lower()
            if skill not in self.host.skills:
                if Global.player.is_bright() and Global.player.sleep(1):
                    Global.main.monologue.set(Dialog.get('learn', [self.skill]))
                    self.host.skills.append(skill)
                    self.die()
            elif self.host == Global.player.character:
                Global.main.monologue.set(Dialog.get('!learn', [self.skill]))


class Potion(Food):
    def describe(self):
        r = super().describe()
        arg = self.tags.get('dur')
        if arg:
            r += '\n' + Dialog.get('Duration') + ': ' + str(arg)
        arg = self.tags.get('var')
        if arg:
            r += '\n' + Dialog.get('Modifier') + ': ' + str(arg)
        return r

    def eat(self):
        host = self.host
        r = super().eat()
        effect = self.tags.get('effect')
        if effect:
            host.states.add(effect, self.tags.get('dur', 0), self.tags.get('var', 0))
        return r

    def hit(self, damage, hitter=None):
        if damage > 0 and self.pos.get_yield() > -9:
            from src.entity.Stock import Stock
            r = Stock.make('Mine', self.pos)
            r.tags.sync('effect', self.tags.get('effect'))
            r.tags.sync('dur', self.tags.get('dur'))
            r.tags.sync('var', self.tags.get('var'))
        return super().hit(damage, hitter)


class Mine(Prop):
    def turn(self):
        super().turn()
        for thing in self.pos.things:
            if thing != self and thing.tags.get('fly') != 1:
                effect = self.tags.get('effect')
                if effect:
                    thing.states.add(effect, self.tags.get('dur', 0), self.tags.get('var', 0))
                self.remove()
                return


class Phantom(Unit):
    def __init__(self, location):
        super().__init__(location)
        self.obstruct_type = Tile.COLLIDE_ITEM
        self.host = None

    def __str__(self):
        return super().__str__() + ',[' + str(self.host) + ']'

    def load(self, p):
        index = super().load(p)
        if p[index]:
            from src.entity.Stock import Stock
            self.set_host(Stock.get(self.location, p[index][2], p[index]))
        return index + 1

    def set_host(self, host):
        self.host = host
        self.tags.sync('spd', self.host.tags.get('spd'))
        self.tags.sync('dmg', self.host.tags.get('dmg'))
        self.tags.sync('DMG', self.host.tags.get('DMG'))
        self.tags.sync('def', self.host.tags.get('def'))
        self.tags.sync('DEF', self.host.tags.get('DEF'))
        self.tags.set('p', self.host.tags.get('p', 1))
        self.tags.set('P', self.host.tags.get('P', 1))
        loot = self.host.tags.remove('loot')
        if loot:
            self.tags.set('loot', loot)

    def set_row(self, row):
        if self.host:
            self.host.form.z = row * 20 + 100

    def update(self):
        bound_x, bound_y = super().update()
        if self.host:
            x = bound_x + self.form.organs[0].lower_joint.x
            y = bound_y - self.form.organs[0].lower_joint.y
            self.host.form.rotation = self.form.organs[0].lower_joint.get_atan()
            self.host.form.place(x, y)

    def die(self):
        super().die()
        if self.host:
            self.host.relocate(to=self.pos, force=True)
            self.host.add()


class Ghost(Unit):
    def use(self):
        pass

    def move_line(self, to, flag=None):
        moved = super().move_line(to, flag)
        if self == Global.player.character:
            for i in self.pos.things:
                if i != self and isinstance(i, Unit) and i.pilot.priority > 3:
                    Global.player.character.remove()
                    Global.player.set_player(i)
                    i.center_camera()
                    break
        return moved


class Pickaxe(Item):
    def use(self):
        self.host.action.attack()
        self.host.action.on_finish = self.destroy

    def destroy(self):
        tile = self.host.pos.get_cardinal(self.host.direction, 1)
        if tile and tile.terrain != '.':
            self.location.sound.register(self.pos, 16, file='critical')
            if tile.things:
                for thing in tile.things:
                    if thing.name == 'Break':
                        thing.remove()
                        tile.set_terrain('.')
                        self.decay(1)
                        return
            else:
                from src.entity.Stock import Stock
                self.host.action.act('rest', 8)
                Stock.make('Break', tile)
                self.decay(1)


class Ceiling(Prop):
    def set_row(self, row):
        self.form.z = row * 20 + 200
