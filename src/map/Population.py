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

    @staticmethod
    def get_from_id(group, identification):
        for i in group:
            if i.id == identification:
                return i

    @staticmethod
    def get_from_name(group, identification):
        for i in group:
            if i.name == identification:
                return i
