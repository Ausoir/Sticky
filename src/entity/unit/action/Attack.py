from src.entity.unit.ai.Faction import Faction
from src.form.Effect import Effect
from src.game.Turn import Turn


class Attack:
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

    def register(self, damage, pos, delay=0, type=0, faction=Faction.FFA, callback=None):
        self.registry.append([delay, pos, damage, type, faction, callback])

    def hit(self, data):
        for thing in data[1].things:
            if thing.faction.is_against(data[4]):
                thing.hit(data[2])
                if data[3]:
                    Effect.get(data[3])(data[1].get_center())
                if data[5]:
                    data[5](thing)
