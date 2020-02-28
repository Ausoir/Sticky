from src.tools.Tag import Tag


class Attribute(Tag):
    def __init__(self, host):
        super().__init__()
        self.host = host

    def update(self):
        if 'p' in self.attributes:
            self.host.hittable = 1
        else:
            self.host.hittable = 0
        if 'col' in self.attributes:
            cols = []
            for i in str(self.attributes['col']):
                cols.append(int(i))
            self.host.collision_type = cols
        if 'ob' in self.attributes:
            self.host.obstruct_type = self.attributes['ob']
        if 'pivx' in self.attributes:
            self.host.form.image.anchor_x = self.attributes['pivx']
        if 'pivy' in self.attributes:
            self.host.form.image.anchor_y = self.host.form.image.height - self.attributes['pivy']
        if 'seed' in self.attributes:
            if self.attributes['seed'] == -1:
                from src.game import Global
                self.attributes['seed'] = Global.r.rand_int(1, 9999)

    def is_combustible(self):
        return self.get('p') and self.get('mat') in ['wood', 'flesh', 'fuel']

    def get_carry_over(self):
        permanent = ['money', 'seed', 'full']
        return (lambda keys: {x: self.attributes[x] for x in keys})(permanent)
