from src.form.Shape import Shape
from src.game import Global
from src.tools.Data import Data


class Terrain(Shape):
    def __init__(self, id, pos, type, color, width):
        super().__init__(1, pos, color, Shape.make_rect((Global.BLOCK, Global.BLOCK)), width)
        self.id = id
        self.visible = 1
        self.type = type

    @classmethod
    def load(cls, pos, id):
        args = Data.get_cache_processed('data/raw/tile.txt')[id]
        return cls(id, pos, args[1], args[2], args[3])

    @classmethod
    def load_from_name(cls, pos, name):
        args = Data.get_cache_processed('data/raw/tile.txt')
        for k, i in enumerate(args):
            if i[0] == name:
                return cls(k, pos, i[1], i[2], i[3])
        return None
