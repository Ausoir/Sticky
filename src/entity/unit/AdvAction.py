from src.entity.Particle import Particle
from src.entity.Stock import Stock
from src.game import Global


class AdvAction:
    @staticmethod
    def get(host, power):
        # noinspection PyUnresolvedReferences
        from src.entity.unit import AdvAction
        r = getattr(AdvAction, power)
        if not r:
            return None
        return r(host)

    def __init__(self, host):
        self.host = host
        self.energy = 0
        self.delay = 4
        self.animation = 'cast'

    def is_valid(self):
        return True

    def on_start(self):
        pass

    def on_cast(self):
        pass


class Summoner(AdvAction):
    def __init__(self, host):
        super().__init__(host)
        self.energy = 2

    def is_valid(self):
        return self.host.is_armed()

    def on_cast(self):
        phantom = Stock.make('Phantom', self.host.get_front_tile())
        phantom.set_host(self.host.weapon)
        phantom.tags = phantom.host.tags
        phantom.faction = self.host.faction
        phantom.pilot.var['ally'] = Global.player.character.id
        from src.entity.unit.item.Weapon import Weapon
        if isinstance(self.host.weapon, Weapon):
            phantom.attributes.strength = max(1, self.host.weapon.durability)
            if self.host.weapon.accuracy > 2:
                phantom.proficiency.append('attack')
            if self.host.weapon.weight > 2:
                phantom.proficiency.append('damage')
            if self.host.weapon.speed < 3:
                phantom.states.add('Speed', -1, 1)
        self.host.weapon.die()


class Necromancer(AdvAction):
    def __init__(self, host):
        super().__init__(host)
        self.energy = 1

    def on_cast(self):
        def casting():
            if channel.effect(5):
                Particle.make('portal', target.get_center(), offset=0)
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
                Particle.make('zwip', target.get_center(), offset=0)
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


class Druid(AdvAction):
    def __init__(self, host):
        super().__init__(host)
        self.energy = 3

    def is_valid(self):
        return self.host.is_armed() or self.host.is_armored()

    def on_cast(self):
        Particle.make('barrier', self.host.vec, offset=0)
        if self.host.is_armored():
            self.host.armor.repair()
        if self.host.is_armed():
            self.host.weapon.repair()


class Warper(AdvAction):
    def __init__(self, host):
        super().__init__(host)
        self.animation = 'block'
        self.delay = 1
        self.energy = 3

    def on_cast(self):
        target = self.host.get_target_tile()
        if target == self.host.pos:
            if self.host == Global.player.character and self.host.stamina(2):
                from src.entity.Space import Space
                Global.player.travel('home', Space())
        else:
            for thing in target.things:
                thing.relocate(self.host.pos.x, self.host.pos.y, force=1)
            self.host.relocate(target.x, target.y, force=1)


class Magi(AdvAction):
    def __init__(self, host):
        super().__init__(host)
        self.energy = 2
        self.delay = 24
        self.aim = None

    def on_start(self):
        def casting():
            if channel.effect(5):
                Particle.make('spin', self.host.vec, glow=-1)
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
        if self.host.var['casting'] == '?':
            Global.menu.display(-1)
        else:
            from src.entity.unit.item.Spell import Spell
            self.host.next_target = self.aim
            Spell.perform(self.host, self.host.var['casting'])


class Psychic(AdvAction):
    def __init__(self, host):
        super().__init__(host)
        self.energy = 3
        self.delay = 12
        self.animation = 'block'

    def is_valid(self):
        return not self.host.is_armed()

    def on_cast(self):
        def casting():
            if terraform.effect(5):
                Particle.make('spin', self.host.vec, glow=-1)
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


class Pyromancer(AdvAction):
    def __init__(self, host):
        super().__init__(host)
        self.energy = 1
        self.delay = 1
        self.animation = 'block'

    def on_cast(self):
        Particle.make('burn', self.host.vec)
        burn = self.host.states.get('Burn')
        if burn:
            burn.end()
        fire = self.host.states.get('Fire')
        if fire:
            from src.entity.unit.item.Spell import Spell
            Spell.perform(self.host, 'Fireball')
        self.host.states.add('Fire', 120)
        self.host.weapon.states.add('Fire', 120)


class Terramancer(AdvAction):
    def __init__(self, host):
        super().__init__(host)
        self.energy = 1
        self.delay = 1
        self.animation = 'block'
        self.aim = None

    def is_valid(self):
        return self.host.get_target_tile().terrain or self.host.var['casting'] != '?'

    def on_start(self):
        self.aim = self.host.get_target_tile()

    def on_cast(self):
        if self.host.var['casting'] == '?':
            if self.aim.terrain and self.aim.terrain.name != 'edge':
                self.host.var['casting'] = self.aim.terrain.name
                self.aim.terrain = None
        else:
            self.host.get_target_tile().set_terrain(self.host.var['casting'])
            self.host.var['casting'] = '?'


