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
        from src.tools.Data import Data
        self.shadow = Data.get_form('g_7x0')
        self.shadow.bound(True)

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
        line = Data.get_line('model.txt', arg)
        self.form = BodyHumanoid(line[1], self)
        self.form.set_model(line[2])

    def set_row(self, row):
        super().set_row(row)
        self.shadow.z = row * 20 + 100

    def show(self, visible):
        super().show(visible)
        self.shadow.show(visible)
        if self.weapon:
            self.weapon.show(visible)
        if self.headgear:
            self.headgear.show(visible)

    def bound(self, visible):
        super().bound(visible)
        self.shadow.bound(visible)
        if self.weapon:
            self.weapon.bound(visible)
        if self.headgear:
            self.headgear.bound(visible)

    def turn(self):
        super().turn()
        if self.weapon:
            self.weapon.turn()
        if self.headgear:
            self.headgear.turn()

    def use(self):
        if self.weapon:
            self.states.trigger(['act', 'use'])
            if not self.action.interact(self.weapon):
                self.weapon.use()
        else:
            self.action.attack()

    def relocate(self, to=None, x=None, y=None, force=False):
        super().relocate(to, x, y, force)
        if self.weapon:
            self.weapon.relocate(to=to, x=x, y=y, force=force)
        if self.armor:
            self.armor.relocate(to=to, x=x, y=y, force=force)
        if self.headgear:
            self.headgear.relocate(to=to, x=x, y=y, force=force)

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
        self.shadow.place(bound_x, bound_y)
        if self.weapon:
            if self.direction == 2:
                x = bound_x + self.form.organs[3].lower_joint.x
                y = bound_y - self.form.organs[3].lower_joint.y
                arm = (self.form.organs[3].lower_joint - self.form.organs[3].upper_joint).get_atan()
                self.weapon.form.rotation = arm - 15
            elif self.direction == 0:
                x = bound_x + self.form.organs[3].lower_joint.x
                y = bound_y - self.form.organs[3].lower_joint.y
                arm = (self.form.organs[3].lower_joint - self.form.organs[3].upper_joint).get_atan()
                self.weapon.form.rotation = arm - 30
            else:
                x = bound_x + self.form.organs[2].lower_joint.x
                y = bound_y - self.form.organs[2].lower_joint.y
                arm = (self.form.organs[2].lower_joint - self.form.organs[2].upper_joint).get_atan()
                self.weapon.form.rotation = arm - 90 + (15 * self.form.side)
            self.weapon.form.place(x, y)
        if self.headgear:
            x = bound_x + self.form.organs[0].lower_joint.x
            y = bound_y - self.form.organs[0].lower_joint.y
            neck = (self.form.organs[0].lower_joint - self.form.organs[0].upper_joint).get_atan()
            self.headgear.form.rotation = neck + 90
            self.headgear.form.place(x, y)
        return bound_x, bound_y

    def face(self, direction):
        if self.headgear:
            self.headgear.face(direction)
        if self.weapon:
            self.weapon.face(direction)
        super().face(direction)

    def get_hitter(self):
        if self.weapon:
            return self.weapon
        return self

    def get_damage(self):
        max_d = super().get_damage()
        if self.weapon:
            return max(0, max_d + self.weapon.tags.get('dmg', 0))
        else:
            return max_d

    def on_attack(self, target):
        super().on_attack(target)
        if self.weapon:
            self.weapon.on_attack(target)

    def get_possessions(self):
        r = self.get_equipments()
        r += self.inventory.items
        return r

    def get_equipments(self):
        r = []
        if self.weapon:
            r.append(self.weapon)
        if self.armor:
            r.append(self.armor)
        if self.headgear:
            r.append(self.headgear)
        return r

    def get_accessibles(self):
        r = []
        from src.entity.unit.item.Item import Item
        for thing in self.pos.things:
            if isinstance(thing, Item):
                r.append(thing)
        r += self.inventory.items
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

    def get_attack_motion(self):
        if not self.weapon:
            return 'kick'
        return super().get_attack_motion()

    def get_attack_speed(self):
        r = super().get_attack_speed()
        if self.weapon:
            r -= self.weapon.get_weight() - 2
        return r

    def get_capacity(self):
        r = 5
        r += self.get_skill('endurance', stacks=True)
        if self.armor:
            r += self.armor.tags.get('space', 0)
        if self.headgear:
            r += self.headgear.tags.get('space', 0)
        return r

    def on_sleep(self, time):
        super().on_sleep(time)
        self.inventory.on_sleep(time)

    def get_equipment_weight(self):
        r = 0
        for i in self.get_possessions():
            r += i.get_weight()
        return r

    def get_weight(self):
        return super().get_weight() + self.get_equipment_weight()
