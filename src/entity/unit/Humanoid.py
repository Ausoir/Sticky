from src.entity.unit.Unit import Unit
from src.game import Global


class Humanoid(Unit):
    faces = []

    def __init__(self):
        super().__init__()
        self.armor = None
        self.headgear = None
        self.weapon = None
        self.action.humanoid = True

    def __str__(self):
        armor = '['+self.armor.__str__()+']' if self.armor else '0'
        headgear = '['+self.headgear.__str__()+']' if self.headgear else '0'
        weapon = '['+self.weapon.__str__()+']' if self.weapon else '0'
        gear = armor + ',' + headgear + ',' + weapon
        return super().__str__() + ',' + gear

    def load(self, p):
        index = super().load(p)
        self.pilot.is_humanoid = True
        e_weapon = self.tags.remove('e_weapon')
        e_armor = self.tags.remove('e_armor')
        e_head = self.tags.remove('e_head')
        from src.entity.Stock import Stock
        from src.tools.Data import Data
        if e_armor:
            p[index] = Global.r.rand_list(Data.get_line('habitat.txt', e_armor)[1])
        sync_hp = 0
        if p[index]:
            if isinstance(p[index], str):
                start = False
                armor = Stock.get(p[index])
                sync_hp += -armor.tags.get('end', 0)
            else:
                start = True
                armor = Stock.get(p[index][2], p[index])
            armor.host = self
            armor.wear(start=start)
        index += 1
        if e_head:
            p[index] = Global.r.rand_list(Data.get_line('habitat.txt', e_head)[1])
        if p[index]:
            if isinstance(p[index], str):
                start = False
                headgear = Stock.get(p[index])
                sync_hp += -headgear.tags.get('end', 0)
            else:
                start = True
                headgear = Stock.get(p[index][2], p[index])
            headgear.host = self
            headgear.wear(start=start)
        index += 1
        if e_weapon:
            p[index] = Global.r.rand_list(Data.get_line('habitat.txt', e_weapon)[1])
        if p[index]:
            if isinstance(p[index], str):
                weapon = Stock.get(p[index])
            else:
                weapon = Stock.get(p[index][2], p[index])
            weapon.on_wield(self)
        if sync_hp:
            self.decay(sync_hp)
        return index + 1

    def add(self):
        r = super().add()
        if r:
            if self.armor:
                self.armor.pos = self.pos
                self.armor.add()
                self.armor.show(False)
            if self.headgear:
                self.headgear.pos = self.pos
                self.headgear.add()
            if self.weapon:
                self.weapon.pos = self.pos
                self.weapon.add()
            return r

    def update_tags(self):
        super().update_tags()
        self.form.organs[0].set(self.make_face())
        self.form.organs[0].form.show(True)
        self.form.randomize(self.get_seed())

    def set_form(self, arg):
        self.form_name = arg
        from src.tools.Data import Data
        from src.form.BodyHumanoid import BodyHumanoid
        line = Data.get_line('model.txt', arg)
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

    def get_equipments(self):
        r = []
        if self.weapon:
            r.append(self.weapon)
        if self.armor:
            r.append(self.armor)
        if self.headgear:
            r.append(self.headgear)
        return r

    def get_skills(self):
        r = super().get_skills()
        if self.weapon and self.weapon.tags.get('skill'):
            r.append(self.weapon.tags.get('skill'))
        if self.armor and self.armor.tags.get('skill'):
            r.append(self.armor.tags.get('skill'))
        if self.headgear and self.headgear.tags.get('skill'):
            r.append(self.headgear.tags.get('skill'))
        return r

    def get_skill(self, skill):
        r = super().get_skill(skill)
        if self.weapon and self.weapon.tags.get('skill') == skill:
            r += 1
        if self.armor and self.armor.tags.get('skill') == skill:
            r += 1
        if self.headgear and self.headgear.tags.get('skill') == skill:
            r += 1
        return r

    def get_equipment_weight(self):
        r = 0
        for i in self.get_equipments() + self.inventory.get_all_items():
            r += i.get_weight()
        return r

    def get_weight(self):
        return super().get_weight() + self.get_equipment_weight()

    def is_vacant(self, weight):
        return self.tags.get('str', 1) >= self.get_equipment_weight() + weight

    def turn(self):
        super().turn()
        if self.tags.get('p', 0) == 1 and self.tags.get('P'):
            self.form.randomize_once(2)

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

    def deregister(self):
        super().deregister()
        if self.weapon:
            self.weapon.deregister()
        if self.armor:
            self.armor.deregister()
        if self.headgear:
            self.headgear.deregister()

    def remove(self):
        if super().remove():
            if self.armor:
                self.armor.host = None
                self.armor.remove()
            if self.weapon:
                self.weapon.remove()
            if self.headgear:
                self.headgear.remove()
            return True

    def die(self):
        self.drop()
        super().die()

    def update(self):
        bound_x, bound_y = super().update()
        if self.weapon:
            if self.direction == 2:
                x = bound_x + self.form.organs[3].lower_joint.x - 1
                y = bound_y - self.form.organs[3].lower_joint.y - 2
                arm = (self.form.organs[3].lower_joint - self.form.organs[3].upper_joint).get_atan()
                self.weapon.form.rotation = arm - 15
            elif self.direction == 0:
                x = bound_x + self.form.organs[3].lower_joint.x
                y = bound_y - self.form.organs[3].lower_joint.y + 4
                arm = (self.form.organs[3].lower_joint - self.form.organs[3].upper_joint).get_atan()
                self.weapon.form.rotation = arm - 30
            else:
                x = bound_x + self.form.organs[2].lower_joint.x
                y = bound_y - self.form.organs[2].lower_joint.y + 2
                arm = (self.form.organs[2].lower_joint - self.form.organs[2].upper_joint).get_atan()
                self.weapon.form.rotation = arm - 90 + (15 * self.form.side)
            self.weapon.form.scale_x = self.form.side
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
        return super().face(direction)

    def display_hp(self):
        hp = self.tags.get('p', 0)
        mhp = self.tags.get('P', 0)
        self.healthbar.appear(hp, mhp)

    def on_attack(self, result, target):
        super().on_attack(result, target)
        if self.weapon:
            self.weapon.on_attack(target)
        else:
            if isinstance(target, Humanoid):
                if self.get_skill('steal'):
                    concentration = self.states.get('Concentration')
                    if concentration:
                        concentration.trigger(['spend'])
                        if target.weapon:
                            target.drop()
                        elif target.headgear:
                            target.unheadgear()
                        elif target.armor:
                            target.unarmor()
                    else:
                        self.pos.location.sound.register(self.pos, 0, file='wear', priority=2)
                        item = target.inventory.take_item(0)
                        if item:
                            self.pick_up(item)

    def drop(self):
        if self.weapon:
            r = self.weapon
            self.weapon.on_unwield()
            self.weapon = None
            return r

    def unarmor(self):
        if self.armor and self.armor.removed == 0:
            return self.armor.unwear()

    def unheadgear(self):
        if self.headgear and self.headgear.removed == 0:
            return self.headgear.unwear()

    def make_face(self):
        heads = self.tags.get('head')
        if heads:
            heads = heads.split('&')
            face = []
            from src.tools.Data import Data
            for image in heads:
                face.append(Data.get_graphics(image))
        else:
            face = Humanoid.faces[self.get_seed() % len(Humanoid.faces)]
        from src.form.Picture import Model
        model = Model(face)
        return model

    def unsheathe(self, index):
        item = self.inventory.take_item(index)
        if item:
            def change():
                self.drop()
                item.on_wield(self)
                self.pos.location.sound.register(self.pos, 0, file='wear')
            self.action.act('grab', 2)
            self.action.on_finish = change
            self.action.delay = 4
            return item

    def pick_up(self, item):
        item.relocate(to=self.pos)
        if self.weapon:
            self.inventory.attempt_add(item)
        else:
            if self.is_vacant(item.get_weight()):
                item.on_wield(self)
            else:
                from src.tools.Dialog import Dialog
                params = [self.get_equipment_weight(), self.tags.get('str', 1), item.get_weight()]
                if self == Global.player.character:
                    Global.main.monologue.set(Dialog.get('!heavy', params))

    def get_damage(self):
        r = super().get_damage()
        if self.weapon:
            r += self.weapon.tags.get('dmg', 0)
        return r

    def get_level(self):
        level = super().get_level()
        if self.tags.get('lvl'):
            return level
        else:
            if self.armor:
                level = max(1, level - self.armor.tags.get_level())
            if self.headgear:
                level = max(1, level - self.headgear.tags.get_level())
            return level
