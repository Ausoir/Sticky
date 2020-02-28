from src.entity.Particle import Particle
from src.game import Global


class Buff:
    def __init__(self, host, name, duration, var):
        self.name = name
        self.host = host
        self.duration = duration
        self.var = var
        self.frame = 0

    def __str__(self):
        return '[' + self.name + ',' + str(self.duration) + ',' + str(self.var) + ']'

    def get_tags(self):
        return []

    def get_display_name(self):
        return self.name.title()

    def describe_duration(self):
        from src.tools.Dialog import Dialog
        if self.duration == -1:
            return Dialog.get('persistent')
        elif self.duration < -1:
            return Dialog.hours(-self.duration - 1)
        else:
            return str(self.duration)

    def describe(self):
        return self.get_display_name() + '\nDuration: ' + self.describe_duration()

    def update(self):
        if self.duration == 0:
            return 1
        elif self.duration > 0:
            self.duration -= 1

    def effect(self, frame):
        self.frame += 1
        return not self.frame % frame

    def end(self):
        self.duration = 0

    def is_valid(self):
        return not self.host.states.get('Immune')

    def on_start(self):
        pass

    def on_load(self):
        pass

    def on_stack(self, duration, var):
        pass

    def on_finish(self):
        pass

    def on_update(self):
        pass

    def trigger(self, arg):
        if arg[0] == 'time':
            if self.duration < -1:
                self.duration += arg[1]
                if self.duration >= -1:
                    self.end()


class BuffTags:
    magic = 'm'
    harmful = 'h'


class Glow(Buff):
    def get_tags(self):
        return [BuffTags.magic]

    def describe(self):
        return 'You emit light.'

    def on_stack(self, duration, var):
        self.duration = max(self.duration, duration)
        self.var = max(self.var, var)

    def on_update(self):
        self.host.pos.glow(self.var)


class Revive(Buff):
    def describe(self):
        from src.tools.Dialog import Dialog
        return Dialog.get('dsc_revive')

    def on_stack(self, duration, var):
        self.duration = duration
        self.var = var


class Health(Buff):
    def get_tags(self):
        if self.var < 0:
            return [BuffTags.magic, BuffTags.harmful]
        return [BuffTags.magic]

    def get_display_name(self):
        if self.var < 0:
            return 'Harm'
        return self.name

    def describe(self):
        if self.var < 0:
            return 'Take constant damage.'
        else:
            return 'Constantly heal.'

    def on_stack(self, duration, var):
        if self.var > 0 == var > 0:
            self.duration = max(self.duration, duration)
        else:
            self.duration = duration
        self.var += var

    def on_update(self):
        if self.effect(10):
            self.host.decay(-self.var)


class Damage(Buff):
    def describe(self):
        return 'You inflict more damage.'

    def on_stack(self, duration, var):
        self.duration = duration
        self.var += var
        self.on_finish()
        self.on_start()

    def on_start(self):
        self.host.strength += self.var

    def on_load(self):
        self.host.strength += self.var

    def on_finish(self):
        self.host.strength -= self.var


class Brand(Buff):
    def get_display_name(self):
        return self.var

    def describe(self):
        return 'Creates special on hit effect.'

    def trigger(self, arg):
        if arg[0] == 'attack':
            from src.game.Script import Script
            Script.execute_code(self.var, host=arg[1])


class Burn(Buff):
    def get_tags(self):
        return [BuffTags.magic, BuffTags.harmful]

    def describe(self):
        return 'Constantly take damage and spread to nearby flammables.'

    def is_valid(self):
        if self.host.tags.is_combustible():
            return super().is_valid()

    def on_start(self):
        if self.host.tags.get('mat') == 'wood':
            self.duration += 32

    def on_update(self):
        self.var += 1
        if not self.var % 2:
            self.host.pos.glow(12)
            Particle.make('burn', self.host.vec, glow=1)
            if not self.var % 4:
                self.var = 0
                self.host.decay(1)
                from src.entity.Stock import Stock
                if self.host.pos.name.startswith('wood') and Global.r.rand_int(1, 8) == 1:
                    Stock.make('Plank', self.host.pos)
                    self.host.pos.set_terrain('.')
                else:
                    x = Global.r.rand_int(-1, 1)
                    y = Global.r.rand_int(-1, 1)
                    neighbor = self.host.pos.get_neighbor(x, y)
                    if neighbor:
                        if not neighbor.things and neighbor.name.startswith('wood'):
                            Stock.make('Flame', neighbor)
                        else:
                            for thing in neighbor.things:
                                thing.states.add('Burn', 12)


