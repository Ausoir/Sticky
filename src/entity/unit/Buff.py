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
        return True

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
        self.host.tags.increment('str', self.var, add=True)

    def on_finish(self):
        self.host.tags.increment('str', -self.var, remove=True)


class Armor(Buff):
    def get_tags(self):
        if self.var < 0:
            return [BuffTags.harmful]
        return []

    def get_display_name(self):
        if self.var < 0:
            return 'Sunder'
        return self.name

    def describe(self):
        return 'Your defense is modified by ' + str(self.var)

    def on_stack(self, duration, var):
        self.duration = duration
        self.var = var


class Curse(Buff):
    def get_tags(self):
        return [BuffTags.harmful]

    def describe(self):
        return 'Die when this curse expire.'

    def describe_duration(self):
        from src.tools.Dialog import Dialog
        return Dialog.day(self.var)

    def on_stack(self, duration, var):
        self.duration = duration
        self.var = var

    def on_finish(self):
        self.host.die()


class Weak(Buff):
    def get_tags(self):
        return [BuffTags.harmful]

    def describe(self):
        return 'Your defense is set to 0.'

    def on_update(self):
        if self.effect(8):
            Particle.make('sweat', self.host.vec)


class Fire(Buff):
    def get_tags(self):
        return [BuffTags.magic]

    def describe(self):
        return 'Cause fire.'

    def on_update(self):
        if self.effect(6):
            Particle.make('kindle', self.host.vec, offset=12)

    def trigger(self, arg):
        super().trigger(arg)
        if arg[0] == 'attack':
            arg[1].states.add('Burn', 16)


class Burn(Buff):
    def get_tags(self):
        return [BuffTags.magic, BuffTags.harmful]

    def describe(self):
        return 'Constantly take damage and spread to nearby flammables.'

    def is_valid(self):
        if self.host.tags.is_combustible() and not self.host.states.get('Fire'):
            return True

    def on_start(self):
        self.host.hit(1, hitter=self)
        if self.host.tags.get('mat') == 'wood':
            self.duration += 32

    def on_update(self):
        self.var += 1
        if not self.var % 2:
            Particle.make('burn', self.host.vec, glow=1)
            if not self.var % 4:
                self.host.hit(1, hitter=self)
                x = Global.r.rand_int(-1, 1)
                y = Global.r.rand_int(-1, 1)
                for thing in self.host.pos.get_neighbor(x, y).things:
                    thing.states.add('Burn', 12)
                self.var = 0


class Banish(Buff):
    def get_tags(self):
        return [BuffTags.magic, BuffTags.harmful]

    def describe(self):
        return 'Become banished to the abyss.'

    def on_finish(self):
        self.host.remove()

    def on_update(self):
        if self.effect(14):
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
            return True

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
    def describe(self):
        return 'You are shapeshifting.'

    def is_valid(self):
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            return True

    def on_start(self):
        Particle.make('mist', self.host.vec)
        Global.player.character.unheadgear()
        Global.player.character.unarmor()
        Global.player.character.drop()
        old_form = Global.player.character.name
        from src.entity.Stock import Stock
        old = Global.player.character.tags.get_carry_over()
        old_state = Global.player.character.states
        unit = Stock.get(self.var)
        unit.pos = Global.player.character.pos
        unit.tags.attributes.update(old)
        unit.add()
        Global.player.character.remove()
        Global.player.set_player(unit)
        Global.player.character.states = old_state
        self.var = old_form

    def on_finish(self):
        Particle.make('mist', self.host.vec)
        from src.entity.Stock import Stock
        old = Global.player.character.tags.get_carry_over()
        old_state = Global.player.character.states
        unit = Stock.get(self.var)
        unit.pos = Global.player.character.pos
        unit.tags.attributes.update(old)
        unit.add()
        Global.player.character.remove()
        Global.player.set_player(unit)
        Global.player.character.states = old_state


class Influence(Buff):
    def get_tags(self):
        return [BuffTags.magic, BuffTags.harmful]

    def describe(self):
        return 'You have limited control.'

    def is_valid(self):
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            return True

    def on_update(self):
        self.host.next_action = self.var


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
        if r:
            self.end()


class Invulnerable(Buff):
    def describe(self):
        return 'Immune to damage.'

    def is_valid(self):
        return self.host.hittable

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

    def on_stack(self, duration, var):
        self.duration = duration

    def trigger(self, arg):
        super().trigger(arg)
        if arg[0] == 'spend':
            self.host.action.frame = 0
            Particle.make('sweat', self.host.pos.get_center())
            self.end()


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
                        Actions.knockdown(thing, 20)
                    Particle.make('batter', tile.get_center())
            Global.location.sound.register(self.host.pos, 1, file='hit_impale')
            self.end()


class Barkskin(Buff):
    def describe(self):
        return 'Incoming damage are reduced by 2 but you are now vulnerable to fire and act slower.'

    def is_valid(self):
        mat = self.host.tags.get('mat')
        return mat and mat != 'wood'

    def on_start(self):
        Particle.make('mist', self.host.vec)
        self.var = self.host.tags.get('mat')
        self.host.tags.set('mat', 'wood')
        self.host.tags.increment('spd', -1, add=True)

    def on_finish(self):
        self.host.tags.set('mat', self.var)
        self.host.tags.increment('spd', 1, remove=True)


class Petrified(Buff):
    def describe(self):
        return 'Incoming damage are reduced by 4 but you are now immobile.'

    def is_valid(self):
        mat = self.host.tags.get('mat')
        return mat and mat != 'metal'

    def on_start(self):
        Particle.make('mist', self.host.vec)
        self.var = self.host.tags.get('mat')
        self.host.tags.set('mat', 'metal')
        self.host.tags.increment('spd', -12, add=True)

    def on_finish(self):
        self.host.tags.set('mat', self.var)
        self.host.tags.increment('spd', 12, remove=True)
