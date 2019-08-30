from src.game import Global
from src.game.Crafting import Crafting
from src.interface.Menu import Menu
from src.interface.MenuPlayer import MenuPlayer
from src.interface.Window import Window
from src.tools.Dialog import Dialog


class MenuAll(MenuPlayer):
    def menu_choice(self):
        self.history = [self.menu_choice]
        text = [self.var[0]]
        self.window.add(Menu.make(text, None, None, color=Window.fore_color0, hover=False, width=320))
        for i in range(len(self.var[1])):
            self.window.add(Menu.make([self.var[1][i]], self.var[2][i], None, name=i, width=320))
        self.sub_window.display(1)

    def menu_conversation(self):
        def conversation(name):
            from src.tools.Data import Data
            if 'talk' in self.var[0].var:
                talk_type = self.var[0].var['talk']
            else:
                talk_type = 'none'
            dialogs = Data.get_line('data/raw/conversation.txt', talk_type)[1:]
            output = []
            for sentence in dialogs:
                new = ','.join(sentence)
                output.append(new)
            Global.menu.show_dialog([output[self.var[0].attributes.gene % len(output)]])
        self.history = [self.menu_conversation]
        self.window.add(Menu.make([self.var[0].name], None, None, color=Window.fore_color0, hover=False, width=320))
        rmb = self.get_message(['Make a conversation'])
        self.window.add(Menu.make(['Talk'], conversation, rmb))
        rmb = self.get_message(['Ask for hints and tips'])
        self.window.add(Menu.make(['Ask'], lambda l: self.direct(self.menu_help), rmb))
        rmb = self.get_message(['Ask this unit to accompany you'])
        self.window.add(Menu.make(['Hire'], lambda l: self.direct(self.menu_hire), rmb))
        from src.entity.unit.Humanoid import Humanoid
        if isinstance(self.var[0], Humanoid):
            if self.var[0].is_armed() or self.var[0].is_headgeared():
                rmb = self.get_message(['Exchange for an equipment'])
                self.window.add(Menu.make(['Exchange'], lambda l: self.direct(self.menu_exchange), rmb))
            from src.entity.unit.Character import Character
            if isinstance(self.var[0], Character) and 'business' in self.var[0].var:
                def talk(name):
                    from src.game.Interaction import Interaction
                    Interaction.talk(self.var[0])
                rmb = self.get_message(['Bring up special dialogue options for this NPC'])
                self.window.add(Menu.make([self.var[0].var['business']], talk, rmb))
        self.sub_window.display(1)

    def menu_travel(self):
        self.history = [self.menu_travel]
        destination = self.var[0].title()
        option = 'Travel'
        text = ['Travel to [' + destination + '] ?']
        panel = Menu.make(text, None, None, color=Window.fore_color0, hover=False, width=320)
        panel.normal_font_color = Window.font_color1
        panel.hover_font_color = Window.font_color3
        panel.redraw()
        self.window.add(panel)
        from src.entity.Space import Space

        def travel(name):
            if Global.player.depart == self.var[0]:
                Global.player.travel(self.var[0], Space(int(self.var[1]), int(self.var[2])))
            elif Global.player.eat():
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
            if Global.player.pay(item.get_value() + int(self.var[0])):
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
                gold = str(i.get_value() + int(self.var[1])) + ' Gold'
                rmb = self.get_message(i.describe().split('\n'))
                self.window.add(Menu.make([i.name], buy, rmb, name=i))
                self.sub_window.add(Menu.make([gold], None, rmb, color=Window.fore_color0, hover=False))
            self.sub_window.display(1)

    def menu_exchange(self):
        def buy(item):
            if Global.player.pay(item[1].get_value()):
                if item[0] == 'w':
                    self.var.drop()
                elif item[0] == 'h':
                    self.var.unheadgear()
                item[1].relocate(Global.player.character.pos.x, Global.player.character.pos.y, force=1)
            else:
                self.toggle()
        items = []
        if self.var.is_armed():
            items.append(['w', self.var.weapon])
        if self.var.is_headgeared():
            items.append(['h', self.var.headgear])
        for i in items:
            gold = str(i[1].get_value() + 1) + ' Gold'
            rmb = self.get_message(i[1].describe().split('\n'))
            self.window.add(Menu.make([i[1].name], buy, rmb, name=i))
            self.sub_window.add(Menu.make([gold], None, rmb, color=Window.fore_color0, hover=False))
        self.sub_window.display(1)

    def menu_trainer(self):
        def click(button_arg):
            past = self.var[0].var['due'] - Global.player.days
            if past <= 0:
                if Global.player.eat():
                    Global.player.sleep(1)
                    self.var[0].var['due'] = Global.player.days + Global.player.character.attributes.get_total()
                    if button_arg[0] <= 1:
                        Global.player.character.var[button_arg[1]] = 0
                        if button_arg[1] == 'exp1':
                            Global.player.character.attributes.strength += 1
                        elif button_arg[1] == 'exp2':
                            Global.player.character.attributes.agility += 1
                        elif button_arg[1] == 'exp3':
                            Global.player.character.attributes.intelligence += 1
                        Global.player.monologue.text('Level Up!')
                    else:
                        Global.player.character.var[button_arg[1]] += 1
                        Global.player.monologue.text('Completed a training session')
            else:
                Global.player.monologue.text('I will be ready to train again in ' + Dialog.date(past))
            self.toggle()
        text = ['What aspect would you like to strengthen?']
        panel = Menu.make(text, None, None, color=Window.fore_color0, hover=False)
        panel.normal_font_color = Window.font_color1
        panel.hover_font_color = Window.font_color3
        panel.redraw()
        self.window.add(panel)
        cost = Global.player.character.attributes.strength - Global.player.character.var['exp1']
        rmb = self.get_message(['Train Strength. Takes ' + str(cost) + ' sessions.'])
        self.sub_window.add(Menu.make(['Strength'], click, rmb, name=[cost, 'exp1']))
        cost = Global.player.character.attributes.agility - Global.player.character.var['exp2']
        rmb = self.get_message(['Train Agility. Takes ' + str(cost) + ' sessions.'])
        self.sub_window.add(Menu.make(['Agility'], click, rmb, name=[cost, 'exp2']))
        cost = Global.player.character.attributes.intelligence - Global.player.character.var['exp3']
        rmb = self.get_message(['Train Intelligence. Takes ' + str(cost) + ' sessions.'])
        self.sub_window.add(Menu.make(['Intelligence'], click, rmb, name=[cost, 'exp3']))
        self.sub_window.display(1)

    def menu_guild(self):
        if self.var[0].var['amount'] <= 0:
            self.show_dialog(['We do not need anything for now. Come back at a later date.'])
            return
        else:
            dur = Dialog.date(self.var[0].var['due'] - Global.player.days)
            reward = int((self.var[0].var['amount'] * self.var[0].var['value']) / 2) + 1
            text = ['We are in need of ' + str(self.var[0].var['amount']) + ' ' + self.var[0].var['item'] + '.',
                    'Deliver full amount within ' + dur + ' to receive ' + str(reward) + ' gold.']
            panel = Menu.make(text, None, None, color=Window.fore_color0, hover=False, width=320, resize=True)
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
                    Global.player.monologue.text('Completed delivery!')
                    Global.player.character.modify_gold(reward)
                elif count > 0:
                    Global.player.monologue.text('Provided ' + str(count) + ' ' + self.var[0].var['item'])
                else:
                    Global.player.monologue.text('No ' + self.var[0].var['item'] + '...')
            rmb = self.get_message(['Provide ' + self.var[0].var['item']])
            self.window.next_y = self.window.size.y + self.window.vec.y - 40 - self.window.margin.y
            self.window.add(Menu.make(['Provide ' + self.var[0].var['item']], sell, rmb, width=320))
            self.sub_window.display(1)

    def menu_insurance(self):
        contract = self.var[0].var['due'] - Global.player.days
        if contract <= 0:
            def insure(arg):
                if Global.player.pay(value):
                    Global.player.character.states.add('Insured', -1, 14)
                    self.var[0].var['due'] = Global.player.days + 14
            text = []
            value = self.var[0].var['value']
            text.append('Would you like to get insured for ' + Dialog.date(self.var[0].var['time'])
                        + ' for only ' + str(value) + ' gold?')
            panel = Menu.make(text, None, None, color=Window.fore_color0, hover=False, width=320, resize=True)
            self.window.add(panel)
            self.window.next_y = self.window.size.y + self.window.vec.y - 40 - self.window.margin.y
            self.window.add(Menu.make(['Get Insurance'], insure, None, width=320))
            self.sub_window.display(1)
            return
        else:
            self.show_dialog(['You cannot be insured again until your current insurance contract is over.',
                              'Your current contract ends in ' + Dialog.date(contract)])

    def menu_craft(self):
        def add_button(window, text):
            def craft(arg):
                Crafting.craft(self.host, text)
                self.host.action.set('block')
                self.toggle()
            if Crafting.is_craftable(self.host, text):
                rmb = self.get_message(Crafting.describe(text).split('\n'))
                button = Menu.make([text], craft, rmb)
            else:
                rmb = self.get_message((Crafting.describe(text) + '\nRequirements not met.').split('\n'))
                button = Menu.make([text], rmb, rmb, color=Window.fore_color0)
                button.hover_font_color = window.normal_font_color
            window.add(button)
        self.history = [self.menu_craft]
        desc = self.get_message(['Repair an equipment'])
        self.window.add(Menu.make(['<Repair>'], lambda l: self.direct(self.menu_repair), desc))
        for i in self.var[:5]:
            add_button(self.window, i)
        for i in self.var[5:]:
            add_button(self.sub_window, i)
        self.window.display(1)
        self.sub_window.display(1)

    def menu_repair(self):
        def repair(arg):
            gear = arg[1]
            if gear.max_durability > gear.durability:
                gear.durability = gear.max_durability
                arg[0].die()
            self.toggle()
        fiber = None
        items = self.host.get_accessibles()
        for i in items:
            if i.name == 'Fiber':
                fiber = i
                break
        rmb_fiber = self.get_message(['Repair an item to max HP, consuming <Fiber> item in the process'])
        if fiber:
            if self.host.is_armed():
                text = ['Repair weapon with fiber']
                self.window.add(Menu.make(text, repair, rmb_fiber, width=320, name=[fiber, self.host.weapon]))
            if self.host.is_armored():
                text = ['Repair armor with fiber']
                self.window.add(Menu.make(text, repair, rmb_fiber, width=320, name=[fiber, self.host.armor]))
            if self.host.is_headgeared():
                text = ['Repair headgear with fiber']
                self.window.add(Menu.make(text, repair, rmb_fiber, width=320, name=[fiber, self.host.headgear]))
        else:
            text = ['Cannot repair without fiber']
            button = Menu.make(text, None, rmb_fiber, color=Window.fore_color0, hover=False, width=320)
            self.window.add(button)
        self.sub_window.display(1)

    def menu_anvil(self):
        self.history = [self.menu_anvil]
        desc = self.get_message(['Repair an equipment'])
        self.window.add(Menu.make(['Repair'], lambda l: self.direct(self.menu_repair), desc, width=320))
        from src.entity.unit.item.Weapon import Weapon
        if self.host.is_armed() and isinstance(self.host.weapon, Weapon):
            text = 'Modify Weapon - %' + str(self.host.weapon.get_enhance_chance()) + ''
            self.window.add(Menu.make([text], lambda l: self.direct(self.menu_mod_weapon), desc, width=320))
        if self.host.is_armored():
            text = 'Modify Armor - %' + str(self.host.armor.get_enhance_chance()) + ''
            self.window.add(Menu.make([text], lambda l: self.direct(self.menu_mod_armor), desc, width=320))
        self.sub_window.display(1)

    def menu_mod_weapon(self):
        from src.entity.Effect import Effect

        def reinforce(arg):
            if self.host.weapon.enhance(Global.r.rand_int(1, 100)):
                self.host.weapon.max_durability *= 2
                if self.host.weapon.max_durability >= 256:
                    self.host.weapon.durability = -1
                    self.host.weapon.max_durability = -1
            else:
                Effect.make('disintegrate', self.host.vec)
                self.host.weapon.die()
            arg.die()
            self.toggle()

        def grip(arg):
            if self.host.weapon.enhance(Global.r.rand_int(1, 100)):
                self.host.weapon.speed -= 1
            else:
                Effect.make('disintegrate', self.host.vec)
                self.host.weapon.die()
            arg.die()
            self.toggle()

        def blade(arg):
            if self.host.weapon.enhance(Global.r.rand_int(1, 100)):
                self.host.weapon.damage += Global.r.rand_int(1, 3)
            else:
                Effect.make('disintegrate', self.host.vec)
                self.host.weapon.die()
            arg.die()
            self.toggle()

        def body(arg):
            if self.host.weapon.enhance(Global.r.rand_int(1, 100)):
                self.host.weapon.weight -= 1
            else:
                Effect.make('disintegrate', self.host.vec)
                self.host.weapon.die()
            arg.die()
            self.toggle()

        def fortify(arg):
            if self.host.weapon.enhance(Global.r.rand_int(1, 100)):
                self.host.weapon.weight += 1
            else:
                Effect.make('disintegrate', self.host.vec)
                self.host.weapon.die()
            arg.die()
            self.toggle()

        items = self.host.get_accessibles()
        flag = ['Scrap', 'Rubber', 'Tooth', 'Plating', 'Plating']
        deny = self.get_message(['No materials...'])
        lmb = [deny, deny, deny, deny]
        for i in items:
            if i.name == flag[0]:
                flag[0] = i
                lmb[0] = reinforce
            if i.name == flag[1]:
                flag[1] = i
                lmb[1] = grip
            if i.name == flag[2]:
                flag[2] = i
                lmb[2] = blade
            if i.name == flag[3]:
                flag[3] = i
                lmb[3] = body
            if i.name == flag[4]:
                flag[4] = i
                lmb[4] = fortify
        desc = self.get_message(['Reinforce to double maximum durability. Requires Scrap.'])
        self.window.add(Menu.make(['Reinforce with Scrap'], lmb[0], desc, width=320, name=flag[0]))
        if self.host.weapon.speed > 1:
            desc = self.get_message(['Improve grip, increasing weapon speed. Requires Rubber.'])
            self.window.add(Menu.make(['Improve Grip with Rubber'], lmb[1], desc, width=320, name=flag[1]))
        desc = self.get_message(['Grind or attach weapon blade, improving attack by 1 ~ 3. Requires Tooth.'])
        self.window.add(Menu.make(['Modify Blade with Tooth'], lmb[2], desc, width=320, name=flag[2]))
        if self.host.weapon.weight > 1:
            desc = self.get_message(['Modify weapon body, decreasing weight. Requires Plating.'])
            self.window.add(Menu.make(['Modify Body with Plating'], lmb[3], desc, width=320, name=flag[3]))
        desc = self.get_message(['Fortify weapon body, increasing weight. Requires Plating.'])
        self.window.add(Menu.make(['Fortify Body with Plating'], lmb[4], desc, width=320, name=flag[3]))
        self.sub_window.display(1)

    def menu_mod_armor(self):
        from src.entity.Effect import Effect

        def reinforce(arg):
            if self.host.armor.enhance(Global.r.rand_int(1, 100)):
                self.host.armor.max_durability += Global.r.rand_int(1, 3)
            else:
                Effect.make('disintegrate', self.host.vec)
                self.host.armor.die()
            arg.die()
            self.toggle()

        def pad(arg):
            if self.host.armor.enhance(Global.r.rand_int(1, 100)):
                self.host.armor.armor += 1
            else:
                Effect.make('disintegrate', self.host.vec)
                self.host.armor.die()
            arg.die()
            self.toggle()

        def refit(arg):
            if self.host.armor.enhance(Global.r.rand_int(1, 100)):
                self.host.armor.weight -= 1
            else:
                Effect.make('disintegrate', self.host.vec)
                self.host.armor.die()
            arg.die()
            self.toggle()

        items = self.host.get_accessibles()
        flag = ['Cloth', 'Plating', 'Tooth']
        deny = self.get_message(['No materials...'])
        lmb = [deny, deny, deny]
        for i in items:
            if i.name == flag[0]:
                flag[0] = i
                lmb[0] = reinforce
            if i.name == flag[1]:
                flag[1] = i
                lmb[1] = pad
            if i.name == flag[2]:
                flag[2] = i
                lmb[2] = refit
        desc = self.get_message(['Improve maximum durability by 1 ~ 3. Requires Cloth.'])
        self.window.add(Menu.make(['Reinforce with Cloth'], lmb[0], desc, width=320, name=flag[0]))
        desc = self.get_message(['Improve defense by 1. Requires Plating.'])
        self.window.add(Menu.make(['Pad with Plating'], lmb[1], desc, width=320, name=flag[1]))
        desc = self.get_message(['Decrease encumbrance by 1. Requires Tooth.'])
        self.window.add(Menu.make(['Refit with '], lmb[2], desc, width=320, name=flag[2]))
        self.sub_window.display(1)

    def menu_hire(self):
        cost = 0
        text = ['Will you hire this person for ' + str(cost) + ' Gold?']
        panel = Menu.make(text, None, None, color=Window.fore_color0, hover=False, width=320)
        panel.normal_font_color = Window.font_color1
        panel.hover_font_color = Window.font_color3
        panel.redraw()
        self.window.add(panel)

        def hire(name):
            if Global.player.pay(cost):
                pass
            self.toggle()
        self.window.next_y = self.window.size.y + self.window.vec.y - 40 - self.window.margin.y
        self.window.add(Menu.make(['Hire'], hire, None, width=320))
        self.sub_window.display(1)

    def menu_beg(self):
        if not self.host.states.get('Hunger'):
            self.show_dialog(['You do not look hungry enough to beg. Go away.'])
        elif self.var[0].attributes.gene % 3 == 0:
            def beg(arg):
                self.host.states.get('Hunger').end()
                del self.var[0].var['business']
                from src.entity.Effect import Effect
                Effect.make('barrier', self.host.vec, offset=0)
                self.toggle()
            from src.tools.Data import Data
            dialogs = Data.get_line('data/raw/conversation.txt', 'beg')[1:]
            output = []
            for sentence in dialogs:
                new = ','.join(sentence)
                output.append(new)
            text = [output[self.var[0].attributes.gene % len(output)]]
            panel = Menu.make(text, None, None, color=Window.fore_color0, hover=False, width=320, resize=True)
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

    def menu_help(self):
        button = Menu.make(['The Basics'], lambda l: self.direct(self.menu_help_basic), None, width=320)
        self.window.add(button)
        button = Menu.make(['Tips'], lambda l: self.direct(self.menu_help_tip), None, width=320)
        self.window.add(button)
        button = Menu.make(['Dungeon Locations'], lambda l: self.direct(self.menu_help_tip), None, width=320)
        self.window.add(button)
        button = Menu.make(['Items'], lambda l: self.direct(self.menu_help_items), None, width=320)
        self.window.add(button)
        self.window.display(1)
        self.sub_window.display(1)

    def menu_help_where(self):
        lmb = self.get_message(['The garden is located within town.',
                                'Look for an area with dirt and grass on the right side of town.'])
        button = Menu.make(['Gardens'], lmb, None)
        self.window.add(button)
        button = Menu.make(['Nests'], lmb, None)
        self.window.add(button)
        button = Menu.make(['Slums'], lmb, None)
        self.window.add(button)
        button = Menu.make(['Dojo'], lmb, None)
        self.window.add(button)
        button = Menu.make(['Sewers'], lmb, None)
        self.window.add(button)
        button = Menu.make(['Outside Town'], lmb, None)
        self.window.add(button)
        button = Menu.make(['Guildsman'], lmb, None)
        self.sub_window.add(button)
        button = Menu.make(['Dealer'], lmb, None)
        self.sub_window.add(button)
        button = Menu.make(['Scrapper'], lmb, None)
        self.sub_window.add(button)
        button = Menu.make(['Trainer'], lmb, None)
        self.sub_window.add(button)
        self.window.display(1)
        self.sub_window.display(1)

    def menu_help_items(self):
        lmb = self.get_message(['Wooden Planks can be found pretty much anywhere.',
                                'With a weapon with damage higher than 2, you can destroy wooden objects for planks.'])
        button = Menu.make(['Planks'], lmb, None)
        self.window.add(button)
        button = Menu.make(['Torch'], lmb, None)
        self.window.add(button)
        button = Menu.make(['Medical Items'], lmb, None)
        self.window.add(button)
        button = Menu.make(['Paper'], lmb, None)
        self.window.add(button)
        button = Menu.make(['Cloth'], lmb, None)
        self.window.add(button)
        button = Menu.make(['Ladder'], lmb, None)
        self.window.add(button)
        button = Menu.make(['Armor'], lmb, None)
        self.sub_window.add(button)
        button = Menu.make(['Weapons'], lmb, None)
        self.sub_window.add(button)
        button = Menu.make(['Food'], lmb, None)
        self.sub_window.add(button)
        button = Menu.make(['Gold'], lmb, None)
        self.sub_window.add(button)
        self.window.display(1)
        self.sub_window.display(1)

    def menu_help_tip(self):
        lmb = self.get_message(['You cannot travel hungry. Check your Status menu under Character menu for hunger.',
                                'You can travel to your latest map without food.',
                                'If you are hungry and stuck in a map, there is nothing much you can do...',
                                'I guess you can try some spells or commit suicide by attacking on yourself.',
                                'I recommend carrying around an amulet of memory if you plan on travelling far.'])
        button = Menu.make(['Travelling'], lmb, None, width=320)
        self.window.add(button)
        self.window.display(1)
        self.sub_window.display(1)

    def menu_help_basic(self):
        lmb = self.get_message(['The default keys are WASD and Left or Right mouse buttons.',
                                'Left mouse button functions as both attacking and interacting.',
                                'Right mouse button can pick up or drop items.',
                                'Right mouse button can also be used to view button description.',
                                'TAB key can be used to access the menu.',
                                'You can edit the data/keymap.txt file to edit controls.'])
        button = Menu.make(['Basic Controls'], lmb, None, width=320)
        self.window.add(button)
        lmb = self.get_message(['So you are looking for a way back? Find a harbor and sail to the mainland.',
                                'You will land on a village full of people like you.',
                                'The trip is very expensive and mainland is a very dangerous place, so prepare.'])
        button = Menu.make(['Purpose'], lmb, None, width=320)
        self.window.add(button)
        lmb = self.get_message(['There are couple ways to earn gold around here.',
                                'First is by seeking dealers who would offer you gold in exchange for certain items.',
                                'Second is by exploring dungeons for treasure.',
                                'You could also join the mercenary guild.'])
        button = Menu.make(['How to make money'], lmb, None, width=320)
        self.window.add(button)
        lmb = self.get_message(['What you are looking for are the merchants.',
                                'They are dressed in gold and wear a top hat.'])
        button = Menu.make(['Where to get food'], lmb, None, width=320)
        self.window.add(button)
        lmb = self.get_message(['You can increase the stats shown in the Character menu by leveling up at the dojo.',
                                'You can also learn abilities and spells if you can find the knowledge.',
                                'Upgrading your weapons and armor at the anvil is also important.',
                                'Also be aware of rumors of legendary artifacts and supernatural powers...'])
        button = Menu.make(['How to become stronger'], lmb, None, width=320)
        self.window.add(button)
        lmb = self.get_message(['From the town, you can head left to the port to sail to different locations.',
                                'There are also couple dungeons inside town, just make sure you have enough food.',
                                'If you leave town by heading right, you will travel towards the deserts.'])
        button = Menu.make(['Locations'], lmb, None, width=320)
        self.window.add(button)
        self.window.display(1)
        self.sub_window.display(1)
