from src.entity.unit.Buff import Buff, StatBuff
from src.game.Turn import Turn


class Buffs:
    def __init__(self, host):
        self.host = host
        self.buffs = []
        self.current = None
        self.current_mode = None

    def __str__(self):
        return ','.join(i.__str__() for i in self.buffs)

    def load(self, buffs):
        for i in buffs:
            self.add(i[0], i[1], i[2], load=True)  # fn, duration, var

    def update(self):
        done = True
        for k, i in enumerate(self.buffs):
            self.current = i
            if i.update():
                if not i.on_finish():
                    if len(self.buffs) > k:
                        self.buffs.pop(k)
            elif self.host.removed == 0:
                i.on_update()
                done = False
        if done and not self.buffs:
            self.on_remove()

    def get(self, name):
        for i in self.buffs:
            if i.name == name and i.duration != 0:
                return i
        return None

    @staticmethod
    def get_buff(buff_name, host, duration, var):
        title = buff_name.title()
        for i in Buff.__subclasses__() + StatBuff.__subclasses__():
            if i.__name__ == title:
                return i(host, title, duration, var)

    def add(self, buff_name, duration, var=0, load=False, stack=True):
        if duration > -2:
            preexisting = self.get(buff_name)
            if not stack or not preexisting or 'stack' not in preexisting.get_tags():
                buff = Buffs.get_buff(buff_name, self.host, duration, var)
                if buff:
                    if load:
                        self.buffs.append(buff)
                    elif buff.is_valid():
                        self.buffs.append(buff)
                        buff.on_start()
                        self.on_add()
                    else:
                        return None
                    return buff
                else:
                    return None
            else:
                preexisting.on_stack(duration, var)
                return preexisting

    def clear(self, fn):
        r = 0
        for i in self.buffs:
            if fn(i):
                i.end()
                r += 1
        if not self.buffs:
            self.on_remove()
        return r

    def trigger(self, arg):
        for i in self.buffs:
            i.trigger(arg)

    def dispel(self):
        if not self.get('Immune'):
            self.clear(lambda x: 'magic' in x.get_tags())

    def on_load(self):
        for i in self.buffs:
            i.on_load()
        self.on_add()

    def on_sleep(self, time):
        hour_tick = int(Turn.HOUR_FRAME / Turn.rounds)
        for i in self.buffs:
            if i.duration > 0:
                if time > 0:
                    i.duration = max(1, i.duration - (time * hour_tick))
                i.trigger(['time', time])

    def on_add(self):
        if self.buffs:
            from src.game.Turn import Turn
            if not Turn.has(self.update):
                Turn.add(self.update)

    def on_remove(self):
        from src.game.Turn import Turn
        Turn.remove(self.host.states.update)

    def set_host(self, host):
        for i in self.buffs:
            host.states.add(i.name, i.duration, i.var)
        self.buffs = []
        self.on_remove()
