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
        self.window.add(Menu.make(['Knowledge'], lambda x: self.direct(self.menu_knowledge), None))
        self.window.add(Menu.make(['Help'], lambda x: self.direct(self.menu_help), None))

    def menu_character(self):
        color = Window.fore_color0
        hp = ['Hit Point represents how many attacks you can endure.']
        if self.host.is_headgeared:
            hp.append(str(max(0, self.host.headgear.durability)) + ' HP comes from your headgear.')
        if self.host.is_armored():
            hp.append(str(max(0, self.host.armor.durability)) + ' HP comes from your armor.')
        rmb = self.get_message(hp)
        self.window.add(Menu.make(['Hit Point'], rmb, rmb, color=color))
        self.sub_window.add(Menu.make([str(self.host.durability)], rmb, rmb, color=color))
        rmb = self.get_message(['Strength represents your maximum stamina.',
                                'More stamina allows you to perform actions without having to rest.'])
        self.window.add(Menu.make(['Strength'], rmb, rmb, color=color))
        self.sub_window.add(Menu.make([str(self.host.attributes.strength)], rmb, rmb, color=color))
        rmb = self.get_message(['Agility represents your maximum encumbrance.',
                                'More encumbrance allows you to wear more encumbering armor and headgear.'])
        self.window.add(Menu.make(['Agility'], rmb, rmb, color=color))
        self.sub_window.add(Menu.make([str(self.host.attributes.agility)], rmb, rmb, color=color))
        rmb = self.get_message(['Intelligence represents your maximum memory.',
                                'More memory allows you to craft more spells and items from memory.'])
        self.window.add(Menu.make(['Intelligence'], rmb, rmb, color=color))
        self.sub_window.add(Menu.make([str(self.host.attributes.intelligence)], rmb, rmb, color=color))
        self.window.add(Menu.make(['Status'], lambda l: self.direct(self.menu_status), None))
        self.window.add(Menu.make(['Proficiency'], lambda l: self.direct(self.menu_proficiency), None))
        self.sub_window.display(1)

    def menu_knowledge(self):
        def add_button(window, text):
            def craft(name):
                Crafting.craft(self.host, text)
                self.host.action.set('block')
                self.toggle()
            if Crafting.is_craftable(self.host, text):
                rmb = self.get_message(Crafting.describe(text).split('\n'))
                button = Menu.make([text], craft, rmb)
            else:
                rmb = self.get_message((Crafting.describe(text) + '\nRequirements not met.').split('\n'))
                button = Menu.make([text], None, rmb, color=Window.fore_color0)
                button.hover_font_color = window.normal_font_color
            window.add(button)

        for i in Global.main.player.knowledge[:6]:
            add_button(self.window, i)
        for i in Global.main.player.knowledge[6:]:
            add_button(self.sub_window, i)
        self.window.display(1)
        self.sub_window.display(1)

    def menu_skills(self):
        def assign(index):
            self.var = index
            self.direct(self.menu_slot_reassign)
        control = Global.main.player.control
        key_buttons = []
        for k, v in control.keymap.items():
            if v[:4] == 'item':
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
            self.direct(self.menu_skills)
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
                item = self.host.armor.get_item_at(arg[0], arg[1], pop=1)
                if item:
                    item.on_equip(self.host)
                    self.host.action.set('block')
                else:
                    Global.main.monologue.text('That inventory slot is empty.')
            self.state = self.menu_equipment
            self.display(1)

        def make_pocket_desc(arg):
            item = self.host.armor.get_item_at(arg[0], arg[1])
            if item:
                self.show_dialog(item.describe().split('\n'))
            else:
                self.show_dialog(['This is an inventory slot. Click on this slot while holding a fitting item.'])

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
            button = Menu.make(['Pockets'], lambda l: self.direct(self.menu_skills), rmb, color=Window.fore_color3)
        else:
            button = Menu.make([''], None, None, color=(0, 0, 0, 0))
        self.window.add(button)
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
        for ky, vy in enumerate(self.host.armor.inventory):
            for kx, vx in enumerate(vy):
                if vx == Armor.VACANT:
                    color = Window.fore_color3
                elif vx == Armor.OCCUPIED:
                    color = (120, 120, 120, 220)
                else:
                    color = Window.fore_color0
                slot = Window([40, 40], name=[kx, ky], color=color)
                slot.vec.x = kx * 48
                slot.vec.y = ky * 48
                slot.on_click = make_pocket
                slot.on_r_click = make_pocket_desc
                self.sub_window.next_y = self.sub_window.vec.y + 8
                self.sub_window.add(slot)
        inventory_items = self.host.armor.items
        for i in inventory_items:
            pos = (i.pos[0] * 48)
            pos.x += (48 * i.volume[0]) / 2
            pos.y += (48 * i.volume[1]) / 2
            pos.x -= (i.form.size.x/2 - i.form.pivot.x)
            pos.y -= (i.form.size.y/2 - i.form.pivot.y)
            item_canvas = CanvasWindow(i.form, vec=pos)
            self.sub_window.next_y = self.sub_window.vec.y + 8
            self.sub_window.add(item_canvas)
            item_canvas.display(1)
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

    def menu_status(self):
        for i in self.host.states.buffs:
            rmb = self.get_message(i.describe().split('\n'))
            self.window.add(Menu.make([i.name.title()], rmb, rmb, color=Window.fore_color0))
            if i.duration == -1:
                dur = 'Persistent'
            else:
                dur = str(i.duration)
            self.sub_window.add(Menu.make([dur], None, None, color=Window.fore_color0))
        self.sub_window.display(1)

    def menu_help(self):
        lmb = self.get_message(['WASD and LMB/RMB'])
        rmb = self.get_message(['Display default game controls'])
        button = Menu.make(['Controls'], lmb, rmb)
        self.window.add(button)
        self.window.display(1)
        self.sub_window.display(1)
