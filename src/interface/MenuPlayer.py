from src.game import Global
from src.game.Crafting import Crafting
from src.interface.Menu import Menu
from src.interface.Window import Window
from src.tools.Data import Data
from src.tools.Dialog import Dialog


class MenuPlayer(Menu):
    def menu_examine(self):
        if Global.player.control.target_mark.form.visible:
            self.history.pop()
            tile = Global.player.control.get_mark()
            if tile:
                if tile.things:
                    self.get_message(tile.things[0].describe())(0)
                else:
                    self.get_message(Dialog.describe_terrain(tile))(0)
            else:
                self.get_message(Dialog.get('Out of sight'))(0)
            Global.player.control.target_mark.form.show(False)
        else:
            self.get_message(Dialog.get('dsc_examine'))(0)

    def menu_main(self):
        def update():
            a_hp, a_mhp, hp, mhp = host.get_durability()
            rmb = self.get_message(Dialog.get('dsc_health', [hp, mhp, a_hp, a_mhp]))
            text = str(int(hp / mhp * 100)) + '% ' + Dialog.get('Health')
            hp_display.set_text(text)
            hp_display.on_click = rmb

            hunger = host.tags.get('hunger', 0) / 100
            datetime = Dialog.date(Global.player.days)
            hunger_level = Global.player.is_hungry()
            if hunger_level == 1:
                text = Dialog.get('Starving')
                rmb = self.get_message(Dialog.get('dsc_hunger', [datetime, hunger]))
            else:
                text = str(int(hunger)) + '% ' + Dialog.get('Hunger')
                rmb = self.get_message(Dialog.get('dsc_date', [datetime, hunger]))
            button_date.set_text(text)
            button_date.on_click = rmb
        host = Global.player.character
        self.update = update
        if host.tags.get('lvl', 0) % 100 == 99:
            text = Dialog.get('Level Up')
        else:
            text = Dialog.get('Character')
        self.window.add(Menu.make(text, lambda _: self.direct(self.menu_character)))
        from src.entity.unit.Humanoid import Humanoid
        if isinstance(host, Humanoid):
            if host.weapon or host.armor or host.headgear:
                self.window.add(Menu.make(Dialog.get('Equipment'), lambda _: self.direct(self.menu_equipment)))
            if host.get_equipment_weight() > 0:
                self.window.add(Menu.make(Dialog.get('Inventory'), lambda _: self.direct(self.menu_inventory)))
        if host.get_skills():
            self.window.add(Menu.make(Dialog.get('Skills'), lambda _: self.direct(self.menu_skill)))
        hp_display = Menu.make('', None, color=None)
        self.window.add(hp_display)
        button_date = Menu.make('', None, color=None)
        self.window.add(button_date)

    def menu_character(self):
        def stat(arg):
            host.tags.increment(arg, 1)
            host.tags.increment('lvl', 1)
            Global.main.monologue.set(Dialog.get('stat_applied', [level + 1]))
            from src.entity.Particle import Particle
            Particle.make('barrier', host.pos)
            host.location.sound.register(host.pos, 0, file='level', priority=1)
        host = Global.player.character
        rmb = self.get_message(Dialog.get('dsc_level'))
        tag_level = host.tags.get('lvl', 0)
        level = int(tag_level / 100)
        experience = tag_level % 100
        text = Dialog.get('Level') + ' ' + str(level) + ' (' + str(experience) + '%)'
        self.window.add(Menu.make(text, rmb, color=None))
        rmb = self.get_message(Global.player.describe_class())
        self.sub_window.add(Menu.make(host.tags.get('class', 'classless').title(), rmb, color=None))
        stats = Data.get_line('raw.txt', 'stat')[1]
        for i in stats:
            tag = host.tags.get(i[1])
            if tag is not None:
                if experience == 99:
                    rmb = self.get_prompt(Dialog.get('dsc_' + i[0]), Dialog.get('Increase Stat'), stat, param=i[1])
                    color = Window.fore_color2
                else:
                    rmb = self.get_message(Dialog.get('dsc_' + i[0]))
                    color = None
                self.window.add(Menu.make(str(tag) + ' ' + Dialog.get(i[0].title()), rmb, color=color))
        self.sub_window.display(1)

    def menu_skill(self):
        index = 0
        for skill in Global.player.character.get_skills():
            name = 'sk.' + skill
            title = skill.title()
            desc = Data.get_line('descriptions.txt', name)
            if desc:
                text = desc[1]
            else:
                text = Dialog.get('!dsc_skill')
            if skill not in Global.player.character.skills:
                text += '\n' + Dialog.get('item_skill')
            button = Menu.make(title, self.get_message(text))
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
            display = '<' + Dialog.get('No Headgear') + '>'
            self.sub_window.add(Menu.make(display, lambda x: x, color=None))
        else:
            display = Global.player.character.headgear.get_display_name()
            headgear_lmb = self.get_prompt(Global.player.character.headgear.describe(), Dialog.get('Drop'),
                                           click_headgear)
            self.sub_window.add(Menu.make(display, headgear_lmb))
        if not Global.player.character.armor:
            display = '<' + Dialog.get('No Armor') + '>'
            self.sub_window.add(Menu.make(display, lambda x: x, color=None))
        else:
            display = Global.player.character.armor.get_display_name()
            armor_lmb = self.get_prompt(Global.player.character.armor.describe(), Dialog.get('Drop'), click_armor)
            self.sub_window.add(Menu.make(display, armor_lmb))
        if not Global.player.character.weapon:
            display = '<' + Dialog.get('No Weapon') + '>'
            self.sub_window.add(Menu.make(display,
                                          lambda _: Global.player.character.action.set('grab'), color=None))
        else:
            display = Global.player.character.weapon.get_display_name()
            weapon_lmb = self.get_prompt(Global.player.character.weapon.describe(), Dialog.get('Drop'),
                                         lambda _: Global.player.character.drop())
            self.sub_window.add(Menu.make(display, weapon_lmb))
        self.window.add(Menu.make(Dialog.get('Money'), None, color=None))
        rmb = self.get_message(Dialog.get('dsc_money'))
        money = Menu.make('$' + str(Global.player.character.tags.get('money', 0)), rmb, color=None)
        self.sub_window.add(money)
        self.sub_window.display(1)

    def menu_inventory(self):
        def click(index):
            if host.weapon:
                index -= 1
            host.unsheathe(index)

        def drop(index):
            host.location.sound.register(host.pos, 0, file='wear')
            host.inventory.take_item(index)

        def sheathe(arg):
            dropped = host.drop()
            host.inventory.attempt_add(dropped)
        host = Global.player.character
        temp = self.window.margin.y
        self.window.margin.y = 2
        temp2 = self.sub_window.margin.y
        self.sub_window.margin.y = 2
        if Global.player.character.weapon:
            items = [Global.player.character.weapon] + Global.player.character.inventory.items
        else:
            items = Global.player.character.inventory.items
        capacity = Global.player.character.tags.get('str', 1)
        text = 'Weight: ' + str(Global.player.character.get_equipment_weight()) + ' / ' + str(capacity)
        capacity_label = Menu.make(text, None, None, height=20, color=None)
        capacity_label.margin.load(0, 0)
        capacity_label.document.set_style(0, 99, dict(font_size=12, bold='True'))
        self.window.add(capacity_label)
        self.sub_window.add(Menu.make('', None, None, height=20, color=None))
        count = 0
        for i in items:
            size = min(self.window.height - 48, int(140 * (i.get_weight() / max(1, capacity))))
            button = Window(0, 0, width=260, height=size + 4, multi_line=True)
            button.document.set_style(0, 1, dict(font_size=max(10, min(24, size))))
            if i == Global.player.character.weapon:
                button.set_text(i.get_display_name() + ' [' + Dialog.get('Held') + ']')
                button.on_click = self.get_prompt(i.describe(), Dialog.get('Store'), sheathe, count)
            else:
                button.set_text(i.get_display_name())
                button.on_click = self.get_prompt2(i.describe(), Dialog.get('Take'),
                                                   Dialog.get('Drop'), click, drop, count, count)
            button.width = button.text.content_width + 16
            button.height = button.text.content_height + 2
            button.margin.load(8, 0)
            label = Window(0, 0, width=0, height=size + 10, multi_line=False)
            label.document.set_style(0, 1, dict(font_size=max(10, min(24, size))))
            label.set_text(Dialog.weight(i.get_weight()))
            label.height = button.text.content_height + 2
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
            if 'hide' not in i.get_tags():
                dur = i.describe_duration()
                rmb = self.get_message(i.describe())
                first_col = Menu.make(i.get_display_name(), rmb, color=Window.fore_color_transparent)
                second_col = Menu.make(dur, None, color=Window.fore_color_transparent)
                buff_list.append([i, second_col])
                self.window.add(first_col)
                self.sub_window.add(second_col)
        if not buff_list:
            self.get_message(Dialog.get('no_status'))()
            self.history.pop()
        else:
            self.sub_window.display(1)

    def menu_craft(self):
        def craft(arg):
            if Global.player.sleep(1):
                Crafting.craft(Global.player.character, arg[0], arg[1])
                Global.player.character.action.act('grab', 8)
        self.window.add(Menu.make(Dialog.get('craftables'), None, color=None))
        self.sub_window.add(Menu.make('', None, color=None))
        for k, item in enumerate(self.var):
            ingreds = Crafting.get_ingredients(item)
            if ingreds:
                if Crafting.is_craftable(Global.player.character, ingreds):
                    fn = self.get_prompt(Crafting.describe(item, ingreds), Dialog.get('Craft'), craft, [item, ingreds])
                else:
                    fn = self.get_message(Crafting.describe(item, ingreds) + '\n' + Dialog.get('reqnotmet'))
                if k < 5:
                    self.window.add(Menu.make(item, fn))
                else:
                    self.sub_window.add(Menu.make(item, fn))
        self.sub_window.display(1)

    def menu_pickup(self):
        def pickup(arg):
            Global.player.character.pick_up(arg)
        params = []
        for item in self.var[:12]:
            fn = self.get_prompt(item.describe(), Dialog.get('Take'), pickup, item)
            params.append([item.name, fn])
        self.var = params
        self.direct(self.menu_many_choice)
