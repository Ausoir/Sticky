from src.game import Global
from src.game.Crafting import Crafting
from src.game.Script import Script
from src.interface.Menu import Menu
from src.interface.Window import Window
from src.tools.Data import Data
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
        Global.player.control.target_mark.form.show(False)

    def menu_world(self):
        def enter(arg):
            if True:  # not Data.is_file('save/' + map_name + '.map'):
                landscape = host.pos.name
                for i in host.pos.things:
                    if i.tags.get('landscape'):
                        landscape = i.name.lower()
                        break
                from src.map.Generator import Generator
                location = Generator.generate_terrain(map_name, landscape)
                location.save()
            host.location.tags.set('enterx', host.pos.x)
            host.location.tags.set('entery', host.pos.y)
            Global.player.player.remove()
            Global.player.travel(map_name)
        host = Global.player.character
        map_name = 'instance'
        # map_name = 'x' + str(host.pos.x) + 'y' + str(host.pos.y)
        self.window.add(Menu.make(Dialog.get('Enter map'), enter))
        a_hp, a_mhp, hp, mhp = host.get_durability()
        rmb = self.get_message(Dialog.get('dsc_health', [a_hp, a_mhp, hp, mhp]))
        text = str(int((hp + a_hp) / (mhp + a_mhp) * 100)) + '% ' + Dialog.get('Health')
        hp_display = Menu.make(text, rmb, color=None)
        self.window.add(hp_display)
        datetime = Dialog.date(Global.player.days)
        hunger = host.tags.get('hunger', 0)
        self.window.add(Menu.make(str(hunger) + '% ' + Dialog.get('Hunger'), rmb, color=None))
        rmb = self.get_message(Dialog.get('dsc_date', [datetime, hunger]))
        self.window.add(Menu.make(datetime, rmb, color=None))

    def menu_character(self):
        host = Global.player.character
        attack = str(host.get_skill('dexterity', stacks=True)) + ' ~ ' + str(host.get_damage())
        mat_def = host.tags.get('def', 0)
        defense = str(mat_def) + ' ~ ' + str(host.get_defense() + mat_def)
        rmb = self.get_message(Dialog.get('dsc_level'))
        self.window.add(Menu.make(Dialog.get('Level'), rmb, color=None))
        tag_level = host.tags.get('level', 0)
        level = str(int(tag_level / 100)) + ' (' + str(tag_level % 100) + '%)'
        self.sub_window.add(Menu.make(level, None, color=None))
        rmb = self.get_message(Dialog.get('dsc_attack'))
        self.window.add(Menu.make(Dialog.get('Attack'), rmb, color=None))
        self.sub_window.add(Menu.make(attack, None, color=None))
        rmb = self.get_message(Dialog.get('dsc_defense'))
        self.window.add(Menu.make(Dialog.get('Defense'), rmb, color=None))
        self.sub_window.add(Menu.make(defense, None, color=None))
        rmb = self.get_message(Dialog.get('dsc_reputation'))
        self.window.add(Menu.make(Dialog.get('Reputation'), rmb, color=None))
        self.sub_window.add(Menu.make('1', None, color=None))
        self.window.add(Menu.make(Dialog.get('Status'), lambda l: self.direct(self.menu_effects)))
        self.window.add(Menu.make(Dialog.get('Give up'), Script.execute_code, name='suicide'))
        self.sub_window.display(1)

    def menu_main(self):
        def update():
            a_hp, a_mhp, hp, mhp = host.get_durability()
            rmb = self.get_message(Dialog.get('dsc_health', [a_hp, a_mhp, hp, mhp]))
            text = str(int((hp + a_hp) / (mhp + a_mhp) * 100)) + '% ' + Dialog.get('Health')
            hp_display.set_text(text)
            hp_display.on_click = rmb

            hunger = host.tags.get('hunger', 0)
            datetime = Dialog.date(Global.player.days)
            if Global.player.is_hungry():
                text = Dialog.get('Hungry')
                rmb = self.get_message(Dialog.get('dsc_hunger', [datetime, hunger]))
            else:
                text = datetime
                rmb = self.get_message(Dialog.get('dsc_date', [datetime, hunger]))
            button_date.set_text(text)
            button_date.on_click = rmb
        host = Global.player.character
        self.update = update
        self.window.add(Menu.make(Dialog.get('Character'), lambda x: self.direct(self.menu_character)))
        from src.entity.unit.Humanoid import Humanoid
        if isinstance(host, Humanoid):
            self.window.add(Menu.make(Dialog.get('Equipment'), lambda x: self.direct(self.menu_equipment)))
            self.window.add(Menu.make(Dialog.get('Inventory'), lambda x: self.direct(self.menu_inventory)))
        self.window.add(Menu.make(Dialog.get('Skills'), lambda x: self.direct(self.menu_skill)))
        hp_display = Menu.make('', None, color=None)
        self.window.add(hp_display)
        button_date = Menu.make('', None, color=None)
        self.window.add(button_date)

    def menu_skill(self):
        skills = {}
        for i in Global.player.character.skills:
            if i in skills:
                skills[i] += 1
            else:
                skills[i] = 1
        index = 0
        for k, v in skills.items():
            name = 'sk.' + k
            stacking = Data.get_line('raw.txt', 'stacking skill')[1]
            if k in [x[0] for x in stacking]:
                title = k.title() + ' ' + str(v)
            else:
                title = k.title()
            data = Data.get_line('script.txt', name)
            desc = Data.get_line('descriptions.txt', name)
            if data and desc:
                button = Menu.make(title, self.get_prompt(desc[1], Dialog.get('Perform'), Script.execute_code, name))
            elif data:
                button = Menu.make(title, Script.execute_code, name=name)
            elif desc:
                button = Menu.make(title, self.get_message(desc[1]))
            else:
                button = Menu.make(title, self.get_message(Dialog.get('!dsc_skill')))
            if index < 6:
                self.window.add(button)
            else:
                self.sub_window.add(button)
            index += 1
        self.sub_window.display(1)

    def menu_equipment(self):
        def click_headgear(name):
            Global.player.character.unheadgear()

        def click_armor(name):
            Global.player.character.unarmor()

        self.window.add(Menu.make(Dialog.get('Headgear'), None, color=None))
        self.window.add(Menu.make(Dialog.get('Body'), None, color=None))
        self.window.add(Menu.make(Dialog.get('Weapon'), None, color=None))
        if not Global.player.character.headgear:
            display = '<' + Dialog.get('noaccessory') + '>'
            self.sub_window.add(Menu.make(display, lambda x: x, color=None))
        else:
            display = Global.player.character.headgear.get_display_name()
            headgear_lmb = self.get_prompt(Global.player.character.headgear.describe(), Dialog.get('Drop'),
                                           click_headgear)
            self.sub_window.add(Menu.make(display, headgear_lmb))
        if not Global.player.character.armor:
            display = '<' + Dialog.get('noarmor') + '>'
            self.sub_window.add(Menu.make(display, lambda x: x, color=None))
        else:
            display = Global.player.character.armor.get_display_name()
            armor_lmb = self.get_prompt(Global.player.character.armor.describe(), Dialog.get('Drop'), click_armor)
            self.sub_window.add(Menu.make(display, armor_lmb))
        if not Global.player.character.weapon:
            display = '<' + Dialog.get('noweapon') + '>'
            self.sub_window.add(Menu.make(display,
                                          lambda l: Global.player.character.action.set('grab'), color=None))
        else:
            display = Global.player.character.weapon.get_display_name()
            weapon_lmb = self.get_prompt(Global.player.character.weapon.describe(), Dialog.get('Drop'),
                                         lambda l: Global.player.character.drop())
            self.sub_window.add(Menu.make(display, weapon_lmb))
        self.window.add(Menu.make(Dialog.get('Money'), None, color=None))
        money = Menu.make('$' + str(Global.player.character.tags.get('money', 0)), None, color=None)
        self.sub_window.add(money)
        self.sub_window.display(1)

    def menu_inventory(self):
        def click(index):
            if Global.player.character.weapon:
                index -= 1
            Global.player.character.unsheathe(index)

        def sheathe(arg):
            dropped = Global.player.character.drop()
            Global.player.character.inventory.attempt_add(dropped)
        temp = self.window.margin.y
        self.window.margin.y = 2
        temp2 = self.sub_window.margin.y
        self.sub_window.margin.y = 2
        if Global.player.character.weapon:
            items = [Global.player.character.weapon] + Global.player.character.inventory.items
        else:
            items = Global.player.character.inventory.items
        text = 'Capacity: ' + str(len(items)) + ' / 12'
        capacity_label = Menu.make(text, None, None, height=20, color=None)
        capacity_label.margin.load(0, 0)
        capacity_label.document.set_style(0, 99, dict(font_size=12, bold='True'))
        self.window.add(capacity_label)
        capacity = Global.player.character.get_capacity()
        text = 'Weight: ' + str(Global.player.character.get_equipment_weight()) + ' / ' + str(capacity)
        capacity_label = Menu.make(text, None, None, height=20, color=None)
        capacity_label.margin.load(0, 0)
        capacity_label.document.set_style(0, 99, dict(font_size=12, bold='True'))
        self.sub_window.add(capacity_label)
        count = 0
        for i in items:
            size = min(self.window.height - 48, int(160 * (i.get_weight() / max(1, capacity))))
            button = Window(0, 0, width=260, height=size + 10, multi_line=True)
            button.document.set_style(0, 1, dict(font_size=max(10, min(24, size))))
            if i == Global.player.character.weapon:
                button.set_text(i.get_display_name() + ' [' + Dialog.get('Held') + ']')
                button.on_click = self.get_prompt(i.describe(), Dialog.get('Store'), sheathe, count)
            else:
                button.set_text(i.get_display_name())
                button.on_click = self.get_prompt(i.describe(), Dialog.get('Take'), click, count)
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

    def menu_effects(self):
        def update():
            for buff in buff_list:
                buff[1].set_text(buff[0].describe_duration())
        self.update = update
        buff_list = []
        for i in Global.player.character.states.buffs:
            dur = i.describe_duration()
            rmb = self.get_message(i.describe())
            first_col = Menu.make(i.get_display_name(), rmb, color=Window.fore_color_transparent)
            second_col = Menu.make(dur, None, color=Window.fore_color_transparent)
            buff_list.append([i, second_col])
            self.window.add(first_col)
            self.sub_window.add(second_col)
        self.sub_window.display(1)

    def menu_craft(self):
        def craft(arg):
            if Global.player.sleep(1):
                Crafting.craft(Global.player.character, arg[0], arg[1])
                Global.player.character.action.act('grab', 8)
        params = []
        for item in self.var:
            ingreds = Crafting.get_ingredients(item)
            if ingreds:
                if Crafting.is_craftable(Global.player.character, ingreds):
                    fn = self.get_prompt(Crafting.describe(item, ingreds), Dialog.get('Craft'), craft, [item, ingreds])
                else:
                    fn = self.get_message(Crafting.describe(item, ingreds) + '\n' + Dialog.get('reqnotmet'))
                params.append([item, fn])
        self.var = params
        self.direct(self.menu_many_choice)
