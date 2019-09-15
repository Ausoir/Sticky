from src.entity.unit.Humanoid import Humanoid


class Character(Humanoid):
    @staticmethod
    def get_var(host, key):
        if isinstance(host, Character) and key in host.var:
            return host.var[key]

    @staticmethod
    def check_var(host, key, value):
        return Character.get_var(host, key) == value

    def __init__(self, loc):
        super().__init__(loc)
        self.var = {}

    def __str__(self):
        var = []
        for k, v in self.var.items():
            var.append(k + ':' + str(v))
        var = '[' + ','.join(var) + ']'
        return super().__str__() + ',' + var

    def load(self, p):
        index = super().load(p)
        for i in p[index]:
            strings = i.split(':')
            if len(strings) > 1:
                if strings[1][0].isdigit() or strings[1][0] == '-':
                    self.var[strings[0]] = int(strings[1])
                else:
                    self.var[strings[0]] = strings[1]
        return index + 1

    def fell(self, distance, me=False):
        if not Character.check_var(self, 'power', 'Assassin') or not me:
            super().fell(distance, me)
