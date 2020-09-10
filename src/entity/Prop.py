from src.entity.Attribute import Attribute
from src.entity.Object import Object
from src.entity.Particle import Particle
from src.entity.unit.Buffs import Buffs
from src.game import Global
from src.game.Turn import Turn


class Prop(Object):
    def __init__(self):
        super().__init__()
        self.direction = 0
        self.hittable = True
        self.states = Buffs(self)
        self.tags = Attribute(self)

    def __str__(self):
        self.tags.set('dir', self.direction)
        return ','.join([super().__str__(), self.tags.__str__(), '[' + self.states.__str__() + ']'])

    def load(self, arg):
        index = super().load(arg)
        self.tags.load(arg[index])
        self.update_tags()
        direction = self.tags.get('dir')
        if direction:
            self.face(direction)
        index += 1
        self.states.load(arg[index])
        return index + 1

    def add(self):
        r = super().add()
        if r:
            self.states.on_load()
            return r

    def remove(self):
        if super().remove():
            Turn.remove(self.states.update)
            return True

    def turn(self):
        pass

    def update_tags(self):
        self.tags.update()
        self.tags.add_tag(self)

    def get_seed(self):
        seed = self.tags.get('seed', -1)
        if seed == -1:
            seed = Global.r.rand_int(0, 99999)
            self.tags.set('seed', seed)
        return seed

    def face(self, direction):
        direction = direction % 4
        if direction != self.direction:
            self.direction = direction
            self.form.face(direction)
            return True

    def set_form(self, arg):
        super().set_form(arg)
        self.form.face(self.direction)

    def die(self):
        self.states.trigger(['die'])
        from src.entity.Particle import Particle
        Particle.make('disintegrate', self.pos, offset=0)
        loot = self.get_loot()
        if loot:
            from src.entity.Stock import Stock
            Stock.make(loot, self.pos)
        on_death = self.tags.remove('!')
        if on_death:
            from src.game.Script import Script
            Script.var['host'] = self
            Script.execute_code(on_death)
        self.remove()

    def get_loot(self):
        loot = self.tags.get('loot')
        if loot:
            if loot.startswith('#'):
                cell_coord = Global.world.get_coordinates(self.pos.x, self.pos.y)
                spawn = Global.world.get_spawn(loot[1:], cell_coord[0], cell_coord[1])
                return spawn
            else:
                return loot

    def decay(self, damage):
        hp = self.tags.get('p')
        if hp is not None:
            new = max(0, hp - damage)
            mhp = self.tags.get('P') or hp
            new = min(new, mhp)
            self.tags.set('p', new)
            if self.tags.get('p') == 0:
                self.die()
                return 2
        return 1

    def get_weight(self):
        return self.tags.get('w', 1)

    def get_value(self):
        return self.tags.get('$', 0)

    def on_natural_spawn(self):
        pass

    def hit(self, damage, hitter=None):
        damage -= self.tags.get('def', 0)
        if damage > 0:
            self.on_hit()
            r = self.decay(damage)
            if r == 2:
                if hitter:
                    hitter.progress_level(0, mode='sabotage', var=self)
            return r
        self.on_hit(effect='slash', sound='hit_armor')
        return 0

    def on_hit(self, effect=None, sound=None):
        if effect is None:
            effect = 'batter'
        if sound is None:
            sound = 'hit_bash'
        self.pos.location.sound.register(self.pos, 5, file=sound)
        Particle.make(effect, self.pos)

    def get_display_name(self):
        from src.tools.Dialog import Dialog
        return Dialog.get(self.name)

    def describe(self):
        from src.tools.Dialog import Dialog
        from src.tools.Data import Data
        r = self.get_display_name()
        data = Data.get_line('descriptions.txt', self.name)
        r += '  (' + Dialog.weight(self.get_weight()) + ')'
        if data:
            r += '\n' + data[1]
        hp = self.tags.get('p')
        max_hp = self.tags.get('P')
        r += '\n' + Dialog.durability(hp, max_hp)
        armor = self.tags.get('def')
        if armor:
            r += '\n' + Dialog.armor(armor)
        damage = self.tags.get('dmg')
        if damage:
            r += '\n' + Dialog.get('Damage') + ': ' + str(damage)
        return r

    def on_sleep(self, time):
        self.states.on_sleep(time)

    def mutate(self):
        mut = self.tags.get('mut')
        if mut and Global.r.rand_bool():
            from src.entity.Stock import Stock
            Stock.make(mut, self.pos)
            self.remove()

    def switch_form(self):
        alt = self.tags.get('alt')
        if alt:
            original = self.form_name
            self.set_form(alt)
            self.form.show(True)
            self.tags.set('alt', original)

    def drown(self):
        if self.tags.get('fly', 0) == 0 and Global.player.player_mode == 1:
            from src.entity.Particle import Particle
            Particle.make('drown', self.pos)
            self.remove()
