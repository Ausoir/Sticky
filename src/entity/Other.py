from src.entity.Particle import Particle
from src.entity.Prop import Prop
from src.entity.Space import Space
from src.entity.unit.Unit import Unit
from src.entity.unit.item.Equipment import Equipment
from src.entity.unit.item.Headgear import Headgear
from src.entity.unit.item.Item import Item
from src.entity.unit.item.Weapon import Weapon
from src.game import Global
from src.map.Tile import Tile
from src.tools.Data import Data
from src.tools.Dialog import Dialog
from src.tools.Random import Random


class Script(Prop):
    def __init__(self, loc):
        super().__init__(loc)
        self.condition = None
        self.mechanism = None
        self.seed = None
        self.rand = None
        self.where = None
        self.who = None

    def __str__(self):
        string = Dialog.deepnonstrlist
        cnm = string(self.condition, 2) + ',' + string(self.mechanism, 2)
        return super().__str__() + ',' + str(self.seed) + ',' + cnm

    def load(self, arg):
        index = super().load(arg)
        self.seed = arg[index]
        self.rand = Random(self.seed)
        index += 1
        self.condition = arg[index]
        index += 1
        self.mechanism = arg[index]
        return index + 1

    def add(self):
        super().add()
        if '!' in self.tags:
            from src.game.Turn import Turn
            Turn.remove(self.turn)

    def turn(self):
        self.where = self.pos
        self.who = self.pos.things
        for i in self.condition:
            if not self.is_triggered(i):
                return
        self.run()

    def trigger(self):
        self.turn()

    def trigger_make(self):
        if self.condition and self.condition[0][0] == 'make':
            self.where = self.pos
            self.who = self.pos.things
            success = True
            for i in self.condition[1:]:
                if not self.is_triggered(i):
                    success = False
                    break
            if success:
                self.run()
            self.remove()

    def is_triggered(self, condition):
        if condition[0] == 'where':
            self.where = self.location.get_tile([condition[1], condition[2]])
            self.who = self.where.things
            return True
        elif condition[0] == 'wherer':
            self.where = self.location.get_tile([self.pos.x + condition[1], self.pos.y + condition[2]])
            self.who = self.where.things
            return True
        elif condition[0] == 'who':
            if len(condition) == 1:
                self.who = self.where.things
            else:
                self.who = []
                for i in self.location.record:
                    if i.name == condition[1]:
                        self.who.append(i)
            return True
        elif condition[0] == 'turn':
            condition[2] += 1
            if condition[2] >= condition[1]:
                condition[2] = 0
                return True
        elif condition[0] == 'bring':
            count = 0
            for i in self.who:
                if i != self:
                    if not condition[1] or condition[1] == i.name:
                        count += 1
            if count == condition[2]:
                return True
        elif condition[0] == 'rand':
            for i in self.condition[self.condition.index(condition) + 1:]:
                if i[0] == condition[1]:
                    if isinstance(condition[3], str) and condition[3].startswith('#'):
                        data = Data.get_line('data/raw/raw.txt', condition[3][1:])[1]
                        i[condition[2]] = self.rand.rand_list(data)
                    else:
                        i[condition[2]] = self.rand.rand_list(condition[3:])
                    return True
        elif condition[0] == 'randr':
            for i in self.condition[self.condition.index(condition) + 1:]:
                if i[0] == condition[1]:
                    i[condition[2]] = self.rand.rand_int(condition[3], condition[4])
                    return True
        elif condition[0] == 'reqvar':
            ok = False
            for i in self.who:
                from src.entity.unit.Character import Character
                if isinstance(i, Character):
                    if not i.require_var(condition[1], condition[2], cost=False):
                        return False
                    else:
                        ok = True
            return ok
        elif condition[0] == 'chance':
            if self.rand.rand_int(1, condition[1]) <= condition[2]:
                return True
        elif condition[0] == 'date':
            if Global.player.days > condition[1]:
                condition[1] = Global.player.days + condition[2]
                return True
        elif condition[0] == 'limit':
            condition[1] -= 1
            if condition[1] == 0:
                return True
        elif condition[0] == 'load':
            from src.game.Turn import Turn
            Turn.remove(self.turn)
            return True
        elif condition[0] == 'once':
            self.remove()
            return True
        elif condition[0] == 'safe':
            return Global.player.is_safe()
        elif condition[0] == 'bright':
            return Global.player.character.is_bright()
        elif condition[0] == 'ask':
            def on_yes(name):
                Global.menu.toggle()
                self.run()
            Global.menu.var = [condition[1], [condition[2]], [on_yes]]
            Global.menu.direct(Global.menu.menu_choice)

    def run(self):
        self.where = self.pos
        for i in self.mechanism:
            self.trigger_mechanism(i)

    def trigger_mechanism(self, arg):
        if arg[0] == 'where':
            self.where = self.location.get_tile([arg[1], arg[2]])
            self.who = self.where.things
        elif arg[0] == 'wherer':
            self.where = self.location.get_tile([self.pos.x + arg[1], self.pos.y + arg[2]])
            self.who = self.where.things
        elif arg[0] == 'who':
            if len(arg) == 1:
                self.who = self.where.things
            else:
                self.who = []
                for i in self.location.record:
                    if i.name == arg[1]:
                        self.who.append(i)
        elif arg[0] == 'trigger':
            for i in self.who:
                if isinstance(i, Script):
                    i.trigger()
        elif arg[0] == 'seed':
            for i in self.who:
                if isinstance(i, Script):
                    i.seed = arg[1]
        elif arg[0] == 'spawn':
            count = 0
            from src.entity.Stock import Stock
            for i in self.location.record:
                if i.name == arg[1]:
                    count += 1
            if count < arg[2]:
                Stock.make(arg[1], self.where)
        elif arg[0] == 'effect':
            Particle.make(arg[1], self.where.get_center(), offset=8, glow=arg[2])
        elif arg[0] == 'message':
            Global.menu.show_dialog([arg[1]])
        elif arg[0] == 'dialog':
            Global.menu.var = [None, arg[1]]
            Global.menu.topic(arg[1])
        elif arg[0] == 'say':
            from src.entity.unit.Character import Character
            for i in self.who:
                if isinstance(i, Character):
                    i.say(arg[1])
        elif arg[0] == 'setvar':
            from src.entity.unit.Character import Character
            for i in self.who:
                if isinstance(i, Character):
                    i.var[arg[1]] = arg[2]
                    return
        elif arg[0] == 'addvar':
            from src.entity.unit.Character import Character
            for i in self.who:
                if isinstance(i, Character):
                    i.var[arg[1]] += arg[2]
                    return
        elif arg[0] == 'remove':
            count = arg[2]
            for thing in reversed(self.who):
                if thing != self and count > 0 and not arg[1] or thing.name == arg[1]:
                    count -= 1
                    thing.remove()
        elif arg[0] == 'hit':
            for thing in self.who:
                if thing != self and not arg[1] or thing.name == arg[1]:
                    thing.hit(arg[2])
        elif arg[0] == 'buff':
            for thing in self.who:
                if thing != self:
                    thing.states.add(arg[1], arg[2], var=arg[3])
        elif arg[0] == 'relocate':
            for thing in self.who:
                if thing != self:
                    if not arg[1] or arg[1] == thing.name:
                        thing.relocate(arg[2], arg[3])
        elif arg[0] == 'move':
            for thing in self.who:
                if thing != self:
                    if not arg[1] or arg[1] == thing.name:
                        thing.move(arg[2], arg[3])
        elif arg[0] == 'thief':
            for i in self.location.record:
                if isinstance(i, Item):
                    if i.get_value() >= arg[1]:
                        i.remove()
        elif arg[0] == 'color':
            Global.draw_group.colorize(1, [arg[1], arg[2], arg[3], arg[4]])
        elif arg[0] == 'darkness':
            self.location.view_range = arg[1]
            self.location.sight_range = arg[2]
            self.location.resize()
        elif arg[0] == 'rand':
            for i in self.mechanism[self.mechanism.index(arg) + 1:]:
                if i[0] == arg[1]:
                    if isinstance(arg[3], str) and arg[3].startswith('#'):
                        i[arg[2]] = self.rand.rand_list(Data.get_line('data/raw/raw.txt', arg[3][1:])[1])
                    else:
                        i[arg[2]] = self.rand.rand_list(arg[3:])
                    break
        elif arg[0] == 'randr':
            for i in self.mechanism[self.mechanism.index(arg) + 1:]:
                if i[0] == arg[1]:
                    i[arg[2]] = self.rand.rand_int(arg[3], arg[4])
                    break
        elif arg[0] == 'enter':
            Global.player.travel(arg[1], Space(int(arg[2]), int(arg[3])))
        elif arg[0] == 'travel':
            Global.menu.var = arg[1:]
            Global.menu.state = Global.menu.menu_travel
            Global.menu.display(1)
        elif arg[0] == 'load':
            building = Data.process_raw(Data.read('data/map/' + arg[1] + '.map'))
            flip = False
            if len(arg) > 2 and arg[2]:
                flip = True
            objs = self.location.load_map(building, new=True, offset=self.where.to_list(), flip=flip)
            for obj in objs:
                if isinstance(obj, Script):
                    obj.trigger_make()
        elif arg[0] == 'make':
            from src.map.Location import Location
            Location.make(arg[1], arg[2])
        elif arg[0] == 'makeif':
            from src.map.Location import Location
            Location.make(arg[1], arg[2], overwrite=False)
        elif arg[0] == 'act':
            from src.entity.unit.Unit import Unit
            for i in self.who:
                if isinstance(i, Unit):
                    i.action.set('wait')
                    i.form.set(arg[1])
                    i.delay = arg[2]


