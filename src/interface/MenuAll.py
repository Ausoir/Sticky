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
            self.var = [Dialog.get('Empty')]
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
                Global.main.monologue.set(Dialog.get(':transacted'))
        host = self.var
        host.load_content()
        if not host.inventory.items:
            self.var = [Dialog.get(':soldout')]
            self.menu_message()
        else:
            count = 0
            Global.r_t.reset(host.get_seed() + 333)
            personality = host.tags.get('cost', 0)
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
                Global.main.monologue.set(Dialog.get(':transacted'))
            else:
                Global.main.monologue.set(Dialog.get(':reqnotmet'))
        host = self.var
        host.load_content()
        if host.inventory.items:
            seed = host.get_seed()
            Global.r_t.reset(seed + 777 + Global.player.days)
            personality = host.tags.get('cost', 0)
            for k in range(min(6, len(host.inventory.items))):
                item = host.inventory.get_item(k)
                if item:
                    value = max(1, item.get_value() + personality + Global.r_t.rand_int(0, item.get_value() * 2))
                    param = [item.name, value, k]
                    lmb = self.get_prompt(Dialog.get(':supply', param), Dialog.get('Sell'), buy, param)
                    self.window.add(Menu.make(item.name, lmb))
                    self.sub_window.add(Menu.make('$' + str(value), lmb, color=None))
            self.sub_window.display(1)
        else:
            self.get_message(Dialog.get('!supply'))()

    def menu_pawn(self):
        def pawn(arg):
            if Global.player.character.weapon == arg[0]:
                Global.player.character.drop().remove()
                Global.player.character.tags.increment('money', arg[1])
                Global.main.monologue.set(Dialog.get(':pawned', [arg[1]]))
                host.tags.set('#', '!pawnbroker2')
            else:
                Global.main.monologue.set(Dialog.get(':reqnotmet'))
        host = self.var
        item = Global.player.character.weapon
        if item and item.get_value() > 1:
            Global.r_t.reset(host.get_seed() + 7711 + Global.player.days)
            personality = host.tags.get('cost', 0)
            value = max(1, item.get_value() + personality + Global.r_t.rand_int(0, item.get_value()))
            param = [item, value]
            self.history.pop()
            self.get_prompt(Dialog.get(':pawn', [item.get_display_name()]), Dialog.get('Pawn'), pawn, param)()
            self.sub_window.display(1)
        else:
            self.history.pop()
            self.get_message(Dialog.get('!pawn'))()

    def menu_store_item(self):
        # noinspection PyUnresolvedReferences
        def store(arg):
            if Global.player.pay(cost):
                host.tags.set('$', 0)
                storing = Global.player.character.drop()
                host.inventory.attempt_add(storing)
                Global.main.monologue.set(Dialog.get(':transacted'))
        item = Global.player.character.weapon
        host = self.var
        host.load_content()
        if not item:
            self.var = [Dialog.get(':store_nothing')]
            self.menu_message()
        elif not host.is_vacant(item.get_weight()):
            self.var = [Dialog.get(':invfull')]
            self.menu_message()
        else:
            count = 0
            Global.r_t.reset(host.get_seed() + 333)
            cost = host.tags.get('cost', 0) + Global.r_t.rand_int(0, item.get_value())
            message = item.describe() + '\n' + Dialog.get(':store_item', [cost])
            self.history.pop()
            self.get_prompt(message, Dialog.get('Store'), store, count)()

    def menu_invest(self):
        # noinspection PyUnresolvedReferences
        def store(arg):
            if Global.player.pay(cost):
                Global.player.tags.increment('invest', cost)
                Global.player.tags.set('investt', Global.player.days % 24)
                Global.main.monologue.set(Dialog.get(':transacted'))
        cost = (self.var.get_seed() % 7 + 1) * self.var.tags.get('cost')
        text = Dialog.get(':invest', [cost, Global.player.tags.get('invest', 0)])
        self.var.tags.set('#', '!banker2')
        self.history.pop()
        self.get_prompt(text, Dialog.get('Store'), store, 0)()

    def menu_insure(self):
        # noinspection PyUnresolvedReferences
        def insure(arg):
            if not Global.player.character.is_hungry():
                if Global.player.pay(cost) and Global.player.try_sleep(1):
                    host.tags.increment('cost', 2)
                    player.states.add('Revive', -1)
                    Global.main.monologue.set(Dialog.get(':transacted'))
                    Global.player.tags.set('brained', 1)
            else:
                Global.main.monologue.set(Dialog.get('!eat'))

        def cancel(arg):
            revival.end()
            Global.main.monologue.set(Dialog.get(':transacted'))

        host = self.var
        player = Global.player.character
        revival = player.states.get('Revive')
        if revival:
            self.history.pop()
            self.get_prompt(Dialog.get(':insurecancel?'), Dialog.get('Cancel'), cancel)()
        else:
            cost = host.tags.get('cost', 0)
            self.history.pop()
            self.get_prompt(Dialog.get(':insure?', [cost]), Dialog.get('Insure'), insure)()

    def menu_hire(self):
        # noinspection PyUnresolvedReferences
        def hire(arg):
            if Global.player.is_sociable(1) and Global.player.pay(cost):
                from src.game.ScriptManual import ScriptManual
                ScriptManual.ally(Global.player.character, host)
        host = self.var
        cost = host.tags.get('cost', 0)
        self.history.pop()
        self.get_prompt(Dialog.get(':hire?', [cost]), Dialog.get('Hire'), hire)()

    def menu_order(self):
        def order(arg):
            host.tags.remove('tgt')
            if arg == 1:
                host.face_toward(Global.player.character.pos)
                from src.game.ScriptManual import ScriptManual
                ScriptManual.swap(Global.player.character, host)
            elif arg == 2:
                host.pilot.load('guard')
            elif arg == 3:
                host.pilot.load('ally')
            elif arg == 4:
                host.action.set('grab')
            elif arg == 5:
                Global.player.companions.append(host.__str__())
                Global.main.monologue.set(Dialog.get(':companion', [host.get_display_name()]))
                host.remove()
            elif arg == 6:
                host.tags.remove('ai')
                host.tags.set('!', '#uncontrol')
                old_host = Global.player.character
                old_host.tags.set('#', 'reclaim')
                Global.player.set_player(host)
                Global.player.companions.append(old_host.__str__())
                old_host.remove()
            self.display(-1)
        host = self.var
        host.face_toward(Global.player.character.pos)
        self.window.add(Menu.make(Dialog.get('Swap'), order, name=1, width=320))
        self.window.add(Menu.make(Dialog.get('Guard'), order, name=2, width=320))
        if Global.player.is_sociable(0):
            self.window.add(Menu.make(Dialog.get('Follow'), order, name=3, width=320))
            from src.entity.unit.Humanoid import Humanoid
            if isinstance(host, Humanoid):
                self.window.add(Menu.make(Dialog.get('Wield'), order, name=4, width=320))
        else:
            self.window.add(Menu.make(Dialog.get('Cannot Follow'), None, width=320, color=None))
        if Global.player.is_sociable(1, notice=False):
            self.window.add(Menu.make(Dialog.get('Join'), order, name=5, width=320))
        else:
            self.window.add(Menu.make(Dialog.get('Cannot Join'), None, width=320, color=None))
        if Global.player.is_sociable(host.get_level(), notice=False):
            self.window.add(Menu.make(Dialog.get('Control'), order, name=6, width=320))
        else:
            self.window.add(Menu.make(Dialog.get('Cannot Control'), None, width=320, color=None))
        self.sub_window.display(1)

    def menu_learn(self):
        # noinspection PyUnresolvedReferences
        def learn(arg):
            if Global.player.is_learnable() and Global.player.pay(cost):
                Global.player.character.tags.set('ab' + str(count), ability)
                Global.main.monologue.set(Dialog.get(':transacted'))
        host = self.var
        cost = host.tags.get('cost2', 0)
        ability = host.tags.get('ab1')
        self.history.pop()
        if ability:
            threshold = host.get_level()
            if Global.player.character.get_level() >= threshold:
                if not Global.player.character.tags.get('ab1'):
                    count = 1
                elif not Global.player.character.tags.get('ab2'):
                    count = 2
                elif not Global.player.character.tags.get('ab3'):
                    count = 3
                else:
                    Global.main.monologue.set(Dialog.get('!learnfull'))
                    return
                self.get_prompt(Dialog.get(':learnab?', [ability, cost, count]), Dialog.get('Learn'), learn)()
            else:
                self.get_message(Dialog.get(':req_level', [threshold]))()
        else:
            self.get_message(Dialog.get('!learnab'))()

    def menu_transport(self):
        def transport(arg):
            if Global.player.pay(cost):
                Global.map_view.overlay.blackout()
                Global.world.travel(host.tags.get('tox'), host.tags.get('toy'))
        host = self.var
        cost = host.tags.get('cost', 0)
        self.history.pop()
        self.get_prompt(Dialog.get(':travel?', [host.tags.get('to'), cost]), Dialog.get('Proceed'), transport)()
