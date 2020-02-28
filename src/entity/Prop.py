from src.entity.Attribute import Attribute
from src.entity.Object import Object


class Prop(Object):
    def __init__(self, location):
        super().__init__(location)
        from src.entity.unit.Buffs import Buffs
        self.hittable = 1
        self.states = Buffs(self)
        self.tags = Attribute(self)

    def __str__(self):
        return ','.join([super().__str__(), self.tags.__str__(), '[' + self.states.__str__() + ']'])

    def load(self, arg):
        index = super().load(arg)
        self.tags.load(arg[index])
        index += 1
        self.states.load(arg[index])
        return index + 1

    def add(self):
        r = super().add()
        self.update_tags()
        self.states.on_load()
        return r

    def update_tags(self):
        self.tags.update()

    def turn(self):
        super().turn()
        self.states.update()

    def die(self):
        from src.entity.Particle import Particle
        Particle.make('disintegrate', self.pos.get_center(), offset=0)
        self.spawn_loot()
        self.remove()

    def spawn_loot(self):
        loot = self.tags.get('loot')
        if loot:
            from src.entity.Stock import Stock
            from src.game import Global
            if loot.startswith('#'):
                from src.entity.Stock import Stock
                from src.tools.Data import Data
                loot_table = Global.r.rand_list(Data.get_line('raw/raw.txt', loot[1:])[1])
                Stock.make(loot_table, self.pos)
            else:
                lootc = self.tags.get('loot%')
                if not lootc or Global.r.rand_int(1, 100) <= lootc:
                    Stock.make(loot, self.pos)

    def decay(self, damage):
        hp = self.tags.get('p')
        if hp is not None:
            self.tags.set('p', min(max(0, hp - damage), self.tags.get('p>', 1000)))
            if self.tags.get('p') == 0:
                self.die()
                return 2
        return 1

    def hit(self, damage, hitter=None):
        material = self.tags.get('mat')
        if material == 'wood':
            damage = max(0, damage - 3)
        elif material == 'metal':
            damage = max(0, damage - 7)
        if damage > 0:
            if hitter:
                if isinstance(hitter, Prop):
                    from src.entity.Particle import Particle
                    if hitter.tags.get('sharp'):
                        if self.tags.get('mat') == 'flesh':
                            self.location.sound.register(self.pos, 7, file='hit_cut')
                            Particle.make('splat', self.vec)
                        else:
                            self.location.sound.register(self.pos, 7, file='hit_bash')
                            Particle.make('slash', self.vec)
                    else:
                        self.location.sound.register(self.pos, 7, file='hit_bash')
                        Particle.make('batter', self.vec)
            return self.decay(damage)
        return 0

    def describe(self):
        r = self.name
        from src.tools.Data import Data
        from src.tools.Dialog import Dialog
        data = Data.get_line('raw/descriptions.txt', r)
        if data:
            r += '\n' + data[1]
        hp = self.tags.get('p')
        if hp:
            max_hp = self.tags.get('p>')
            r += '\n' + Dialog.durability(hp, max_hp)
        mat = Dialog.material(self.tags.attributes.get('mat'))
        if mat:
            r += '\n' + mat
        return r

    def on_sleep(self, time):
        for i in self.states.buffs:
            i.trigger(['time', time])
