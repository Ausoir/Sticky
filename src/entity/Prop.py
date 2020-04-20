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
        self.update_tags()
        index += 1
        self.states.load(arg[index])
        return index + 1

    def add(self):
        r = super().add()
        if r:
            Turn.add(self.turn)
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
        Particle.make('disintegrate', self.pos, offset=0)
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
            self.tags.set('p', min(max(0, hp - damage), self.tags.get('P', 1000)))
            if self.tags.get('p') == 0:
                self.die()
                return 2
        return 1

    def get_weight(self):
        return self.tags.get('w', 1)

    def hit(self, damage, hitter=None):
        damage = max(0, damage - self.tags.get('def', 0))
        if damage > 0:
            if hitter:
                if isinstance(hitter, Prop):
                    from src.entity.Particle import Particle
                    if hitter.tags.get('sharp'):
                        if self.tags.get('mat') == 'flesh':
                            self.location.sound.register(self.pos, 7, file='hit_cut')
                            Particle.make('splat', self.pos)
                        else:
                            self.location.sound.register(self.pos, 7, file='hit_bash')
                            Particle.make('slash', self.pos)
                    else:
                        self.location.sound.register(self.pos, 7, file='hit_bash')
                        Particle.make('batter', self.pos)
            return self.decay(damage)
        return 0

    def get_display_name(self):
        return self.name

    def get_description(self):
        from src.tools.Data import Data
        return Data.get_line('descriptions.txt', self.name)

    def describe(self):
        r = self.name
        from src.tools.Dialog import Dialog
        r += '   (' + Dialog.weight(self.tags.get('w', 1)) + ')'
        from src.tools.Data import Data
        data = Data.get_line('descriptions.txt', r)
        if data:
            r += '\n' + data[1]
        hp = self.tags.get('p')
        max_hp = self.tags.get('P')
        r += '\n' + Dialog.durability(hp, max_hp)
        armor = self.tags.get('def')
        if armor:
            r += '\n' + Dialog.armor(armor)
        hinder = self.tags.get('spd')
        if hinder:
            r += '\n' + Dialog.get('terrain speed', [hinder])
        damage = self.tags.get('dmg')
        if damage:
            r += '\n' + Dialog.get('Damage') + ': ' + Dialog.sign(damage)
        return r

    def on_sleep(self, time):
        self.states.trigger(['time', time])