class Aeromancer(AdvAction):
    def __init__(self, host):
        super().__init__(host)
        self.energy = 3
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
        Particle.make('wind', self.host.pos.get_center())
        channel = self.host.states.add('Channel', -1)
        self.host.states.add('Levitate', -1)
        channel.on_update = on_update


class Enchanter(AdvAction):
    def __init__(self, host):
        super().__init__(host)
        self.energy = 1
        self.delay = 20
        self.aim = None
        self.selection = []
        self.buff = [['Glow', 240, 4], ['Fire', 30, 0], ['Levitate', 60, 0], ['Barkskin', 30, 0], ['Slowfall', 60, 0],
                     ['Speed', 30, 1]]
        self.hex = [['Glow', 240, 3], ['Levitate', 60, 0], ['Speed', 30, -1], ['Bleed', 300, 0], ['Cripple', 120, 0],
                    ['Weak', 60, 0], ['Exhaustion', 120, 0], ['Shock', 60, 0], ['Burn', 10, 0], ['Stun', 30, 0]]

    def is_valid(self):
        return self.host.get_target_tile().things

    def on_start(self):
        def casting():
            if channel.effect(4):
                Particle.make('spin', self.host.vec, glow=-1)
        self.host.var['casting'] = '?'
        self.aim = self.host.get_target_tile()
        if (self.aim - self.host.pos).difference() <= 1:
            self.selection = self.buff
        else:
            self.selection = self.hex

        def fn(arg):
            self.host.var['casting'] = arg
            Global.menu.toggle()
        spells = []
        for i in self.selection:
            spells.append([i[0], fn])
        channel = self.host.states.add('Channel', 20)
        channel.on_update = casting
        Global.menu.var = spells
        Global.menu.state = Global.menu.menu_many_choice
        Global.menu.display(1)

    def on_cast(self):
        cast = self.host.var['casting']
        if cast == '?':
            Global.menu.display(-1)
        else:
            for i in self.selection:
                if i[0] == cast:
                    for thing in self.aim.things:
                        thing.states.add(i[0], i[1], i[2])
                    return


class Witch(AdvAction):
    def __init__(self, host):
        super().__init__(host)
        self.energy = 2
        self.delay = 6
        self.original = None
        self.target = None
        self.brain = None

    def on_cast(self):
        def casting():
            if channel.effect(5):
                Particle.make('spin', self.host.vec, glow=-1)

        def on_finish():
            self.target.pilot = self.brain
            self.original.center_camera()
            Global.player.control.player = self.original
            Particle.make('spin', self.host.vec, glow=-1)
        channel = self.host.states.add('Channel', 80)
        channel.on_update = casting
        channel.on_finish = on_finish
        from src.entity.unit.Unit import Unit
        for thing in self.host.get_target_tile().things:
            if isinstance(thing, Unit):
                Particle.make('barrier', thing.vec)
                from src.entity.unit.ai.Pilot import Manual
                self.brain = thing.pilot
                self.target = thing
                self.original = Global.player.control.player
                thing.pilot = Manual(thing, [])
                Global.player.control.player = thing
                thing.center_camera()
                return


class Prophet(AdvAction):
    def __init__(self, host):
        super().__init__(host)
        self.energy = 3
        self.delay = 8
        self.past_self = None
        self.past_map = None

    def on_cast(self):
        def reload(arg):
            Particle.make('sonic', self.host.vec)
            channel.end()
            from src.tools.Data import Data
            from src.map.Location import Location
            Global.main.background_color = (0, 0, 0)
            self.host.load(Data.process_raw(self.past_self))
            self.host.location = Location(self.host.location.name, Data.process_raw(self.past_map))
            Global.player.travel(self.host.location.name, self.host.pos)
        channel = self.host.states.add('Foresee', 60)
        channel.trigger = reload
        Global.main.background_color = (180, 180, 180)
        self.past_self = self.host.__str__()
        self.past_map = self.host.location.__str__()


class Duplicater(AdvAction):
    def __init__(self, host):
        super().__init__(host)
        self.energy = 3
        self.delay = 8
        self.past_self = None

    def on_cast(self):
        def casting():
            if channel.effect(5):
                Particle.make('portal', self.host.pos.get_center(), offset=128)

        def on_finish():
            Particle.make('sonic', self.host.vec)
        channel = self.host.states.add('Channel', 60)
        channel.on_update = casting
        channel.on_finish = on_finish
