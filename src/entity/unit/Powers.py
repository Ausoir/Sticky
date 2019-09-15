from src.entity.Effect import Effect
from src.entity.Stock import Stock
from src.game import Global


class Power:
    @staticmethod
    def get(host, power):
        # noinspection PyUnresolvedReferences
        from src.entity.unit import Powers
        r = getattr(Powers, power)
        if not r:
            return None
        return r(host)

    def __init__(self, host):
        self.host = host
        self.stamina = 0
        self.delay = 4
        self.animation = 'cast'

    def is_valid(self):
        return True

    def on_start(self):
        pass

    def on_cast(self):
        pass


class Thief(Power):
    def __init__(self, host):
        super().__init__(host)
        self.stamina = 3

    def is_valid(self):
        from src.entity.unit.Humanoid import Humanoid
        for thing in self.host.get_interact_pos().things:
            if isinstance(thing, Humanoid):
                return True

    def on_cast(self):
        from src.entity.unit.Humanoid import Humanoid
        for thing in self.host.get_interact_pos().things:
            if isinstance(thing, Humanoid):
                item = thing.armor.get_item(0)
                if item:
                    item.on_equip(self.host)


class Summoner(Power):
    def __init__(self, host):
        super().__init__(host)
        self.stamina = 2

    def is_valid(self):
        return self.host.is_armed()

    def on_cast(self):
        phantom = Stock.make('Phantom', self.host.get_interact_pos())
        phantom.form.organs[0].set(self.host.weapon.form)
        phantom.durability = self.host.weapon.durability
        phantom.attributes.strength = self.host.weapon.durability
        phantom.loot = self.host.weapon.loot
        phantom.faction = self.host.faction
        self.host.weapon.loot = []
        phantom.states.add('Sick', 80)
        self.host.weapon.die()


class Necromancer(Power):
    def __init__(self, host):
        super().__init__(host)
        self.stamina = 1

    def on_cast(self):
        def casting():
            if channel.effect(5):
                Effect.make('portal', target.get_center(), offset=0)
            total = 0
            if channel.frame == 38:
                for corpse in target.things:
                    if corpse.name == 'Corpse':
                        total += corpse.durability
            if total > 1:
                r = Stock.make('Undead', target)
                r.faction = self.host.faction
                r.durability = total * 2
                r.attributes.strength = total
            else:
                Effect.make('zwip', target.get_center(), offset=0)
        channel = self.host.states.add('Channel', 40)
        channel.on_update = casting
        target = self.host.get_target_tile()
        aoe = self.host.location.get_area(target, 2, 2)
        for tile in aoe:
            corpses = []
            for thing in tile.things:
                if thing.name == 'Corpse':
                    corpses.append(thing)
                    thing.gravity = 0
                    thing.states.add('Banish', 40)
                    thing.move(target.x - thing.pos.x, target.y - thing.pos.y)


class Druid(Power):
    def __init__(self, host):
        super().__init__(host)
        self.stamina = 3

    def is_valid(self):
        return self.host.is_armed() or self.host.is_armored()

    def on_cast(self):
        Effect.make('barrier', self.host.vec, offset=0)
        if self.host.is_armored():
            self.host.armor.repair()
        if self.host.is_armed():
            self.host.weapon.repair()


class Warper(Power):
    def __init__(self, host):
        super().__init__(host)
        self.animation = 'block'
        self.delay = 1
        self.stamina = 1

    def on_cast(self):
        target = self.host.get_target_tile()
        for thing in target.things:
            thing.relocate(self.host.pos.x, self.host.pos.y, force=1)
        self.host.relocate(target.x, target.y, force=1)


class Magi(Power):
    def __init__(self, host):
        super().__init__(host)
        self.stamina = 3
        self.delay = 24
        self.aim = None

    def on_start(self):
        def casting():
            if channel.effect(5):
                Effect.make('spin', self.host.vec)
        self.host.var['casting'] = '?'
        self.aim = self.host.next_target
        spells = []
        for i in Global.player.get_spell_list():
            def fn(arg):
                self.host.var['casting'] = arg
                Global.menu.toggle()
            spells.append([i, fn])
        channel = self.host.states.add('Channel', 20)
        channel.on_update = casting
        Global.menu.var = spells
        Global.menu.state = Global.menu.menu_many_choice
        Global.menu.display(1)

    def on_cast(self):
        if self.host.var['casting'] != '?':
            from src.entity.unit.item.Spell import Spell
            self.host.next_target = self.aim
            Spell.perform(self.host, self.host.var['casting'])


class Psychic(Power):
    def __init__(self, host):
        super().__init__(host)
        self.stamina = 3
        self.delay = 12
        self.animation = 'block'

    def is_valid(self):
        return not self.host.is_armed()

    def on_cast(self):
        def casting():
            if terraform.effect(5):
                Effect.make('spin', self.host.vec)
            pointer = self.host.get_target_tile()
            for target in targets:
                target.states.add('Levitate', 4)
                target.move(pointer.x - target.pos.x, pointer.y - target.pos.y)
        targets = []
        for thing in self.host.get_target_tile().things:
            targets.append(thing)
        terraform = self.host.states.add('Channel', 6)
        terraform.on_update = casting
        self.host.states.add('Stun', 6)


