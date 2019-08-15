from src.entity.Effect import Effect
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
        return 1

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


class Modified(Buff):
    def describe(self):
        return 'This object has a +' + self.var + ' modification.'


class Hunger(Buff):
    def describe(self):
        return 'You cannot travel or perform any time consuming actions.'

    def is_valid(self):
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            return 1


class Glow(Buff):
    def describe(self):
        return 'You emit light.'

    def on_stack(self, duration, var):
        self.duration = max(self.duration, duration)
        self.var = max(self.var, var)

    def on_update(self):
        self.host.glow(self.var)


class Bleed(Buff):
    def describe(self):
        dmg = str(int(self.duration / 100))
        return 'Take ' + dmg + ' damage over ' + str(self.duration) + ' ticks.'

    def is_valid(self):
        if Tags.flesh in self.host.tags:
            return 1

    def on_finish(self):
        self.host.hit(self.var)

    def on_stack(self, duration, var):
        self.var += 1
        self.duration += duration

    def on_update(self):
        if not self.duration % 100:
            self.host.hit(1)
        if self.effect(9):
            Effect.make('blood', self.host.vec)


class Distraction(Buff):
    def describe(self):
        return 'Being attacked in this state is likely lethal.'

    def is_valid(self):
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            return 1

    def on_stack(self, duration, var):
        self.duration = max(self.duration, duration)


class Cripple(Buff):
    def describe(self):
        return 'You are unable to jump.'

    def is_valid(self):
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            return 1

    def on_stack(self, duration, var):
        self.duration = max(duration, self.duration)

    def on_update(self):
        if self.effect(19):
            self.host.form.randomize_once(8)


class Weak(Buff):
    def describe(self):
        return 'Your defense is set to 0. Your resting time tripled.'

    def on_update(self):
        if self.effect(8):
            Effect.make('sweat', self.host.vec)


class Sick(Buff):
    def describe(self):
        return 'You will die if this effect expires naturally.'

    def on_update(self):
        if self.effect(6):
            Effect.make('poison', self.host.vec)

    def on_finish(self):
        if self.var == 0:
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
        self.host.pos[0].light = 40
        if self.effect(6):
            Effect.make('kindle', self.host.vec)

    def trigger(self, arg):
        if arg[0] == 'attack':
            arg[1].states.add('Burn', 8)


class Rift(Buff):
    def get_tags(self):
        return [BuffTags.magic]

    def describe(self):
        return 'A portal is bound to you.'

    def on_stack(self, duration, var):
        self.on_finish()
        self.var = var

    def on_finish(self):
        obj = self.host.location.get_object(self.var)
        if obj:
            Effect.make('zwip', obj.pos[0].get_center(), offset=24)
            Effect.make('zwip', self.host.pos[0].get_center(), offset=24)
            obj.remove()


class Shock(Buff):
    def get_tags(self):
        return [BuffTags.magic]

    def describe(self):
        return 'You are immune to shock.'

    def on_update(self):
        self.host.pos[0].light = 40
        if self.effect(6):
            Effect.make('shock', self.host.vec)


class Burn(Buff):
    def get_tags(self):
        return [BuffTags.magic]

    def describe(self):
        return 'Constantly take damage and spread to nearby flammables.'

    def is_valid(self):
        if Tags.indestructible not in self.host.tags and Tags.is_combustible(self.host.tags):
            return 1

    def on_start(self):
        self.host.hit(1)
        if Tags.wood in self.host.tags:
            self.duration = 40

    def on_update(self):
        self.var += 1
        self.host.glow(1)
        if not self.var % 8:
            self.host.hit(1)
            x = Global.r.rand_int(-1, 1)
            y = Global.r.rand_int(-1, 1)
            for thing in self.host.get_offset_tile(x, y).things:
                thing.states.add('Burn', 8)
        Effect.make('burn', self.host.vec)


class Levitate(Buff):
    def get_tags(self):
        return [BuffTags.magic]

    def describe(self):
        return 'You are flying.'

    def is_valid(self):
        if self.host.gravity:
            return 1

    def on_start(self):
        self.host.gravity = 0

    def on_load(self):
        self.host.gravity = 0

    def on_stack(self, duration, var):
        self.duration = max(self.duration, duration)

    def on_finish(self):
        self.host.gravity = 1

    def on_update(self):
        Effect.make('zip', self.host.pos[0].get_center())


class Banish(Buff):
    def get_tags(self):
        return [BuffTags.magic]

    def describe(self):
        return 'You are being banished.'

    def on_finish(self):
        self.host.remove()

    def on_update(self):
        if self.effect(5):
            Effect.make('zwip', self.host.vec, offset=8)


class Stun(Buff):
    def get_tags(self):
        return [BuffTags.magic]

    def describe(self):
        return 'You are stunned.'

    def is_valid(self):
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            return 1

    def on_start(self):
        if self.host.action.set('hit', auto=1):
            self.host.delay = self.duration

    def on_load(self):
        if self.host.action.set('hit', auto=1):
            self.host.delay = self.duration

    def on_finish(self):
        self.host.action.exert(0, 99)

    def on_update(self):
        if self.effect(6):
            Effect.make('zap', self.host.pos[0].get_center())


class Speed(Buff):
    def describe(self):
        return 'Your move speed is altered.'

    def is_valid(self):
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            return 1

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
