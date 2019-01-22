from src.form.Shape import Shape


class Terrain(Shape):
    BLOCK = None

    @classmethod
    def make(cls, terrain, pos):
        if hasattr(cls, terrain):
            return getattr(cls, terrain)(pos)
        print('Failed to create terrain '+terrain)

    @classmethod
    def dirt(cls, pos):
        return cls(pos, 1, (180, 120, 90), 0)

    @classmethod
    def mark(cls, pos):
        return cls(pos, 0, (215, 215, 215), 1)

    def __init__(self, pos, type, color, width):
        super().__init__(1, pos, color, Shape.make_rect((Terrain.BLOCK, Terrain.BLOCK)), width)
        self.visible = 1
        self.type = type
