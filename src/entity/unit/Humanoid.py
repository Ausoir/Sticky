from src.entity.unit.Inventory import Inventory
from src.entity.unit.Unit import Unit


class Humanoid(Unit):
    faces = []

    def __init__(self, location):
        super().__init__(location)
        self.inventory = Inventory(self)
        self.armor = None
        self.headgear = None
        self.weapon = None
        self.action.humanoid = True

    def __str__(self):
        armor = '['+self.armor.__str__()+']' if self.armor else '0'
        headgear = '['+self.headgear.__str__()+']' if self.headgear else '0'
        weapon = '['+self.weapon.__str__()+']' if self.weapon else '0'
        gear = armor + ',' + headgear + ',' + weapon
        return super().__str__() + ',' + gear + ',' + self.inventory.__str__()

    def load(self, p):
        index = super().load(p)
        from src.entity.Stock import Stock
        if p[index]:
            if isinstance(p[index], str):
                armor = Stock.get(self.location, p[index])
            else:
                armor = Stock.get(self.location, p[index][2], p[index])
            armor.pos = self.pos
            armor.host = self
            armor.add()
            armor.wear(start=True)
        index += 1
        if p[index]:
            if isinstance(p[index], str):
                headgear = Stock.get(self.location, p[index])
            else:
                headgear = Stock.get(self.location, p[index][2], p[index])
            headgear.pos = self.pos
            headgear.host = self
            headgear.add()
            headgear.wear(start=True)
        index += 1
        if p[index]:
            if isinstance(p[index], str):
                weapon = Stock.get(self.location, p[index])
            else:
                weapon = Stock.get(self.location, p[index][2], p[index])
            weapon.on_wield(self)
            weapon.add()
        index += 1
        self.inventory.load(p[index])
        for i in self.get_possessions():
            i.id = self.location.get_id()
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
        self.form.set_model(line[2])

    def show(self, visible):
        super().show(visible)
        if self.weapon:
            self.weapon.show(visible)
        if self.headgear:
            self.headgear.show(visible)

    def bound(self, visible):
        super().bound(visible)
        if self.weapon:
            self.weapon.bound(visible)
        if self.headgear:
            self.headgear.bound(visible)

    def turn(self):
        super().turn()
        if self.weapon:
            self.weapon.states.update()

    def use(self):
        from src.game.Script import Script
        if self.weapon:
            if not Script.execute_code(self.weapon.tags.get('#'), host=self):
                self.weapon.use()
        else:
            self.action.kick()

    def relocate(self, x, y, force=0):
        super().relocate(x, y, force)
        if self.weapon:
            self.weapon.relocate(x, y, force=1)
        if self.armor:
            self.armor.relocate(x, y, force=1)
        if self.headgear:
            self.headgear.relocate(x, y, force=1)

    def remove(self):
        super().remove()
        if self.armor:
            self.armor.host = None
            self.armor.remove()
        if self.weapon:
            self.weapon.remove()
        if self.headgear:
            self.headgear.remove()

    def die(self):
        self.drop()
        self.inventory.drop_all()
        super().die()

    def update(self):
        bound_x, bound_y = super().update()
        if self.weapon:
            if self.direction == 2:
                x = bound_x + self.form.organs[3].lower_joint.x
                y = bound_y - self.form.organs[3].lower_joint.y
                arm = (self.form.organs[3].lower_joint - self.form.organs[3].upper_joint).get_atan()
                self.weapon.form.rotation = arm - 15
            elif self.direction == 4:
                x = bound_x + self.form.organs[3].lower_joint.x
                y = bound_y - self.form.organs[3].lower_joint.y
                arm = (self.form.organs[3].lower_joint - self.form.organs[3].upper_joint).get_atan()
                self.weapon.form.rotation = arm - 30
            else:
                x = bound_x + self.form.organs[2].lower_joint.x
                y = bound_y - self.form.organs[2].lower_joint.y
                arm = (self.form.organs[2].lower_joint - self.form.organs[2].upper_joint).get_atan()
                self.weapon.form.rotation = arm - 90
            self.weapon.form.place(x, y)
        if self.headgear:
            x = bound_x + self.form.organs[0].lower_joint.x
            y = bound_y - self.form.organs[0].lower_joint.y - 2
            neck = (self.form.organs[0].lower_joint - self.form.organs[0].upper_joint).get_atan()
            self.headgear.form.rotation = neck + 90
            self.headgear.form.place(x, y)

    def face(self, direction):
        if self.armor:
            self.armor.face(direction)
        if self.headgear:
            self.headgear.face(direction)
        if self.weapon:
            self.weapon.face(direction)
        super().face(direction)

    def get_defense(self):
        max_d = super().get_defense()
        if self.armor:
            return max_d + self.armor.armor
        else:
            return max_d

    def get_hitter(self):
        if self.weapon:
            return self.weapon
        return self

    def get_damage(self):
        max_d = super().get_damage()
        if self.weapon:
            return max_d + self.weapon.damage
        else:
            return max_d

    def on_attack(self, target):
        super().on_attack(target)
        if self.weapon:
            self.weapon.on_attack(target)

    def get_possessions(self):
        r = []
        if self.weapon:
            r.append(self.weapon)
        if self.armor:
            r.append(self.armor)
        if self.headgear:
            r.append(self.headgear)
        r += self.inventory.items
        return r

    def get_accessibles(self):
        r = []
        from src.entity.unit.item.Item import Item
        for thing in self.pos.things:
            if isinstance(thing, Item):
                r.append(thing)
        r += self.get_possessions()
        return r

    def drop(self):
        if self.weapon:
            r = self.weapon
            self.weapon.on_unwield()
            self.weapon = None
            return r

    def unarmor(self):
        if self.armor:
            return self.armor.unwear()

    def unheadgear(self):
        if self.headgear:
            return self.headgear.unwear()

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

    def get_attack_speed(self):
        if not self.weapon:
            return 0
        return self.weapon.tags.get('spd', 0)

    def get_capacity(self):
        r = 5
        r += self.get_skill('endurance', stacks=True)
        if self.armor:
            r += self.armor.get_weight()
        return r

    def on_sleep(self, time):
        self.inventory.on_sleep(time)