class Pyromancer(Power):
    def __init__(self, host):
        super().__init__(host)
        self.stamina = 1
        self.delay = 1
        self.animation = 'block'

    def on_cast(self):
        Effect.make('burn', self.host.vec)
        burn = self.host.states.get('Burn')
        if burn:
            burn.end()
        fire = self.host.states.get('Fire')
        if fire:
            from src.entity.unit.item.Spell import Spell
            Spell.perform(self.host, 'Fireball')
        self.host.states.add('Fire', 120)
        self.host.weapon.states.add('Fire', 120)


class Terramancer(Power):
    def __init__(self, host):
        super().__init__(host)
        self.stamina = 1
        self.delay = 1
        self.animation = 'block'
        self.aim = None

    def is_valid(self):
        return self.host.get_target_tile().terrain or self.host.var['casting'] != '?'

    def on_start(self):
        self.aim = self.host.get_target_tile()

    def on_cast(self):
        if self.host.var['casting'] == '?':
            if self.aim.terrain:
                self.host.var['casting'] = self.aim.terrain.name
                self.aim.terrain = None
        else:
            self.host.get_target_tile().set_terrain(self.host.var['casting'])
            self.host.var['casting'] = '?'


class Aeromancer(Power):
    def __init__(self, host):
        super().__init__(host)
        self.stamina = 1
        self.delay = 2
        self.animation = 'block'

    def on_cast(self):
        def on_update():
            if self.host.next_target.distance() > 3:
                self.host.move(self.host.next_target.x, self.host.next_target.y, distance=1)
            else:
                from src.entity.unit.item.Spell import Spell
                Spell.perform(self.host, 'Dispell')
                channel.end()
        Effect.make('wind', self.host.pos.get_center())
        channel = self.host.states.add('Channel', 30)
        self.host.states.add('Levitate', 30)
        channel.on_update = on_update


class Enchanter(Power):
    def __init__(self, host):
        super().__init__(host)
        self.stamina = 1
        self.delay = 20
        self.buffs = ['Glow', 'Fire', 'Levitate', 'Speed', 'Barkskin', 'Slowfall']

    def is_valid(self):
        return self.host.get_target_tile().things

    def on_start(self):
        def casting():
            if channel.effect(5):
                Effect.make('spin', self.host.vec)
        self.host.var['casting'] = '?'
        spells = []
        for i in self.buffs:
            def fn(arg):
                self.host.var['casting'] = arg
                Global.menu.toggle()
            spells.append([i, fn])
        channel = self.host.states.add('Channel', 20)
        channel.on_update = casting
        Global.menu.var = spells
        Global.menu.state = Global.menu.menu_many_choice
        Global.menu.display(1)

    def on_cast(self):
        if self.host.var['casting'] != '?':
            self.host.states.add(self.host.var['casting'], 60)


class Hexer(Power):
    def __init__(self, host):
        super().__init__(host)
        self.stamina = 1
        self.delay = 10
        self.aim = None
        self.hex = ['Glow', 'Bleed', 'Cripple', 'Weak', 'Exhaustion', 'Shock', 'Burn', 'Stun', 'Speed']

    def is_valid(self):
        return self.host.get_target_tile().things

    def on_start(self):
        def casting():
            if channel.effect(4):
                Effect.make('spin', self.host.vec)
        self.host.var['casting'] = '?'
        self.aim = self.host.get_target_tile()
        spells = []
        for i in self.hex:
            def fn(arg):
                self.host.var['casting'] = arg
                Global.menu.toggle()
            spells.append([i, fn])
        channel = self.host.states.add('Channel', 10)
        channel.on_update = casting
        Global.menu.var = spells
        Global.menu.state = Global.menu.menu_many_choice
        Global.menu.display(1)

    def on_cast(self):
        if self.host.var['casting'] != '?':
            for thing in self.aim.things:
                thing.states.add(self.host.var['casting'], 60)


class Witch(Power):
    def __init__(self, host):
        super().__init__(host)
        self.stamina = 2
        self.delay = 6
        self.original = None
        self.target = None
        self.brain = None

    def on_cast(self):
        def casting():
            if channel.effect(5):
                Effect.make('spin', self.host.vec)

        def on_finish():
            self.target.pilot = self.brain
            self.original.center_camera()
            Global.player.control.player = self.original
            Effect.make('spin', self.host.vec)
        channel = self.host.states.add('Channel', 80)
        channel.on_update = casting
        channel.on_finish = on_finish
        from src.entity.unit.Unit import Unit
        for thing in self.host.get_target_tile().things:
            if isinstance(thing, Unit):
                Effect.make('barrier', thing.vec)
                from src.entity.unit.ai.Pilot import Manual
                self.brain = thing.pilot
                self.target = thing
                self.original = Global.player.control.player
                thing.pilot = Manual(thing)
                Global.player.control.player = thing
                thing.center_camera()
                return


class Prophet(Power):
    def __init__(self, host):
        super().__init__(host)
        self.stamina = 3
        self.delay = 8
        self.past_self = None
        self.past_map = None

    def on_cast(self):
        def casting():
            if channel.effect(5):
                Effect.make('portal', self.host.pos.get_center(), offset=128)

        def on_finish():
            from src.tools.Data import Data
            from src.map.Location import Location
            Effect.make('sonic', self.host.vec)
            self.host.load(Data.process_raw(self.past_self))
            self.host.location = Location(self.host.location.name, Data.process_raw(self.past_map))
            Global.player.travel(self.host.location.name, self.host.pos)
        channel = self.host.states.add('Channel', 60)
        channel.on_update = casting
        channel.on_finish = on_finish
        self.past_self = self.host.__str__()
        self.past_map = self.host.location.__str__()
