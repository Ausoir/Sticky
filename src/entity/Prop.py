from src.entity.Attribute import Attribute
from src.entity.Object import Object
from src.game.Turn import Turn


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
        if r:
            Turn.add(self.turn)
            self.update_tags()
            self.states.on_load()
            return r

    def remove(self):
        Turn.remove(self.turn)
        super().remove()

    def update_tags(self):
        self.tags.update()

    def turn(self):
        self.states.update()

    def die(self):
        from src.entity.Particle import Particle
        Particle.make('disintegrate', self.pos.get_center(), offset=0)
        loot = self.get_loot()
        if loot:
            from src.entity.Stock import Stock
            Stock.make(loot, self.pos)
        self.remove()

    def get_loot(self):
        loot = self.tags.get('loot')
        if loot:
            if loot.startswith('#'):
                seed = self.tags.get('seed', 0)
                from src.tools.Data import Data
                spawn_list = Data.get_line('raw.txt', loot[1:])[1]
                return spawn_list[seed % len(spawn_list)]
            else:
                return loot

    def decay(self, damage):
        hp = self.tags.get('p')
        if hp is not None:
            self.tags.set('p', min(max(0, hp - damage), self.tags.get('p>', 1000)))
            if self.tags.get('p') == 0:
                self.die()
                return 2
        return 1

    def hit(self, damage, hitter=None):
        damage = max(0, damage - self.tags.get_material_defense())
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
        data = Data.get_line('descriptions.txt', r)
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