class Bridge(Prop):
    def load(self, arg):
        super().load(arg)
        self.gravity = 0

    def turn(self):
        super().turn()
        support = 0
        adj = [self.get_offset_tile(-1, 0), self.get_offset_tile(1, 0)]
        for i in adj:
            if i.is_land(Tile.CHECK_FIRM):
                support += 2
            elif i.is_land([Tile.COLLIDE_DOODAD]):
                support += 1
        if support < 2:
            self.die()


class Credit(Item):
    def __init__(self, loc):
        super().__init__(loc)
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
        self.host.action.set('wait')
        self.host.var[self.var] += self.amount
        self.die()


class RepairKit(Item):
    def __init__(self, loc):
        super().__init__(loc)
        self.charge = 0

    def __str__(self):
        return super().__str__() + ',' + str(self.charge)

    def load(self, arg):
        index = super().load(arg)
        self.charge = arg[index]
        return index + 1

    def describe(self):
        return super().describe() + '\nCharges: ' + str(self.charge)

    def on_sleep(self, time):
        if self.host:
            diff = max(0, self.host.headgear.max_durability - self.host.headgear.durability)
            if diff > 0:
                diff = max(self.charge, diff)
                self.host.headgear.durability += diff
                self.charge = max(0, self.charge - diff)
            diff = max(0, self.host.armor.max_durability - self.host.armor.durability)
            if diff > 0:
                diff = max(self.charge, diff)
                self.host.armor.durability += diff
                self.charge = max(0, self.charge - diff)
            if self.charge == 0:
                self.die()

    def use(self):
        for i in self.host.get_possessions():
            if i == 'Fiber':
                i.die()
                self.charge = min(20, self.charge + 8)
                Particle.make('heal', self.host.vec)


