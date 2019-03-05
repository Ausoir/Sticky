from src.entity.Effect import Effect
from src.game.Tags import Tags


class Buffs:
    MODE_LOAD = 0
    MODE_BEGIN = 1
    MODE_UPDATE = 2
    MODE_OVERLAP = 3
    MODE_FINISH = 4

    def __init__(self, host):
        self.host = host
        self.buffs = []
        self.current = None
        self.current_mode = None

    def __str__(self):
        r = []
        for i in self.buffs:
            r.append('[' + i[1] + ',' + str(i[2]) + ',' + str(i[3]) + ']')
        return ','.join(r)

    def load(self, buffs):
        for i in buffs:
            self.add(i[0], i[1], i[2], Buffs.MODE_LOAD)  # fn, duration, var

    def update(self):
        for k, i in enumerate(self.buffs):
            self.current = i
            if i[2] == 0:
                self.perform(i, Buffs.MODE_FINISH)
                self.buffs.pop(k)
            else:
                self.perform(i, Buffs.MODE_UPDATE)
                i[0]()
                if i[2] > 0:
                    i[2] -= 1

    def get(self, buff):
        for i in self.buffs:
            if buff == i[1]:
                return i
        return None

    def add(self, buff, duration, var=0, mode=MODE_BEGIN):
        preexisting = self.get(buff)
        if not preexisting:
            fn = getattr(self, buff)
            buff = [fn, buff, duration, var]
            self.buffs.append(buff)
            self.perform(buff, mode)
        else:
            preexisting[2] = duration
            self.perform(preexisting, Buffs.MODE_OVERLAP)

    def perform(self, buff, mode):
        self.current_mode = mode
        self.current = buff
        buff[0]()

    def clear(self, force):
        r = 0
        for i in self.buffs:
            if force or i[2] >= 0:
                self.end(i)
                r = 1
        return r

    def end(self, arg=None):
        if arg:
            arg[2] = 0
        else:
            self.current[2] = 0

    def var(self, arg=None, value=None):
        if arg:
            if value:
                arg[3] = value
            return arg[3]
        else:
            if value:
                self.current[3] = value
            return self.current[3]

    def bleed(self):
        if self.current_mode == Buffs.MODE_BEGIN or self.current_mode == Buffs.MODE_LOAD:
            if Tags.flesh not in self.host.tags:
                self.end()
                self.var(value=-1)
        var = self.var()
        if var > 9:
            Effect.make('blood', self.host.motion_pos)
            self.var(value=0)
        elif var >= 0:
            self.var(value=var+1)
        if self.current_mode == Buffs.MODE_FINISH and var >= 0:
            self.host.hit(1)

    def fire(self):
        self.var(value=self.var()+1)
        if not self.var() % 6:
            Effect.make('kindle', self.host.motion_pos)

    def air(self):
        Effect.make('wind', self.host.pos[0].get_center())

    def conjuration(self):
        Effect.make('barrier', self.host.motion_pos, offset=0)

    def burn(self):
        self.var(value=self.var()+1)
        if not self.var() % 4:
            self.host.hit(1)
        Effect.make('burn', self.host.motion_pos)
        if self.current_mode == Buffs.MODE_BEGIN:
            if Tags.wood in self.host.tags:
                self.current[2] = 40

    def levitate(self):
        if self.current_mode == Buffs.MODE_BEGIN or self.current_mode == Buffs.MODE_LOAD:
            if self.host.gravity:
                self.host.gravity = 0
            else:
                self.end()
                self.var(value=1)
        elif self.current_mode == Buffs.MODE_FINISH and not self.var():
            self.host.gravity = 1
        Effect.make('zip', self.host.pos[0].get_center())

    def rift(self):
        if self.current_mode == Buffs.MODE_FINISH:
            obj = self.host.location.get_object(self.var())
            if obj:
                obj.remove()

    def stun(self):
        if self.current_mode == Buffs.MODE_BEGIN or self.current_mode == Buffs.MODE_LOAD:
            self.host.action.set('hit')
            self.host.delay = self.current[2]
        else:
            self.var(value=self.var()+1)
            if not self.var() % 6:
                Effect.make('zap', self.host.motion_pos, offset=0)

    def barrier(self):
        if self.current_mode == Buffs.MODE_BEGIN:
            self.host.durability += 3
        elif self.current_mode == Buffs.MODE_FINISH:
            self.host.durability -= 3
            self.host.hit(0)
        self.var(value=self.var()+1)
        if not self.var() % 10:
            Effect.make('barrier', self.host.motion_pos, offset=0)
