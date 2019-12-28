from src.entity.unit.Unit import Unit
from src.tools import Direction


class Humanoid(Unit):
    faces = []

    def __init__(self, loc):
        super().__init__(loc)
        self.armor = None
        self.headgear = None
        from src.entity.Stock import Stock
        self.fist = Stock.get('Fist')
        self.body = Stock.get('Body')
        self.weapon = self.fist
        self.fist.host = self
        self.body.host = self

    def __str__(self):
        armor = '['+self.armor.__str__()+']' if self.is_armored() else '0'
        headgear = '['+self.headgear.__str__()+']' if self.headgear else '0'
        weapon = '['+self.weapon.__str__()+']' if self.is_armed() else '0'
        gear = armor + ',' + headgear + ',' + weapon
        return super().__str__() + ',' + gear

    def load(self, p):
        index = super().load(p)
        from src.entity.Stock import Stock
        self.form.randomize_clip('hit', 4)
        self.form.organs[0].set(self.make_face())
        self.armor = self.body
        if p[index]:
            if isinstance(p[index], str):
                armor = Stock.get(p[index])
            else:
                armor = Stock.get(p[index][2], p[index])
            armor.host = self
            armor.wear()
        else:
            self.make_armor()
        index += 1
        if p[index]:
            if isinstance(p[index], str):
                headgear = Stock.get(p[index])
            else:
                headgear = Stock.get(p[index][2], p[index])
            headgear.host = self
            headgear.use()
        index += 1
        if p[index]:
            if isinstance(p[index], str):
                weapon = Stock.get(p[index])
            else:
                weapon = Stock.get(p[index][2], p[index])
            weapon.on_equip(self)
        for i in self.get_possessions():
            i.id = Stock.location.get_id()
        return index + 1

    def set_form(self, arg):
        self.form_name = arg
        from src.tools.Data import Data
        from src.form.BodyHumanoid import BodyHumanoid
        line = Data.get_line('raw/model.txt', arg)
        self.form = BodyHumanoid(line[1], self)

    def show(self, visible):
        super().show(visible)
        self.weapon.show(visible)
        if self.headgear:
            self.headgear.show(visible)

    def bound(self, visible):
        super().bound(visible)
        self.weapon.bound(visible)
        if self.headgear:
            self.headgear.bound(visible)

    def turn(self):
        super().turn()
        self.weapon.states.update()

    def use(self):
        self.weapon.use()

    def relocate(self, x, y, force=0):
        super().relocate(x, y, force)
        self.weapon.pos = self.pos
        if self.headgear:
            self.headgear.pos = self.pos

    def hit(self, damage, accuracy=None, hitter=None):
        damage = self.armor.get_reduction(damage)
        r = super().hit(damage, accuracy, hitter)
        if r == 1:
            self.form.randomize_once(8)
        return r

    def die(self):
        self.drop()
        super().die()

    def update(self):
        super().update()
        if self.direction == 2:
            x = self.vec.x + self.form.organs[3].lower_joint.x
            y = self.vec.y + self.form.organs[3].lower_joint.y + 2
            arm = (self.form.organs[3].lower_joint - self.form.organs[3].upper_joint).get_atan()
            self.weapon.form.rotation = arm + 60
        elif self.direction == 4:
            x = self.vec.x + self.form.organs[3].lower_joint.x
            y = self.vec.y + self.form.organs[3].lower_joint.y + 2
            arm = (self.form.organs[3].lower_joint - self.form.organs[3].upper_joint).get_atan()
            self.weapon.form.rotation = arm - 120
        else:
            x = self.vec.x + self.form.organs[2].lower_joint.x
            y = self.vec.y + self.form.organs[2].lower_joint.y + 2
            arm = (self.form.organs[2].lower_joint - self.form.organs[2].upper_joint).get_atan()
            self.weapon.form.rotation = arm + 90 + (Direction.side[self.direction] * 90)
        self.weapon.form.place(x, y)
        if self.headgear:
            x = self.vec.x + self.form.organs[0].lower_joint.x
            y = self.vec.y + self.form.organs[0].lower_joint.y - 2
            neck = (self.form.organs[0].lower_joint - self.form.organs[0].upper_joint).get_atan()
            self.headgear.form.rotation = neck + 90
            self.headgear.form.place(x, y)

    def face(self, direction):
        self.armor.face(direction)
        if self.headgear:
            self.headgear.face(direction)
        self.weapon.face(direction)
        super().face(direction)

    def get_dodge(self):
        if self.action.current_action == 'fall':
            return 0
        if self.action.current_action == 'block':
            r = self.weapon.weight * 4 + 4
            if self.get_proficiency('block'):
                return r * 4
            return r
        else:
            return self.get_proficiency('dodge') + self.armor.armor

    def get_hitter(self):
        return self.weapon

    def get_possessions(self):
        r = [self.weapon, self.armor]
        if self.headgear:
            r.append(self.headgear)
        return r

    def make_fist(self):
        self.fist.on_equip(self)
        self.fist.form.show(False)

    def make_armor(self):
        self.armor = self.body
        self.armor.host = self
        self.armor.wear()
        self.face(self.direction)

    def drop(self):
        if self.is_armed():
            r = self.weapon
            self.weapon.on_unequip()
            self.make_fist()
            return r

    def unarmor(self):
        if self.is_armored():
            self.armor.on_unequip()
            self.make_armor()
            return 1
        return 0

    def unheadgear(self):
        if self.headgear:
            self.headgear.on_unequip()
            self.headgear = None
            return 1
        return 0

    def is_armed(self):
        return self.weapon.name != 'Fist'

    def is_armored(self):
        return self.armor.name != 'Body'

    def make_face(self):
        from src.form.Model import Model
        face = Humanoid.faces[self.attributes.gene % len(Humanoid.faces)]
        model = Model(face)
        return model
