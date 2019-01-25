from src.entity.Unit import Unit


class Humanoid(Unit):
    def __init__(self, form, loc):
        super().__init__(form, loc)
        self.pos2 = self.location.get_tile(self.pos + (0, -1))
        self.form.randomize_clip('hit', 4)
        self.form.randomize_clip('dead1', 16)
        self.form.randomize_clip('dead2', 16)
        self.form.randomize_clip('dead3', 16)

    def remove(self):
        super().remove()
        self.pos2.remove(self)

    def draw(self, tile, surface, pos):
        if tile != self.pos2:
            super().draw(tile, surface, pos)

    def relocate(self, x, y):
        change = super().relocate(x, y)
        old_pos2 = self.pos2
        self.pos2 = self.location.get_tile(self.pos + (0, -1))
        if change:
            old_pos2.things.remove(self)
            self.pos2.things.append(self)
        return change

    def hit(self, hitter, damage):
        r = super().hit(hitter, damage)
        self.form.randomize_once(18)
        return r

    def will_hit(self, tile):
        return tile == self.pos or tile == self.pos2
