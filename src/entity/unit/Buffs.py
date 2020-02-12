from src.entity.unit.Buff import Buff, BuffTags


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

    def add(self, buff, duration, var=0, load=False, stack=True):
        if not self.get('Immune'):
            preexisting = self.get(buff)
            if not stack or not preexisting:
                for i in Buff.__subclasses__():
                    if i.__name__ == buff:
                        buff = i(self.host, buff, duration, var)
                        break
                if buff.is_valid():
                    self.buffs.append(buff)
                    if load:
                        buff.on_load()
                    else:
                        buff.on_start()
                return buff
            else:
                preexisting.on_stack(duration, var)
                return preexisting

    def clear(self, fn):
        r = 0
        for i in self.buffs:
            if fn(i):
                i.end()
                r = 1
        return r

    def trigger(self, arg):
        for i in self.buffs:
            i.trigger(arg)

    def dispel(self):
        self.clear(lambda x: BuffTags.magic in x.get_tags())
