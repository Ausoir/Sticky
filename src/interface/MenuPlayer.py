from src.entity.unit.item.Armor import Armor
from src.entity.unit.item.Headgear import Headgear
from src.game import Global
from src.game.Crafting import Crafting
from src.interface.CanvasWindow import CanvasWindow
from src.interface.Menu import Menu
from src.interface.Window import Window
from src.tools.Dialog import Dialog


class MenuPlayer(Menu):
    def menu_main(self):
        self.window.add(Menu.make(Dialog.get('character'), lambda x: self.direct(self.menu_character), None))
        self.window.add(Menu.make(Dialog.get('equipment'), lambda x: self.direct(self.menu_equipment), None))
        if len(Global.player.knowledge) > 0:
            self.window.add(Menu.make(Dialog.get('knowledge'), lambda x: self.direct(self.menu_knowledge), None))
        if self.host.action.skills or self.host.proficiency:
            self.window.add(Menu.make(Dialog.get('skill'), lambda l: self.direct(self.menu_martial), None))

    def menu_character(self):
        color = Window.fore_color_transparent
        rmb = self.get_message(Dialog.get('dsc_HP'))
        text = str(self.host.durability) + ' ' + Dialog.get('HP')
        self.window.add(Menu.make(text, rmb, rmb, color=color))
        rmb = self.get_message(Dialog.get('dsc_STR', [self.host.var['protein']]))
        text = str(self.host.attributes.strength) + ' ' + Dialog.get('Strength')
        self.window.add(Menu.make(text, rmb, rmb, color=color))
        rmb = self.get_message(Dialog.get('dsc_AGI', [self.host.var['calories']]))
        text = str(self.host.attributes.agility) + ' ' + Dialog.get('Agility')
        self.window.add(Menu.make(text, rmb, rmb, color=color))
        rmb = self.get_message(Dialog.get('dsc_INT', [self.host.var['calories']]))
        text = str(self.host.attributes.intelligence) + ' ' + Dialog.get('Intelligence')
        self.window.add(Menu.make(text, rmb, rmb, color=color))
        if 'power_1' in self.host.var:
            rmb = self.get_message(Dialog.get('dsc_ENG'))
            text = str(self.host.attributes.breath) + ' ' + Dialog.get('Energy')
            self.window.add(Menu.make(text, rmb, rmb, color=color))
        rmb = self.get_message(Dialog.get('dsc_location'))
        self.sub_window.add(Menu.make(Global.player.character.location.name.title(), rmb, rmb, color=None))
        rmb = self.get_message(Dialog.get('dsc_date'))
        self.sub_window.add(Menu.make(Dialog.date(Global.player.days), rmb, rmb, color=None))
        rmb = self.get_message(Dialog.get('dsc_hunger'))
        if self.host.states.get('Hunger'):
            self.sub_window.add(Menu.make(Dialog.get('Hungry'), rmb, rmb, color=None))
        self.sub_window.display(1)

    def menu_knowledge(self):
        count = 0
        for i in Global.player.knowledge:
            count += 1
            if Global.player.is_spell(i):
                rmb = self.get_message((Crafting.describe(i) + '\n' + Dialog.get('dsc_craftDesk')))
            else:
                rmb = self.get_message((Crafting.describe(i) + '\n' + Dialog.get('dsc_craftWorkbench')))
            button = Menu.make(i, rmb, rmb, resize=False)
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
                text = Dialog.get('Key') + ' [' + control.get_key_name(k) + ']'
                button = Menu.make(text, None, None, color=(0, 0, 0, 0))
                button.hover_font_color = None
                key_buttons.append(button)
                self.window.add(button)
        for k, v in enumerate(self.host.armor.pockets):
            if v == -1:
                desc = self.get_message(Dialog.get('assign item'))
                action_button = Menu.make('<' + Dialog.get('Assign') + '>', assign, desc, name=k)
            else:
                action_button = Menu.make(self.host.armor.items[v].name, assign, None, name=k)
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
            self.window.add(Menu.make(i.name, assign_click, None, name=first_key))
        self.sub_window.flush()
        for second_key, i in enumerate(second):
            self.sub_window.add(Menu.make(i.name, assign_click, None, name=second_key + 6))
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
                    Global.player.character.say(Dialog.get('cant fit', [weapon.get_display_name()]))
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
                    Global.player.character.say(Dialog.get('cant store'))
            self.state = self.menu_equipment
            self.display(1)

        def make_pocket_desc(arg):
            item = self.host.armor.get_item_at(arg[0], arg[1])
            if item:
                self.show_dialog(item.describe())
            else:
                self.show_dialog(Dialog.get('dsc_inventoryslot'))

        rmb = self.get_message(self.host.headgear.describe())
        if not self.host.is_headgeared():
            display = '<' + Dialog.get('noaccessory') + '>'
        else:
            display = self.host.headgear.get_display_name()
        self.window.add(Menu.make(display, click_headgear, rmb, resize=False))
        rmb = self.get_message(self.host.armor.describe())
        if not self.host.is_armored():
            display = '<' + Dialog.get('noarmor') + '>'
        else:
            display = self.host.armor.get_display_name()
        self.window.add(Menu.make(display, click_armor, rmb, resize=False))
        if len(self.host.armor.pockets) > 0:
            rmb = self.get_message('Designate items for quick access.')
            button = Menu.make('<' + Dialog.get('Pockets') + '>', lambda l: self.direct(self.menu_pocket), rmb)
            self.window.add(button)
        if 'offhand' in self.host.action.skills:
            rmb = self.get_message(self.host.offhand.describe())
            display = self.host.offhand.get_display_name()
            if not self.host.is_shielded():
                display = '<' + Dialog.get('nooffhand') + '>'
            self.window.add(Menu.make(display, lambda l: self.host.swap(), rmb, resize=False))
        rmb = self.get_message(self.host.weapon.describe())
        if not self.host.is_armed():
            display = '<' + Dialog.get('noweapon') + '>'
        else:
            display = self.host.weapon.get_display_name()
        self.window.add(Menu.make(display, lambda l: self.host.drop(), rmb, resize=False))
        if self.host.armor.get_inventory_slots() > 0:
            rmb = self.get_message(Dialog.get('dsc_inventory'))
            inventory = Menu.make(Dialog.get('inventoryslots'), rmb, rmb, color=Window.fore_color_transparent)
        else:
            rmb = self.get_message(Dialog.get('dsc_noinventory'))
            inventory = Menu.make(Dialog.get('noinventory'), rmb, rmb, color=Window.fore_color_transparent)
        self.sub_window.add(inventory)
        for ky, vy in enumerate(self.host.armor.inventory):
            for kx, vx in enumerate(vy):
                if vx == Armor.VACANT:
                    color = Window.fore_color3
                elif vx == Armor.OCCUPIED:
                    color = (120, 120, 120, 220)
                else:
                    color = Window.fore_color_transparent
                slot = Window(0, 0, width=40, height=40, name=[kx, ky], color=color)
                slot.x = kx * 48
                slot.y = ky * 48 + 48
                slot.on_click = make_pocket
                slot.on_r_click = make_pocket_desc
                slot.hover_color = None
                self.sub_window.next_y = self.sub_window.y + 8
                self.sub_window.add(slot)
        inventory_items = self.host.armor.items
        for i in inventory_items:
            pos = (i.pos * 48)
            pos.x += (48 * i.volume[0]) / 2
            pos.y += (48 * i.volume[1]) / 2 + 48
            pos.x -= (i.form.width/2 - i.form.image.anchor_x)
            pos.y -= (i.form.height/2 - i.form.image.anchor_y)
            item_canvas = CanvasWindow(pos.x, pos.y, i.form.image)
            self.sub_window.next_y = self.sub_window.y + 8
            self.sub_window.add(item_canvas)
            item_canvas.display(1)
        money = Menu.make('$' + str(Global.player.character.var['money']), None, None, color=None)
        self.window.add(money)
        self.sub_window.display(1)

    def menu_status(self):
        rmb = self.get_message(Dialog.get('dsc_location'))
        self.window.add(Menu.make(Dialog.get('Location'), rmb, rmb, color=None))
        self.sub_window.add(Menu.make(Global.player.character.location.name.title(), rmb, rmb, color=None))
        rmb = self.get_message(Dialog.get('dsc_date'))
        self.window.add(Menu.make(Dialog.get('Date'), rmb, rmb, color=None))
        self.sub_window.add(Menu.make(Dialog.date(Global.player.days), rmb, rmb, color=None))
        rmb = self.get_message(Dialog.get('dsc_hunger'))
        if self.host.states.get('Hunger'):
            self.window.add(Menu.make(Dialog.get('Hungry'), rmb, rmb, color=None))
            self.sub_window.add(Menu.make('', None, None, color=None, hover=False))
        if self.host.var['calories'] > 0:
            rmb = self.get_message(Dialog.get('dsc_calories'))
            self.window.add(Menu.make(Dialog.get('Calories'), rmb, rmb, color=None))
            self.sub_window.add(Menu.make(str(self.host.var['calories']), None, None, color=None))
        if self.host.var['protein'] > 0:
            rmb = self.get_message(Dialog.get('dsc_protein'))
            self.window.add(Menu.make(Dialog.get('Protein'), rmb, rmb, color=None))
            self.sub_window.add(Menu.make(str(self.host.var['protein']), None, None, color=None))
        self.sub_window.display(1)

    def menu_martial(self):
        from src.entity.unit.item.Item import Item
        buttons = []
        for i in self.host.action.skills:
            name = i.title()
            rmb = self.get_message(Item.description['Sk.' + name])
            button = Menu.make(name, rmb, rmb, color=None)
            buttons.append(button)
        for i in self.host.proficiency:
            name = i.title()
            rmb = self.get_message(Item.description['Pr.' + name])
            button = Menu.make(name + ' Expertise', rmb, rmb, color=None)
            buttons.append(button)
        count = 0
        for i in buttons:
            count += 1
            if count < 6:
                self.window.add(i)
            else:
                self.sub_window.add(i)
        self.sub_window.display(1)

    def menu_effects(self):
        for i in self.host.states.buffs:
            if i.duration == -1:
                dur = Dialog.get('persistent')
            else:
                dur = str(i.duration)
            rmb = self.get_message(i.describe() + ['Duration: ' + dur])
            self.window.add(Menu.make(i.name.title(), rmb, rmb, color=Window.fore_color_transparent))
            self.sub_window.add(Menu.make(dur, None, None, color=Window.fore_color_transparent, hover=False))
        self.sub_window.display(1)

    def menu_travel(self):
        self.history = [self.menu_travel]
        self.history_var = [self.var]
        if len(self.var) > 3:
            destination = self.var[3]
        else:
            destination = self.var[0].title()
        text = Dialog.get('travelto?', [destination])
        panel = Menu.make(text, None, None, color=Window.fore_color_transparent, hover=False, width=320)
        panel.normal_font_color = Window.font_color1
        panel.hover_font_color = Window.font_color3
        panel.redraw()
        self.window.add(panel)
        from src.entity.Space import Space

        def travel(name):
            if Global.player.eat():
                Global.player.sleep(1)
                Global.player.travel(self.var[0], Space(int(self.var[1]), int(self.var[2])))
            else:
                self.toggle()
        rmb = self.get_message(Dialog.get('travelto', [destination]))
        self.window.next_y = self.window.height + self.window.y - 40 - self.window.margin.y
        self.window.add(Menu.make(Dialog.get('Travel'), travel, rmb, width=320))
        self.sub_window.display(1)
