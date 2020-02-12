from src.entity.Particle import Particle
from src.game import Global


class Interaction:
    @staticmethod
    def interact(service, target):  # mass interaction substitute for Other class
        if service == 'artifact':
            from src.entity.Stock import Stock
            from src.tools.Data import Data
            spell = Global.r.rand_list(Data.process_raw(Data.read('raw/spells.txt')))
            r = Stock.make('Wand', target.pos)
            r.name = spell[0] + ' Wand'
            r.spell = spell[0]
            target.host.action.act('grab', 8)
            target.die()
        elif service == 'bandage':
            status = target.host.states.get('Bleed')
            if status:
                Particle.make('barrier', target.host.vec)
                status.trigger(['remove'])
                target.hit(1)
                target.host.action.act('grab', 8)
        elif service == 'cure':
            Particle.make('barrier', target.host.vec)
            sick = target.host.states.get('Sick')
            if sick:
                sick.trigger(['remove'])
        elif target.name == 'rspawn':
            from src.entity.Stock import Stock
            Stock.make(Global.r.rand_list([v for v in Stock.registry.values()])[0], target.host.pos)
            target.host.action.act('grab', 8)
            target.hit(1)
        else:
            return False
        return True
