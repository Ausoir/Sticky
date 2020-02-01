from src.entity.unit.item.Armor import Armor
from src.entity.unit.item.Headgear import Headgear
from src.game import Global
from src.game.Crafting import Crafting
from src.interface.Menu import Menu
from src.interface.Window import Window
from src.tools.Dialog import Dialog


class MenuPlayer(Menu):
    def menu_main(self):
        self.window.add(Menu.make(Dialog.get('equipment'), lambda x: self.direct(self.menu_equipment)))
        self.window.add(Menu.make(Dialog.get('inventory'), lambda x: self.direct(self.menu_inventory)))
        self.window.add(Menu.make(Dialog.get('knowledge'), lambda x: self.direct(self.menu_knowledge)))
        hp = self.host.tags.get('p')
        mhp = self.host.tags.get('p>')
        rmb = self.get_message(Dialog.get('dsc_health', [hp, mhp]))
        text = str(int(hp / mhp * 100)) + '% ' + Dialog.get('health')
        self.window.add(Menu.make(text, rmb, color=None))
        rmb = self.get_message(Dialog.get('dsc_date'))
        self.window.add(Menu.make(Dialog.date(Global.player.days), rmb, color=None))
        rmb = self.get_message(Dialog.get('dsc_hunger'))
        if self.host.states.get('Hunger'):
            self.window.add(Menu.make(Dialog.get('Hungry'), rmb, color=None))

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

    def menu_equipment(self):
        def click_headgear(name):
            if not self.host.unheadgear() and isinstance(self.host.weapon, Headgear):
                self.host.weapon.use()
            self.direct(self.menu_equipment)

        def click_armor(name):
            if not self.host.unarmor() and isinstance(self.host.weapon, Armor):
                self.host.weapon.use()
            self.direct(self.menu_equipment)

        self.window.add(Menu.make(Dialog.get('headgear'), None, color=None, hover=False))
        self.window.add(Menu.make(Dialog.get('body'), None, color=None, hover=False))
        self.window.add(Menu.make(Dialog.get('weapon'), None, color=None, hover=False))
        if not self.host.headgear:
            display = '<' + Dialog.get('noaccessory') + '>'
            self.sub_window.add(Menu.make(display, lambda x: x, color=None))
        else:
            display = self.host.headgear.get_display_name()
            headgear_lmb = self.get_prompt(self.host.headgear.describe(), Dialog.get('drop'), click_headgear)
            self.sub_window.add(Menu.make(display, headgear_lmb))
        if not self.host.is_armored():
            display = '<' + Dialog.get('noarmor') + '>'
            self.sub_window.add(Menu.make(display, lambda x: x, color=None))
        else:
            display = self.host.armor.get_display_name()
            armor_lmb = self.get_prompt(self.host.armor.describe(), Dialog.get('drop'), click_armor)
            self.sub_window.add(Menu.make(display, armor_lmb))
        if not self.host.is_armed():
            display = '<' + Dialog.get('noweapon') + '>'
            self.sub_window.add(Menu.make(display, lambda x: x, color=None))
        else:
            display = self.host.weapon.get_display_name()
            weapon_lmb = self.get_prompt(self.host.weapon.describe(), Dialog.get('drop'), lambda l: self.host.drop())
            self.sub_window.add(Menu.make(display, weapon_lmb))
        money = Menu.make('$' + str(Global.player.character.tags.get('money', 0)), None, color=None)
        self.sub_window.add(money)
        self.sub_window.display(1)

    def menu_inventory(self):
        def click(index):
            item = self.host.inventory.get_item(index)
            if item:
                def change():
                    self.host.drop()
                    item.on_equip(self.host)
                self.host.action.set('wait')
                self.host.action.set_animation('pocket')
                self.host.action.on_finish = change
                self.host.delay = 4
            self.toggle()

        def sheathe(arg):
            weapon = self.host.drop()
            self.host.inventory.attempt_add(weapon)
            Global.menu.display(1)
        temp = self.window.margin.y
        self.window.margin.y = 2
        temp2 = self.sub_window.margin.y
        self.sub_window.margin.y = 2
        if self.host.is_armed():
            sheathe = Menu.make('Store', sheathe, None, height=20)
            sheathe.margin.load(8, 0)
            sheathe.document.set_style(0, 99, dict(font_size=12, bold='True'))
            self.window.add(sheathe)
        else:
            self.window.add(Menu.make('', None, None, height=20, color=None, hover=False))
        text = 'Capacity: ' + str(self.host.inventory.get_weight()) + ' / ' + str(self.host.inventory.get_capacity())
        capacity_label = Menu.make(text, None, None, height=20, color=None)
        capacity_label.margin.load(0, 0)
        capacity_label.document.set_style(0, 99, dict(font_size=12, bold='True'))
        self.sub_window.add(capacity_label)
        capacity = self.host.inventory.get_capacity()
        if capacity > 0:
            count = 0
            for i in self.host.inventory.items:
                size = int(160 * (i.weight / capacity))
                button = Window(0, 0, width=0, height=size + 8, multi_line=False)
                button.on_click = self.get_prompt(i.describe(), Dialog.get('take'), click, count)
                button.document.set_style(0, 1, dict(font_size=min(24, size)))
                button.set_text(i.get_display_name())
                button.width = button.text.content_width + 16
                button.margin.load(8, 0)
                label = Window(0, 0, width=0, height=size + 8, multi_line=False)
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
        self.window.add(Menu.make(Dialog.get('location'), rmb, color=None))
        self.sub_window.add(Menu.make(Global.player.character.location.name.title(), rmb, color=None))
        rmb = self.get_message(Dialog.get('dsc_date'))
        self.window.add(Menu.make(Dialog.get('date'), rmb, color=None))
        self.sub_window.add(Menu.make(Dialog.date(Global.player.days), rmb, color=None))
        rmb = self.get_message(Dialog.get('dsc_hunger'))
        if self.host.states.get('Hunger'):
            self.window.add(Menu.make(Dialog.get('hungry'), rmb, color=None))
            self.sub_window.add(Menu.make('', None, None, color=None, hover=False))
        if self.host.tags['calories'] > 0:
            rmb = self.get_message(Dialog.get('dsc_calories'))
            self.window.add(Menu.make(Dialog.get('calories'), rmb, color=None))
            self.sub_window.add(Menu.make(str(self.host.tags['calories']), None, None, color=None))
        if self.host.tags['protein'] > 0:
            rmb = self.get_message(Dialog.get('dsc_protein'))
            self.window.add(Menu.make(Dialog.get('protein'), rmb, color=None))
            self.sub_window.add(Menu.make(str(self.host.tags['protein']), None, None, color=None))
        self.sub_window.display(1)

    def menu_martial(self):
        from src.entity.unit.item.Item import Item
        buttons = []
        for i in self.host.action.skills:
            name = i.title()
            rmb = self.get_message(Item.description['Sk.' + name])
            button = Menu.make(name, rmb, color=None)
            buttons.append(button)
        for i in self.host.proficiency:
            name = i.title()
            rmb = self.get_message(Item.description['Pr.' + name])
            button = Menu.make(name + ' Expertise', rmb, color=None)
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
            dur = i.describe_duration()
            rmb = self.get_message(i.describe() + '\nDuration: ' + dur)
            self.window.add(Menu.make(i.get_display_name(), rmb, color=Window.fore_color_transparent))
            self.sub_window.add(Menu.make(dur, None, color=Window.fore_color_transparent, hover=False))
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

    def menu_craft(self):
        def add_button(window, item):
            def craft(arg):
                Crafting.craft(self.host, item, ingreds)
                self.host.action.set('wait')
                self.toggle()
            ingreds = Crafting.get_ingredients(item)
            if ingreds:
                if Crafting.is_craftable(self.host, ingreds):
                    lmb = self.get_prompt(Crafting.describe(item, ingreds), Dialog.get('craft'), craft)
                    button = Menu.make(item, lmb, name=item)
                else:
                    lmb = self.get_message(Crafting.describe(item, ingreds) + '\n' + Dialog.get('reqnotmet'))
                    button = Menu.make(item, lmb, name=item, color=Window.fore_color_disabled)
                window.add(button)
        if self.var:
            for i in self.var[:6]:
                add_button(self.window, i)
            for i in self.var[6:]:
                add_button(self.sub_window, i)
            self.window.display(1)
            self.sub_window.display(1)