class Banish(Buff):
    def get_tags(self):
        return [BuffTags.magic, BuffTags.harmful]

    def describe(self):
        return 'Become banished to the abyss.'

    def end(self):
        self.var = 1
        super().end()

    def on_finish(self):
        if self.var == 0:
            self.host.remove()

    def on_update(self):
        if self.effect(4):
            Particle.make('zwip', self.host.vec)


class Effect(Buff):
    def get_tags(self):
        return [BuffTags.magic]

    def describe(self):
        return 'Produces effect.'

    def on_update(self):
        if self.effect(6):
            Particle.make(self.var, self.host.pos.get_center())


class Speed(Buff):
    def get_tags(self):
        if self.var < 0:
            return [BuffTags.magic, BuffTags.harmful]
        return [BuffTags.magic]

    def get_display_name(self):
        if self.var < 0:
            return 'Slow'
        return 'Fast'

    def describe(self):
        return 'Your move speed is altered.'

    def is_valid(self):
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            return super().is_valid()

    def on_start(self):
        Particle.make('wind', self.host.vec)
        self.host.tags.increment('spd', self.var, add=True)

    def on_finish(self):
        self.host.tags.increment('spd', -self.var, remove=True)

    def trigger(self, arg):
        super().trigger(arg)
        if arg[0] == 'hit':
            self.end()


class Shapeshift(Buff):
    def __str__(self):
        return '[' + self.name + ',' + str(self.duration) + ',\'' + str(self.var) + '\']'

    def get_tags(self):
        return [BuffTags.magic, BuffTags.harmful]

    def describe(self):
        return 'You are shapeshifting.'

    def on_start(self):
        Particle.make('mist', self.host.vec)
        from src.entity.unit.Humanoid import Humanoid
        if isinstance(self.host, Humanoid):
            self.host.drop()
            self.host.unarmor()
            self.host.unheadgear()
            self.host.inventory.drop_all()
        from src.entity.Stock import Stock
        unit = Stock.make(self.var, self.host.pos)
        unit.tags.remove('ai')
        self.var = self.change_host(unit).__str__()

    def on_stack(self, duration, var):
        self.duration = duration
        self.var = var
        self.on_finish()
        self.on_start()

    def on_finish(self):
        Particle.make('mist', self.host.vec)
        from src.entity.Stock import Stock
        from src.tools.Data import Data
        data = Data.parse(self.var)
        unit = Stock.get(self.host.location, data[2], data)
        unit.pos = self.host.pos
        unit.add()
        self.change_host(unit)

    def change_host(self, unit):
        old_host = self.host
        for i in self.host.states.buffs:
            i.host = unit
        unit.states = old_host.states
        from src.entity.unit.Buffs import Buffs
        old_host.states = Buffs(old_host)
        old_host.remove()
        if old_host == Global.player.character:
            Global.player.set_player(unit)
        return old_host


class Invisible(Buff):
    def __init__(self, host, name, duration, var):
        super().__init__(host, name, duration, var)
        self.orig = None
        self.begin = True

    def get_tags(self):
        return [BuffTags.magic]

    def describe(self):
        return 'You are invisible.'

    def on_start(self):
        Particle.make('mist', self.host.pos.get_center())
        self.on_load()
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            for unit in self.host.get_team(ally=False):
                if unit.pilot.priority == 1:
                    unit.pilot.lose(self.host)

    def on_load(self):
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            self.host.stealth += 40

    def on_finish(self):
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            self.host.stealth -= 40
        self.host.show(True)

    def on_update(self):
        if self.begin:
            self.begin = False
            self.host.show(False)

    def trigger(self, arg):
        super().trigger(arg)
        r = False
        if arg[0] == 'move':
            r = self.var == 1
        elif arg[0] == 'act':
            r = self.var != -1
        elif arg[0] == 'attack':
            r = self.var != -1
        elif arg[0] == 'hit':
            r = self.var != -1
        elif arg[0] == 'time' and arg[1] > 0:
            r = self.var != -1
        if r:
            self.end()


class Invulnerable(Buff):
    def describe(self):
        return 'Immune to damage.'

    def is_valid(self):
        if not self.host.hittable:
            return super().is_valid()

    def on_start(self):
        self.host.hittable = 0

    def on_finish(self):
        self.host.hittable = 1


class Immune(Buff):
    def describe(self):
        return 'Immune to status effects.'


