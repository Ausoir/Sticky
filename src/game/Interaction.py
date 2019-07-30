from src.game import Global
from src.game.Tags import Tags


class Interaction:
    @staticmethod
    def trigger(tile):
        for thing in tile.things:
            if Tags.interactive in thing.tags:
                return Interaction.interact(thing)

    @staticmethod
    def interact(target):
        if Tags.workable in target.tags:
            from src.tools.Data import Data
            conversation = Data.get_line('data/raw/raw.txt', 'crafts')[1]
            Global.menu.var = conversation
            Global.menu.state = Global.menu.menu_craft
            Global.menu.display(1)
            return True
        elif target.name in ['Talker', 'Merchant']:
            target.talk()
            return True
        elif target.name in ['Talker', 'Merchant']:
            target.talk()
            return True
        elif target.name == 'Food':
            hunger = target.host.states.get('Hunger')
            if hunger:
                hunger.end()
                target.host.action.set('block')
                target.hit(1)
            else:
                target.use()
            return True
        elif target.name == 'Backpack':
            if target.host.is_armored():
                if target.host.armor.inventory[1][1] == 1:
                    target.host.armor.inventory[1][1] = 2
                    target.host.action.set('block')
                    target.die()
            return True
        elif target.name == 'Bow':
            target.hit(1)
            if target.durability > 0:
                target.host.action.set('arch')
            return True
        elif target.name == 'Treatment':
            status = target.host.states.get('Sick')
            if status:
                status.trigger(['remove'])
                target.die()
        return False
