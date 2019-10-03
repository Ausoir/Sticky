from src.entity.Other import Script
from src.entity.Particle import Particle
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
        if isinstance(target, Script):
            target.trigger()
        elif target.name == 'Table':
            if Global.player.is_safe() and Global.player.character.is_bright():
                from src.tools.Data import Data
                products = Data.get_line('data/raw/raw.txt', 'basic_craft')[1]
                recipe = []
                from src.game.Crafting import Crafting
                for i in products:
                    recipe.append([i, Crafting.get_ingredients(i), None])
                Global.menu.var = recipe
                Global.player.menu(Global.menu.menu_craft)
        elif target.name == 'Workbench':
            if Global.player.is_safe() and Global.player.character.is_bright():
                knowledge = Global.player.get_craft_list()
                if knowledge:
                    recipe = []
                    from src.game.Crafting import Crafting
                    for i in knowledge:
                        recipe.append([i, Crafting.get_ingredients(i), None])
                    Global.menu.var = recipe
                    Global.player.menu(Global.menu.menu_craft)
                else:
                    Global.player.character.say('I know no items to craft here!')
        elif target.name == 'Desk':
            if Global.player.is_safe() and Global.player.character.is_bright():
                knowledge = Global.player.get_spell_list()
                if knowledge:
                    def make_spell(arg):
                        from src.entity.Stock import Stock
                        from src.game.Crafting import Crafting
                        result_spell = arg[:-7]
                        scroll = Crafting.craft(Global.player.character, 'Spell', ['Paper'])
                        scroll.name = arg
                        scroll.spell = result_spell
                    spells = []
                    for i in knowledge:
                        spells.append([i + ' Scroll', ['Paper'], make_spell])
                    Global.menu.var = spells
                    Global.player.menu(Global.menu.menu_craft)
                else:
                    Global.player.character.say('I know of no spells to craft!')
        elif target.name == 'Paper':
            if Global.player.is_safe() and Global.player.character.is_bright():
                knowledge = Global.player.get_spell_list()
                if knowledge:
                    def make_spell(arg):
                        from src.entity.Stock import Stock
                        from src.game.Crafting import Crafting
                        result_spell = arg[:-7]
                        make_pen = Data.get_line('data/raw/spells.txt', result_spell)[1]
                        scroll = Crafting.craft(Global.player.character, 'Spell', ['Paper', make_pen])
                        scroll.name = arg
                        scroll.spell = result_spell
                    from src.tools.Data import Data
                    spells = []
                    for i in knowledge:
                        pen = Data.get_line('data/raw/spells.txt', i)
                        if pen:
                            pen = pen[1]
                            spells.append([i + ' Scroll', ['Paper', pen], make_spell])
                    Global.menu.var = spells
                    Global.player.menu(Global.menu.menu_craft)
                else:
                    Global.player.character.say('I know of no spells to craft!')
        elif target.name == 'Disassembler':
            def disassemble(arg):
                if Global.player.memorize():
                    Global.player.knowledge.append(disassembled)
                    Global.player.character.say('Learned [' + disassembled + ']!')
                    Global.player.character.weapon.die()
                    Global.menu.toggle()
            from src.entity.unit.item.Spell import Spell
            if isinstance(Global.player.character.weapon, Spell):
                disassembled = Global.player.character.weapon.spell
                if disassembled not in Global.player.knowledge:
                    if Global.player.is_safe() and Global.player.character.is_bright():
                        Global.menu.var = ['This artifact contains the spell [' + disassembled + ']. Disassemble?',
                                           ['Yes'], [disassemble]]
                        Global.player.menu(Global.menu.menu_choice)
                else:
                    Global.player.character.say('[' + disassembled + '] is already known.')
            else:
                Global.player.character.say('Only spell artifacts can be disassembled at this table.')
        elif target.name == 'Constructor':
            if Global.player.is_safe() and Global.player.character.is_bright():
                def make_furniture(arg):
                    from src.entity.Stock import Stock
                    from src.game.Crafting import Crafting
                    scroll = Crafting.craft(Global.player.character, 'Box', req)
                    scroll.name = 'Packed ' + arg
                    scroll.loot = [arg]
                furniture_list = []
                from src.tools.Data import Data
                furniture = Data.get_line('data/raw/raw.txt', 'furniture')[1]
                req = ['Plank', 'Saw', 'Hammer']
                for i in furniture:
                    furniture_list.append([i, req, make_furniture])
                Global.menu.var = furniture_list
                Global.player.menu(Global.menu.menu_craft)
        elif target.name in ['Kitchen', 'Campfire']:
            if Global.player.is_safe() and Global.player.character.is_bright():
                from src.tools.Data import Data
                products = Data.get_line('data/raw/raw.txt', 'cook')[1]
                recipe = []
                from src.game.Crafting import Crafting
                for i in products:
                    recipe.append([i, Crafting.get_ingredients(i), None])
                Global.menu.var = recipe
                Global.player.menu(Global.menu.menu_craft)
        elif target.name in ['Bed', 'Sofa']:
            if Global.player.is_safe() and Global.player.drink():
                Global.player.character.attributes.rest()
                Global.main.colorize(0, [0, 0, 0, 255], fade=2)
                Global.player.sleep(1)
        elif target.name == 'Target':
            if Global.player.is_safe():
                def sell(arg):
                    if arg == 1 and host.require_var('protein', host.attributes.strength, cost=False):
                        if Global.player.drink():
                            Particle.make('barrier', host.vec)
                            Global.player.sleep(1)
                            host.require_var('protein', host.attributes.strength, cost=True)
                            host.attributes.strength += 1
                    if arg == 0 and host.require_var('calories', host.attributes.agility, cost=False):
                        if Global.player.drink():
                            Particle.make('barrier', host.vec)
                            Global.player.sleep(1)
                            host.require_var('calories', host.attributes.agility, cost=True)
                            host.attributes.agility += 1
                    Global.menu.toggle()
                host = Global.player.character
                strength = str(host.var['protein']) + ' of ' + str(host.attributes.strength)
                agility = str(host.var['calories']) + ' of ' + str(host.attributes.agility)
                text = 'You have ' + strength + ' proteins required for Strength training'
                text += ' and ' + agility + ' proteins required for Agility training.'
                Global.menu.var = [text, ['Train Agility', 'Train Strength'], [sell, sell]]
                Global.menu.direct(Global.menu.menu_choice)
        elif target.name == 'Anvil':
            if Global.player.is_safe() and Global.player.character.is_bright():
                Global.player.menu(Global.menu.menu_anvil)
        elif Tags.intelligent in target.tags and target.faction == Global.player.character.faction:
            from src.entity.Stock import Stock
            Global.menu.var = [target]
            Global.player.menu(Global.menu.menu_conversation)
        elif Tags.drinkable in target.tags:
            hunger = target.host.states.get('Thirst')
            if hunger:
                hunger.end()
                target.host.action.set('wait')
                target.hit(1)
            else:
                return False
        elif target.name == 'Pocket':
            if target.host.is_armored():
                max_hp = target.host.armor.max_durability
                if max_hp > 1:
                    if len(target.host.armor.pockets) < 4:
                        target.host.armor.max_durability -= 1
                        target.host.armor.durability = min(max_hp, target.host.armor.durability)
                        target.host.armor.pockets.append(-1)
                        target.host.action.set('wait')
                        target.die()
                    else:
                        Global.player.character.say('Cannot add more pockets!')
                else:
                    Global.player.character.say('Cannot attach pockets to this armor!')
        elif target.name == 'Pouch':
            if target.host.is_armored():
                if target.host.attributes.agility >= target.host.get_encumbrance() + 1:
                    for y in range(2):
                        for x in range(3):
                            if target.host.armor.inventory[y][x] == 1:
                                target.host.armor.weight += 1
                                target.host.armor.inventory[y][x] = 2
                                target.host.action.set('wait')
                                target.die()
                                return True
                    Global.player.character.say('Cannot add more inventory slots!')
                else:
                    Global.player.character.say('Agility is too low!')
        elif target.name == 'Bottle':
            from src.entity.Stock import Stock
            for thing in target.pos.things:
                if thing.name in ['Water', 'Surface']:
                    target.die()
                    Stock.make('Dirty Water Bottle', target.pos)
                    target.host.action.set('wait')
                    break
            return False
        elif target.name == 'Artifact Pouch':
            from src.entity.Stock import Stock
            from src.tools.Data import Data
            spell = Global.r.rand_list(Data.process_raw(Data.read('data/raw/spells.txt')))
            r = Stock.make('Wand', target.pos)
            r.name = spell[0] + ' Wand'
            r.spell = spell[0]
            target.host.action.set('wait')
            target.die()
        elif target.name == 'Bow':
            if target.durability != 0:
                target.host.action.set('arch')
                target.hit(1)
            else:
                return False
        elif target.name == 'Revolver':
            if target.durability != 0:
                target.host.action.set('shoot')
                target.hit(1)
            else:
                return False
        elif target.name == 'Bandage':
            status = target.host.states.get('Bleed')
            if status:
                Particle.make('barrier', target.host.vec)
                status.trigger(['remove'])
                target.hit(1)
                target.host.action.set('wait')
        elif target.name == 'Medicine':
            Particle.make('barrier', target.host.vec)
            target.host.states.add('Healthy', 300, var=1)
        elif target.name == 'Sampler':
            for thing in target.host.pos.things:
                if thing != target.host:
                    target.tags = thing.tags
                    target.host.action.set('wait')
                    break
        elif target.name == 'Jelly':
            status = target.host.states.get('Sick')
            if status:
                status.duration += 100
                target.die()
                target.host.action.set('wait')
        elif target.name == 'Dimension Coin':
            from src.entity.Stock import Stock
            Stock.make(Global.r.rand_list([v for v in Stock.registry.values()])[0], target.host.pos)
            target.host.action.set('wait')
            target.hit(1)
        elif target.name == 'Headband':
            if target.host.is_headgeared():
                target.host.headgear.durability = -1
                target.host.headgear.max_durability = -1
                target.host.action.set('wait')
                Global.player.character.say('Headband attached!')
                target.die()
            else:
                return False
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
            if Global.player.days >= target.var['due']:
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
            items = [Stock.get(i) for i in target.var['item'].split('&')]
            Global.menu.var = [target, target.attributes.gene % 2, items]
            Global.menu.direct(Global.menu.menu_shop)
        elif target.var['business'] == 'Train':
            Global.menu.var = [target]
            Global.menu.direct(Global.menu.menu_trainer)
        elif target.var['business'] == 'Supply':
            if Global.player.days >= target.var['due']:
                from src.tools.Data import Data
                from src.tools.Random import Random
                from src.entity.Stock import Stock
                data = Data.get_line('data/raw/trade.txt', target.var['type'])
                rng = Random(target.attributes.gene + Global.player.days)
                due_date = Global.player.days + rng.rand_int(2, 5)
                item = rng.rand_list(data[1])
                value = Stock.get(item).get_value()
                target.var['due'] = due_date
                target.var['item'] = item
                target.var['amount'] = rng.rand_int(1, 7)
                target.var['value'] = rng.rand_int(1, 8) + int(value * target.var['amount'] * .5)
            Global.menu.var = [target]
            Global.menu.direct(Global.menu.menu_guild)
        elif target.var['business'] == 'Provide':
            if Global.player.days >= target.var['due']:
                from src.entity.Stock import Stock
                target.var['due'] = Global.player.days + target.var['time']
                target.var['amount'] = target.var['need']
            Global.menu.var = [target]
            Global.menu.direct(Global.menu.menu_guild)
        elif target.var['business'] == 'Pawn':
            selling = Global.player.character.weapon
            price = int(selling.get_value() * .7 - (target.attributes.gene % 3) - 1)
            if Global.player.character.is_armed() and price > 0:
                def sell(arg):
                    selling.loot = []
                    selling.die()
                    Global.player.character.var['money'] += price
                    Global.player.character.say('Sold ' + selling.get_display_name() + ' for $' + str(price) + '!')
                    Global.menu.toggle()
                text = 'Would you like to sell your ' + selling.get_display_name() + ' for $' + str(price) + '?'
                Global.menu.var = [text, ['Yes'], [sell]]
                Global.menu.direct(Global.menu.menu_choice)
            else:
                Global.menu.show_dialog(['You are not holding anything that you can sell here.'])
        elif target.var['business'] == 'Insurance':
            from src.tools.Random import Random
            from src.entity.Stock import Stock
            Global.menu.var = [target]
            Global.menu.direct(Global.menu.menu_insurance)
        elif target.var['business'] == 'Treatment':
            def treat(arg):
                if Global.player.character.require_var('money', target.var['value']):
                    from src.entity.unit.Buff import BuffTags
                    Global.player.character.states.clear(lambda x: BuffTags.harmful in x.tags)
                    Global.menu.toggle()
                    Global.player.character.say('All debuffs removed.')
            Global.menu.var = ['I can cure you of all illness for $' + str(target.var['value']) + '.',
                               ['Cure'], [treat]]
            Global.menu.direct(Global.menu.menu_choice)
        elif target.var['business'] == 'Inn':
            def buy(arg):
                if target.var['own'] == 0:
                    if Global.player.character.require_var('money', cost):
                        target.var['own'] = 1
                        Global.player.character.var['home'] = target.location.name
                        Global.player.character.say('Home set!')
                        Global.menu.toggle()
                elif target.var['own'] == 1 or Global.player.days >= target.var['due']:
                    if Global.player.character.require_var('money', cost * 20):
                        target.var['due'] = Global.player.days + 14
                        target.var['own'] = 2
                        Global.player.character.say('Bought a place!')
                        Global.menu.toggle()
                else:
                    from src.entity.Space import Space
                    Global.player.travel('storage', Space())
            cost = target.var['value']
            if target.var['own'] == 0:
                text = 'Would you like to set this place as home for $' + str(cost) + '?'
            elif target.var['own'] == 1 or Global.player.days >= target.var['due']:
                text = 'Would you like to get a private room for $' + str(cost * 20) + ' per week?'
            else:
                from src.tools.Dialog import Dialog
                left = Dialog.day(target.var['due'] - Global.player.days)
                text = 'Would you like to enter your private room? You have ' + left + ' until your next rent.'
            Global.menu.var = [text, ['Yes'], [buy]]
            Global.menu.direct(Global.menu.menu_choice)
        elif target.var['business'] == 'Enter':
            def pay(arg):
                if Global.player.character.require_var('money', cost):
                    from src.entity.Space import Space
                    Global.player.travel(target.location.name, Space(int(dest[0]), int(dest[1])))

            def gift(arg):
                for possession in Global.player.character.get_accessibles():
                    if possession.name == item:
                        possession.die()
                        from src.entity.Space import Space
                        Global.player.travel(target.location.name, Space(int(dest[0]), int(dest[1])))
                        return
                Global.player.character.say('No item...')
            cost = target.var['value']
            item = target.var['item']
            dest = target.var['destination'].split('&')[1:]
            Global.menu.var = ['You cannot enter empty handed. Pay $' + str(cost) + ' or bring ' + item + '.',
                               ['Pay money', 'Give ' + item], [pay, gift]]
            Global.menu.direct(Global.menu.menu_choice)
