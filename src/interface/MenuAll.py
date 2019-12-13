from src.entity.Particle import Particle
from src.game import Global
from src.game.Crafting import Crafting
from src.interface.Menu import Menu
from src.interface.MenuPlayer import MenuPlayer
from src.interface.Window import Window
from src.tools.Data import Data
from src.tools.Dialog import Dialog


# noinspection PyUnresolvedReferences
class MenuAll(MenuPlayer):
    def topic(self, name):
        if Data.get_line('raw/choices.txt', name):
            self.var = [self.var[0], name]
            self.direct(self.menu_conversation)
        else:
            if name.startswith('#'):
                self.direct(getattr(self, 'menu_' + name[1:].lower()))
            else:
                dialog = Data.get_line('raw/conversation.txt', name)
                if dialog:
                    self.show_dialog([','.join(dialog[1])])

    def menu_conversation(self):
        if self.var[0]:
            self.window.add(Menu.make('[' + self.var[0].name + ']', None, None, color=None, hover=False))
        options = Data.get_line('raw/choices.txt', self.var[1])
        self.window.add(Menu.make(options[1][0], None, None, color=None, hover=False, resize=True))
        for option in options[1][1:]:
            self.sub_window.add(Menu.make(option.replace('#', ''), self.topic, None, width=160, name=option))
        self.sub_window.display(1)

    def menu_talk(self):
        if 'talk' in self.var[0].var:
            talk_type = self.var[0].var['talk']
        else:
            talk_type = 'none'
        self.history.pop()
        self.history_var.pop()
        dialogs = Data.get_line('raw/conversation.txt', talk_type)[1:]
        output = Menu.get_conversation(dialogs)
        self.show_dialog([output[self.var[0].attributes.gene % len(output)]])

    def menu_move(self):
        from src.tools import Direction
        pos = Global.player.character.pos
        Global.player.character.relocate(self.var[0].pos.x, self.var[0].pos.y)
        self.var[0].relocate(pos.x, pos.y)
        self.display(-1)

    def menu_hire(self):
        cost = self.var[0].attributes.get_total() + self.var[0].armor.get_value() + self.var[0].headgear.get_value()
        cost += self.var[0].weapon.get_value() - 3
        text = 'Hire this person for $' + str(cost) + '?'
        panel = Menu.make(text, None, None, color=Window.fore_color_transparent, hover=False, width=320)
        panel.normal_font_color = Window.font_color1
        panel.hover_font_color = Window.font_color3
        panel.redraw()
        self.window.add(panel)

        def hire(name):
            if Global.player.character.require_var('money', cost):
                from src.entity.unit.ai.Task import Follow
                self.var[0].pilot.var['ally'] = Global.player.character.id
                self.var[0].pilot.var['def'] = Follow(self.var[0].pilot)
            self.toggle()
        self.window.next_y = self.window.size.y + self.window.vec.y - 40 - self.window.margin.y
        self.window.add(Menu.make('Hire', hire, None, width=320))
        self.sub_window.display(1)

    def menu_rent(self):
        def buy(arg):
            if charvar.var['own'] == 1 or Global.player.days >= charvar.var['due']:
                if Global.player.character.require_var('money', cost):
                    charvar.var['due'] = Global.player.days + 14
                    charvar.var['own'] = 2
                    charvar.say(Dialog.get('thanks'))
                    self.toggle()
            else:
                from src.map.Location import Location
                Location.make('static/storage', 'storage', overwrite=False)
                from src.entity.Space import Space
                Global.player.travel('storage', Space())
        charvar = self.var[0]
        cost = charvar.var['rent']
        if charvar.var['own'] == 1 or Global.player.days >= charvar.var['due']:
            self.var = [Dialog.get('?rent', [cost]), [Dialog.get('Yes')], [buy]]
        else:
            left = Dialog.day(charvar.var['due'] - Global.player.days)
            self.var = [Dialog.get('?rententer', [left]), [Dialog.get('Enter')], [buy]]
        self.state = self.menu_choice
        self.display(1)

    def menu_rest(self):
        def stay(arg):
            if Global.player.character.require_var('money', cost):
                Global.player.sleep(2)
                self.toggle()
        cost = self.var[0].var['stay']
        self.var = [Dialog.get('?inn', [cost]), [Dialog.get('Yes')], [stay]]
        self.state = self.menu_choice
        self.display(1)

    def menu_loan(self):
        def buy(arg):
            if Global.player.character.var['debt'] <= 0:
                Global.player.character.var['money'] += 50
                Global.player.character.var['debt'] += 60
                self.var[0].say(Dialog.get('thanks'))
                self.toggle()
        cost = self.var[0].var['loan']
        if cost < 0:
            cost = self.var[0].attributes.gene % 15 + 10
        text = Dialog.get('innstay', [cost])
        option = Dialog.get('getroom')
        self.var = [text, [Dialog.get('?inn', [cost2]), option], [stay, buy]]
        self.state = self.menu_choice
        self.display(1)

    def menu_invest(self):
        def buy(arg):
            if self.var[0].var['own'] == 1 or Global.player.days >= self.var[0].var['due']:
                if Global.player.character.require_var('money', cost):
                    self.var[0].var['due'] = Global.player.days + 14
                    self.var[0].var['own'] = 2
                    Global.player.character.say('Bought a place!')
                    self.toggle()
        cost = self.var[0].var['loan']
        text = Dialog.get('innstay', [cost])
        option = Dialog.get('getroom')
        self.var = [text, [Dialog.get('?inn', [cost2]), option], [stay, buy]]
        self.state = self.menu_choice
        self.display(1)

    def menu_pawn(self):
        selling = Global.player.character.weapon
        price = int(selling.get_value() * .7 - (self.var[0].attributes.gene % 3) - 1)
        if Global.player.character.is_armed() and price > 0:
            def sell(arg):
                selling.loot = []
                selling.die()
                Global.player.character.var['money'] += price
                self.var[0].say(Dialog.get('thanks'))
                self.toggle()
            text = Dialog.get('?sell', [selling.get_display_name(), str(price)])
            self.var = [text, [Dialog.get('Yes')], [sell]]
            self.state = self.menu_choice
            self.display(1)
        else:
            self.dialog_text = ['You are not holding anything that you can sell here.']
            self.state = self.menu_dialog
            self.display(1)

    def menu_shop(self):
        def buy(item):
            if Global.player.character.require_var('money', item.get_value() + int(self.var[1])):
                self.var[2].remove(item)
                self.var[0].var['item'] = '&'.join([x.name for x in self.var[2]])
                item.relocate(Global.player.character.pos.x, Global.player.character.pos.y, force=1)
                item.add()
                tgt.say(Dialog.get('thanks'))
            self.toggle()
        if Global.player.days >= self.var[0].var['due']:
            from src.tools.Random import Random
            from src.tools.Data import Data
            rng = Random(self.var[0].attributes.gene + Global.player.days)
            due_date = Global.player.days + (self.var[0].attributes.gene % 14) + 6
            data = Data.get_line('raw/trade.txt', self.var[0].var['trade'])
            merchandise = []
            for i in range(rng.rand_int(3, 6)):
                merchandise.append(rng.rand_list(data[1]))
            self.var[0].var['item'] = '&'.join(merchandise)
            self.var[0].var['due'] = due_date
        if not self.var[0].var['item']:
            self.show_dialog([Dialog.get('soldout')])
        else:
            from src.entity.Stock import Stock
            for i in self.var[0].var['item'].split('&'):
                item = Stock.get(i)
                if item:
                    money = '$' + str(item.get_value() + int(self.var[0].attributes.gene % 2))
                    rmb = self.get_message(item.describe().split('\n'))
                    self.window.add(Menu.make(item.name, buy, rmb, name=i))
                    self.sub_window.add(Menu.make(money, None, None, color=None, hover=False))
            self.sub_window.display(1)

    def menu_exchange(self):
        def buy(item):
            if Global.player.character.require_var('money', item[1].get_value() + 2):
                if item[0] == 'w':
                    self.var[0].drop()
                elif item[0] == 'a':
                    self.var[0].unarmor()
                elif item[0] == 'h':
                    self.var[0].unheadgear()
                elif item[0] == 'i':
                    self.var[0].armor.get_item(0).on_unequip()
                item[1].relocate(Global.player.character.pos.x, Global.player.character.pos.y, force=1)
                self.var[0].say(Dialog.get('exchanged'))
            self.toggle()
        items = []
        if self.var[0].is_armed():
            items.append(['w', self.var[0].weapon])
        if self.var[0].is_armored():
            items.append(['a', self.var[0].armor])
        if self.var[0].is_headgeared():
            items.append(['h', self.var[0].headgear])
        if self.var[0].armor.items:
            items.append(['i', self.var[0].armor.items[0]])
        for i in items:
            money = '$' + str(i[1].get_value() + 2)
            rmb = self.get_message(i[1].describe().split('\n'))
            self.window.add(Menu.make(i[1].name, buy, rmb, name=i))
            self.sub_window.add(Menu.make(money, None, rmb, color=Window.fore_color_transparent, hover=False))
        self.sub_window.display(1)

    def menu_train(self):
        def click(button_arg):
            if Global.player.eat():
                Global.player.sleep(1)
                if button_arg[1] == 'exp1':
                    Global.player.character.attributes.strength += 1
                elif button_arg[1] == 'exp2':
                    Global.player.character.attributes.agility += 1
                elif button_arg[1] == 'exp3':
                    Global.player.character.attributes.intelligence += 1
                Global.player.character.say(Dialog.get('Level Up!'))
            self.toggle()
        text = Dialog.get('tuition cost', [self.var[0].var['value']])
        panel = Menu.make(text, None, None, color=Window.fore_color_transparent, width=320, hover=False, resize=True)
        panel.normal_font_color = Window.font_color1
        panel.hover_font_color = Window.font_color3
        panel.redraw()
        self.window.add(panel)
        self.window.next_y = self.window.size.y + self.window.vec.y
        cost = Global.player.character.attributes.get_total()
        rmb = self.get_message([Dialog.get('trainint', [cost])])
        self.window.add(Menu.make(Dialog.get('Intelligence'), click, rmb, width=320, name=[cost, 'exp3']), reverse=True, index=0)
        rmb = self.get_message([Dialog.get('trainagi', [cost])])
        self.window.add(Menu.make(Dialog.get('Agility'), click, rmb, width=320, name=[cost, 'exp2']), reverse=True, index=0)
        rmb = self.get_message([Dialog.get('trainstr', [cost])])
        self.window.add(Menu.make(Dialog.get('Strength'), click, rmb, width=320, name=[cost, 'exp1']), reverse=True, index=0)
        self.sub_window.display(1)

    def menu_provide(self):
        if Global.player.days >= self.var[0].var['due']:
            from src.tools.Data import Data
            from src.tools.Random import Random
            from src.entity.Stock import Stock
            data = Data.get_line('raw/trade.txt', self.var[0].var['type'])
            rng = Random(self.var[0].attributes.gene + Global.player.days)
            due_date = Global.player.days + rng.rand_int(2, 5)
            item = rng.rand_list(data[1])
            value = Stock.get(item).get_value()
            self.var[0].var['due'] = due_date
            self.var[0].var['item'] = item
            self.var[0].var['amount'] = rng.rand_int(1, 7)
            self.var[0].var['value'] = rng.rand_int(1, 8) + int(value * self.var[0].var['amount'] * .7)
        self.state = self.menu_guild
        self.display(1)

    def menu_supply(self):
        if Global.player.days >= self.var[0].var['due']:
            from src.entity.Stock import Stock
            self.var[0].var['due'] = Global.player.days + self.var[0].var['time']
            self.var[0].var['amount'] = self.var[0].var['need']
        self.state = self.menu_guild
        self.display(1)

    def menu_guild(self):
        if self.var[0].var['amount'] <= 0:
            dur = Dialog.day(self.var[0].var['due'] - Global.player.days)
            self.show_dialog([Dialog.get('dealeroff', [dur])])
            return
        else:
            dur = Dialog.day(self.var[0].var['due'] - Global.player.days)
            reward = self.var[0].var['value']
            text = Dialog.get('dealerdeal', [self.var[0].var['amount'], self.var[0].var['item'], dur, reward])
            panel = Menu.make(text, None, None, color=None, hover=False, width=320, resize=True)
            panel.redraw()
            self.window.add(panel)

            def sell(name):
                items = Global.player.character.get_accessibles()
                count = 0
                for item in items:
                    if item.name == self.var[0].var['item']:
                        item.loot = None
                        item.die()
                        count += 1
                self.var[0].var['amount'] -= count
                if self.var[0].var['amount'] <= 0:
                    Global.player.character.say(Dialog.get('dealcomplete'))
                    Global.player.character.var['money'] += reward
                elif count > 0:
                    Global.player.character.say(Dialog.get('dealdelivery', [count, self.var[0].var['item']]))
                else:
                    Global.player.character.say('No ' + self.var[0].var['item'] + '...')
            rmb = self.get_message([Dialog.get('provideitem', [self.var[0].var['item']])])
            self.window.next_y = self.window.size.y + self.window.vec.y - 40 - self.window.margin.y
            self.window.add(Menu.make(Dialog.get('provideitem', [self.var[0].var['item']]), sell, rmb, width=320))
            self.sub_window.display(1)

    def menu_quest(self):
        def proceed(arg):
            Global.player.character.say('FAR')
        import math
        mission = int(math.sin(Global.player.days + self.var[0].attributes.gene) * 10) % 3 + 1
        reward = 40
        self.var = [Dialog.get('sergentquest' + str(mission), [reward]),
                    [Dialog.get('Accept and Proceed')], [proceed]]
        self.state = self.menu_choice
        self.display(1)

    def menu_diagnose(self):
        def treat(arg):
            if Global.player.character.require_var('money', self.var[0].var['value']):
                from src.entity.unit.Buff import BuffTags
                Global.player.character.states.clear(lambda x: BuffTags.harmful in x.tags)
                self.toggle()
                Global.player.character.say(Dialog.get('treated'))
        self.var = [Dialog.get('treated', [self.var[0].var['value']]), [Dialog.get('Cure')], [treat]]
        self.state = self.menu_choice
        self.display(1)

    def menu_examine(self):
        def exam(arg):
            self.direct(self.menu_effects)
        self.var = [Dialog.get('diagnose'), [Dialog.get('Yes')], [exam]]
        self.state = self.menu_choice
        self.display(1)

    def menu_insurance(self):
        contract = Global.player.character.states.get('Revive')
        if not contract:
            def package(arg):
                if Global.player.character.require_var('money', value):
                    Global.player.character.states.add('Revive', -1, 'Insurance')
                    Global.player.character.say(Dialog.get('insurebought'))
                    tgt.var['record'] += 1
                    tgt.say(Dialog.get('thanks'))
                    self.toggle()
            text = []
            tgt = self.var[0]
            value = int(self.var[0].attributes.gene % 9 + 4) + (tgt.var['record'] * tgt.var['inc'])
            text.append(Dialog.get('dsc_insurance', [str(value)]))
            panel = Menu.make(text, None, None, color=Window.fore_color_transparent,
                              hover=False, width=320, resize=True)
            self.window.add(panel)
            self.window.next_y = self.window.size.y + self.window.vec.y - 40 - self.window.margin.y
            self.window.add(Menu.make(Dialog.get('insureyes', [str(value)]), package, None, width=320))
            self.sub_window.display(1)
            return
        else:
            self.show_dialog([Dialog.get('insurefull')])

    def menu_craft(self):
        def add_button(window, item, ingreds, callback):
            def craft(arg):
                if callback:
                    callback(arg)
                else:
                    Crafting.craft(self.host, item, ingreds)
                self.host.action.set('wait')
                self.toggle()
            if Crafting.is_craftable(self.host, ingreds):
                rmb = self.get_message(Crafting.describe(item, ingreds).split('\n'))
                button = Menu.make(item, craft, rmb, name=item)
            else:
                rmb = self.get_message((Crafting.describe(item, ingreds) + '\n' + Dialog.get('reqnotmet')).split('\n'))
                button = Menu.make(item, rmb, rmb, name=item, color=Window.fore_color_disabled)
            window.add(button)
        self.history = [self.menu_craft]
        self.history_var = [self.var]
        if self.var:
            for i in self.var[:6]:
                add_button(self.window, i[0], i[1], i[2])
            for i in self.var[6:]:
                add_button(self.sub_window, i[0], i[1], i[2])
            self.window.display(1)
            self.sub_window.display(1)
        else:
            self.show_dialog([Dialog.get('nocraftables')])

    def menu_anvil(self):
        self.history = [self.menu_anvil]
        self.history_var = [self.var]
        from src.entity.unit.item.Weapon import Weapon
        if self.host.is_armed() and isinstance(self.host.weapon, Weapon):
            text = Dialog.get('modifyitem', [self.host.weapon.get_display_name()])
            desc = self.get_message([Dialog.get('dsc_modifyweapon')])
            self.window.add(Menu.make(text, lambda l: self.direct(self.menu_mod_weapon), desc, width=320))
        if self.host.is_armored():
            text = Dialog.get('modifyitem', [self.host.armor.get_display_name()])
            desc = self.get_message([Dialog.get('dsc_modifyarmor')])
            self.window.add(Menu.make(text, lambda l: self.direct(self.menu_mod_armor), desc, width=320))
        self.sub_window.display(1)

    def menu_mod_weapon(self):
        def reinforce(arg):
            if self.host.weapon.enhance(Global.r.rand_int(1, 100)):
                self.host.weapon.max_durability *= 2
                if self.host.weapon.max_durability >= 128:
                    self.host.weapon.durability = -1
                    self.host.weapon.max_durability = -1
            else:
                Particle.make('disintegrate', self.host.vec)
                self.host.weapon.die()
            arg.die()
            self.toggle()

        def grip(arg):
            if self.host.weapon.enhance(Global.r.rand_int(1, 100)):
                self.host.weapon.speed -= 1
            else:
                Particle.make('disintegrate', self.host.vec)
                self.host.weapon.die()
            arg.die()
            self.toggle()

        def blade(arg):
            if self.host.weapon.enhance(Global.r.rand_int(1, 100)):
                self.host.weapon.damage += Global.r.rand_int(1, 3)
            else:
                Particle.make('disintegrate', self.host.vec)
                self.host.weapon.die()
            arg.die()
            self.toggle()

        def body(arg):
            if self.host.weapon.enhance(Global.r.rand_int(1, 100)):
                self.host.weapon.weight -= 1
            else:
                Particle.make('disintegrate', self.host.vec)
                self.host.weapon.die()
            arg.die()
            self.toggle()

        def fortify(arg):
            if self.host.weapon.enhance(Global.r.rand_int(1, 100)):
                self.host.weapon.weight += 1
            else:
                Particle.make('disintegrate', self.host.vec)
                self.host.weapon.die()
            arg.die()
            self.toggle()

        text = Dialog.get('modchance', [self.host.weapon.get_enhance_chance()])
        self.window.add(Menu.make(text, None, None, width=320, resize=True, color=Window.fore_color_transparent))
        items = self.host.get_accessibles()
        flag = ['Scrap', 'Rubber', 'Tooth', 'Plating', 'Plating']
        deny = self.get_message([Dialog.get('nomaterial')])
        for i in items:
            if i.name == flag[0]:
                flag[0] = i
            if i.name == flag[1]:
                flag[1] = i
            if i.name == flag[2]:
                flag[2] = i
            if i.name == flag[3]:
                flag[3] = i
            if i.name == flag[4]:
                flag[4] = i
        desc = self.get_message([Dialog.get('dsc_reinforcewith', [Dialog.get('Scrap')])])
        if isinstance(flag[0], str):
            self.window.add(Menu.make(Dialog.get('reinforcewith', [Dialog.get('Scrap')]),
                                      deny, desc, width=320, name=flag[0], color=Window.fore_color_disabled))
        else:
            self.window.add(Menu.make(Dialog.get('reinforcewith', [Dialog.get('Scrap')]),
                                      reinforce, desc, width=320, name=flag[0]))
        if self.host.weapon.speed > 1:
            if isinstance(flag[1], str):
                self.window.add(Menu.make(Dialog.get('improvegripwith', [Dialog.get('Rubber')]), deny, deny,
                                          width=320, name=flag[0], color=Window.fore_color_disabled))
            else:
                desc = self.get_message([Dialog.get('dsc_improvewith', [Dialog.get('Rubber')])])
                self.window.add(Menu.make(Dialog.get('improvegripwith', [Dialog.get('Rubber')]),
                                          grip, desc, width=320, name=flag[1]))
        if self.host.weapon.speed > 1:
            desc = self.get_message([Dialog.get('dsc_modifybladewith', [Dialog.get('Tooth')])])
            if isinstance(flag[2], str):
                self.window.add(Menu.make(Dialog.get('modifybladewith', [Dialog.get('Tooth')]),
                                          deny, desc, width=320, name=flag[0], color=Window.fore_color_disabled))
            else:
                self.window.add(Menu.make(Dialog.get('modifybladewith', [Dialog.get('Tooth')]),
                                          blade, desc, width=320, name=flag[2]))
        if self.host.weapon.weight > 1:
            desc = self.get_message([])
            if isinstance(flag[3], str):
                self.window.add(Menu.make(Dialog.get('dsc_modifybodywith', [Dialog.get('Plating')]),
                                          deny, desc, width=320, name=flag[0], color=Window.fore_color_disabled))
            else:
                self.window.add(Menu.make(Dialog.get('dsc_modifybodywith', [Dialog.get('Plating')]),
                                          body, desc, width=320, name=flag[3]))
        desc = self.get_message([Dialog.get('dsc_fortifybodywith', [Dialog.get('Plating')])])
        if isinstance(flag[4], str):
            self.window.add(Menu.make(Dialog.get('fortifybodywith', [Dialog.get('Plating')]),
                                      deny, desc, width=320, name=flag[0], color=Window.fore_color_disabled))
        else:
            self.window.add(Menu.make(Dialog.get('fortifybodywith', [Dialog.get('Plating')]),
                                      fortify, desc, width=320, name=flag[3]))
        self.sub_window.display(1)

    def menu_mod_armor(self):
        def reinforce(arg):
            if self.host.armor.enhance(Global.r.rand_int(1, 100)):
                self.host.armor.max_durability += 1
            else:
                Particle.make('disintegrate', self.host.vec)
                self.host.armor.die()
            arg.die()
            self.toggle()

        def pad(arg):
            if self.host.armor.enhance(Global.r.rand_int(1, 100)):
                self.host.armor.armor += 1
            else:
                Particle.make('disintegrate', self.host.vec)
                self.host.armor.die()
            arg.die()
            self.toggle()

        def refit(arg):
            if self.host.armor.enhance(Global.r.rand_int(1, 100)):
                self.host.armor.weight -= 1
            else:
                Particle.make('disintegrate', self.host.vec)
                self.host.armor.die()
            arg.die()
            self.toggle()

        text = Dialog.get('modchance', [self.host.armor.get_enhance_chance()])
        self.window.add(Menu.make([text], None, None, width=320, resize=True, color=Window.fore_color_transparent))
        items = self.host.get_accessibles()
        flag = ['Cloth', 'Plating', 'Tooth']
        deny = self.get_message(['No materials...'])
        for i in items:
            if i.name == flag[0]:
                flag[0] = i
            if i.name == flag[1]:
                flag[1] = i
            if i.name == flag[2]:
                flag[2] = i
        desc = self.get_message([Dialog.get('dsc_reinforcearmorwith', [Dialog.get('Cloth')])])
        if isinstance(flag[0], str):
            self.window.add(Menu.make(Dialog.get('reinforcewith', [Dialog.get('Cloth')]),
                                      deny, desc, width=320, name=flag[0], color=Window.fore_color_disabled))
        else:
            self.window.add(Menu.make(Dialog.get('reinforcewith', [Dialog.get('Cloth')]),
                                      reinforce, desc, width=320, name=flag[0]))
        desc = self.get_message([Dialog.get('dsc_padwith', [Dialog.get('Cloth')])])
        if isinstance(flag[1], str):
            self.window.add(Menu.make(Dialog.get('padwith', [Dialog.get('Plating')]),
                                      deny, desc, width=320, name=flag[0], color=Window.fore_color_disabled))
        else:
            self.window.add(Menu.make(Dialog.get('padwith', [Dialog.get('Plating')]),
                                      pad, desc, width=320, name=flag[1]))
        desc = self.get_message([Dialog.get('dsc_refitwith', [Dialog.get('Tooth')])])
        if isinstance(flag[2], str):
            self.window.add(Menu.make(Dialog.get('refitwith', [Dialog.get('Tooth')]),
                                      deny, desc, width=320, name=flag[0], color=Window.fore_color_disabled))
        else:
            self.window.add(Menu.make(Dialog.get('refitwith', [Dialog.get('Tooth')]),
                                      refit, desc, width=320, name=flag[2]))
        self.sub_window.display(1)

    def menu_skip(self):
        if self.visible == 1:
            self.toggle()
        from src.entity.Space import Space
        Global.player.travel('start', Space())
