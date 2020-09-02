from src.entity.unit.Unit import Unit


class Population:
    def __init__(self):
        self.teams = [[], [], [], [], []]
        self.other = []

    def __str__(self):
        r = []
        for i in self.other:
            if i.save:
                r.append('['+i.__str__()+']')
        for team in self.teams:
            for i in team:
                if i.save:
                    r.append('['+i.__str__()+']')
        return ','.join(r)

    def add(self, unit):
        if not isinstance(unit, Unit):
            self.other.append(unit)
        else:
            team = unit.tags.get('team', 0)
            self.teams[team].append(unit)

    def remove(self, unit):
        if not isinstance(unit, Unit):
            if unit.removed == 0:
                self.other.remove(unit)
                return True
        else:
            team = unit.tags.get('team', 0)
            if unit in self.teams[team]:
                self.teams[team].remove(unit)
                return True
            else:
                for k, i in enumerate(self.teams):
                    if k != team and unit in i:
                        i.remove(unit)
                        return True

    def adjust(self, unit):
        if self.remove(unit):
            self.add(unit)

    def get_units(self):
        r = []
        for i in self.teams:
            r += i
        return r

    def get_team(self, team):
        if team == 0:
            return []
        else:
            return self.teams[team]

    def get_foe(self, team):
        if team == 0:
            return []
        else:
            r = []
            for k, i in enumerate(self.teams):
                if k != 0 and k != team:
                    r += i
            return r

    def get_all(self):
        return self.get_units() + self.other

    def get_close(self, pos, mag):
        r = []
        for i in self.get_all():
            if (i.pos - pos).difference() < mag:
                r.append(i)
        return r

    def get_from_name(self, identification, group=None):
        if group is None:
            group = self.get_all()
        for i in group:
            if i.name == identification:
                return i
