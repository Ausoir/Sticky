from src.game import Global
from src.game.Crafting import Crafting
from src.interface.Menu import Menu
from src.interface.MenuPlayer import MenuPlayer
from src.interface.Window import Window


class MenuAll(MenuPlayer):
    def menu_choice(self):
        self.history = [self.menu_choice]
        text = [self.var[0]]
        self.window.add(Menu.make(text, None, None, color=Window.fore_color0, hover=False, width=320))
        for i in range(len(self.var[1])):
            self.window.add(Menu.make([self.var[1][i]], self.var[2][i], None, name=i, width=320))
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
            if Global.player.pay(item.get_value()):
                item.relocate(Global.player.character.pos[0].x, Global.player.character.pos[0].y, force=1)
                item.add()
            else:
                self.toggle()
        self.history = [self.menu_shop]
        for i in self.var:
            gold = str(i.get_value()) + ' Gold'
            rmb = self.get_message(i.describe().split('\n'))
            self.window.add(Menu.make([i.name], buy, rmb, name=i))
            self.sub_window.add(Menu.make([gold], None, rmb, color=Window.fore_color0, hover=False))
        self.sub_window.display(1)

    def menu_trainer(self):
        def click(stat, sessions):
            def training():
                if Global.player.eat():
                    Global.player.sleep(1)
                    if sessions <= 1:
                        Global.player.experience[stat] = 0
                        if stat == 0:
                            Global.player.character.attributes.strength += 1
                        elif stat == 1:
                            Global.player.character.attributes.agility += 1
                        elif stat == 2:
                            Global.player.character.attributes.intelligence += 1
                        Global.player.monologue.text('Completed current training!')
                    else:
                        Global.player.experience[stat] += 1
                        Global.player.monologue.text('Completed a training session.')
                self.toggle()
            return training
        self.history = [self.menu_trainer]
        text = ['<Chu>', 'What aspect would you like to strengthen?']
        panel = Menu.make(text, None, None, color=Window.fore_color0, hover=False)
        panel.normal_font_color = Window.font_color1
        panel.hover_font_color = Window.font_color3
        panel.redraw()
        self.window.add(panel)
        cost = Global.player.character.attributes.strength - Global.player.experience[0]
        rmb = self.get_message(['Increase Strength. Takes ' + str(cost) + ' sessions.'])
        self.sub_window.add(Menu.make(['Strength'], click(0, cost), rmb))
        cost = Global.player.character.attributes.agility - Global.player.experience[1]
        rmb = self.get_message(['Increase Agility. Takes ' + str(cost) + ' sessions.'])
        self.sub_window.add(Menu.make(['Agility'], click(1, cost), rmb))
        cost = Global.player.character.attributes.intelligence - Global.player.experience[1]
        rmb = self.get_message(['Increase Intelligence. Takes ' + str(cost) + ' sessions.'])
        self.sub_window.add(Menu.make(['Intelligence'], click(2, cost), rmb))
        self.sub_window.display(1)

    def menu_guild(self):
        self.history = [self.menu_guild]
        if self.var[3] <= 0:
            self.show_dialog(['<Guildsman>', 'We do not need anything for now. Come back at a later date.'])
            return
        else:
            dur = self.var[1] - Global.player.days
            if dur % 2 == 1:
                dur = str(int(dur / 2)) + ' and half days'
            elif dur > 2:
                dur = str(dur / 2) + ' days'
            else:
                dur = 'one day'
            reward = int((self.var[3] * self.var[4]) / 2) + 1
            text = ['<Guildsman>', 'We are currently in need of ' + str(self.var[3]) + ' ' + self.var[2] + '.',
                    'Deliver full amount within ' + dur + ' to receive ' + str(reward) + ' gold.']
            panel = Menu.make(text, None, None, color=Window.fore_color0, hover=False, width=320)
            panel.redraw()
            self.window.add(panel)

            def sell(name):
                items = Global.player.character.get_accessibles()
                count = 0
                for item in items:
                    if item.name == self.var[2]:
                        item.loot = None
                        item.die()
                        count += 1
                self.var[3] -= count
                if self.var[3] <= 0:
                    Global.player.monologue.text('Completed guild quest!')
                    Global.player.character.modify_gold(reward)
                elif count > 0:
                    Global.player.monologue.text('Provided ' + str(count) + ' ' + self.var[2])
                else:
                    Global.player.monologue.text('No ' + self.var[2] + '...')
            rmb = self.get_message(['Provide ' + self.var[2]])
            self.window.next_y = self.window.size.y + self.window.vec.y - 40 - self.window.margin.y
            self.window.add(Menu.make(['Provide ' + self.var[2]], sell, rmb, width=320))
            self.sub_window.display(1)

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
                button = Menu.make([text], None, rmb, color=Window.fore_color0)
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
            self.window.add(Menu.make(['Modify Armor'], lambda l: self.direct(self.menu_repair), desc, width=320))
        self.sub_window.display(1)

    def menu_mod_weapon(self):
        from src.entity.Effect import Effect

        def reinforce(arg):
            if self.host.weapon.enhance(Global.r.rand_int(0, 99)):
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
            if self.host.weapon.enhance(Global.r.rand_int(0, 99)):
                self.host.weapon.speed -= 1
            else:
                Effect.make('disintegrate', self.host.vec)
                self.host.weapon.die()
            arg.die()
            self.toggle()

        def blade(arg):
            if self.host.weapon.enhance(Global.r.rand_int(0, 99)):
                self.host.weapon.damage += 1
            else:
                Effect.make('disintegrate', self.host.vec)
                self.host.weapon.die()
            arg.die()
            self.toggle()

        def body(arg):
            if self.host.weapon.enhance(Global.r.rand_int(0, 99)):
                self.host.weapon.weight -= 1
            else:
                Effect.make('disintegrate', self.host.vec)
                self.host.weapon.die()
            arg.die()
            self.toggle()

        items = self.host.get_accessibles()
        flag = ['Scrap', 'Rubber', 'Tooth', 'Plating']
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
        desc = self.get_message(['Reinforce to double maximum durability. Requires Scrap.'])
        self.window.add(Menu.make(['Reinforce with Scrap'], lmb[0], desc, width=320, name=flag[0]))
        if self.host.weapon.speed > 1:
            desc = self.get_message(['Improve grip, increasing weapon speed. Requires Rubber.'])
            self.window.add(Menu.make(['Improve Grip with Rubber'], lmb[1], desc, width=320, name=flag[1]))
        desc = self.get_message(['Grind or attach weapon blade, increasing attack. Requires Tooth.'])
        self.window.add(Menu.make(['Modify Blade with Tooth'], lmb[2], desc, width=320, name=flag[2]))
        if self.host.weapon.weight > 1:
            desc = self.get_message(['Improve weapon body, decreasing weight. Requires Plating.'])
            self.window.add(Menu.make(['Modify Body with Plating'], lmb[3], desc, width=320, name=flag[3]))
        self.sub_window.display(1)
