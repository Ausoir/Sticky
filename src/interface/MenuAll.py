from src.game import Global
from src.interface.Menu import Menu
from src.interface.MenuPlayer import MenuPlayer
from src.interface.Window import Window
from src.tools.Dialog import Dialog


class MenuAll(MenuPlayer):
    def menu_search(self):
        def buy(index):
            appraise = host.inventory.items[index].get_value() + int(host.attributes.gene % 2)
            if Global.player.character.require_var('money', appraise):
                sold = host.inventory.get_item(index)
                sold.relocate(Global.player.character.pos.x, Global.player.character.pos.y, force=1)
                sold.add()
            self.toggle()
        loot = self.var[0].tags.get('loot')
        if loot:
            if loot.startswith('#'):
                from src.entity.Stock import Stock
                from src.tools.Data import Data
                loot = Global.r.rand_list(Data.get_line('raw/trade.txt', loot[1:])[1])
                self.var[0].tags.set('loot', loot)
            from src.entity.Stock import Stock
            count = 0
            for item in host.inventory.items:
                money = '$' + str(item.get_value() + int(host.attributes.gene % 2))
                lmb = self.get_prompt(item.describe(), Dialog.get('buy'), buy, count)
                self.window.add(Menu.make(item.name, lmb))
                self.sub_window.add(Menu.make(money, lmb, color=None, hover=False))
                count += 1
            self.sub_window.display(1)

    def menu_shop(self):
        def buy(index):
            appraise = host.inventory.items[index].get_value() + int(host.attributes.gene % 2)
            if Global.player.character.require_var('money', appraise):
                sold = host.inventory.get_item(index)
                sold.relocate(Global.player.character.pos.x, Global.player.character.pos.y, force=1)
                sold.add()
            self.toggle()
        host = self.var[0]
        if not host.inventory.items:
            self.get_message(Dialog.get('soldout'))(None)
        else:
            from src.entity.Stock import Stock
            count = 0
            for item in host.inventory.items:
                money = '$' + str(item.get_value() + int(host.attributes.gene % 2))
                lmb = self.get_prompt(item.describe(), Dialog.get('buy'), buy, count)
                self.window.add(Menu.make(item.name, lmb))
                self.sub_window.add(Menu.make(money, lmb, color=None, hover=False))
                count += 1
            self.sub_window.display(1)

    def menu_pawn(self):
        def buy(index):
            Global.player.character.tags['money'] += 1
            wpn.remove()
            self.toggle()
        if Global.player.character.is_armed():
            wpn = Global.player.character.weapon
            self.get_prompt(Dialog.get('?pawn', [wpn]), Dialog.get('buy'), buy, 0)
        else:
            self.get_message(Dialog.get('xpawn', [', '.join(self.var[1])]))

    def menu_provide(self):
        if Global.player.days >= self.var[0].var['due']:
            from src.tools.Data import Data
            from src.tools.Random import Random
            from src.entity.Stock import Stock
            data = Data.get_line('raw/trade.txt', self.var[0].tags['type'])
            rng = Random(self.var[0].attributes.gene + Global.player.days)
            due_date = Global.player.days + rng.rand_int(2, 5)
            item = rng.rand_list(data[1])
            value = Stock.get(item).get_value()
            self.var[0].tags['due'] = due_date
            self.var[0].tags['item'] = item
            self.var[0].tags['amount'] = rng.rand_int(1, 7)
            self.var[0].tags['value'] = rng.rand_int(1, 8) + int(value * self.var[0].tags['amount'] * .7)
        self.state = self.menu_guild
        self.display(1)

    def menu_supply(self):
        if Global.player.days >= self.var[0].tags['due']:
            from src.entity.Stock import Stock
            self.var[0].tags['due'] = Global.player.days + self.var[0].tags['time']
            self.var[0].tags['amount'] = self.var[0].tags['need']
        self.state = self.menu_guild
        self.display(1)

    def menu_guild(self):
        if self.var[0].var['amount'] <= 0:
            dur = Dialog.day(self.var[0].var['due'] - Global.player.days)
            self.get_message(Dialog.get('dealeroff', [dur]))(None)
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
            if Global.player.character.require_var('money', self.var[0].tags['value']):
                from src.entity.unit.Buff import BuffTags
                Global.player.character.states.clear(lambda x: BuffTags.harmful in x.tags)
                self.toggle()
                Global.player.character.say(Dialog.get('treated'))
        self.var = [Dialog.get('treated', [self.var[0].tags['value']]), [Dialog.get('Cure')], [treat]]
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
                    self.toggle()
            text = []
            tgt = self.var[0]
            value = int(self.var[0].attributes.gene % 9 + 4) + (tgt.tags['record'] * tgt.tags['inc'])
            text.append(Dialog.get('dsc_insurance', [str(value)]))
            panel = Menu.make(text, None, None, color=Window.fore_color_transparent,
                              hover=False, width=320, resize=True)
            self.window.add(panel)
            self.window.next_y = self.window.size.y + self.window.vec.y - 40 - self.window.margin.y
            self.window.add(Menu.make(Dialog.get('insureyes', [str(value)]), package, None, width=320))
            self.sub_window.display(1)
            return
        else:
            self.get_message(Dialog.get('insurefull'))(None)

    def menu_mod_armor(self):
        def implement(arg):
            if self.host.armor.enhance(Global.r.rand_int(1, 100)):
                self.host.armor.modify(arg)
            self.toggle()
        text = Dialog.get('modchance', [self.host.armor.get_enhance_chance()])
        self.window.add(Menu.make(text, None, width=320, resize=True, color=Window.fore_color_transparent))
        items = self.host.get_accessibles()
        mods = [['Cloth', 'reinforce', implement],
                ['Plating', 'pad', implement],
                ['Tooth', 'refit', implement]]
        deny = self.get_message(['No materials...'])
        for i in items:
            for modification in mods:
                if i.name == modification[0]:
                    modification[2] = deny
        for modification in mods:
            dialog_text = modification[1] + 'with'
            desc = self.get_prompt(Dialog.get('dsc_' + dialog_text, [Dialog.get(modification[0])]),
                                   Dialog.get('proceed'), implement)
            self.window.add(Menu.make(Dialog.get(dialog_text, [Dialog.get(modification[0])]),
                                      desc, width=320, name=modification[1]))
        self.sub_window.display(1)
