from src.entity.unit.Unit import Unit


class Population:
    def __init__(self):
        self.good = []
        self.bad = []
        self.other = []

    def __str__(self):
        r = []
        for i in self.other:
            if i.save:
                r.append('['+i.__str__()+']')
        for i in self.bad:
            if i.save:
                r.append('['+i.__str__()+']')
        for i in self.good:
            if i.save:
                r.append('['+i.__str__()+']')
        return ','.join(r)

    def add(self, unit):
        if not isinstance(unit, Unit):
            self.other.append(unit)
        elif unit.tags.get('bad'):
            self.bad.append(unit)
        else:
            self.good.append(unit)

    def remove(self, unit):
        if unit in self.other:
            self.other.remove(unit)
        elif unit in self.bad:
            self.bad.remove(unit)
        elif unit in self.good:
            self.good.remove(unit)

    def get_units(self):
        return self.good + self.bad

    def get_all(self):
        return self.good + self.bad + self.other

    def get_close(self, pos, mag):
        r = []
        for i in self.get_all():
            if (i.pos - pos).difference() < mag:
                r.append(i)
        return r

    def get_from_pos(self, x, y, group=None):
        if group is None:
            group = self.get_all()
        for i in group:
            if i.pos.x == x and i.pos.y == y:
                return i

    def get_from_name(self, identification, group=None):
        if group is None:
            group = self.get_all()
        for i in group:
            if i.name == identification:
                return i
