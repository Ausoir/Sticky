from src.entity.unit.Humanoid import Humanoid
from src.game import Global
from src.interface.Menu import Menu
from src.interface.MenuPlayer import MenuPlayer
from src.tools.Dialog import Dialog


class MenuAll(MenuPlayer):
    # noinspection PyUnresolvedReferences
    def menu_container(self):
        # noinspection PyUnresolvedReferences
        def retrieve(arg):
            sold = host.inventory.take_item(arg)
            Global.player.character.pick_up(sold)
        host = self.var
        have = host.tags.remove('have', 0)
        if have > 0:
            loots = []
            for i in range(have):
                loot = host.get_loot()
                if loot:
                    loots.append('?' + loot)
            host.inventory.load(loots)
            host.tags.remove('loot')
        if not host.inventory.items:
            self.var = [Dialog.get('empty')]
            self.menu_message()
        else:
            for i in host.inventory.get_range():
                item = host.inventory.get_item(i)
                lmb = self.get_prompt(item.describe(), Dialog.get('Take'), retrieve, i)
                self.window.add(Menu.make(item.get_display_name(), lmb))
            self.sub_window.display(1)

    # noinspection PyUnresolvedReferences
    def menu_shop(self):
        # noinspection PyUnresolvedReferences
        def buy(arg):
            if Global.player.pay(arg[1]):
                sold = host.inventory.take_item(arg[0])
                Global.player.character.pick_up(sold)
                Global.main.monologue.set(Dialog.get('transacted'))
        host = self.var
        if not host.inventory.items:
            self.var = [Dialog.get('soldout')]
            self.menu_message()
        else:
            count = 0
            Global.r_t.reset(host.get_seed() + 333)
            personality = Global.r_t.rand_int(0, 2)
            for item_num in range(min(6, len(host.inventory.items))):
                item = host.inventory.get_item(item_num)
                value = max(1, item.get_value() + personality + Global.r_t.rand_int(0, item.get_value()))
                lmb = self.get_prompt(item.describe(), Dialog.get('Buy'), buy, [count, value])
                self.window.add(Menu.make(item.name, lmb))
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
                Global.main.monologue.set(Dialog.get('transacted'))
            else:
                Global.main.monologue.set(Dialog.get('reqnotmet'))
        if isinstance(self.var, Humanoid):
            host = self.var
            if isinstance(host, Humanoid):
                if host.inventory.items:
                    seed = host.get_seed()
                    Global.r_t.reset(seed + 777 + Global.player.days)
                    personality = seed % 3
                    for k in range(min(6, len(host.inventory.items))):
                        item = host.inventory.get_item(k)
                        value = max(0, item.get_value() + personality + Global.r_t.rand_int(0, 2))
                        param = [item.name, value]
                        lmb = self.get_prompt(Dialog.get('supply', param), Dialog.get('Sell'), buy, param)
                        self.window.add(Menu.make(item.name, lmb))
                        self.sub_window.add(Menu.make('$' + str(value), lmb, color=None))
                    self.sub_window.display(1)
                else:
                    self.get_message(Dialog.get('!supply'))()

    def menu_store_item(self):
        # noinspection PyUnresolvedReferences
        def store(arg):
            if Global.player.pay(cost):
                host.tags.set('$', 1)
                storing = Global.player.character.drop()
                host.inventory.attempt_add(storing)
                Global.main.monologue.set(Dialog.get('transacted'))
        if isinstance(self.var, Humanoid):
            item = Global.player.character.weapon
            host = self.var
            if not item:
                self.var = [Dialog.get('store_nothing')]
                self.menu_message()
            elif not host.is_vacant(item.get_weight()):
                self.var = [Dialog.get('invfull')]
                self.menu_message()
            else:
                count = 0
                Global.r_t.reset(host.get_seed() + 333)
                personality = Global.r_t.rand_int(0, 2)
                cost = max(1, item.get_value() + personality + Global.r_t.rand_int(0, item.get_value()))
                message = item.describe() + '\n' + Dialog.get('store_item', [cost])
                self.get_prompt(message, Dialog.get('Store'), store, count)()

    def menu_train(self):
        # noinspection PyUnresolvedReferences
        def train(arg):
            if Global.player.pay(cost):
                Global.player.character.tags.increment('lvl', 1)
                Global.player.character.tags.increment(stat[1], stat[2])
                Global.main.monologue.set(Dialog.get('transacted'))
        cost = Global.player.character.tags.get('lvl', 0) ** 2
        from src.tools.Data import Data
        raw = Data.get_line('raw.txt', 'stat')[1]
        stat = raw[self.var.get_seed() % len(raw)]
        data = Data.get_line('descriptions.txt', stat[0])
        name = stat[0].title()
        if data:
            message = data[0] + '\n' + Dialog.get('train', [name])
        else:
            message = Dialog.get('train', [name, cost])
        self.get_prompt(message, Dialog.get('Train') + ' ' + name, train)()

    def menu_hire(self):
        # noinspection PyUnresolvedReferences
        def hire(arg):
            if Global.player.pay(cost):
                host.tags.set('team', Global.player.character.tags.get('team', 0))
                host.pilot.load('ally')
                host.tags.set('#', '>menu>order')
        host = self.var
        cost = host.get_seed() % 8 + 2
        self.get_prompt(Dialog.get('hire?', [cost]), Dialog.get('Hire'), hire)()

    def menu_order(self):
        def order(arg):
            if arg == 1:
                host.face_toward(Global.player.character.pos)
                from src.game.ScriptManual import ScriptManual
                ScriptManual.push(Global.player.character, host)
            elif arg == 2:
                host.tags.remove('tgt')
                host.pilot.load('guard')
            elif arg == 3:
                host.tags.remove('tgt')
                host.pilot.load('ally')
            elif arg == 4:
                host.action.set('grab')
            self.display(-1)
        host = self.var
        host.face_toward(Global.player.character.pos)
        self.window.add(Menu.make(Dialog.get('Swap'), order, name=1, width=320))
        self.window.add(Menu.make(Dialog.get('Guard'), order, name=2, width=320))
        self.window.add(Menu.make(Dialog.get('Follow'), order, name=3, width=320))
        self.window.add(Menu.make(Dialog.get('Wield'), order, name=4, width=320))
        self.sub_window.display(1)
