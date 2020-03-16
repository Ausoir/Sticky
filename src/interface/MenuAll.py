from src.game import Global
from src.interface.Menu import Menu
from src.interface.MenuPlayer import MenuPlayer
from src.interface.Window import Window
from src.tools.Dialog import Dialog


class MenuAll(MenuPlayer):
    def menu_shop(self):
        from src.entity.unit.Humanoid import Humanoid
        if isinstance(self.var, Humanoid):
            host = self.var

            def buy(index):
                appraise = host.inventory.items[index].get_value() + int(host.tags.get('seed', 0) % 2)
                if Global.player.pay(appraise):
                    sold = host.inventory.get_item(index)
                    sold.relocate(Global.player.character.pos.x, Global.player.character.pos.y, force=1)
                    sold.add()
                self.toggle()
            if not host.inventory.items:
                self.get_message(Dialog.get('soldout'))(None)
            else:
                count = 0
                for item in host.inventory.items:
                    money = '$' + str(item.get_value() + int(host.tags.get('seed', 0) % 2))
                    lmb = self.get_prompt(item.describe(), Dialog.get('buy'), buy, count)
                    self.window.add(Menu.make(item.name, lmb))
                    self.sub_window.add(Menu.make(money, lmb, color=None))
                    count += 1
                self.sub_window.display(1)

    def menu_pawn(self):
        def buy(index):
            Global.player.character.tags.increment('money', 1, add=True)
            wpn.remove()
            self.toggle()
        from src.tools.Data import Data
        data = Data.get_line('raw.txt', 'pawn')
        if Global.player.character.weapon and Global.player.character.weapon.name in data[1]:
            wpn = Global.player.character.weapon
            self.get_prompt(Dialog.get('?pawn', [wpn.name]), Dialog.get('buy'), buy, 0)(None)
        else:
            self.get_message(Dialog.get('xpawn', [', '.join(data[1])]))(None)

    def menu_provide(self):
        def buy(index):
            Global.player.character.tags['money'] += 1
            wpn.remove()
            self.toggle()
        from src.tools.Data import Data
        data = Data.get_line('raw.txt', 'pawn')
        if Global.player.character.weapon and Global.player.character.weapon.name in data[1]:
            wpn = Global.player.character.weapon
            self.get_prompt(Dialog.get('?pawn', [wpn]), Dialog.get('buy'), buy, 0)()
        else:
            self.get_message(Dialog.get('xpawn', [', '.join(data[1])]))()

    def menu_quest(self):
        def proceed(arg):
            Global.main.monologue.set('FAR')
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
                Global.main.monologue.set(Dialog.get('treated'))
        self.var = [Dialog.get('treated', [self.var[0].tags['value']]), [Dialog.get('Cure')], [treat]]
        self.state = self.menu_choice
        self.display(1)

    def menu_insurance(self):
        contract = Global.player.character.states.get('Revive')
        if not contract:
            def package(arg):
                if Global.player.character.require_var('money', value):
                    Global.player.character.states.add('Revive', -1, 'Insurance')
                    Global.main.monologue.set(Dialog.get('insurebought'))
                    tgt.var['record'] += 1
                    self.toggle()
            text = []
            tgt = self.var[0]
            value = int(self.var[0].attributes.gene % 9 + 4) + (tgt.tags['record'] * tgt.tags['inc'])
            text.append(Dialog.get('dsc_insurance', [str(value)]))
            panel = Menu.make(text, None, None, color=Window.fore_color_transparent, width=320, resize=True)
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
