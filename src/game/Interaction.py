from src.entity.Particle import Particle
from src.game import Global
from src.tools.Dialog import Dialog


class Interaction:
    @staticmethod
    def trigger(tile):
        targets = []
        for thing in tile.things:
            if '!' in thing.tags:
                targets.append(thing)
        if targets:
            if len(targets) > 1:
                arg2 = []
                arg3 = []
                for i in targets:
                    arg2.append(i.name)
                    arg3.append(lambda x: Interaction.interact(targets[x].tags['!'], targets[x]))
                Global.menu.var = ['There are more than one possible interactions at this position. Choose one.',
                                   arg2, arg3]
                Global.player.menu(Global.menu.menu_choice)
                return True
            else:
                return Interaction.interact(targets[0].tags['!'], targets[0])

    @staticmethod
    def interact(service, target):  # mass interaction substitute for Other class
        if service == 'run':
            target.trigger()
        elif service == 'craft':
            if Global.player.is_safe() and Global.player.character.is_bright():
                from src.tools.Data import Data
                products = Data.get_line('data/raw/raw.txt', 'basic_craft')[1]
                recipe = []
                from src.game.Crafting import Crafting
                for i in products:
                    recipe.append([i, Crafting.get_ingredients(i), None])
                Global.menu.var = recipe
                Global.player.menu(Global.menu.menu_craft)
        elif service == 'tinker':
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
        elif service == 'scribe':
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
        elif target.name == 'Disassembler':
            def disassemble(arg):
                if Global.player.memorize():
                    Global.player.knowledge.append(disassembled)
                    Global.player.character.say('Learned [' + disassembled + ']!')
                    Global.player.character.weapon.die()
                    Global.menu.toggle()
            from src.entity.unit.item.Spell import Spell
            if Global.player.character.is_armed():
                weapon = Global.player.character.weapon
                if isinstance(weapon, Spell):
                    disassembled = weapon.spell
                    if disassembled not in Global.player.knowledge:
                        if Global.player.is_safe() and Global.player.character.is_bright():
                            Global.menu.var = [Dialog.get('disassemble_spell?', [disassembled]),
                                               ['Yes'], [disassemble]]
                            Global.player.menu(Global.menu.menu_choice)
                    else:
                        Global.player.character.say(Dialog.get('spellknown', [disassembled]))
                else:
                    from src.game.Crafting import Crafting
                    disassembled = weapon.name
                    if Crafting.get_ingredients(disassembled):
                        if Global.player.is_safe() and Global.player.character.is_bright():
                            Global.menu.var = [Dialog.get('disassemble?', [disassembled]),
                                               ['Yes'], [disassemble]]
                            Global.player.menu(Global.menu.menu_choice)
                    else:
                        Global.player.character.say('This item can not be disassembled.')
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
        elif target.name in ['Bed', 'Sofa']:
            if Global.player.is_safe() and Global.player.eat():
                def rest(arg):
                    Global.menu.toggle()
                    Global.player.character.attributes.rest()
                    Global.draw_group.colorize(0, [0, 0, 0, 255], fade=2)
                    Global.player.sleep(1)
                Global.menu.var = [Dialog.get('?rest', [target.name]), [Dialog.get('Rest')], [rest]]
                Global.menu.direct(Global.menu.menu_choice)
        elif target.name == 'Target':
            if Global.player.is_safe():
                def sell(arg):
                    if arg == 1 and host.require_var('protein', host.attributes.strength + 1, cost=False):
                        if Global.player.eat():
                            Particle.make('barrier', host.vec)
                            Global.player.sleep(1)
                            host.require_var('protein', host.attributes.strength + 1, cost=True)
                            host.attributes.strength += 1
                    if arg == 0 and host.require_var('calories', host.attributes.agility + 1, cost=False):
                        if Global.player.eat():
                            Particle.make('barrier', host.vec)
                            Global.player.sleep(1)
                            host.require_var('calories', host.attributes.agility + 1, cost=True)
                            host.attributes.agility += 1
                    Global.menu.toggle()
                host = Global.player.character
                strength = str(host.var['protein']) + '/' + str(host.attributes.strength + 1)
                agility = str(host.var['calories']) + '/' + str(host.attributes.agility + 1)
                text = 'You have ' + strength + ' proteins required for Strength training'
                text += ' and ' + agility + ' calories required for Agility training.'
                Global.menu.var = [text, ['Train Agility', 'Train Strength'], [sell, sell]]
                Global.menu.direct(Global.menu.menu_choice)
        elif target.name == 'Anvil':
            if Global.player.is_safe() and Global.player.character.is_bright():
                Global.player.menu(Global.menu.menu_anvil)
        elif 'service' in target.var and target.faction == Global.player.character.faction:
            target.face_toward(Global.player.character.pos)
            from src.entity.Stock import Stock
            from src.entity.unit.Character import Character
            if isinstance(target, Character):
                if 'service' in target.var:
                    service = target.var['service']
                else:
                    service = 'Default'
                target.say('?')
                Global.menu.var = [target, service]
                Global.menu.topic(service)
            else:
                Global.menu.display(-1)
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
                    Stock.make('Water Bottle', target.pos)
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
                Particle.make('heal', target.host.vec)
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
