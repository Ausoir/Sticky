from src.entity.unit.ai.Faction import Faction
from src.form.Effect import Effect
from src.game.Turn import Turn


class Attack:
    BATTER = 1
    BLOODY = 2

    def __init__(self):
        Turn.add(self)
        self.registry = []
        self.delay = 0

    def turn(self):
        new_reg = []
        while self.registry:
            new = self.registry.pop(0)
            if new[0] == 0:
                self.hit(new)
            else:
                new[0] -= 1
                new_reg.append(new)
        self.registry = new_reg

    def register(self, dealer, damage, pos, delay=0, type=BATTER, faction=Faction.FFA, callback=None):
        self.registry.append([delay, pos, dealer, damage, type, faction, callback])

    def hit(self, data):
        for thing in data[1].things:
            if thing.faction.is_against(data[5]):
                thing.hit(data[2], data[3])
                if data[4] == Attack.BATTER:
                    Effect.batter(data[1].get_center())
                elif data[4] == Attack.BLOODY:
                    Effect.blood(data[1].get_center())
                if data[6]:
                    data[6](thing)