class Food(Item):
    def __init__(self, loc):
        super().__init__(loc)
        self.nutrition = [-1, 0, 0, 0]

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
        if expire > 2:
            return super().get_value() + self.nutrition[1] + self.nutrition[2]
        elif expire > 0:
            return super().get_value() + self.nutrition[1] + self.nutrition[2] - 1
        else:
            return 0

    def describe(self):
        r = super().describe()
        r += '\nCalories: ' + str(self.nutrition[1])
        r += '\nProtein: ' + str(self.nutrition[2])
        expire = self.get_expiration()
        if expire:
            r += '\nExpires in ' + Dialog.day(expire)
        else:
            r += '\nThis food has expired.'
        return r

    def get_expiration(self):
        left = max(0, self.nutrition[0] - Global.player.days)
        return left

    def use(self):
        if self.get_expiration():
            if self.host.states.get('Nausea'):
                self.host.say('I have nausea...')
            else:
                hunger = self.host.states.get('Hunger')
                if hunger:
                    hunger.end()
                    self.host.action.set('wait')
                    self.eat()
                else:
                    self.host.say('I am not hungry.')
        else:
            self.host.say('This food has expired...')

    def eat(self):
        self.host.var['calories'] += self.nutrition[1]
        self.host.var['protein'] += self.nutrition[2]
        self.hit(1)


