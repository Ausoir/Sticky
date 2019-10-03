from src.entity.unit.item.Armor import Armor
from src.entity.unit.item.Headgear import Headgear
from src.game import Global
from src.game.Crafting import Crafting
from src.interface.CanvasWindow import CanvasWindow
from src.interface.Menu import Menu
from src.interface.Window import Window


class MenuPlayer(Menu):
    def menu_main(self):
        self.window.add(Menu.make(['Character'], lambda x: self.direct(self.menu_character), None))
        self.window.add(Menu.make(['Equipment'], lambda x: self.direct(self.menu_equipment), None))
        if len(Global.player.knowledge) > 0:
            self.window.add(Menu.make(['Knowledge'], lambda x: self.direct(self.menu_knowledge), None))

    def menu_character(self):
        color = Window.fore_color_transparent
        rmb = self.get_message(['Hit Point represents how many attacks you can endure.',
                                'Hit Point is usually equal to your armor durability + 1.'])
        self.sub_window.add(Menu.make([str(self.host.durability) + ' HP'], rmb, rmb, color=color))
        rmb = self.get_message(['Strength represents your maximum stamina.',
                                'More stamina allows you to perform actions without having to rest.',
                                'Increase this stat by finding a target dummy or find a trainer.',
                                'Protein is required to level up this attribute.'])
        self.sub_window.add(Menu.make([str(self.host.attributes.strength) + ' Strength'], rmb, rmb, color=color))
        rmb = self.get_message(['Agility represents your maximum encumbrance.',
                                'More encumbrance allows you to wear more advanced equipment.',
                                'Increase this stat by finding a target dummy or find a trainer.',
                                'Calories are required to level up this attribute.'])
        self.sub_window.add(Menu.make([str(self.host.attributes.agility) + ' Agility'], rmb, rmb, color=color))
        rmb = self.get_message(['Intelligence represents your maximum memory.',
                                'More memory allows you to craft more spells and items from memory.',
                                'Increase this stat by casting Clairvoyance or find a trainer.',
                                'Calories are required to level up this attribute.'])
        self.sub_window.add(Menu.make([str(self.host.attributes.intelligence) + ' Intelligence'], rmb, rmb, color=color))
        if self.host.var['power'] != 'Power':
            rmb = self.get_message(['Energy is required to perform some unique skills.',
                                    'Energy can be restored by resting at a bed or sofa.',
                                    'Maximum Energy is equal to the sum of Strength, Agility, and Intelligence.'])
            self.sub_window.add(Menu.make([str(self.host.attributes.breath) + ' Energy'], rmb, rmb, color=color))
        self.window.add(Menu.make(['Status'], lambda l: self.direct(self.menu_status), None))
        if self.host.states.buffs:
            self.window.add(Menu.make(['Condition'], lambda l: self.direct(self.menu_effects), None))
        if self.host.proficiency:
            self.window.add(Menu.make(['Proficiency'], lambda l: self.direct(self.menu_proficiency), None))
        if self.host.action.skills:
            self.window.add(Menu.make(['Skills'], lambda l: self.direct(self.menu_martial), None))
        self.sub_window.display(1)

    def menu_knowledge(self):
        count = 0
        for i in Global.player.knowledge:
            count += 1
            if Global.player.is_spell(i):
                rmb = self.get_message((Crafting.describe(i) + '\nCraft this spell at a Desk.').split('\n'))
            else:
                rmb = self.get_message((Crafting.describe(i) + '\nCraft this item at a Workbench.').split('\n'))
            button = Menu.make([i], rmb, rmb, resize=False)
            if count <= 6:
                self.window.add(button)
            else:
                self.sub_window.add(button)
        self.window.display(1)
        self.sub_window.display(1)

    def menu_pocket(self):
        def assign(index):
            self.var = index
            self.direct(self.menu_slot_reassign)
        control = Global.player.control
        key_buttons = []
        for k, v in control.keymap.items():
            if v.startswith('pocket_'):
                button = Menu.make(['Key [' + control.get_key_name(k) + ']'], None, None, color=(0, 0, 0, 0))
                button.hover_font_color = None
                key_buttons.append(button)
                self.window.add(button)
        for k, v in enumerate(self.host.armor.pockets):
            if v == -1:
                desc = self.get_message(['Click to assign item.'])
                action_button = Menu.make(['<Assign>'], assign, desc, name=k)
            else:
                action_button = Menu.make([self.host.armor.items[v].name], assign, None, name=k)
            self.sub_window.add(action_button)
        self.sub_window.display(1)

    def menu_slot_reassign(self):
        def assign_click(index):
            self.host.armor.pockets[self.var] = index
            self.direct(self.menu_pocket)
        first = self.host.armor.items[:6]
        second = self.host.armor.items[6:]
        self.window.flush()
        for first_key, i in enumerate(first):
            self.window.add(Menu.make([i.name], assign_click, None, name=first_key))
        self.sub_window.flush()
        for second_key, i in enumerate(second):
            self.sub_window.add(Menu.make([i.name], assign_click, None, name=second_key + 6))
        self.window.display(1)
        self.sub_window.display(1)

    def menu_equipment(self):
        def click_headgear(name):
            if not self.host.unheadgear() and isinstance(self.host.weapon, Headgear):
                self.host.weapon.use()
            self.direct(self.menu_equipment)

        def click_armor(name):
            if not self.host.unarmor() and isinstance(self.host.weapon, Armor):
                self.host.weapon.use()
            self.direct(self.menu_equipment)

        def make_pocket(arg):
            if self.host.is_armed():
                weapon = self.host.weapon
                if self.host.armor.is_vacant(weapon, arg[0], arg[1]):
                    self.host.drop()
                    self.host.armor.add_inventory(weapon, arg[0], arg[1])
                else:
                    Global.player.character.say(weapon.get_display_name() + ' cannot fit in there!')
            else:
                item = self.host.armor.get_item_at(arg[0], arg[1], pop=1)
                if item:
                    def change():
                        item.on_equip(self.host)
                    self.host.action.set('wait')
                    self.host.action.set_animation('interact')
                    self.host.action.on_finish = change
                    self.host.delay = 12
                else:
                    Global.player.character.say('Nothing to store in that inventory slot!')
            self.state = self.menu_equipment
            self.display(1)

        def make_pocket_desc(arg):
            item = self.host.armor.get_item_at(arg[0], arg[1])
            if item:
                self.show_dialog(item.describe().split('\n'))
            else:
                self.show_dialog(['This is an inventory slot. Click on this slot while holding an item small enough.'])

        rmb = self.get_message(self.host.headgear.describe().split('\n'))
        display = self.host.headgear.get_display_name()
        if not self.host.is_headgeared():
            display = '<No Accessory>'
        self.window.add(Menu.make([display], click_headgear, rmb, resize=False))
        rmb = self.get_message(self.host.armor.describe().split('\n'))
        display = self.host.armor.get_display_name()
        if not self.host.is_armored():
            display = '<No Armor>'
        self.window.add(Menu.make([display], click_armor, rmb, resize=False))
        if len(self.host.armor.pockets) > 0:
            rmb = self.get_message(['Designate items for quick access.'])
            button = Menu.make(['Pockets'], lambda l: self.direct(self.menu_pocket), rmb, color=Window.fore_color3)
            self.window.add(button)
        if 'offhand' in self.host.action.skills:
            rmb = self.get_message(self.host.offhand.describe().split('\n'))
            display = self.host.offhand.get_display_name()
            if not self.host.is_shielded():
                display = '<No Offhand>'
            self.window.add(Menu.make([display], lambda l: self.host.swap(), rmb, resize=False))
        rmb = self.get_message(self.host.weapon.describe().split('\n'))
        display = self.host.weapon.get_display_name()
        if not self.host.is_armed():
            display = '<No Weapon>'
        self.window.add(Menu.make([display], lambda l: self.host.drop(), rmb, resize=False))
        if self.host.armor.get_inventory_slots() > 0:
            rmb = self.get_message(['Each white square below represents an empty inventory slot.'])
            inventory = Menu.make(['Inventory Slots'], rmb, rmb, color=Window.fore_color_transparent)
        else:
            rmb = self.get_message(['Your armor does not provide any inventory space.'])
            inventory = Menu.make(['No Inventory'], rmb, rmb, color=Window.fore_color_transparent)
        self.sub_window.add(inventory)
        for ky, vy in enumerate(self.host.armor.inventory):
            for kx, vx in enumerate(vy):
                if vx == Armor.VACANT:
                    color = Window.fore_color3
                elif vx == Armor.OCCUPIED:
                    color = (120, 120, 120, 220)
                else:
                    color = Window.fore_color_transparent
                slot = Window([40, 40], name=[kx, ky], color=color)
                slot.vec.x = kx * 48
                slot.vec.y = ky * 48 + 48
                slot.on_click = make_pocket
                slot.on_r_click = make_pocket_desc
                self.sub_window.next_y = self.sub_window.vec.y + 8
                self.sub_window.add(slot)
        inventory_items = self.host.armor.items
        for i in inventory_items:
            pos = (i.pos * 48)
            pos.x += (48 * i.volume[0]) / 2
            pos.y += (48 * i.volume[1]) / 2 + 48
            pos.x -= (i.form.size.x/2 - i.form.pivot.x)
            pos.y -= (i.form.size.y/2 - i.form.pivot.y)
            item_canvas = CanvasWindow(i.form, vec=pos)
            self.sub_window.next_y = self.sub_window.vec.y + 8
            self.sub_window.add(item_canvas)
            item_canvas.display(1)
        money = Menu.make(['$' + str(Global.player.character.var['money'])], None, None, color=None)
        self.window.add(money)
        self.sub_window.display(1)

    def menu_status(self):
        rmb = self.get_message(['Your current location.'])
        self.window.add(Menu.make(['Location'], rmb, rmb, color=None))
        self.sub_window.add(Menu.make([Global.player.character.location.name.title()], rmb, rmb, color=None))
        rmb = self.get_message(['Current date, in YYYY/MM/DD format.'])
        self.window.add(Menu.make(['Date'], rmb, rmb, color=None))
        from src.tools.Dialog import Dialog
        self.sub_window.add(Menu.make([Dialog.date(Global.player.days)], rmb, rmb, color=None))
        rmb = self.get_message(['You cannot perform time consuming actions like resting or travelling while thirsty.',
                                'Become quenched by putting drinkable items in inventory or drinking them manually.'])
        if self.host.states.get('Thirst'):
            self.window.add(Menu.make(['Thirsty'], rmb, rmb, color=None))
        else:
            self.window.add(Menu.make(['Quenched'], rmb, rmb, color=None))
        self.sub_window.add(Menu.make([''], None, None, color=None, hover=False))
        if self.host.var['calories'] > 0:
            rmb = self.get_message(['Calories are essential for training Agility and Intelligence.',
                                    'You cannot consume food while you have calories more than 0.'])
            self.window.add(Menu.make(['Calories'], rmb, rmb, color=None))
            self.sub_window.add(Menu.make([str(self.host.var['calories'])], None, None, color=None))
        if self.host.var['protein'] > 0:
            rmb = self.get_message(['Protein are essential for training Strength.'])
            self.window.add(Menu.make(['Protein'], rmb, rmb, color=None))
            self.sub_window.add(Menu.make([str(self.host.var['protein'])], None, None, color=None))
        self.sub_window.display(1)

    def menu_proficiency(self):
        count = 0
        for i in self.host.proficiency:
            button = Menu.make([i.title()], None, None)
            if count < 6:
                self.window.add(button)
            else:
                self.sub_window.add(button)
            count += 1
        self.sub_window.display(1)

    def menu_martial(self):
        count = 0
        for i in self.host.action.skills:
            button = Menu.make([i.title()], None, None)
            if count < 6:
                self.window.add(button)
            else:
                self.sub_window.add(button)
            count += 1
        self.sub_window.display(1)

    def menu_effects(self):
        for i in self.host.states.buffs:
            rmb = self.get_message(i.describe().split('\n'))
            self.window.add(Menu.make([i.name.title()], rmb, rmb, color=Window.fore_color_transparent))
            if i.duration == -1:
                dur = 'Persistent'
            else:
                dur = str(i.duration)
            self.sub_window.add(Menu.make([dur], None, None, color=Window.fore_color_transparent))
        self.sub_window.display(1)

    def menu_dead(self):
        if self.var[0] == 0:
            self.show_dialog(['You die...', 'Sign: ' + self.var[1]])
        elif self.var[0] == 1:
            self.show_dialog(['You have been revived by your medical guild.',
                              'Your insurance expires.', 'Good luck!'])
        else:
            self.show_dialog(['Your ' + self.var[2] + ' insurance does not cover death via ' + self.var[1] + '.',
                              ' You die...'])
