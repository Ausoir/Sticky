from src.entity.unit.item.Armor import Armor
from src.entity.unit.item.Headgear import Headgear
from src.game import Global
from src.game.Crafting import Crafting
from src.interface.Menu import Menu
from src.interface.Window import Window
from src.tools.Dialog import Dialog


class MenuPlayer(Menu):
    def menu_main(self):
        self.window.add(Menu.make(Dialog.get('character'), lambda x: self.direct(self.menu_character), None))
        self.window.add(Menu.make(Dialog.get('equipment'), lambda x: self.direct(self.menu_equipment), None))
        self.window.add(Menu.make(Dialog.get('inventory'), lambda x: self.direct(self.menu_inventory), None))
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
            button = Menu.make(i, rmb, rmb)
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

        if not self.host.headgear:
            rmb = None
            display = '<' + Dialog.get('noaccessory') + '>'
        else:
            rmb = self.get_message(self.host.headgear.describe())
            display = self.host.headgear.get_display_name()
        self.window.add(Menu.make(Dialog.get('headgear'), None, None, color=None, hover=False))
        self.sub_window.add(Menu.make(display, click_headgear, rmb))
        rmb = self.get_message(self.host.armor.describe())
        if not self.host.is_armored():
            display = '<' + Dialog.get('noarmor') + '>'
        else:
            display = self.host.armor.get_display_name()
        self.window.add(Menu.make(Dialog.get('body'), None, None, color=None, hover=False))
        self.sub_window.add(Menu.make(display, click_armor, rmb))
        if len(self.host.armor.pockets) > 0:
            rmb = self.get_message('Designate items for quick access.')
            button = Menu.make('<' + Dialog.get('Pockets') + '>', lambda l: self.direct(self.menu_pocket), rmb)
            self.window.add(Menu.make('', None, None, color=None, hover=False))
            self.sub_window.add(button)
        rmb = self.get_message(self.host.weapon.describe())
        if not self.host.is_armed():
            display = '<' + Dialog.get('noweapon') + '>'
        else:
            display = self.host.weapon.get_display_name()
        self.window.add(Menu.make(Dialog.get('weapon'), None, None, color=None, hover=False))
        self.sub_window.add(Menu.make(display, lambda l: self.host.drop(), rmb))
        money = Menu.make('$' + str(Global.player.character.tags['money']), None, None, color=None)
        self.sub_window.add(money)
        self.sub_window.display(1)

    def menu_inventory(self):
        def click(index):
            item = self.host.inventory.items[index]
            if item:
                def change():
                    self.host.drop()
                    self.host.inventory.items.remove(item)
                    item.on_equip(self.host)
                self.host.action.set('wait')
                self.host.action.set_animation('pocket')
                self.host.action.on_finish = change
                self.host.delay = 4

        def sheathe(arg):
            weapon = self.host.drop()
            self.host.inventory.attempt_add(weapon)
        temp = self.window.margin.y
        self.window.margin.y = 2
        temp2 = self.sub_window.margin.y
        self.sub_window.margin.y = 2
        if self.host.is_armed():
            sheathe = Menu.make('Sheathe', sheathe, None, height=20)
            sheathe.margin.load(8, 0)
            sheathe.document.set_style(0, 99, dict(font_size=12, bold='True'))
            self.window.add(sheathe)
        else:
            self.window.add(Menu.make('', None, None, height=20, color=None, hover=False))
        text = 'Capacity: ' + str(self.host.inventory.get_weight()) + ' / ' + str(self.host.inventory.get_capacity())
        capacity = Menu.make(text, None, None, height=20, color=None)
        capacity.margin.load(0, 0)
        capacity.document.set_style(0, 99, dict(font_size=12, bold='True'))
        self.sub_window.add(capacity)
        count = 0
        for i in self.host.inventory.items:
            size = int(160 * (i.weight / self.host.inventory.get_capacity()))
            button = Window(0, 0, width=0, height=size + 8, multi_line=False, name=count)
            button.on_click = click
            button.document.set_style(0, 1, dict(font_size=min(24, size)))
            button.set_text(i.get_display_name())
            button.width = button.text.content_width + 16
            button.margin.load(8, 0)
            label = Window(0, 0, width=0, height=size + 8, multi_line=False, name=count)
            label.document.set_style(0, 1, dict(font_size=min(24, size)))
            label.set_text(Dialog.weight(i.weight))
            label.margin.load(100, 0)
            self.window.add(button)
            self.sub_window.add(label)
            count += 1
        self.sub_window.display(1)
        self.window.margin.y = temp
        self.sub_window.margin.y = temp2

    def menu_status(self):
        rmb = self.get_message(Dialog.get('dsc_location'))
        self.window.add(Menu.make(Dialog.get('location'), rmb, rmb, color=None))
        self.sub_window.add(Menu.make(Global.player.character.location.name.title(), rmb, rmb, color=None))
        rmb = self.get_message(Dialog.get('dsc_date'))
        self.window.add(Menu.make(Dialog.get('date'), rmb, rmb, color=None))
        self.sub_window.add(Menu.make(Dialog.date(Global.player.days), rmb, rmb, color=None))
        rmb = self.get_message(Dialog.get('dsc_hunger'))
        if self.host.states.get('Hunger'):
            self.window.add(Menu.make(Dialog.get('hungry'), rmb, rmb, color=None))
            self.sub_window.add(Menu.make('', None, None, color=None, hover=False))
        if self.host.var['calories'] > 0:
            rmb = self.get_message(Dialog.get('dsc_calories'))
            self.window.add(Menu.make(Dialog.get('calories'), rmb, rmb, color=None))
            self.sub_window.add(Menu.make(str(self.host.var['calories']), None, None, color=None))
        if self.host.var['protein'] > 0:
            rmb = self.get_message(Dialog.get('dsc_protein'))
            self.window.add(Menu.make(Dialog.get('protein'), rmb, rmb, color=None))
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