class Sonic(Prop):
    def turn(self):
        if self.durability == 0:
            self.remove()
        else:
            self.durability -= 1
            Particle.make('sonic', self.get_offset_tile(Global.r.rand_int(-3, 3), Global.r.rand_int(-3, 3)).get_center())
            for x in range(-9, 10):
                for y in range(-9, 10):
                    if Global.r.rand_bool():
                        pos = str(self.pos.x + x) + ',' + str(self.pos.y + y)
                        self.location.draw_tiles[pos] = self.get_offset_tile(x, y)


class Block(Prop):
    def __init__(self, loc):
        super().__init__(loc)
        self.standables = Tile.CHECK_FOUNDATION.copy()
        self.standables.append(Tile.COLLIDE_BACK)


class Corpse(Prop):
    def __init__(self, loc):
        super().__init__(loc)
        self.direction = 1
        self.collision_type = 0
        self.standables = Tile.CHECK_LANDABLE
        self.form = Data.get_form('g_9x3', group=Global.draw_group.objects)
        self.is_ragdoll = False

    def invalid(self, state):
        pass

    def set_form(self, arg):
        self.form_name = arg

    def set(self, form):
        self.is_ragdoll = True
        self.add()
        self.form = form
        self.durability = 8
        dead = 'dead' + str(Global.r.rand_int(1, 2))
        self.form.randomize_clip(dead, 8)
        self.form.set_state(dead)
        self.form.set_state = self.invalid
        self.form.enable(True)
        return self

    def update(self):
        super().update()
        if self.is_ragdoll:
            self.form.place(self.vec.x, self.vec.y)

    def is_hit(self, chance, faction=0):
        if self.hittable:
            return 1

    def hit(self, damage, accuracy=None, hitter=None):
        r = super().hit(damage, accuracy, hitter)
        if r == 2:
            from src.game.Tags import Tags
            if hitter and Tags.sharp in hitter.tags:
                from src.entity.Stock import Stock
                Stock.make('Raw Meat', self.pos)
        else:
            if self.is_ragdoll:
                self.form.randomize_once(18)
        return r

    def die(self):
        self.remove()


class Break(Prop):
    def die(self):
        super().die()
        if self.pos.terrain:
            self.pos.terrain = None


