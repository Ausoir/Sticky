from src.entity.Attribute import Attribute
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
        if self.duration == -1:
            from src.tools.Dialog import Dialog
            return Dialog.get('persistent')
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
        pass


class BuffTags:
    magic = 'm'
    harmful = 'h'


class Modified(Buff):
    def describe(self):
        return 'Has a +' + self.var + ' modification.'

    def on_stack(self, duration, var):
        self.var = self.var + var


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


class Heal(Buff):
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

    def trigger(self, arg):
        if arg[0] == 'time':
            self.var -= 1
            if self.var <= 0:
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
            return [BuffTags.harmful]
        return []

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


class Venom(Buff):
    def describe(self):
        return 'Cause sickness.'

    def trigger(self, arg):
        if arg[0] == 'attack':
            arg[1].states.add('Heal', self.var, -1)


class Barkskin(Buff):
    def describe(self):
        return 'You are immune to weak attacks but vulnerable to fire.'

    def is_valid(self):
        return self.host.tags.get('mat') != 'wood'

    def on_start(self):
        Particle.make('mist', self.host.vec)
        self.var = self.host.tags.get('mat')
        self.host.tags.set('mat', 'wood')

    def on_finish(self):
        self.host.tags.set('mat', self.var)


class Degenerate(Buff):
    def describe(self):
        return 'You are morphed into a slime.'

    def is_valid(self):
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            return True

    def on_start(self):
        Particle.make('mist', self.host.vec)
        from src.entity.Stock import Stock
        r = Stock.make('Slime', self.host.pos)
        self.var = r.id

    def on_load(self):
        self.on_start()


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

    def get_tags(self):
        return [BuffTags.magic]

    def describe(self):
        return 'You are invisible.'

    def render(self):
        if not Global.player.editor_mode:
            diff = self.host.pos.get_center() - self.host.vec
            self.host.vec.x += diff.x * .07
            self.host.vec.y += diff.y * .07
        else:
            self.orig()

    def on_start(self):
        self.var = self.host.tags.get('col', -1)
        from src.map.Tile import Tile
        self.host.tags.set('col', Tile.COLLIDE_MAGIC)
        self.host.form.show(False)

    def on_load(self):
        from src.map.Tile import Tile
        self.host.tags.set('col', Tile.COLLIDE_MAGIC)
        self.host.form.show(False)

    def on_finish(self):
        if self.var == -1:
            self.host.tags.remove('col')
        else:
            self.host.tags.set('col', self.var)
        self.host.form.show(True)


class Immune(Buff):
    def describe(self):
        return 'Immune to status effects.'


class Foresee(Buff):
    def describe(self):
        return 'You are experiencing the future.'

    def on_update(self):
        if self.effect(5):
            Particle.make('portal', self.host.pos.get_center(), offset=128)

    def on_finish(self):
        self.trigger(None)
