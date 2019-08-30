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
                Global.menu.state = Global.menu.menu_choice
                Global.menu.display(1)
                return True
            else:
                return Interaction.interact(targets[0])

    @staticmethod
    def interact(target):  # mass interaction substitute for Other class
        if target.name == 'Interactive':
            target.trigger()
        elif target.name == 'Table':
            if Global.player.is_safe():
                from src.tools.Data import Data
                products = Data.get_line('data/raw/raw.txt', 'crafts')[1]
                Global.menu.var = products
                Global.menu.state = Global.menu.menu_craft
                Global.menu.display(1)
        elif target.name == 'Desk':
            if Global.player.is_safe():
                from src.tools.Data import Data
                products = Data.get_line('data/raw/raw.txt', 'writes')[1]
                craftables = []
                for i in products:
                    if i in Global.player.knowledge:
                        craftables.append(i)
                Global.menu.var = craftables
                Global.menu.state = Global.menu.menu_craft
                Global.menu.display(1)
        elif target.name in ['Bed', 'Sofa']:
            if Global.player.is_safe() and Global.player.eat():
                Global.player.character.attributes.rest()
                Global.main.colorize(0, [0, 0, 0, 255], fade=2)
                Global.player.sleep(1)
        elif target.name == 'Anvil':
            if Global.player.is_safe():
                Global.menu.state = Global.menu.menu_anvil
                Global.menu.display(1)
        elif Tags.intelligent in target.tags and target.faction == Global.player.character.faction:
            from src.entity.Stock import Stock
            Global.menu.var = [target]
            Global.menu.state = Global.menu.menu_conversation
            Global.menu.display(1)
        elif target.name == 'Food':
            hunger = target.host.states.get('Hunger')
            if hunger:
                hunger.end()
                target.host.action.set('block')
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
                    target.host.action.set('block')
                    target.die()
        elif target.name == 'Backpack':
            if target.host.is_armored():
                if target.host.armor.inventory[1][1] == 1:
                    target.host.armor.inventory[1][1] = 2
                    target.host.action.set('block')
                    target.die()
        elif target.name == 'Scroll Bag':
            from src.entity.Stock import Stock
            from src.tools.Data import Data
            spell = Global.r.rand_list(Data.process_raw(Data.read('data/raw/spells.txt')))
            Stock.make(spell[0], target.pos)
            target.die()
        elif target.name == 'Bow':
            target.hit(1)
            if target.durability > 0:
                target.host.action.set('arch')
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
            target.host.action.set('block')
        elif target.name == 'Ancient Potion':
            if (target.host.attributes.gene + Global.player.days) % 2 == 0:
                target.host.attributes.strength += 1
            else:
                target.host.attributes.agility += 1
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
            Global.menu.display(1)
        elif target.var['business'] == 'Trade':
            from src.entity.Stock import Stock
            Global.menu.var = [target, target.attributes.gene % 3,
                               [Stock.get(i) for i in target.var['item'].split('&')]]
            Global.menu.state = Global.menu.menu_shop
            Global.menu.history.append(Global.menu.state)
            Global.menu.display(1)
        elif target.var['business'] == 'Train':
            Global.menu.var = [target]
            Global.menu.state = Global.menu.menu_trainer
            Global.menu.history.append(Global.menu.state)
            Global.menu.display(1)
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
            Global.menu.state = Global.menu.menu_guild
            Global.menu.history.append(Global.menu.state)
            Global.menu.display(1)
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
            Global.menu.state = Global.menu.menu_insurance
            Global.menu.history.append(Global.menu.state)
            Global.menu.display(1)
