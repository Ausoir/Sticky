from src.entity.Particle import Particle
from src.entity.Prop import Prop
from src.entity.unit.Unit import Unit
from src.entity.unit.item.Headgear import Headgear
from src.entity.unit.item.Item import Item
from src.entity.unit.item.Weapon import Weapon
from src.game import Global
from src.map.Tile import Tile
from src.tools.Data import Data
from src.tools.Dialog import Dialog


class Scripter(Prop):
    def __init__(self, location):
        super().__init__(location)
        from src.game.Script import Script
        self.script = Script(self)

    def __str__(self):
        return super().__str__() + ',[' + self.script.__str__() + ']'

    def load(self, arg):
        index = super().load(arg)
        self.script.load(arg[index])
        return index + 1

    def add(self):
        super().add()
        self.script.run()

    def run_make(self):
        from src.game.Script import Script
        if self.script.period == Script.MAKE:
            self.script.run_script()


class Door(Prop):
    def __init__(self, location):
        super().__init__(location)
        self.form1 = None
        self.form2 = None

    def load(self, arg):
        index = super().load(arg)
        self.form1 = self.form
        self.form2 = Data.get_form(self.tags.get('morph'))
        self.form2.show(True)
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
                    self.form2.bound(True)
                    self.form = self.form2
                    self.form1.show(False)
                    self.obstruct_type = Tile.COLLIDE_ITEM
            else:
                if self.obstruct_type != Tile.COLLIDE_FOG:
                    self.form1.show(True)
                    self.form1.bound(True)
                    self.form = self.form1
                    self.form2.show(False)
                    self.obstruct_type = Tile.COLLIDE_FOG


class Credit(Item):
    def __init__(self, location):
        super().__init__(location)
        self.var = None
        self.amount = 0

    def __str__(self):
        return super().__str__() + ',' + self.var + ',' + str(self.amount)

    def load(self, arg):
        index = super().load(arg)
        self.var = arg[index]
        index += 1
        self.amount = arg[index]
        return index + 1

    def describe(self):
        return super().describe() + '\n' + Dialog.get(self.var.title()) + ': ' + str(self.amount)

    def use(self):
        self.host.action.act('grab', 8)
        self.host.var[self.var] += self.amount
        self.die()


class Food(Item):
    def __init__(self, location):
        super().__init__(location)
        self.nutrition = [-1, 0]

    def __str__(self):
        return super().__str__() + ',' + Dialog.nonstrlist(self.nutrition)

    def load(self, arg):
        index = super().load(arg)
        self.nutrition = arg[index]
        if self.nutrition[0] < 0:
            self.nutrition[0] = Global.player.days + -self.nutrition[0]
        return index + 1

    def get_value(self):
        expire = self.get_expiration()
        points = expire + self.nutrition[1]
        if points > 8:
            return 3
        elif points > 3:
            return 2
        return 1

    def describe(self):
        r = super().describe()
        r += '\n' + Dialog.get('Nutrition') + ': ' + str(self.nutrition[1])
        expire = self.get_expiration()
        if expire:
            r += '\n' + Dialog.get('food_expire', [Dialog.day(expire)])
        else:
            r += '\n' + Dialog.get('food_expired')
        return r

    def get_expiration(self):
        left = max(0, self.nutrition[0] - Global.player.days)
        return left

    def use(self):
        if self.get_expiration():
            hunger = self.host.tags.get('full')
            if hunger < 10:
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
        self.host.tags.increment('full', self.nutrition[1] + self.host.get_skill('asceticism', stacks=True))
        self.decay(1)


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

    def set(self, form):
        self.has_host = True
        self.form = form
        self.add()
        dead = 'dead' + str(Global.r.rand_int(1, 2))
        self.form.randomize_clip(dead, 8)
        self.form.set_state(dead)
        self.form.set_state = self.invalid
        return self

    def update(self):
        super().update()
        if self.has_host:
            self.form.place(self.vec.x, self.vec.y)

    def hit(self, damage, hitter=None):
        r = super().hit(damage, hitter)
        if r != 2:
            if self.has_host:
                self.form.randomize_once(6)
        return r

    def die(self):
        self.remove()


