from src.entity.unit.ai.Task import Move, Pickup, Attack, Travel, Melee
from src.entity.unit.item.Weapon import Weapon


class Behavior:
    @classmethod
    def make(cls, pilot, type):
        if type == 'Melee':
            move = Travel(pilot, 0)
            return cls(move, Melee(pilot, move))
        else:
            move = Move(pilot, 0)
            return cls(move, Attack(pilot, move))

    def __init__(self, move, hunt):
        self.move = move
        self.hunt = hunt

    def spot_enemy(self, pilot, targets):
        pilot.priority = 1
        pilot.var = pilot.prioritize(targets)
        pilot.add_task(self.hunt)

    def spot_item(self, pilot, targets):
        pilot.priority = 2
        weapons = []
        for i in targets:
            if isinstance(i, Weapon):
                weapons.append(i)
        if weapons:
            pilot.var = pilot.prioritize(weapons)
            pilot.add_task(self.move)
            pilot.add_task(Pickup(pilot))
