from src.game import Global
from src.game.Crafting import Crafting
from src.interface.Menu import Menu
from src.interface.MenuPlayer import MenuPlayer
from src.interface.Window import Window
from src.tools.Dialog import Dialog


class MenuAll(MenuPlayer):
    def menu_choice(self):
        if self.var[0]:
            text = [self.var[0]]
            self.window.add(Menu.make(text, None, None, color=Window.fore_color_transparent,
                                      hover=False, width=320, resize=True))
            self.window.next_y = self.window.size.y + self.window.vec.y
            for i in range(len(self.var[1])):
                button = Menu.make([self.var[1][i]], self.var[2][i], None, name=i, width=320)
                self.window.add(button, reverse=True, index=0)
        else:
            for i in range(len(self.var[1])):
                button = Menu.make([self.var[1][i]], self.var[2][i], None, name=i, width=320)
                self.window.add(button)
        self.sub_window.display(1)

    def menu_many_choice(self):
        for k, v in enumerate(self.var):
            button = Menu.make([self.var[k][0]], self.var[k][1], self.var[k][1], name=self.var[k][0])
            if k < 6:
                self.window.add(button)
            else:
                self.sub_window.add(button)
        self.sub_window.display(1)

    def menu_story(self):
        def branch(name):
            if Data.get_line('data/raw/choices.txt', name):
                self.var = [self.var[0], name]
                self.direct(self.menu_story)
            else:
                dialog = Data.get_line('data/raw/conversation.txt', name)
                if dialog:
                    self.show_dialog([','.join(dialog[1])])
        from src.tools.Data import Data
        options = Data.get_line('data/raw/choices.txt', self.var[1])
        length = len(options[1])
        if length <= 6:
            width = 320
        else:
            width = 160
        for option in options[1][:6]:
            self.window.add(Menu.make([option], branch, None, width=width, name=option))
        for option in options[1][6:]:
            self.sub_window.add(Menu.make([option], branch, None, width=width, name=option))
        self.sub_window.display(1)

    def menu_conversation(self):
        def conversation(name):
            from src.tools.Data import Data
            if 'talk' in self.var[0].var:
                talk_type = self.var[0].var['talk']
            else:
                talk_type = 'none'
            dialogs = Data.get_line('data/raw/conversation.txt', talk_type)[1:]
            output = Menu.get_conversation(dialogs)
            Global.menu.show_dialog([output[self.var[0].attributes.gene % len(output)]])

        def tutorial(name):
            self.var = [self.var[0], 'Start']
            self.direct(self.menu_story)
        self.history = [self.menu_conversation]
        self.history_var = [self.var]
        self.window.add(Menu.make(['[' + self.var[0].name + ']'], None, None, color=Window.fore_color_transparent,
                                  hover=False))
        if 'greet' in self.var[0].var:
            greet = self.var[0].var['greet']
        else:
            greet = 'greet'
        from src.tools.Data import Data
        dialogs = Data.get_line('data/raw/conversation.txt', greet)[1:]
        output = Menu.get_conversation(dialogs)
        self.window.add(Menu.make([output[self.var[0].attributes.gene % len(output)]], None, None, color=None,
                                  hover=False, resize=True))
        from src.entity.unit.Humanoid import Humanoid
        if isinstance(self.var[0], Humanoid):
            from src.entity.unit.Character import Character
            if isinstance(self.var[0], Character) and 'business' in self.var[0].var:
                def talk(name):
                    from src.game.Interaction import Interaction
                    Interaction.talk(self.var[0])
                rmb = self.get_message(['Bring up special dialogue options for this NPC'])
                self.sub_window.add(Menu.make([self.var[0].var['business']], talk, rmb))
            if self.var[0].is_armed() or self.var[0].is_headgeared() or self.var[0].armor.items:
                rmb = self.get_message(['Exchange for an equipment'])
                self.sub_window.add(Menu.make(['Exchange'], lambda l: self.direct(self.menu_exchange), rmb))
        rmb = self.get_message(['Make a conversation'])
        self.sub_window.add(Menu.make(['Talk'], conversation, rmb))
        rmb = self.get_message(['Ask for hints and tips'])
        self.sub_window.add(Menu.make(['Ask'], tutorial, rmb))
        rmb = self.get_message(['Ask this unit to accompany you'])
        self.sub_window.add(Menu.make(['Hire'], lambda l: self.direct(self.menu_hire), rmb))
        self.sub_window.display(1)

    def menu_travel(self):
        self.history = [self.menu_travel]
        self.history_var = [self.var]
        destination = self.var[0].title()
        option = 'Travel'
        text = ['Travel to [' + destination + '] ?']
        panel = Menu.make(text, None, None, color=Window.fore_color_transparent, hover=False, width=320)
        panel.normal_font_color = Window.font_color1
        panel.hover_font_color = Window.font_color3
        panel.redraw()
        self.window.add(panel)
        from src.entity.Space import Space

        def travel(name):
            if Global.player.drink():
                Global.player.sleep(1)
                Global.player.travel(self.var[0], Space(int(self.var[1]), int(self.var[2])))
            else:
                self.toggle()
        rmb = self.get_message(['Travel to ' + destination])
        self.window.next_y = self.window.size.y + self.window.vec.y - 40 - self.window.margin.y
        self.window.add(Menu.make([option], travel, rmb, width=320))
        self.sub_window.display(1)

    def menu_shop(self):
        def buy(item):
            if Global.player.character.require_var('money', item.get_value() + int(self.var[1])):
                self.var[2].remove(item)
                self.var[0].var['item'] = '&'.join([x.name for x in self.var[2]])
                item.relocate(Global.player.character.pos.x, Global.player.character.pos.y, force=1)
                item.add()
            else:
                self.toggle()
        if not self.var[0].var['item']:
            self.show_dialog(['I am all out of merchandise. Thank you for your patronage!'])
        else:
            for i in self.var[2]:
                money = '$' + str(i.get_value() + int(self.var[1]))
                rmb = self.get_message(i.describe().split('\n'))
                self.window.add(Menu.make([i.name], buy, rmb, name=i))
                self.sub_window.add(Menu.make([money], None, rmb, color=Window.fore_color_transparent, hover=False))
            self.sub_window.display(1)

    def menu_exchange(self):
        def buy(item):
            if Global.player.character.require_var('money', item[1].get_value()):
                if item[0] == 'w':
                    self.var[0].drop()
                elif item[0] == 'h':
                    self.var[0].unheadgear()
                elif item[0] == 'i':
                    self.var[0].armor.get_item(0).on_unequip()
                item[1].relocate(Global.player.character.pos.x, Global.player.character.pos.y, force=1)
            else:
                self.toggle()
        items = []
        if self.var[0].is_armed():
            items.append(['w', self.var[0].weapon])
        if self.var[0].is_headgeared():
            items.append(['h', self.var[0].headgear])
        if self.var[0].armor.items:
            items.append(['i', self.var[0].armor.items[0]])
        for i in items:
            money = '$' + str(i[1].get_value() + 1)
            rmb = self.get_message(i[1].describe().split('\n'))
            self.window.add(Menu.make([i[1].name], buy, rmb, name=i))
            self.sub_window.add(Menu.make([money], None, rmb, color=Window.fore_color_transparent, hover=False))
        self.sub_window.display(1)

    def menu_trainer(self):
        def click(button_arg):
            if Global.player.drink():
                Global.player.sleep(1)
                if button_arg[1] == 'exp1':
                    Global.player.character.attributes.strength += 1
                elif button_arg[1] == 'exp2':
                    Global.player.character.attributes.agility += 1
                elif button_arg[1] == 'exp3':
                    Global.player.character.attributes.intelligence += 1
                Global.player.character.say('Level Up!')
            self.toggle()
        text = ['I can help you level up an attribute. Tuition is $' + str(self.var[0].var['value']) + ' per lesson.']
        panel = Menu.make(text, None, None, color=Window.fore_color_transparent, width=320, hover=False, resize=True)
        panel.normal_font_color = Window.font_color1
        panel.hover_font_color = Window.font_color3
        panel.redraw()
        self.window.add(panel)
        self.window.next_y = self.window.size.y + self.window.vec.y
        cost = Global.player.character.attributes.get_total()
        rmb = self.get_message(['Train Intelligence. Requires ' + str(cost) + ' minerals.'])
        self.window.add(Menu.make(['Intelligence'], click, rmb, width=320, name=[cost, 'exp3']), reverse=True, index=0)
        rmb = self.get_message(['Train Agility. Requires ' + str(cost) + ' carbs.'])
        self.window.add(Menu.make(['Agility'], click, rmb, width=320, name=[cost, 'exp2']), reverse=True, index=0)
        rmb = self.get_message(['Train Strength. Requires ' + str(cost) + ' protein.'])
        self.window.add(Menu.make(['Strength'], click, rmb, width=320, name=[cost, 'exp1']), reverse=True, index=0)
        self.sub_window.display(1)

    def menu_guild(self):
        if self.var[0].var['amount'] <= 0:
            dur = Dialog.day(self.var[0].var['due'] - Global.player.days)
            self.show_dialog(['We do not need anything for now. Come back in ' + dur + '.'])
            return
        else:
            dur = Dialog.day(self.var[0].var['due'] - Global.player.days)
            reward = self.var[0].var['value']
            text = ['We are in need of ' + str(self.var[0].var['amount']) + ' ' + self.var[0].var['item'] + '.',
                    'Deliver full amount in ' + dur + ' to receive $' + str(reward) + '.']
            panel = Menu.make(text, None, None, color=Window.fore_color_transparent, hover=False, width=320, resize=True)
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
                    Global.player.character.say('Completed delivery!')
                    Global.player.character.var['money'] += reward
                elif count > 0:
                    Global.player.character.say('Provided ' + str(count) + ' ' + self.var[0].var['item'])
                else:
                    Global.player.character.say('No ' + self.var[0].var['item'] + '...')
            rmb = self.get_message(['Provide ' + self.var[0].var['item']])
            self.window.next_y = self.window.size.y + self.window.vec.y - 40 - self.window.margin.y
            self.window.add(Menu.make(['Provide ' + self.var[0].var['item']], sell, rmb, width=320))
            self.sub_window.display(1)

    def menu_insurance(self):
        contract = self.var[0].var['due'] - Global.player.days
        if contract <= 0:
            def package(arg):
                def insure(arg2):
                    if Global.player.character.require_var('money', value):
                        Global.player.character.states.add('Insured', -1, packages[arg] + '/' + str(time))
                        tgt.var['due'] = Global.player.days + time
                        self.toggle()
                Global.menu.var = [descriptions[arg] + ' Take the ' + packages[arg] +
                                   ' package for $' + str(costs[arg]) + '?',
                                   ['Pay'], [insure]]
                Global.player.menu(Global.menu.menu_choice)
            text = []
            tgt = self.var[0]
            time = (self.var[0].attributes.gene % 21 + 7) * 2
            value = int(time / 3) + (self.var[0].attributes.gene % 8)
            packages = ['Premium', 'Workers', 'Urban']
            costs = [value * 2, value, max(1, value - 4)]
            descriptions = ['The premium package covers everything: accidents, illness, suicide, homicide, '
                            'and wildlife hazards. You are guaranteed a second chance!',
                            'The workers package covers against all accidents, illness, and wildlife.',
                            'The urban package covers homicide and suicide.']
            text.append('Insurance contract lasts for ' + Dialog.day(time) +
                        '. Each package provide different coverage.')
            panel = Menu.make(text, None, None, color=Window.fore_color_transparent,
                              hover=False, width=320, resize=True)
            self.window.add(panel)
            self.window.next_y = self.window.size.y + self.window.vec.y - 40 - self.window.margin.y
            self.window.add(Menu.make(['Get Premium Package'], package, None, width=320, name=0))
            self.window.next_y = self.window.size.y + self.window.vec.y - 80 - self.window.margin.y * 2
            self.window.add(Menu.make(['Get Workers Package'], package, None, width=320, name=1))
            self.window.next_y = self.window.size.y + self.window.vec.y - 120 - self.window.margin.y * 3
            self.window.add(Menu.make(['Get Urban Package'], package, None, width=320, name=2))
            self.sub_window.display(1)
            return
        else:
            self.show_dialog(['You cannot be insured again until your current insurance contract is over.',
                              'Your current contract ends in ' + Dialog.day(contract)])

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
                button = Menu.make([item], craft, rmb, name=item)
            else:
                rmb = self.get_message((Crafting.describe(item, ingreds) + '\nRequirements not met.').split('\n'))
                button = Menu.make([item], rmb, rmb, name=item, color=Window.fore_color_disabled)
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
            self.show_dialog(['You do not know of anything that can be crafted here.'])

    def menu_anvil(self):
        self.history = [self.menu_anvil]
        self.history_var = [self.var]
        from src.entity.unit.item.Weapon import Weapon
        if self.host.is_armed() and isinstance(self.host.weapon, Weapon):
            text = 'Modify [' + self.host.weapon.get_display_name() + ']'
            desc = self.get_message(['Modify and upgrade the properties of your weapon'])
            self.window.add(Menu.make([text], lambda l: self.direct(self.menu_mod_weapon), desc, width=320))
        if self.host.is_armored():
            text = 'Modify [' + self.host.armor.get_display_name() + ']'
            desc = self.get_message(['Modify and upgrade the properties of your armor'])
            self.window.add(Menu.make([text], lambda l: self.direct(self.menu_mod_armor), desc, width=320))
        self.sub_window.display(1)

    def menu_mod_weapon(self):
        from src.entity.Particle import Particle

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

        text = 'Modification Success Chance - ' + str(self.host.weapon.get_enhance_chance()) + '%'
        self.window.add(Menu.make([text], None, None, width=320, resize=True, color=Window.fore_color_transparent))
        items = self.host.get_accessibles()
        flag = ['Scrap', 'Rubber', 'Tooth', 'Plating', 'Plating']
        deny = self.get_message(['No materials...'])
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
        if isinstance(flag[0], str):
            self.window.add(Menu.make(['Reinforce with Scrap'], deny, deny, width=320, name=flag[0],
                                      color=Window.fore_color_disabled))
        else:
            desc = self.get_message(['Reinforce to double maximum durability. Requires Scrap.'])
            self.window.add(Menu.make(['Reinforce with Scrap'], reinforce, desc, width=320, name=flag[0]))
        if self.host.weapon.speed > 1:
            if isinstance(flag[1], str):
                self.window.add(Menu.make(['Improve Grip with Rubber'], deny, deny, width=320, name=flag[0],
                                          color=Window.fore_color_disabled))
            else:
                desc = self.get_message(['Improve grip, increasing weapon speed. Requires Rubber.'])
                self.window.add(Menu.make(['Improve Grip with Rubber'], grip, desc, width=320, name=flag[1]))
        if self.host.weapon.speed > 1:
            if isinstance(flag[2], str):
                self.window.add(Menu.make(['Modify Blade with Tooth'], deny, deny, width=320, name=flag[0],
                                          color=Window.fore_color_disabled))
            else:
                desc = self.get_message(['Grind or attach weapon blade, improving attack by 1 ~ 3. Requires Tooth.'])
                self.window.add(Menu.make(['Modify Blade with Tooth'], blade, desc, width=320, name=flag[2]))
        if self.host.weapon.weight > 1:
            if isinstance(flag[3], str):
                self.window.add(Menu.make(['Modify Body with Plating'], deny, deny, width=320, name=flag[0],
                                          color=Window.fore_color_disabled))
            else:
                desc = self.get_message(['Modify weapon body, decreasing weight. Requires Plating.'])
                self.window.add(Menu.make(['Modify Body with Plating'], body, desc, width=320, name=flag[3]))
        if isinstance(flag[4], str):
            self.window.add(Menu.make(['Fortify Body with Plating'], deny, deny, width=320, name=flag[0],
                                      color=Window.fore_color_disabled))
        else:
            desc = self.get_message(['Fortify weapon body, increasing weight. Requires Plating.'])
            self.window.add(Menu.make(['Fortify Body with Plating'], fortify, desc, width=320, name=flag[3]))
        self.sub_window.display(1)

    def menu_mod_armor(self):
        from src.entity.Particle import Particle

        def reinforce(arg):
            if self.host.armor.enhance(Global.r.rand_int(1, 100)):
                self.host.armor.max_durability += Global.r.rand_int(1, 8)
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

        text = 'Modification Success Chance - ' + str(self.host.armor.get_enhance_chance()) + '%'
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
        if isinstance(flag[0], str):
            self.window.add(Menu.make(['Reinforce with Cloth'], deny, deny, width=320, name=flag[0],
                                      color=Window.fore_color_disabled))
        else:
            desc = self.get_message(['Improve maximum durability by 1 ~ 8. Requires Cloth.'])
            self.window.add(Menu.make(['Reinforce with Cloth'], reinforce, desc, width=320, name=flag[0]))
        if isinstance(flag[1], str):
            self.window.add(Menu.make(['Pad with Plating'], deny, deny, width=320, name=flag[0],
                                      color=Window.fore_color_disabled))
        else:
            desc = self.get_message(['Improve defense by 1. Requires Plating.'])
            self.window.add(Menu.make(['Pad with Plating'], pad, desc, width=320, name=flag[1]))
        if isinstance(flag[2], str):
            self.window.add(Menu.make(['Refit with Tooth'], deny, deny, width=320, name=flag[0],
                                      color=Window.fore_color_disabled))
        else:
            desc = self.get_message(['Decrease encumbrance by 1. Requires Tooth.'])
            self.window.add(Menu.make(['Refit with Tooth'], refit, desc, width=320, name=flag[2]))
        self.sub_window.display(1)

    def menu_hire(self):
        cost = self.var[0].attributes.get_total()
        text = ['Will you hire this person for $' + str(cost) + '?']
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
        self.window.add(Menu.make(['Hire'], hire, None, width=320))
        self.sub_window.display(1)

    def menu_beg(self):
        if not self.host.states.get('Thirst'):
            self.show_dialog(['You do not look desperate enough to beg. Go away.'])
        elif self.var[0].attributes.gene % 4 == 0:
            def beg(arg):
                self.host.states.get('Thirst').end()
                del self.var[0].var['business']
                from src.entity.Particle import Particle
                Particle.make('barrier', self.host.vec, offset=0)
                self.toggle()
            from src.tools.Data import Data
            dialogs = Data.get_line('data/raw/conversation.txt', 'beg')[1:]
            output = []
            for sentence in dialogs:
                new = ','.join(sentence)
                output.append(new)
            text = [output[self.var[0].attributes.gene % len(output)]]
            panel = Menu.make(text, None, None, color=Window.fore_color_transparent, hover=False, width=320, resize=True)
            panel.normal_font_color = Window.font_color1
            panel.hover_font_color = Window.font_color3
            panel.redraw()
            self.window.add(panel)
            self.window.next_y = self.window.size.y + self.window.vec.y - 40 - self.window.margin.y
            self.window.add(Menu.make(['Beg'], beg, None, width=320))
            self.sub_window.display(1)
        else:
            del self.var[0].var['business']
            self.show_dialog(['Go away!'])
