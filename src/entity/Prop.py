from src.entity.Attribute import Attribute
from src.entity.Object import Object


class Prop(Object):
    def __init__(self, loc):
        super().__init__(loc)
        from src.entity.unit.Buffs import Buffs
        self.hittable = 1
        self.states = Buffs(self)
        self.tags = Attribute(self)
        from src.map import Depth
        self.depth = Depth.unit_depth

    def __str__(self):
        return ','.join([super().__str__(), self.tags.__str__(), '[' + self.states.__str__() + ']'])

    def load(self, arg):
        index = super().load(arg)
        self.tags.load(arg[index])
        index += 1
        self.states.load(arg[index])
        return index + 1

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
                loot_table = Global.r.rand_list(Data.get_line('raw/trade.txt', loot[1:])[1])
                Stock.make(loot_table, self.pos)
            else:
                lootc = self.tags.get('loot%')
                if not lootc or Global.r.rand_int(1, 100) <= lootc:
                    Stock.make(loot, self.pos)

    def decay(self, damage):
        hp = self.tags.get('p')
        if hp:
            self.tags.set('p', min(max(0, hp - damage), self.tags.get('p>', 999)))
            if self.tags.get('p') == 0:
                self.tags.remove('p')
                self.die()
                return 2
        return 1

    def hit(self, damage, hitter=None):
        if self.tags.get('mat') == 'Metal':
            damage = max(0, damage - 4)
        elif self.tags.get('mat') == 'Wood':
            damage = max(0, damage - 2)
        if damage > 0:
            if hitter:
                if isinstance(hitter, Prop):
                    from src.entity.Particle import Particle
                    if hitter.tags.get('sharp'):
                        if self.tags.get('mat') == 'flesh':
                            self.location.sound.register(self.pos, damage, file='hit_bloody')
                            Particle.make('splat', self.vec)
                        else:
                            self.location.sound.register(self.pos, damage, file='hit_cut')
                            Particle.make('slash', self.vec)
                    else:
                        self.location.sound.register(self.pos, damage, file='hit_bash')
                        Particle.make('batter', self.vec)
        return self.decay(damage)
