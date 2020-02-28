from src.game import Global
from src.game.Crafting import Crafting
from src.interface.Menu import Menu
from src.interface.Window import Window
from src.tools.Dialog import Dialog


class MenuPlayer(Menu):
    def menu_examine(self):
        if not Global.player.control.target_mark.form.visible:
            Global.player.control.move_mark_toward(0)
        tile = Global.player.control.get_mark()
        if tile:
            if tile.things:
                self.get_message(tile.things[0].describe())(0)
            else:
                self.get_message(Dialog.describe_terrain(tile))(0)
        else:
            self.get_message(Dialog.get('oos'))(0)

    def menu_main(self):
        def update():
            hp = Global.player.character.tags.get('p')
            mhp = Global.player.character.tags.get('p>')
            trmb = self.get_message(Dialog.get('dsc_health', [hp, mhp]))
            text = str(int(hp / mhp * 100)) + '% ' + Dialog.get('health')
            hp_display.set_text(text)
            hp_display.on_click = trmb
        self.update = update
        self.window.add(Menu.make(Dialog.get('equipment'), lambda x: self.direct(self.menu_equipment)))
        self.window.add(Menu.make(Dialog.get('inventory'), lambda x: self.direct(self.menu_inventory)))
        self.window.add(Menu.make(Dialog.get('skills'), lambda x: self.direct(self.menu_skill)))
        hp = Global.player.character.tags.get('p')
        mhp = Global.player.character.tags.get('p>')
        rmb = self.get_message(Dialog.get('dsc_health', [hp, mhp]))
        text = str(int(hp / mhp * 100)) + '% ' + Dialog.get('health')
        hp_display = Menu.make(text, rmb, color=None)
        self.window.add(hp_display)
        rmb = self.get_message(Dialog.get('dsc_date'))
        self.window.add(Menu.make(Dialog.date(Global.player.days), rmb, color=None))
        rmb = self.get_message(Dialog.get('dsc_hunger'))
        fullness = Global.player.character.tags.get('full', 0)
        if fullness <= 0:
            self.window.add(Menu.make(Dialog.get('hungry'), rmb, color=None))
        elif fullness < 10:
            self.window.add(Menu.make(Dialog.get('peckish'), rmb, color=None))

    def menu_skill(self):
        from src.tools.Data import Data
        from src.game.Script import Script
        skills = {}
        for i in Global.player.character.skills:
            if i in skills:
                skills[i] += 1
            else:
                skills[i] = 1
        index = 0
        for k, v in skills.items():
            name = 'sk.' + k
            data = Data.get_line('raw/script.txt', name)
            stacking = Data.get_line('raw/raw.txt', 'stacking skill')[1]
            if k in [x[0] for x in stacking]:
                title = k.title() + ' ' + str(v)
            else:
                title = k.title()
            if data:
                button = Menu.make(title, Script.execute_code, name=name)
            else:
                desc = Data.get_line('raw/descriptions.txt', name)
                if desc:
                    rmb = self.get_message(desc[1])
                else:
                    rmb = None
                button = Menu.make(title, rmb)
            if index < 6:
                self.window.add(button)
            else:
                self.sub_window.add(button)
            index += 1
        self.sub_window.display(1)

    def menu_equipment(self):
        def click_headgear(name):
            Global.player.character.unheadgear()
            self.toggle()

        def click_armor(name):
            Global.player.character.unarmor()
            self.toggle()

        self.window.add(Menu.make(Dialog.get('headgear'), None, color=None))
        self.window.add(Menu.make(Dialog.get('body'), None, color=None))
        self.window.add(Menu.make(Dialog.get('weapon'), None, color=None))
        if not Global.player.character.headgear:
            display = '<' + Dialog.get('noaccessory') + '>'
            self.sub_window.add(Menu.make(display, lambda x: x, color=None))
        else:
            display = Global.player.character.headgear.get_display_name()
            headgear_lmb = self.get_prompt(Global.player.character.headgear.describe(), Dialog.get('drop'),
                                           click_headgear)
            self.sub_window.add(Menu.make(display, headgear_lmb))
        if not Global.player.character.armor:
            display = '<' + Dialog.get('noarmor') + '>'
            self.sub_window.add(Menu.make(display, lambda x: x, color=None))
        else:
            display = Global.player.character.armor.get_display_name()
            armor_lmb = self.get_prompt(Global.player.character.armor.describe(), Dialog.get('drop'), click_armor)
            self.sub_window.add(Menu.make(display, armor_lmb))
        if not Global.player.character.weapon:
            display = '<' + Dialog.get('noweapon') + '>'
            self.sub_window.add(Menu.make(display, lambda x: x, color=None))
        else:
            display = Global.player.character.weapon.get_display_name()
            weapon_lmb = self.get_prompt(Global.player.character.weapon.describe(), Dialog.get('drop'),
                                         lambda l: Global.player.character.drop())
            self.sub_window.add(Menu.make(display, weapon_lmb))
        attack = str(Global.player.character.get_damage())
        defense = str(Global.player.character.get_defense())
        self.sub_window.add(Menu.make(attack, None, color=None))
        self.sub_window.add(Menu.make(defense, None, color=None))
        money = Menu.make('$' + str(Global.player.character.tags.get('money', 0)), None, color=None)
        self.sub_window.add(money)
        self.sub_window.display(1)

    def menu_inventory(self):
        def click(index):
            if Global.player.character.weapon:
                index -= 1
            item = Global.player.character.inventory.get_item(index)
            if item:
                def change():
                    Global.player.character.drop()
                    item.on_wield(Global.player.character)
                Global.player.character.action.act('grab', 8)
                Global.player.character.action.on_finish = change
                Global.player.character.action.delay = 4
            self.toggle()

        def sheathe(arg):
            dropped = Global.player.character.drop()
            Global.player.character.inventory.attempt_add(dropped)
            self.previous()
        temp = self.window.margin.y
        self.window.margin.y = 2
        temp2 = self.sub_window.margin.y
        self.sub_window.margin.y = 2
        items = Global.player.character.inventory.items
        text = 'Capacity: ' + str(len(items)) + ' / 12'
        capacity_label = Menu.make(text, None, None, height=20, color=None)
        capacity_label.margin.load(0, 0)
        capacity_label.document.set_style(0, 99, dict(font_size=12, bold='True'))
        self.window.add(capacity_label)
        capacity = Global.player.character.inventory.get_capacity()
        text = 'Weight: ' + str(Global.player.character.inventory.get_weight()) + ' / ' + str(capacity)
        capacity_label = Menu.make(text, None, None, height=20, color=None)
        capacity_label.margin.load(0, 0)
        capacity_label.document.set_style(0, 99, dict(font_size=12, bold='True'))
        self.sub_window.add(capacity_label)
        count = 0
        weapon = Global.player.character.weapon
        if weapon:
            weapon_display = Window(0, 0, width=260, height=24, multi_line=True)
            weapon_display.set_text(weapon.get_display_name() + ' [' + Dialog.get('held') + ']')
            weapon_display.on_click = self.get_prompt(weapon.describe(), Dialog.get('store'), sheathe, count)
            self.window.add(weapon_display)
            weapon_label = Window(0, 0, width=0, height=24)
            weapon_label.set_text(Dialog.weight(weapon.get_weight()))
            weapon_label.margin.load(100, 0)
            self.sub_window.add(weapon_label)
        for i in items:
            size = min(self.window.height - 48, int(160 * (i.get_weight() / max(1, capacity))))
            button = Window(0, 0, width=260, height=size + 10, multi_line=True)
            button.document.set_style(0, 1, dict(font_size=max(10, min(24, size))))
            button.set_text(i.get_display_name())
            button.on_click = self.get_prompt(i.describe(), Dialog.get('take'), click, count)
            button.width = button.text.content_width + 16
            button.margin.load(8, 0)
            label = Window(0, 0, width=0, height=size + 10, multi_line=False)
            label.document.set_style(0, 1, dict(font_size=max(10, min(24, size))))
            label.set_text(Dialog.weight(i.get_weight()))
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
        if Global.player.character.states.get('Hunger'):
            self.window.add(Menu.make(Dialog.get('hungry'), rmb, color=None))
            self.sub_window.add(Menu.make('', None, None, color=None))
        if Global.player.character.tags['calories'] > 0:
            rmb = self.get_message(Dialog.get('dsc_calories'))
            self.window.add(Menu.make(Dialog.get('calories'), rmb, color=None))
            self.sub_window.add(Menu.make(str(Global.player.character.tags['calories']), None, None, color=None))
        if Global.player.character.tags['protein'] > 0:
            rmb = self.get_message(Dialog.get('dsc_protein'))
            self.window.add(Menu.make(Dialog.get('protein'), rmb, color=None))
            self.sub_window.add(Menu.make(str(Global.player.character.tags['protein']), None, None, color=None))
        self.sub_window.display(1)

    def menu_effects(self):
        for i in Global.player.character.states.buffs:
            dur = i.describe_duration()
            rmb = self.get_message(i.describe() + '\nDuration: ' + dur)
            self.window.add(Menu.make(i.get_display_name(), rmb, color=Window.fore_color_transparent))
            self.sub_window.add(Menu.make(dur, None, color=Window.fore_color_transparent))
        self.sub_window.display(1)

    def menu_travel(self):
        self.history = [self.menu_travel]
        self.history_var = [self.var]
        if len(self.var) > 3:
            destination = self.var[3]
        else:
            destination = self.var[0].title()
        text = Dialog.get('travelto?', [destination])
        panel = Menu.make(text, None, None, color=Window.fore_color_transparent, width=320)
        panel.normal_font_color = Window.font_color1
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
                Crafting.craft(Global.player.character, item, ingreds)
                Global.player.character.action.act('grab', 8)
                self.toggle()
            ingreds = Crafting.get_ingredients(item)
            if ingreds:
                if Crafting.is_craftable(Global.player.character, ingreds):
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
