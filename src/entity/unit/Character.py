from src.entity.unit.Humanoid import Humanoid
from src.game.Interaction import Interaction
from src.interface.Textbox import Textbox
from src.tools.Dialog import Dialog


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
        self.monologue = Textbox(self, [0, 0])
        self.var = {}

    def __str__(self):
        return super().__str__() + ',' + Dialog.dict(self.var)

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

    def draw(self):
        super().draw()
        from src.game.Camera import Camera
        # self.monologue.pos = [self.vec.x + Camera.pos[0], self.vec.y + Camera.pos[1] - 60]
        # self.monologue.draw(surface)

    def say(self, text):
        self.monologue.text(text)

    def use(self):
        if 'use' in self.weapon.tags:
            Interaction.interact(self.weapon.tags['use'], self.weapon)
        else:
            super().use()

    def fell(self, distance, me=False):
        if not Character.check_var(self, 'talent', 'Assassin') or not me:
            if distance > 1:
                self.var['sign'] = 'Accident'
            super().fell(distance, me)

    def hit(self, damage, accuracy=None, hitter=None):
        r = super().hit(damage, accuracy, hitter)
        if r == 2:
            from src.entity.unit.Unit import Unit
            from src.entity.unit.Buff import Buff
            from src.entity.unit.item.Item import Item
            if hitter == self.weapon:
                self.var['sign'] = 'Suicide'
            elif isinstance(hitter, Humanoid) or (isinstance(hitter, Item) and hitter.host):
                self.var['sign'] = 'Homicide'
            elif isinstance(hitter, Unit):
                self.var['sign'] = 'Wildlife'
            elif isinstance(hitter, Buff):
                self.var['sign'] = 'Illness'
        return r

    def out_of_bounds(self):
        self.var['sign'] = 'Accident'
        super().out_of_bounds()

    def is_bright(self):
        from src.game import Global
        if Global.player.is_daytime() or self.pos.light > 0:
            return True
        self.say('Too dark!')

    def stamina(self, mag):
        if self.attributes.breath >= mag:
            self.attributes.breath -= mag
            return True
        else:
            self.say('Not enough stamina!')
            return False

    def require_var(self, var, mag, cost=True):
        if var in self.var:
            if self.var[var] >= mag:
                if cost:
                    self.var[var] -= mag
                return True
            else:
                self.say('Not enough ' + var + '!')
                return False