class Mushroom(Item):
    def die(self):
        if self.host:
            self.host.states.add('Sick', 40)
        else:
            for thing in self.pos.things:
                thing.states.add('Sick', 40)
        super().die()


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
    skills = ['Peek', 'Block', 'Sprint', 'Leap', 'Offhand', 'Tackle', 'Lunge', 'Flurry', 'Slam', 'Charge']

    def __init__(self, loc):
        super().__init__(loc)
        self.skill = None

    def __str__(self):
        return super().__str__() + ',' + self.skill

    def load(self, arg):
        index = super().load(arg)
        self.skill = arg[index]
        if self.skill == 'Random':
            self.skill = Global.r.rand_list(Manual.skills)
        return index + 1

    def get_display_name(self):
        return 'Manual of ' + self.skill

    def describe(self):
        r = super().describe() + '\nTeaches skill [' + self.skill + ']'
        if self.skill in Item.description:
            r += '\n' + Item.description[self.skill]
        r += '\nRequires ' + str(self.get_req()) + ' Strength'
        return r

    def get_req(self):
        req = 2
        for i in self.host.action.skills:
            if i.title() in Manual.skills:
                req += 1
        return req

    def use(self):
        skill = self.skill.lower()
        if skill not in self.host.action.skills:
            req = self.get_req()
            if self.host.attributes.strength >= req:
                self.host.action.skills.append(skill)
                if self.host == Global.player.character:
                    Global.player.character.say('Learned ' + self.skill + '!')
                    self.die()
            elif self.host == Global.player.character:
                Global.player.character.say('Need ' + str(req) + ' Strength to learn this skill!')
        elif self.host == Global.player.character:
            Global.player.character.say('I already know ' + self.skill + '.')


class Handcuff(Item):
    def __init__(self, loc):
        super().__init__(loc)
        self.capture = None

    def __str__(self):
        return super().__str__() + ',[' + str(self.capture) + ']'

    def load(self, arg):
        index = super().load(arg)
        if arg[index][0] != 'None':
            from src.entity.Stock import Stock
            self.capture = Stock.get(None, data=arg[index])
        return index + 1

    def describe(self):
        r = super().describe()
        if self.capture:
            return r + '\nContains ' + self.capture.name
        else:
            return r

    def use(self):
        if not self.capture:
            def change():
                for i in self.host.pos.things:
                    if i != self.host and isinstance(i, Prop):
                        self.capture = i
                        i.remove()
                Particle.make('portal', self.host.pos.get_center())
            self.host.action.set('wait')
            self.host.action.set_animation('interact')
            self.host.action.on_finish = change
            self.host.delay = 5
        else:
            self.host.action.set('wait')
            self.host.action.set_animation('interact')
            from src.entity.Stock import Stock
            self.capture.pos = self.host.get_front_tile()
            Particle.make('portal', self.capture.pos.get_center())
            self.capture.add()
            self.capture = None


class MemoryAmulet(Headgear):
    def __init__(self, loc):
        super().__init__(loc)
        self.visible = 0
        self.memory_map = None
        self.memory_pos = Space()

    def __str__(self):
        return super().__str__() + ',' + self.memory_map + ',' + self.memory_pos.__str__()

    def load(self, arg):
        index = super().load(arg)
        self.memory_map = arg[index]
        index += 1
        self.memory_pos.load(arg[index])
        return index + 1

    def use(self):
        super().use()
        self.memory_map = self.host.location.name
        self.memory_pos = self.host.pos

    def activate(self):
        super().activate()
        self.hit(1)
        Global.player.travel(self.memory_map, self.memory_pos)


class RubyAmulet(Headgear):
    def __init__(self, loc):
        super().__init__(loc)
        self.visible = 0

    def die(self):
        if self.host:
            return
        super().die()

    def activate(self):
        super().activate()
        if self.durability <= 0:
            for thing in self.host.pos.things:
                if thing.name == 'Corpse':
                    self.weight = thing.durability
                    thing.die()
                    break

    def on_sleep(self, time):
        self.durability = self.weight


