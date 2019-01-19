from src.entity.Space import Space


class Tile(Space):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.object = None
