from src.entity.Object import Object
from src.game.Tags import Tags
from src.map.Tile import Tile
from src.tools.Dialog import Dialog


class Prop(Object):
    def __init__(self, loc):
        super().__init__(loc)
        from src.entity.unit.Buffs import Buffs
        self.hittable = 1
        self.collision_type = Tile.COLLIDE_PROP
        self.faction = 0  # 0: Neutral, 1: Player, 2: Enemy, 3: Beast, 4: Undead
        self.attributes = None
        self.states = Buffs(self)
        self.tags = {}

    def __str__(self):
        return ','.join([super().__str__(), Dialog.dict(self.tags), '[' + self.attributes.__str__() + ']',
                         '[' + self.states.__str__() + ']'])

    def load(self, arg):
        index = super().load(arg)
        for i in arg[index]:
            strings = i.split(':')
            if len(strings) > 1:
                if strings[1][0].isdigit() or strings[1][0] == '-':
                    self.tags[strings[0]] = int(strings[1])
                else:
                    self.tags[strings[0]] = strings[1]
        index += 1
        self.load_attributes(arg[index])
        index += 1
        self.states.load(arg[index])
        if 'ind' in self.tags:
            self.hittable = 0
        if 'col' in self.tags:
            self.collision_type = self.tags['col']
        return index + 1

    def load_attributes(self, arg):
        from src.entity.unit.Attribute import Attribute
        self.attributes = Attribute()
        self.attributes.load(arg)

    def turn(self):
        super().turn()
        self.states.update()

    def get_tag(self, key):
        if key in self.tags:
            return self.tags[key]

    def glow(self, radius):
        if not radius:
            self.pos.light = min(40, self.pos.light + 20)
        else:
            aoe = self.location.get_area(self.pos, radius, radius)
            for pos in aoe:
                pos.light = min(40, pos.light + 20)

    def die(self):
        from src.entity.Particle import Particle
        Particle.make('disintegrate', self.pos.get_center(), offset=0)
        self.spawn_loot()
        self.remove()

    def spawn_loot(self):
        if 'loot' in self.tags:
            from src.entity.Stock import Stock
            from src.game import Global
            loot = self.tags['loot']
            if loot.startswith('#'):
                from src.entity.Stock import Stock
                from src.tools.Data import Data
                loot_table = Global.r.rand_list(Data.get_line('raw/trade.txt', loot[1:])[1])
                Stock.make(loot_table, self.pos)
            else:
                if 'loot%' not in self.tags or Global.r.rand_int(1, 100) <= self.tags['loot%']:
                    Stock.make(loot, self.pos)

    def is_hit(self, chance, faction=0):
        if self.hittable and (self.faction != faction or not faction or not self.faction):
            if self.is_var('mat', 'Metal'):
                return chance > 4
            elif self.is_var('mat', 'Wood'):
                return chance > 2
            return 1

    def hit(self, damage, accuracy=None, hitter=None):
        if damage > 0:
            if hitter:
                if isinstance(hitter, Prop):
                    from src.entity.Particle import Particle
                    if Tags.sharp in hitter.tags:
                        if Tags.flesh in self.tags:
                            Particle.make('splat', self.vec)
                        else:
                            Particle.make('slash', self.vec)
                    else:
                        Particle.make('batter', self.vec)
        if self.attributes.hp != -1:
            self.attributes.hp = max(0, self.attributes.hp - damage)
            if self.attributes.hp == 0:
                self.attributes.hp = -1
                self.die()
                return 2
        return 1

    def is_var(self, key, arg):
        if key in self.tags:
            return self.tags[key] == arg
