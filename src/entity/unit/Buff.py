from src.entity.Effect import Effect
from src.game.Tags import Tags
from src.tools.Random import Random


class Buff:
    def __init__(self, host, name, duration, var):
        self.name = name
        self.host = host
        self.duration = duration
        self.var = var
        self.frame = 0

    def __str__(self):
        return '[' + self.name + ',' + str(self.duration) + ',' + str(self.var) + ']'

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


class Bleed(Buff):
    def is_valid(self):
        if Tags.flesh in self.host.tags:
            return 1

    def on_finish(self):
        self.host.hit(1)

    def on_stack(self, duration, var):
        self.duration = int(self.duration / 2)

    def on_update(self):
        if self.effect(9):
            Effect.make('blood', self.host.vec)


class Fire(Buff):
    def on_update(self):
        if self.effect(6):
            Effect.make('kindle', self.host.vec)


class Air(Buff):
    def on_update(self):
        Effect.make('wind', self.host.pos[0].get_center(), offset=24)


class Rift(Buff):
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
    def on_update(self):
        if self.effect(6):
            Effect.make('shock', self.host.vec)


class Burn(Buff):
    def is_valid(self):
        if Tags.metal not in self.host.tags:
            return 1

    def on_start(self):
        if Tags.wood in self.host.tags:
            self.duration = 40

    def on_update(self):
        self.var += 1
        if not self.var % 8:
            self.host.hit(1)
            x = Random.rand_int(-1, 1)
            y = Random.rand_int(-1, 1)
            for thing in self.host.get_offset_tile(x, y).things:
                thing.states.add('Burn', 8)
        Effect.make('burn', self.host.vec)


class Levitate(Buff):
    def is_valid(self):
        if self.host.gravity:
            return 1

    def on_start(self):
        self.host.gravity = 0

    def on_load(self):
        self.host.gravity = 0

    def on_finish(self):
        self.host.gravity = 1

    def on_update(self):
        Effect.make('zip', self.host.pos[0].get_center())


class Banish(Buff):
    def on_finish(self):
        self.host.remove()

    def on_update(self):
        if self.effect(2):
            Effect.make('zwip', self.host.vec, offset=8)


class Stun(Buff):
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
        self.host.gravity = 1

    def on_update(self):
        if self.effect(6):
            Effect.make('zap', self.host.pos[0].get_center())
