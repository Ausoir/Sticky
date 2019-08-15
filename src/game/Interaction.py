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
                Global.menu.var = ['There are more than one possible interactions at this position.', arg2, arg3]
                Global.menu.state = Global.menu.menu_choice
                Global.menu.display(1)
                return True
            else:
                return Interaction.interact(targets[0])

    @staticmethod
    def interact(target):  # mass interaction substitute for Other class
        if target.name == 'Interactive':
            target.trigger()
        elif Tags.workable in target.tags:
            from src.tools.Data import Data
            conversation = Data.get_line('data/raw/raw.txt', 'crafts')[1]
            Global.menu.var = conversation
            Global.menu.state = Global.menu.menu_craft
            Global.menu.display(1)
        elif Tags.restable in target.tags:
            if Global.player.is_safe() and Global.player.eat():
                Global.main.colorize(0, [0, 0, 0, 255], fade=2)
                Global.player.sleep(1)
                Global.player.character.attributes.breath = 0
        elif target.name == 'Anvil':
            Global.menu.state = Global.menu.menu_anvil
            Global.menu.display(1)
        elif target.name in ['Talker', 'Merchant']:
            target.talk()
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
        elif target.name == 'Bow':
            target.hit(1)
            if target.durability > 0:
                target.host.action.set('arch')
        elif target.name == 'Treatment':
            status = target.host.states.get('Sick')
            if status:
                status.trigger(['remove'])
                target.die()
        elif target.name == 'Sampler':
            for thing in target.host.pos[0].things:
                if thing != target.host:
                    target.tags = thing.tags
                    break
            target.host.action.set('block')
        else:
            return False
        return True
