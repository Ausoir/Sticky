from src.entity.Particle import Particle
from src.game import Global
from src.game.Tags import Tags


class Buff:
    def __init__(self, host, name, duration, var):
        self.tags = self.get_tags()
        self.name = name
        self.host = host
        self.duration = duration
        self.var = var
        self.frame = 0

    def __str__(self):
        return '[' + self.name + ',' + str(self.duration) + ',' + str(self.var) + ']'

    def get_tags(self):
        return []

    def describe(self):
        return self.name + '\nDuration:' + str(self.duration)

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
        return 'Target object has a +' + self.var + ' modification.'

    def on_stack(self, duration, var):
        self.var = self.var + var


class Hunger(Buff):
    def describe(self):
        return 'You cannot travel or perform any time consuming actions.'

    def is_valid(self):
        if Tags.insubstantial not in self.host.tags:
            return True


class Nausea(Buff):
    def describe(self):
        from src.tools.Dialog import Dialog
        return 'You cannot eat for ' + Dialog.day(self.var) + '.'

    def trigger(self, arg):
        if arg[0] == 'time':
            self.var -= arg[1]
            if self.var <= 0:
                self.end()


class Glow(Buff):
    def describe(self):
        return 'You emit light.'

    def on_stack(self, duration, var):
        self.duration = max(self.duration, duration)
        self.var = max(self.var, var)

    def on_update(self):
        self.host.glow(self.var)


class Revive(Buff):
    def describe(self):
        from src.tools.Dialog import Dialog
        return Dialog.get('dsc_revive')

    def on_stack(self, duration, var):
        self.duration = duration
        self.var = var


class Bleed(Buff):
    def get_tags(self):
        return [BuffTags.harmful]

    def describe(self):
        dmg = str(int(self.duration / 100))
        return 'Take ' + dmg + ' damage over ' + str(self.duration) + ' ticks.'

    def is_valid(self):
        if Tags.flesh in self.host.tags and Tags.insubstantial not in self.host.tags:
            return True

    def on_stack(self, duration, var):
        self.duration += duration

    def on_update(self):
        if not self.duration % 100:
            self.host.hit(1, hitter=self)
        if self.effect(9):
            Particle.make('blood', self.host.vec)

    def trigger(self, arg):
        if arg[0] == 'remove':
            self.var = 1
            self.end()


class Distraction(Buff):
    def get_tags(self):
        return [BuffTags.harmful]

    def describe(self):
        return 'Next attack will kill.'

    def on_stack(self, duration, var):
        self.duration = max(self.duration, duration)


class Cripple(Buff):
    def get_tags(self):
        return [BuffTags.harmful]

    def describe(self):
        return 'You are unable to jump.'

    def is_valid(self):
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            return True

    def on_stack(self, duration, var):
        self.duration = max(duration, self.duration)

    def on_update(self):
        if self.effect(19):
            self.host.form.randomize_once(8)

    def on_start(self):
        self.host.attributes.speed -= self.var

    def on_load(self):
        self.host.attributes.speed -= self.var

    def on_finish(self):
        self.host.attributes.speed += self.var


class Weak(Buff):
    def get_tags(self):
        return [BuffTags.harmful]

    def describe(self):
        return 'Your defense is set to 0.'

    def on_update(self):
        if self.effect(8):
            Particle.make('sweat', self.host.vec)


class Exhaustion(Buff):
    def get_tags(self):
        return [BuffTags.harmful]

    def describe(self):
        return 'Your resting time is quadrupled.'

    def on_update(self):
        if self.effect(8):
            Particle.make('sweat', self.host.vec)


class Sick(Buff):
    def get_tags(self):
        return [BuffTags.harmful]

    def describe(self):
        return 'You will die when this effect expires.'

    def is_valid(self):
        if Tags.insubstantial not in self.host.tags:
            return True

    def on_update(self):
        if self.effect(6):
            Particle.make('poison', self.host.vec)

    def on_finish(self):
        if self.var == 0:
            if not self.host.states.get('Healthy'):
                self.host.die()

    def trigger(self, arg):
        if arg[0] == 'remove':
            self.var = 1
            self.end()


class Fire(Buff):
    def get_tags(self):
        return [BuffTags.magic]

    def describe(self):
        return 'You are immune to fire.'

    def on_update(self):
        self.host.pos.light = 40
        if self.effect(6):
            Particle.make('kindle', self.host.vec)

    def trigger(self, arg):
        if arg[0] == 'attack':
            arg[1].states.add('Burn', 16)


class Shock(Buff):
    def get_tags(self):
        return [BuffTags.magic, BuffTags.harmful]

    def describe(self):
        return 'Your stamina is draining.'

    def on_update(self):
        self.host.pos.light = 40
        if self.effect(12):
            self.host.action.set('hit')
            self.host.attributes.breath = max(0, self.host.attributes.breath - 1)
            self.host.attributes.exert(0, 1)
            self.host.attributes.exert(1, 1)
            Particle.make('shock', self.host.vec)


