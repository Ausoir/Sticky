from src.game import Global
from src.game.Crafting import Crafting
from src.interface.Menu import Menu
from src.interface.MenuPlayer import MenuPlayer
from src.interface.Window import Window


class MenuAll(MenuPlayer):
    def menu_travel(self):
        self.history = [self.menu_travel]
        penalty = 0
        destination = self.var[0].title()
        option = 'Travel'
        if Global.main.player.character.states.get('Hunger'):
            if Global.main.player.character.states.get('Sick'):
                self.show_dialog(['You cannot travel because you are dying. Check your status menu.'])
                return
            else:
                text = ['You are starving. You can force travel, but without treatment you will die soon after.',
                        'Travel to [' + destination + '] ?']
                panel = Menu.make_button(text, None, None, color=Window.fore_color0, hover=False, width=320)
                option = 'Force Travel'
                self.window.add_child(panel)
                penalty = 2
        else:
            text = ['Travel to [' + destination + '] ?']
            panel = Menu.make_button(text, None, None, color=Window.fore_color0, hover=False, width=320)
            panel.normal_font_color = Window.font_color1
            panel.hover_font_color = Window.font_color3
            panel.redraw()
            self.window.add_child(panel)
        from src.entity.Space import Space

        def travel():
            if penalty == 0:
                self.host.states.add('Hunger', -1)
            else:
                self.host.states.add('Sick', Global.r.rand_int(60, 300))
            Global.main.player.sleep(1)
            Global.main.player.travel(self.var[0], Space(int(self.var[1]), int(self.var[2])))
        rmb = self.get_message(['Travel to ' + destination])
        self.window.next_y = self.window.size.y + self.window.vec.y - 40 - self.window.margin.y
        self.window.add_child(Menu.make_button([option], travel, rmb, width=320))
        self.sub_window.display(1)

    def menu_shop(self):
        def click(item):
            def buy():
                if Global.main.player.character.modify_gold(-item.get_value()):
                    item.relocate(Global.main.player.character.pos[0].x, Global.main.player.character.pos[0].y, force=1)
                    item.add()
            return buy
        self.history = [self.menu_shop]
        from src.entity.Stock import Stock
        for i in self.var:
            item = Stock.get(i)
            gold = str(item.get_value()) + ' Gold'
            rmb = self.get_message(item.describe().split('\n'))
            self.window.add_child(Menu.make_button([i], click(item), rmb))
            self.sub_window.add_child(Menu.make_button([gold], None, rmb, color=Window.fore_color0, hover=False))
        self.sub_window.display(1)

    def menu_trainer(self):
        def click(stat, sessions):
            def training():
                if not self.host.states.get('Hunger'):
                    Global.main.player.sleep(1)
                    self.host.states.add('Hunger', -1)
                    if sessions <= 1:
                        Global.main.player.experience[stat] = 0
                        if stat == 0:
                            Global.main.player.character.attributes.strength += 1
                        elif stat == 1:
                            Global.main.player.character.attributes.agility += 1
                        elif stat == 2:
                            Global.main.player.character.attributes.intelligence += 1
                        Global.main.player.monologue.text('Completed current training!')
                    else:
                        Global.main.player.experience[stat] += 1
                        Global.main.player.monologue.text('Completed a training session.')
                    self.toggle()
                else:
                    self.show_dialog(['You are too hungry to train!', 'Eat something first.'])
            return training
        self.history = [self.menu_trainer]
        text = ['<Chu>', 'What aspect would you like to strengthen?']
        panel = Menu.make_button(text, None, None, color=Window.fore_color0, hover=False)
        panel.normal_font_color = Window.font_color1
        panel.hover_font_color = Window.font_color3
        panel.redraw()
        self.window.add_child(panel)
        cost = Global.main.player.character.attributes.strength - Global.main.player.experience[0]
        rmb = self.get_message(['Increase Strength. Takes ' + str(cost) + ' sessions.'])
        self.sub_window.add_child(Menu.make_button(['Strength'], click(0, cost), rmb))
        cost = Global.main.player.character.attributes.agility - Global.main.player.experience[1]
        rmb = self.get_message(['Increase Agility. Takes ' + str(cost) + ' sessions.'])
        self.sub_window.add_child(Menu.make_button(['Agility'], click(1, cost), rmb))
        cost = Global.main.player.character.attributes.intelligence - Global.main.player.experience[1]
        rmb = self.get_message(['Increase Intelligence. Takes ' + str(cost) + ' sessions.'])
        self.sub_window.add_child(Menu.make_button(['Intelligence'], click(2, cost), rmb))
        self.sub_window.display(1)

    def menu_guild(self):
        self.history = [self.menu_guild]
        if self.var[3] <= 0:
            self.show_dialog(['<Guildsman>', 'We do not need anything for now. Come back at a later date.'])
            return
        else:
            dur = self.var[1] - Global.main.player.days
            if dur % 2 == 1:
                dur = str(int(dur / 2)) + ' and half days'
            elif dur > 2:
                dur = str(dur / 2) + ' days'
            else:
                dur = 'one day'
            reward = int((self.var[3] * self.var[4]) / 2) + 1
            text = ['<Guildsman>', 'We are currently in need of ' + str(self.var[3]) + ' ' + self.var[2] + '.',
                    'Deliver full amount within ' + dur + ' to receive ' + str(reward) + ' gold.']
            panel = Menu.make_button(text, None, None, color=Window.fore_color0, hover=False, width=320)
            panel.normal_font_color = Window.font_color1
            panel.hover_font_color = Window.font_color3
            panel.redraw()
            self.window.add_child(panel)

            def sell():
                items = Global.main.player.character.get_accessibles()
                count = 0
                for item in items:
                    if item.name == self.var[2]:
                        item.loot = None
                        item.die()
                        count += 1
                self.var[3] -= count
                if self.var[3] <= 0:
                    Global.main.player.monologue.text('Completed guild quest!')
                    Global.main.player.character.modify_gold(reward)
                elif count > 0:
                    Global.main.player.monologue.text('Provided ' + str(count) + ' ' + self.var[2])
                else:
                    Global.main.player.monologue.text('No ' + self.var[2] + '...')
            rmb = self.get_message(['Provide ' + self.var[2]])
            self.window.next_y = self.window.size.y + self.window.vec.y - 40 - self.window.margin.y
            self.window.add_child(Menu.make_button(['Provide ' + self.var[2]], sell, rmb, width=320))
            self.sub_window.display(1)

    def menu_craft(self):
        def add_button(window, text):
            def craft():
                Crafting.craft(self.host, text)
                self.host.action.set('block')
                self.toggle()
            if Crafting.is_craftable(self.host, text):
                rmb = self.get_message(Crafting.describe(text).split('\n'))
                button = Menu.make_button([text], craft, rmb)
            else:
                rmb = self.get_message((Crafting.describe(text) + '\nRequirements not met.').split('\n'))
                button = Menu.make_button([text], None, rmb, color=Window.fore_color0)
                button.hover_font_color = window.normal_font_color
            window.add_child(button)

        def repair():
            self.direct(self.menu_repair)

        self.history = [self.menu_craft]
        desc = self.get_message(['Repair an equipment'])
        self.window.add_child(Menu.make_button(['Repair'], repair, desc))
        for i in self.var[:5]:
            add_button(self.window, i)
        for i in self.var[5:]:
            add_button(self.sub_window, i)
        self.window.display(1)
        self.sub_window.display(1)

    def menu_repair(self):
        def click(mat, gear):
            def repair():
                if gear.max_durability > gear.durability:
                    gear.durability = gear.max_durability
                    mat.die()
            return repair

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
                self.window.add_child(Menu.make_button(text, click(fiber, self.host.weapon), rmb_fiber, width=320))
            if self.host.is_armored():
                text = ['Repair armor with fiber']
                self.window.add_child(Menu.make_button(text, click(fiber, self.host.armor), rmb_fiber, width=320))
            if self.host.is_headgeared():
                text = ['Repair headgear with fiber']
                self.window.add_child(Menu.make_button(text, click(fiber, self.host.headgear), rmb_fiber, width=320))
        else:
            text = ['Cannot repair without fiber']
            button = Menu.make_button(text, None, rmb_fiber, color=Window.fore_color0, hover=False, width=320)
            self.window.add_child(button)
