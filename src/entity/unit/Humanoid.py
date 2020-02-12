from src.entity.unit.Unit import Unit
from src.tools import Direction


class Humanoid(Unit):
    faces = []

    def __init__(self):
        super().__init__()
        self.armor = None
        self.headgear = None
        from src.entity.Stock import Stock
        self.fist = Stock.get('Fist')
        self.weapon = self.fist
        self.fist.host = self

    def __str__(self):
        armor = '['+self.armor.__str__()+']' if self.armor else '0'
        headgear = '['+self.headgear.__str__()+']' if self.headgear else '0'
        weapon = '['+self.weapon.__str__()+']' if self.is_armed() else '0'
        gear = armor + ',' + headgear + ',' + weapon
        return super().__str__() + ',' + gear

    def load(self, p):
        index = super().load(p)
        from src.entity.Stock import Stock
        if p[index]:
            if isinstance(p[index], str):
                armor = Stock.get(p[index])
            else:
                armor = Stock.get(p[index][2], p[index])
            armor.update_tags()
            armor.host = self
            armor.wear(start=True)
        else:
            self.make_armor()
        index += 1
        if p[index]:
            if isinstance(p[index], str):
                headgear = Stock.get(p[index])
            else:
                headgear = Stock.get(p[index][2], p[index])
            headgear.update_tags()
            headgear.host = self
            headgear.wear(start=True)
        index += 1
        if p[index]:
            if isinstance(p[index], str):
                weapon = Stock.get(p[index])
            else:
                weapon = Stock.get(p[index][2], p[index])
            weapon.update_tags()
            weapon.on_equip(self)
        from src.game import Global
        for i in self.get_possessions():
            i.id = Global.location.get_id()
        return index + 1

    def update_tags(self):
        super().update_tags()
        self.form.organs[0].set(self.make_face())
        self.form.organs[0].form.show(True)

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
        from src.game.Script import Script
        if self.is_armed():
            if not Script.execute_code(self.weapon.tags.get('#')):
                self.weapon.use()
        else:
            super().use()

    def relocate(self, x, y, force=0):
        super().relocate(x, y, force)
        self.weapon.pos = self.pos
        if self.headgear:
            self.headgear.pos = self.pos

    def remove(self):
        super().remove()
        self.weapon.remove()
        if self.headgear:
            self.headgear.remove()

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
        if self.armor:
            self.armor.face(direction)
        if self.headgear:
            self.headgear.face(direction)
        self.weapon.face(direction)
        super().face(direction)

    def get_defense(self):
        min_d, max_d = self.armor.get_defense()
        if self.action.current_action == 'fall':
            return min_d, min_d
        return min_d, max_d + self.get_skill('dodge')

    def get_hitter(self):
        return self.weapon

    def get_damage(self):
        min_d, max_d = super().get_damage()
        min_d2, max_d2 = self.weapon.get_damage()
        return min_d + min_d2, max_d + max_d2

    def on_attack(self, target):
        super().on_attack(target)
        self.weapon.on_attack(target)

    def get_possessions(self):
        r = [self.weapon, self.armor]
        if self.headgear:
            r.append(self.headgear)
        return r

    def make_fist(self):
        self.fist.on_equip(self)
        self.fist.form.show(False)

    def make_armor(self):
        self.armor = None
        self.form.set_model('image/unit/body')
        self.face(self.direction)

    def drop(self):
        if self.is_armed():
            r = self.weapon
            self.weapon.on_unequip()
            self.make_fist()
            return r

    def unarmor(self):
        if self.armor:
            self.armor.unwear()
            self.make_armor()
            return 1
        return 0

    def unheadgear(self):
        if self.headgear:
            self.headgear.unwear()
            self.headgear = None
            return 1
        return 0

    def is_armed(self):
        return self.weapon.name != 'Fist'

    def make_face(self):
        from src.form.Model import Model
        face = Humanoid.faces[self.tags.get('seed', 0) % len(Humanoid.faces)]
        model = Model(face)
        return model

    def get_skill(self, skill, stacks=False):
        r = super().get_skill(skill, stacks)
        if self.armor:
            if stacks or r == 0:
                if self.armor.tags.get('skill') == skill:
                    r += 1
        if self.headgear:
            if stacks or r == 0:
                if self.headgear.tags.get('skill') == skill:
                    r += 1
        return r
