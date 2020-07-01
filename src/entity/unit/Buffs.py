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
        for k, i in enumerate(self.buffs):
            self.current = i
            if i.update():
                i.on_finish()
                self.buffs.pop(k)
            else:
                i.on_update()

    def get(self, name):
        for i in self.buffs:
            if i.name == name and i.duration != 0:
                return i
        return None

    def add(self, buff_name, duration, var=0, load=False, stack=True):
        preexisting = self.get(buff_name)
        if not stack or not preexisting or 'stack' not in preexisting.get_tags():
            buff = None
            for i in Buff.__subclasses__() + StatBuff.__subclasses__():
                if i.__name__ == buff_name:
                    buff = i(self.host, buff_name, duration, var)
                    break
            if buff:
                if load:
                    self.buffs.append(buff)
                elif buff.is_valid():
                    self.buffs.append(buff)
                    buff.on_start()
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
        return r

    def trigger(self, arg):
        for i in self.buffs:
            i.trigger(arg)

    def dispel(self):
        self.clear(lambda x: 'magic' in x.get_tags())

    def on_load(self):
        for i in self.buffs:
            i.on_load()

    def on_sleep(self, time):
        for i in self.buffs:
            if i.duration > 0:
                i.duration = max(0, i.duration - (time * Turn.HOUR_FRAME))
                i.trigger(['time', time])
