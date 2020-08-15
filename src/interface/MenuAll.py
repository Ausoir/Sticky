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
        host.load_content()
        if not host.inventory.items:
            self.var = [Dialog.get('empty')]
            self.menu_message()
        else:
            for i in host.inventory.get_range():
                item = host.inventory.get_item(i)
                if item:
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
        host.load_content()
        if not host.inventory.items:
            self.var = [Dialog.get('soldout')]
            self.menu_message()
        else:
            count = 0
            Global.r_t.reset(host.get_seed() + 333)
            personality = Global.r_t.rand_int(0, 2)
            for item_num in range(min(6, len(host.inventory.items))):
                item = host.inventory.get_item(item_num)
                if item:
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
                host.inventory.take_item(arg[2]).remove()
                Global.player.character.tags.increment('money', receipt)
                Global.main.monologue.set(Dialog.get('transacted'))
            else:
                Global.main.monologue.set(Dialog.get('reqnotmet'))
        host = self.var
        host.load_content()
        if host.inventory.items:
            seed = host.get_seed()
            Global.r_t.reset(seed + 777 + Global.player.days)
            personality = seed % 2
            for k in range(min(6, len(host.inventory.items))):
                item = host.inventory.get_item(k)
                if item:
                    value = max(1, item.get_value() + personality + Global.r_t.rand_int(0, 1))
                    param = [item.name, value, k]
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
        item = Global.player.character.weapon
        host = self.var
        host.load_content()
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
            self.history.pop()
            self.get_prompt(message, Dialog.get('Store'), store, count)()

    def menu_invest(self):
        # noinspection PyUnresolvedReferences
        def store(arg):
            if Global.player.pay(cost):
                Global.player.character.tags.increment('invest', cost)
                Global.player.character.tags.set('investt', Global.player.days % 24)
                Global.main.monologue.set(Dialog.get('transacted'))
        Global.r_t.reset(self.var.get_seed() + 777)
        cost = Global.r_t.rand_int(7, 35)
        text = Dialog.get('invest', [cost, Global.player.character.tags.get('invest', 0)])
        self.var.tags.set('#', '!banker2')
        self.history.pop()
        self.get_prompt(text, Dialog.get('Store'), store, 0)()

    def menu_insure(self):
        # noinspection PyUnresolvedReferences
        def insure(arg):
            if Global.player.pay(cost):
                player.states.add('Revive', duration)
                Global.main.monologue.set(Dialog.get('transacted'))
        host = self.var
        player = Global.player.character
        cost = (host.get_seed() % 4 + 1) * host.get_value() + player.get_level()
        from src.game.Turn import Turn
        duration = (host.get_seed() % 168 + 1) * Turn.HOUR_FRAME
        self.history.pop()
        self.get_prompt(Dialog.get('insure?', [cost, int(duration / Turn.HOUR_FRAME)]), Dialog.get('Insure'), insure)()

    def menu_hire(self):
        # noinspection PyUnresolvedReferences
        def hire(arg):
            if Global.player.pay(cost):
                from src.game.ScriptManual import ScriptManual
                ScriptManual.ally(Global.player.character, host)
        host = self.var
        cost = (host.get_seed() % 5 + 1) * host.get_value()
        self.history.pop()
        self.get_prompt(Dialog.get('hire?', [cost]), Dialog.get('Hire'), hire)()

    def menu_order(self):
        def order(arg):
            if arg == 1:
                host.face_toward(Global.player.character.pos)
                from src.game.ScriptManual import ScriptManual
                ScriptManual.swap(Global.player.character, host)
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
        if Global.player.is_sociable():
            self.window.add(Menu.make(Dialog.get('Follow'), order, name=3, width=320))
            self.window.add(Menu.make(Dialog.get('Wield'), order, name=4, width=320))
        self.sub_window.display(1)

    def menu_victory(self):
        datetime = Dialog.date(Global.player.days)
        self.get_message(Dialog.get('dsc_victory', [datetime]))()
        self.sub_window.display(1)
        Global.player.dead = 11