class Explosive(Item):
    def die(self):
        if self.states.get('Burn'):
            from src.entity.Stock import Stock
            Stock.make('Flame', self.pos)
            aoe = self.location.get_area(self.pos, 1, 1)
            for tile in aoe:
                Particle.make('explode', tile.get_center(), offset=4, glow=2)
                for thing in tile.things:
                    thing.states.add('Burn', 24)
                    thing.hit(1)
        super().die()


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
            if Global.r.rand_bool():
                data = Data.get_line('raw/raw.txt', 'stacking skill')[1]
                data = [x[0] for x in data]
            else:
                data = Data.get_line('raw/raw.txt', 'unique skill')[1]
            self.skill = Global.r.rand_list(data)
        return index + 1

    def get_display_name(self):
        return '<' + self.skill.title() + '> ' + Dialog.get('manual')

    def describe(self):
        r = super().describe() + '\n' + Dialog.get('manual_skill', [self.skill.title()])
        data = Data.get_line('raw/descriptions.txt', 'sk.' + self.skill)
        if data:
            r += '\n' + data[1]
        return r

    def use(self):
        if self.host == Global.player.character:
            self.host.action.act('eat', 8)
            self.host.action.on_finish = self.learn

    def learn(self):
        skill = self.skill.lower()
        if skill not in self.host.skills:
            if Global.player.is_bright() and Global.player.sleep(1):
                Global.main.monologue.set(Dialog.get('monologue_learn', [self.skill]))
                self.host.skills.append(skill)
                self.die()
        elif self.host == Global.player.character:
            Global.main.monologue.set(Dialog.get('!monologue_learn', [self.skill]))


class Glasses(Headgear):
    def __init__(self, location):
        super().__init__(location)
        self.sight = 4

    def __str__(self):
        return super().__str__() + ',' + str(self.sight)

    def load(self, arg):
        index = super().load(arg)
        self.sight = arg[index]
        return index + 1

    def activate(self):
        super().activate()
        if self.host == Global.player.character:
            def done():
                self.host.center_camera()
            channel = self.host.states.add('Channel', 12)
            channel.on_finish = done
            new_pos = self.location.collide_land(self.host.pos, self.host.next_target.x, self.host.next_target.y,
                                                   distance=self.sight, flag=Tile.CHECK_FIRM)
            from src.game.TempObject import TempObject
            viewer = TempObject(new_pos)
            from src.game.Camera import Camera
            Camera.target = viewer


class SafetyHat(Headgear):
    def __init__(self, location):
        super().__init__(location)
        self.light = 6

    def __str__(self):
        return super().__str__() + ',' + str(self.light)

    def load(self, arg):
        index = super().load(arg)
        self.light = arg[index]
        return index + 1

    def on_unwield(self):
        light = self.host.states.get('Glow')
        if light:
            light.end()
        super().on_unwield()

    def activate(self):
        super().activate()
        light = self.host.states.get('Glow')
        if light:
            light.end()
        else:
            self.host.states.add('Glow', -1, var=self.light)


class Tazer(Weapon):
    def __init__(self, location):
        super().__init__(location)
        self.charge = 0

    def __str__(self):
        return super().__str__() + ',' + str(self.charge)

    def load(self, arg):
        index = super().load(arg)
        self.charge = arg[index]
        return index + 1

    def describe(self):
        return super().describe() + '\nCurrent charge: ' + str(self.charge)

    def on_sleep(self, time):
        self.charge = 100

    def on_attack(self, target):
        super().on_attack(target)
        if self.charge >= 100:
            target.states.add('Effect', 60, var='zap')
            self.charge = 0
        else:
            self.charge = self.charge + 50


class Pickaxe(Weapon):
    def use(self):
        self.host.action.attack()
        self.host.action.on_finish = self.destroy

    def destroy(self):
        self.host.action.act('rest', 8)
        tile = self.host.get_front_tile(self.host.direction, mag=1)
        if tile and tile.terrain != '.':
            if tile.things:
                for thing in tile.things:
                    if thing.name == 'Break':
                        thing.remove()
                        tile.set_terrain('.')
            else:
                from src.entity.Stock import Stock
                Stock.make('Break', tile)


class Mine(Prop):
    def __init__(self, location):
        super().__init__(location)
        self.area = 4
        self.damage = 12

    def __str__(self):
        return super().__str__() + ',' + str(self.area) + ',' + str(self.damage)

    def load(self, arg):
        index = super().load(arg)
        self.area = arg[index]
        index += 1
        self.damage = arg[index]
        return index + 1

    def turn(self):
        super().turn()
        if self.pos.is_land([Tile.COLLIDE_UNIT]):
            from src.entity.unit.Actions import Actions
            for tile in self.location.get_area(self.pos, self.area, self.area):
                for thing in tile.things.copy():
                    Actions.knockdown(thing)
                    thing.states.add('Burn', 12)
                    thing.hit(self.damage)
                Particle.make('explode', tile.get_center())
            self.remove()


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
        self.form.organs[0].set(self.host.form)
        self.tags.set('mat', self.host.tags.get('mat'))
        if isinstance(self.host, Weapon):
            self.strength = self.host.damage
        self.tags.set('p', self.host.tags.get('p'))
        self.host.loot = []
