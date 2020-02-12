from src.tools.Dialog import Dialog


class Attribute:
    inactive = '!'
    script = '#'
    collision = 'col'
    obstruct = 'ob'
    pivot = 'piv'
    material = 'mat'
    insubstantial = 'ix'
    combustible = 'pf'
    intelligent = 'ii'
    listener = 'il'

    def __init__(self, host):
        self.host = host
        self.attributes = {}

    def __str__(self):
        return Dialog.dict(self.attributes)

    def load(self, arg):
        for i in arg:
            strings = i.split(':')
            if len(strings) > 1:
                if strings[1][0].isdigit() or strings[1][0] == '-':
                    self.attributes[strings[0]] = int(strings[1])
                else:
                    self.attributes[strings[0]] = strings[1]

    def remove(self, param):
        if param in self.attributes:
            del self.attributes[param]

    def get(self, param, default=None):
        if param in self.attributes:
            return self.attributes[param]
        return default

    def set(self, param, arg, add=False):
        if param in self.attributes or add:
            self.attributes[param] = arg
            return True

    def increment(self, param, arg, add=False, remove=False):
        if param in self.attributes:
            self.attributes[param] += arg
            if remove:
                if self.attributes[param] == 0:
                    del self.attributes[param]
            return True
        elif add:
            self.attributes[param] = arg
            return True

    def require(self, param, arg, cost=True):
        if param in self.attributes:
            if self.attributes[param] >= arg:
                if cost:
                    self.attributes[param] -= arg
                return True

    def update(self):
        if 'p' in self.attributes:
            self.host.hittable = 1
        else:
            self.host.hittable = 0
        if Attribute.collision in self.attributes:
            cols = []
            for i in str(self.attributes['col']):
                cols.append(int(i))
            self.host.collision_type = cols
        if Attribute.obstruct in self.attributes:
            self.host.obstruct_type = self.attributes['ob']
        if Attribute.pivot in self.attributes:
            self.host.form.image.anchor_y = self.host.form.image.height - self.attributes['piv']
        if 'seed' in self.attributes:
            if self.attributes['seed'] == -1:
                from src.game import Global
                self.attributes['seed'] = Global.r.rand_int(1, 9999)

    def is_combustible(self):
        return self.get('p') and self.get('mat') in ['wood', 'flesh', 'fuel']

    def get_carry_over(self):
        permanent = ['money', 'talent', 'seed', 'full']
        return (lambda keys: {x: self.attributes[x] for x in keys})(permanent)
