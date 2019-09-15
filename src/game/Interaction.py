from src.game import Global
from src.game.Tags import Tags


class Interaction:
    @staticmethod
    def trigger(tile):
        targets = []
        for thing in tile.things:
            if Tags.interactive in thing.tags:
                targets.append(thing)
        if targets:
            if len(targets) > 1:
                arg2 = []
                arg3 = []
                for i in targets:
                    arg2.append(i.name)
                    arg3.append(lambda x: Interaction.interact(targets[x]))
                Global.menu.var = ['There are more than one possible interactions at this position. Choose one.',
                                   arg2, arg3]
                Global.player.menu(Global.menu.menu_choice)
                return True
            else:
                return Interaction.interact(targets[0])

    @staticmethod
    def interact(target):  # mass interaction substitute for Other class
        if target.name == 'Interactive':
            target.trigger()
        elif target.name == 'Table':
            if Global.player.is_safe() and Global.player.is_bright():
                from src.tools.Data import Data
                products = Data.get_line('data/raw/raw.txt', 'basic_craft')[1]
                Global.menu.var = products
                Global.player.menu(Global.menu.menu_craft)
        elif target.name == 'Desk':
            if Global.player.is_safe() and Global.player.is_bright():
                from src.tools.Data import Data
                Global.menu.var = Global.player.knowledge
                Global.player.menu(Global.menu.menu_craft)
        elif target.name == 'Disassembler':
            def disassemble(arg):
                disassembled = Global.player.character.weapon.spell
                if disassembled not in Global.player.knowledge:
                    Global.player.knowledge.append(disassembled)
                    Global.player.monologue.text('Learned [' + disassembled + ']!')
                    Global.player.character.weapon.die()
                else:
                    Global.player.monologue.text('[' + disassembled + '] is already known.')
            from src.entity.unit.item.Spell import Spell
            if isinstance(Global.player.character.weapon, Spell):
                if Global.player.is_safe() and Global.player.is_bright():
                    Global.menu.var = ['Disassemble ' + Global.player.character.weapon.get_display_name() + '?',
                                       ['Yes'], [disassemble]]
                    Global.player.menu(Global.menu.menu_choice)
            else:
                Global.player.monologue.text('Only spells can be disassembled at this table.')
        elif target.name in ['Bed', 'Sofa']:
            if Global.player.is_safe() and Global.player.eat():
                Global.player.character.attributes.rest()
                Global.main.colorize(0, [0, 0, 0, 255], fade=2)
                Global.player.sleep(1)
        elif target.name == 'Anvil':
            if Global.player.is_safe() and Global.player.is_bright():
                Global.player.menu(Global.menu.menu_anvil)
        elif Tags.intelligent in target.tags and target.faction == Global.player.character.faction:
            from src.entity.Stock import Stock
            Global.menu.var = [target]
            Global.player.menu(Global.menu.menu_conversation)
        elif target.name == 'Food':
            hunger = target.host.states.get('Hunger')
            if hunger:
                hunger.end()
                target.host.action.set('wait')
                target.hit(1)
            else:
                target.use()
        elif target.name == 'Pockets':
            if target.host.is_armored():
                used = False
                if target.host.armor.inventory[3][0] == 1:
                    target.host.armor.inventory[3][0] = 2
                    used = True
                if target.host.armor.inventory[3][2] == 1:
                    target.host.armor.inventory[3][2] = 2
                    used = True
                if used:
                    target.host.action.set('wait')
                    target.die()
        elif target.name == 'Backpack':
            if target.host.is_armored():
                if target.host.armor.inventory[1][1] == 1:
                    target.host.armor.inventory[1][1] = 2
                    target.host.action.set('wait')
                    target.die()
        elif target.name == 'Bottle':
            from src.entity.Stock import Stock
            for thing in target.pos.things:
                if thing.name in ['Water', 'Surface']:
                    target.die()
                    Stock.make('Water Bottle', target.pos)
                    break
            return False
        elif target.name == 'Artifact Pouch':
            from src.entity.Stock import Stock
            from src.tools.Data import Data
            spell = Global.r.rand_list(Data.process_raw(Data.read('data/raw/spells.txt')))
            Stock.make(spell[0], target.pos)
            target.die()
        elif target.name == 'Bow':
            target.hit(1)
            if target.durability > 1:
                target.host.action.set('arch')
            else:
                return False
        elif target.name == 'Medicine':
            status = target.host.states.get('Sick')
            if status:
                status.trigger(['remove'])
                target.die()
        elif target.name == 'Sampler':
            for thing in target.host.pos.things:
                if thing != target.host:
                    target.tags = thing.tags
                    break
        elif target.name == 'Jelly':
            status = target.host.states.get('Sick')
            if status:
                status.duration += 100
                target.die()
        elif target.name == 'Cleansing Potion':
            seed = (target.host.attributes.gene + Global.player.days) % 3
            if seed == 0:
                target.host.attributes.strength = max(target.host.attributes.strength + 1, 3)
            elif seed == 1:
                target.host.attributes.agility = max(target.host.attributes.agility + 1, 3)
            elif seed == 2:
                target.host.attributes.intelligence = max(target.host.attributes.intelligence + 1, 3)
        else:
            return False
        return True

    @staticmethod
    def talk(target):
        target.face(1 if Global.player.character.pos.x > target.pos.x else -1)
        if target.var['business'] == 'Beg':
            Global.menu.var = [target]
            Global.menu.state = Global.menu.menu_beg
            Global.menu.history.append(Global.menu.state)
            Global.menu.history_var.append(Global.menu.var)
            Global.player.menu(Global.menu.menu_beg)
        elif target.var['business'] == 'Trade':
            if Global.player.days > target.var['due']:
                from src.tools.Random import Random
                from src.tools.Data import Data
                rng = Random(target.attributes.gene + Global.player.days)
                due_date = Global.player.days + (target.attributes.gene % 14) + 6
                data = Data.get_line('data/raw/trade.txt', target.var['trade'])
                merchandise = []
                for i in range(rng.rand_int(3, 6)):
                    merchandise.append(rng.rand_list(data[1]))
                target.var['item'] = '&'.join(merchandise)
                target.var['due'] = due_date
            from src.entity.Stock import Stock
            Global.menu.var = [target, target.attributes.gene % 2,
                               [Stock.get(i) for i in target.var['item'].split('&')]]
            Global.menu.history.append(Global.menu.state)
            Global.menu.history_var.append(Global.menu.var)
            Global.player.menu(Global.menu.menu_shop)
        elif target.var['business'] == 'Train':
            Global.menu.var = [target]
            Global.menu.history.append(Global.menu.state)
            Global.menu.history_var.append(Global.menu.var)
            Global.player.menu(Global.menu.menu_trainer)
        elif target.var['business'] == 'Sell':
            if Global.player.days > target.var['due']:
                from src.tools.Data import Data
                from src.tools.Random import Random
                from src.entity.Stock import Stock
                data = Data.get_line('data/raw/trade.txt', 'host')
                rng = Random(target.attributes.gene + Global.player.days)
                due_date = Global.player.days + rng.rand_int(1, 3)
                value = Stock.get(rng.rand_list(data[1])).get_value()
                target.var['due'] = due_date
                target.var['item'] = rng.rand_list(data[1])
                target.var['amount'] = 1
                target.var['value'] = value + 1
            Global.menu.var = [target]
            Global.menu.state = Global.menu.menu_guild
            Global.menu.history.append(Global.menu.state)
            Global.menu.history_var.append(Global.menu.var)
            Global.menu.display(1)
        elif target.var['business'] == 'Supply':
            if Global.player.days > target.var['due']:
                from src.tools.Data import Data
                from src.tools.Random import Random
                from src.entity.Stock import Stock
                data = Data.get_line('data/raw/trade.txt', 'guild')
                rng = Random(target.attributes.gene + Global.player.days)
                due_date = Global.player.days + rng.rand_int(2, 5)
                value = Stock.get(rng.rand_list(data[1])).get_value()
                target.var['due'] = due_date
                target.var['item'] = rng.rand_list(data[1])
                target.var['amount'] = rng.rand_int(1, 7)
                target.var['value'] = rng.rand_int(1, 3) * value
            Global.menu.var = [target]
            Global.menu.history.append(Global.menu.state)
            Global.menu.history_var.append(Global.menu.var)
            Global.player.menu(Global.menu.menu_guild)
        elif target.var['business'] == 'Sell Scrap':
            if Global.player.days > target.var['due']:
                from src.entity.Stock import Stock
                target.var['due'] = Global.player.days + 1
                target.var['item'] = 'Scrap'
                target.var['amount'] = 1
                target.var['value'] = 1
            Global.menu.var = [target]
            Global.menu.state = Global.menu.menu_guild
            Global.menu.display(1)
        elif target.var['business'] == 'Insurance':
            from src.tools.Random import Random
            from src.entity.Stock import Stock
            target.var['time'] = (target.attributes.gene % 21 + 7) * 2
            target.var['value'] = int(target.var['time'] / 2) + (target.attributes.gene % 8)
            Global.menu.var = [target]
            Global.menu.history.append(Global.menu.state)
            Global.menu.history_var.append(Global.menu.var)
            Global.player.menu(Global.menu.menu_insurance)
        elif target.var['business'] == 'Inn':
            def set_home(arg):
                if target.location.name != 'home':
                    if Global.player.pay(target.var['value']):
                        target.location.name = 'home'
                else:
                    Global.player.monologue.text('This region is already your home.')
            Global.menu.var = ['Would you like to set this place as home for ' + target.var['value'] + ' gold?',
                               ['Set home'], [set_home]]
            Global.player.menu(Global.menu.menu_choice)
        elif target.var['business'] == 'Enter':
            def gold(arg):
                if Global.player.pay(cost):
                    from src.entity.Space import Space
                    Global.player.travel(target.location.name, Space(int(dest[0]), int(dest[1])))

            def gift(arg):
                for possession in Global.player.character.get_accessibles():
                    if possession.name == item:
                        possession.die()
                        from src.entity.Space import Space
                        Global.player.travel(target.location.name, Space(int(dest[0]), int(dest[1])))
                        return
                Global.player.monologue.text('No item...')
            cost = target.var['value']
            item = target.var['item']
            dest = target.var['destination'].split('&')[1:]
            Global.menu.var = ['You cannot enter empty handed. Pay ' + str(cost) + ' Gold or bring ' + item + '.',
                               ['Pay Gold', 'Give ' + item], [gold, gift]]
            Global.player.menu(Global.menu.menu_choice)
