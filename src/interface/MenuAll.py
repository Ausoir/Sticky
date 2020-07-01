from src.entity.unit.Humanoid import Humanoid
from src.game import Global
from src.interface.Menu import Menu
from src.interface.MenuPlayer import MenuPlayer
from src.tools.Dialog import Dialog


class MenuAll(MenuPlayer):
    # noinspection PyUnresolvedReferences
    def menu_container(self):
        # noinspection PyUnresolvedReferences
        def buy(arg):
            sold = host.inventory.take_item(arg)
            Global.player.character.pick_up(sold)
        if isinstance(self.var, Humanoid):
            host = self.var
            have = host.tags.remove('have', 0)
            if have > 0:
                loots = []
                for i in range(have):
                    loot = host.get_loot()
                    if loot:
                        loots.append('?' + loot)
                host.inventory.load(loots)
            if not host.inventory.items:
                self.var = [Dialog.get('empty')]
                self.menu_message()
            else:
                for i in host.inventory.get_range():
                    item = host.inventory.get_item(i)
                    lmb = self.get_prompt(item.describe(), Dialog.get('Take'), buy, i)
                    self.window.add(Menu.make(item.get_display_name(), lmb))
                self.sub_window.display(1)

    # noinspection PyUnresolvedReferences
    def menu_shop(self):
        # noinspection PyUnresolvedReferences
        def buy(arg):
            if Global.player.pay(arg[1]):
                sold = host.inventory.take_item(arg[0])
                Global.player.character.pick_up(sold)
        if isinstance(self.var, Humanoid):
            host = self.var
            if not host.inventory.items:
                self.var = [Dialog.get('soldout')]
                self.menu_message()
            else:
                count = 0
                Global.r_t.reset(host.tags.get('seed', 0) + 333)
                personality = Global.r_t.rand_int(0, 2)
                for item_num in range(min(6, len(host.inventory.items))):
                    item = host.inventory.get_item(item_num)
                    value = max(1, item.get_value() + personality + Global.r_t.rand_int(0, item.get_value()))
                    lmb = self.get_prompt(item.describe(), Dialog.get('Buy'), buy, [count, value])
                    self.window.add(Menu.make(item.get_display_name(), lmb))
                    self.sub_window.add(Menu.make('$' + str(value), lmb, color=None))
                    count += 1
                self.sub_window.display(1)

    def menu_supply(self):
        def buy(arg):
            subjects = Global.player.character.get_accessibles()
            receipt = 0
            for i in subjects:
                if i.name == arg[0]:
                    i.remove()
                    receipt += arg[1]
            if receipt > 0:
                Global.player.character.tags.increment('money', receipt)
                self.get_message(Dialog.get('supply_success', [receipt]))()
            else:
                self.get_message(Dialog.get('supply_fail', [arg[0]]))()
        if isinstance(self.var, Humanoid):
            host = self.var
            if isinstance(host, Humanoid):
                items = []
                day = int(Global.player.days / 24)
                Global.r_t.reset(host.tags.get('seed', 0) + 777 + day)
                personality = Global.r_t.rand_int(0, 1)
                for k, item in enumerate(host.inventory.items):
                    value = max(0, item.get_value() + personality + Global.r_t.rand_int(0, 1))
                    param = [item.name, value]
                    select = self.get_prompt(Dialog.get('supply', param), Dialog.get('Sell'), buy, param)
                    items.append([item.name, select])
                if items:
                    self.var = items
                    self.direct(self.menu_many_choice)
                else:
                    self.get_message(Dialog.get('!supply'))()

    def menu_contract(self):
        def proceed(arg):
            Global.player.tags.set('quest', arg)
            from src.game.Script import Script
            Script.var['1'] = 'data/map/quest/' + str(arg)
            self.execute_code('quest')
        if isinstance(self.var, Humanoid):
            quest = Global.player.tags.remove('quest', default=0)
            if quest == 999:
                self.load('contract_success')
            elif quest > 0:
                self.load('contract_fail')
            else:
                host = self.var
                day = int(Global.player.days / 36)
                Global.r_t.reset(host.tags.get('seed', 0) + 2000 + day)
                mission = Global.r_t.rand_int(1, 1)
                self.var = [Dialog.get('contract' + str(mission)), Dialog.get('Accept'), proceed, mission]
                self.menu_prompt()

    def menu_storage(self):
        def proceed(arg):
            Global.main.monologue.set('FAR')
        import math
        mission = int(math.sin(Global.player.days + self.var[0].attributes.gene) * 10) % 3 + 1
        reward = 40
        self.var = [Dialog.get('sergentquest' + str(mission), [reward]),
                    [Dialog.get('Proceed')], [proceed]]
        self.state = self.menu_many_choice
        self.display(1)