class Concentration(Buff):
    def describe(self):
        return 'You are concentrated.'

    def is_valid(self):
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            return super().is_valid()

    def effect_on_load(self):
        if self.host.get_skill('heightened sense'):
            copy = self.host.sight
            from src.map.Tile import Tile
            new = []
            for i in copy:
                if i != Tile.COLLIDE_FOG:
                    new.append(i)
            self.host.sight = new
        if self.host.get_skill('hide'):
            self.host.states.add('Invisible', -1, var=1)

    def effect_on_apply(self):
        if self.host.get_skill('iron will'):
            for i in self.host.states.buffs:
                if BuffTags.harmful in i.get_tags():
                    i.end()
                    return

    def on_start(self):
        self.effect_on_load()
        Particle.make('sweat', self.host.pos.get_center(), offset=4)
        self.effect_on_apply()

    def on_load(self):
        self.effect_on_load()

    def on_stack(self, duration, var):
        self.effect_on_apply()
        self.duration = duration

    def on_finish(self):
        if self.host.get_skill('heightened sense'):
            from src.map.Tile import Tile
            self.host.sight.append(Tile.COLLIDE_FOG)

    def trigger(self, arg):
        super().trigger(arg)
        if arg[0] == 'spend':
            self.host.action.frame = 0
            Particle.make('sweat', self.host.pos.get_center())
            self.duration = 1


class Vengeance(Buff):
    def describe(self):
        return 'At 4 stacks nearby enemies will be pushed away and knocked down.'

    def on_stack(self, duration, var):
        self.var += 1
        self.duration = duration
        if self.var >= 3:
            from src.tools import Direction
            from src.entity.unit.Actions import Actions
            for i in Direction.coord.values():
                tile = self.host.pos.get_neighbor(i[0], i[1])
                if tile:
                    for thing in tile.things:
                        thing.move(i[0], i[1])
                        Actions.knockdown(thing)
                    Particle.make('batter', tile.get_center())
            self.host.location.sound.register(self.host.pos, 1, file='critical')
            self.end()


class Barkskin(Buff):
    def get_tags(self):
        return [BuffTags.magic]

    def describe(self):
        return 'Incoming damage are reduced by 2 but you are now vulnerable to fire and act slower.'

    def is_valid(self):
        mat = self.host.tags.get('mat')
        if mat and mat != 'wood':
            return super().is_valid()

    def on_start(self):
        Particle.make('mist', self.host.vec)
        self.var = self.host.tags.get('mat')
        self.host.tags.set('mat', 'wood')
        self.host.tags.increment('spd', -1, add=True)

    def on_finish(self):
        self.host.tags.set('mat', self.var)
        self.host.tags.increment('spd', 1, remove=True)


class Petrified(Buff):
    def get_tags(self):
        return [BuffTags.magic]

    def describe(self):
        return 'Incoming damage are reduced by 4 but you are now immobile.'

    def is_valid(self):
        mat = self.host.tags.get('mat')
        if mat and mat != 'metal':
            return super().is_valid()

    def on_start(self):
        Particle.make('mist', self.host.vec)
        self.var = self.host.tags.get('mat')
        self.host.tags.set('mat', 'metal')
        self.host.tags.increment('spd', -12, add=True)

    def on_finish(self):
        self.host.tags.set('mat', self.var)
        self.host.tags.increment('spd', 12, remove=True)


class Vision(Buff):
    def __str__(self):
        return '[' + self.name + ',' + str(self.duration) + ',\'' + str(self.var) + '\']'

    def get_tags(self):
        return [BuffTags.magic]

    def describe(self):
        return 'Improves sight.'

    def is_valid(self):
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            return super().is_valid()

    def on_start(self):
        Particle.make('portal', self.host.vec)
        self.var = self.host.sight
        from src.map.Tile import Tile
        self.host.sight = [Tile.COLLIDE_MAGIC]

    def on_finish(self):
        self.host.sight = self.var


class Levitate(Buff):
    def get_tags(self):
        return [BuffTags.magic]

    def describe(self):
        return 'Levitate off the ground.'

    def is_valid(self):
        return not self.host.tags.get('fly')

    def on_start(self):
        Particle.make('wind', self.host.vec)
        self.host.tags.set('fly', 1, add=True)

    def on_finish(self):
        self.host.tags.remove('fly')

    def trigger(self, arg):
        if arg[0] == 'time':
            if arg[1] > 0:
                self.end()

    def on_update(self):
        if self.effect(16):
            Particle.make('wind', self.host.vec)