class Burn(Buff):
    def get_tags(self):
        return [BuffTags.magic, BuffTags.harmful]

    def describe(self):
        return 'Constantly take damage and spread to nearby flammables.'

    def is_valid(self):
        if Tags.indestructible not in self.host.tags and Tags.is_combustible(self.host.tags)\
                and not self.host.states.get('Fire'):
            for i in self.host.pos.things:
                if i.name in ['Water', 'Surface']:
                    return False
            return True

    def on_start(self):
        self.host.hit(1, hitter=self)
        if Tags.wood in self.host.tags:
            self.duration = 40

    def on_update(self):
        self.var += 1
        if not self.var % 2:
            Particle.make('burn', self.host.vec, glow=1)
            if not self.var % 4:
                self.host.hit(1, hitter=self)
                x = Global.r.rand_int(-1, 1)
                y = Global.r.rand_int(-1, 1)
                for thing in self.host.get_offset_tile(x, y).things:
                    thing.states.add('Burn', 12)
                self.var = 0


class Levitate(Buff):
    def get_tags(self):
        return [BuffTags.magic]

    def describe(self):
        return 'You are flying.'

    def on_stack(self, duration, var):
        self.duration = max(self.duration, duration)

    def on_update(self):
        Particle.make('zip', self.host.pos.get_center())


class Banish(Buff):
    def get_tags(self):
        return [BuffTags.magic, BuffTags.harmful]

    def describe(self):
        return 'You are being banished to the abyss.'

    def on_finish(self):
        self.host.remove()

    def on_update(self):
        if self.effect(14):
            Particle.make('zwip', self.host.vec)


class Effect(Buff):
    def get_tags(self):
        return [BuffTags.magic]

    def describe(self):
        return 'Produces visual effect.'

    def on_update(self):
        if self.effect(6):
            Particle.make(self.var, self.host.pos.get_center())


class Speed(Buff):
    def get_tags(self):
        return [BuffTags.harmful]

    def describe(self):
        return 'Your move speed is altered.'

    def is_valid(self):
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            return True

    def on_start(self):
        self.host.attributes.speed += self.var

    def on_load(self):
        self.host.attributes.speed += self.var

    def on_finish(self):
        self.host.attributes.speed -= self.var


class Venom(Buff):
    def describe(self):
        return 'Attacks will cause poisoning.'

    def trigger(self, arg):
        if arg[0] == 'attack':
            arg[1].states.add('Sick', self.var)


class Healthy(Buff):
    def describe(self):
        return 'You are immune to Sickness for the duration.'

    def on_stack(self, duration, var):
        self.duration += duration
        if self.duration > 500:
            self.duration = -1
        self.var = max(self.var, var)

    def trigger(self, arg):
        if arg[0] == 'time':
            self.var -= 1
            if self.var <= 0:
                self.end()


class Channel(Buff):
    def describe(self):
        return 'You are channeling magic.'


class Barkskin(Buff):
    def describe(self):
        return 'You are immune to weak attacks but vulnerable to fire.'

    def is_valid(self):
        return Tags.wood not in self.host.tags

    def on_start(self):
        Particle.make('mist', self.host.vec)
        self.host.tags.append(Tags.wood)

    def on_finish(self):
        self.host.tags.remove(Tags.wood)


class Slowfall(Buff):
    def describe(self):
        return 'You are immune to falling and cause no fall damage.'

    def is_valid(self):
        return Tags.lightweight not in self.host.tags

    def on_start(self):
        Particle.make('mist', self.host.vec)
        self.host.tags.append(Tags.lightweight)

    def on_finish(self):
        self.host.tags.remove(Tags.lightweight)


class Lichform(Buff):
    def describe(self):
        return 'You are immune to bleeding, sickness, and hunger.'

    def is_valid(self):
        return Tags.insubstantial not in self.host.tags

    def on_start(self):
        Particle.make('mist', self.host.vec)
        self.host.tags.append(Tags.insubstantial)

    def on_finish(self):
        self.host.tags.remove(Tags.insubstantial)


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

    def on_finish(self):
        self.host.tags.remove(Tags.lightweight)


class Influence(Buff):
    def get_tags(self):
        return [BuffTags.magic, BuffTags.harmful]

    def describe(self):
        return 'You are forced an action.'

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
        self.host.form.show(False)

    def on_load(self):
        self.on_start()

    def on_finish(self):
        self.host.form.show(True)


class Immune(Buff):
    def describe(self):
        return 'You are immune to all status effects and resistant to dispell.'


class Foresee(Buff):
    def describe(self):
        return 'You are experiencing the future.'

    def on_update(self):
        if self.effect(5):
            Particle.make('portal', self.host.pos.get_center(), offset=128)

    def on_finish(self):
        self.trigger(None)


class Charging(Buff):
    def describe(self):
        return 'You are gathering power.'

    def on_update(self):
        if self.effect(2):
            Particle.make('wind', self.host.pos.get_center(), offset=128)

    def on_stack(self, duration, var):
        self.duration = max(self.duration, duration)
        self.var = self.var + var
