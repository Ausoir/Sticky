from src.form.Effect import Effect


class Buffs:
    MODE_LOAD = 0
    MODE_BEGIN = 1
    MODE_UPDATE = 2
    MODE_FINISH = 3

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
            i[2] -= 1
            if i[2] <= 0:
                self.perform(i, Buffs.MODE_FINISH)
                self.buffs.pop(k)
                continue
            self.perform(i, Buffs.MODE_UPDATE)
            i[0]()

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

    def perform(self, buff, mode):
        self.current_mode = mode
        self.current = buff
        buff[0]()

    def fire(self):
        self.current[3] += 1
        if not self.current[3] % 6:
            Effect.kindle(self.host.motion_pos)

    def air(self):
        Effect.zip(self.host.pos[0].get_center())

    def conjuration(self):
        Effect.barrier(self.host.pos[0].get_center())

    def burn(self):
        if self.current_mode == Buffs.MODE_BEGIN:
            if self.get('insulation'):
                self.current[2] = 0
            else:
                self.host.hit(1)
                Effect.burn(self.host.pos[0].get_center())
        elif self.current_mode == Buffs.MODE_UPDATE:
            self.host.hit(0)
            Effect.burn(self.host.pos[0].get_center())

    def levitate(self):
        if self.current_mode == Buffs.MODE_BEGIN:
            if self.host.gravity:
                self.host.gravity = 0
            else:
                self.current[2] = 0
                self.current[3] = 1
        elif self.current_mode == Buffs.MODE_FINISH and not self.current[3]:
            self.host.gravity = 1
        Effect.zip(self.host.pos[0].get_center())

    def insulation(self):
        self.current[3] += 1
        if not self.current[3] % 4:
            Effect.wind(self.host.pos[0].get_center())

    def rift(self):
        if self.current_mode == Buffs.MODE_FINISH:
            obj = self.host.location.get_object(self.current[3])
            if obj:
                obj.remove()

    def stun(self):
        if self.current_mode == Buffs.MODE_BEGIN or self.current_mode == Buffs.MODE_LOAD:
            self.host.action.set('hit')
            self.host.delay = self.current[2]