class LifeAmulet(Headgear):
    def __init__(self, loc):
        super().__init__(loc)
        self.visible = 0
        self.max_durability = 3

    def die(self):
        if self.host:
            return
        super().die()

    def on_sleep(self, time):
        self.durability = min(self.max_durability, self.durability + time)

    def enhance(self, rng):
        r = super().enhance(rng)
        if r:
            self.max_durability += 3
            self.weight += 1
        return r


class Glasses(Headgear):
    def __init__(self, loc):
        super().__init__(loc)
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
            new_pos = self.host.location.collide_land(self.host.pos, self.host.next_target.x, self.host.next_target.y,
                                                      distance=self.sight, flag=Tile.CHECK_LARGE)
            from src.game.TempObject import TempObject
            viewer = TempObject(new_pos)
            from src.game.Camera import Camera
            Camera.target = viewer


class SafetyHat(Headgear):
    def __init__(self, loc):
        super().__init__(loc)
        self.light = 4

    def __str__(self):
        return super().__str__() + ',' + str(self.light)

    def load(self, arg):
        index = super().load(arg)
        self.light = arg[index]
        return index + 1

    def on_unequip(self):
        light = self.host.states.get('Glow')
        if light:
            light.end()
        super().on_unequip()

    def activate(self):
        super().activate()
        light = self.host.states.get('Glow')
        if light:
            light.end()
        else:
            self.host.states.add('Glow', -1, var=self.light)


class Tazer(Weapon):
    def __init__(self, loc):
        super().__init__(loc)
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
            target.states.add('Influence', 60, var='hit')
            target.states.add('Effect', 60, var='zap')
            self.charge = 0
        else:
            self.charge = self.charge + 50


class Pickaxe(Weapon):
    def attack(self, chance=0, delay=1, callback=None):
        super().attack(chance, delay, callback)
        breakables = Data.get_line('raw/raw.txt', 'breakable')[1]
        for i in range(self.reach):
            tile = self.host.location.collide_line(self.host.pos, self.host.next_target.x, self.host.next_target.y,
                                                   lambda arg1, arg2: None, distance=i + 1)
            if tile.terrain and tile.terrain.name.split(' ')[0] in breakables:
                if not tile.things:
                    down = self.location.get_tile(tile + (0, 1))
                    below = self.host.location.collide_land(down, 0, 7, flag=[Tile.COLLIDE_TERRAIN], distance=7)
                    if below != self.location.get_tile(tile + (0, 8)):
                        from src.entity.Stock import Stock
                        Stock.make('Break', tile)


class Ballistic(Equipment):
    def __init__(self, loc):
        super().__init__(loc)
        self.motion = None
        self.ammo = 0

    def __str__(self):
        return super().__str__() + ',' + self.motion + ',' + str(self.ammo)

    def load(self, arg):
        index = super().load(arg)
        self.motion = arg[index]
        index += 1
        self.ammo = arg[index]
        return index + 1

    def is_reloaded(self):
        return self.ammo > 0

    def use(self):
        if self.is_reloaded():
            self.host.action.set(self.motion)
            self.ammo -= 1
        else:
            self.host.say('Out of ammunition.')


class Unnatural(Unit):
    def hit(self, damage, accuracy=None, hitter=None):
        from src.game.Tags import Tags
        if hitter and Tags.silver in hitter.tags:
            if accuracy:
                accuracy *= 2
            damage *= 2
        return super().hit(damage, accuracy, hitter)


class Phantom(Unit):
    def __init__(self, loc):
        super().__init__(loc)
        self.collision_type = Tile.COLLIDE_ITEM
        self.host = None

    def __str__(self):
        return super().__str__() + ',[' + str(self.host) + ']'

    def load(self, p):
        index = super().load(p)
        if p[index]:
            from src.entity.Stock import Stock
            self.set_host(Stock.get(p[index][2], p[index]))
        return index + 1

    def set_host(self, host):
        self.host = host
        self.form.organs[0].set(self.host.form)
        self.tags = self.host.tags
        self.host.loot = []
