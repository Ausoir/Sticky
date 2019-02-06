from src.form.Shape import Shape
from src.game import Global
from src.tools.Data import Data


class Terrain(Shape):
    def __init__(self, id, name, pos, type, color, stroke_width, width=Global.BLOCK, height=Global.BLOCK):
        super().__init__(1, pos, color, Shape.make_rect((width, height)), stroke_width)
        self.name = name
        self.id = id
        self.visible = 1
        self.type = type

    @classmethod
    def make(cls, id, name, pos, type, color, width):
        # if type > 9:
        #     return cls(id, name, pos, type, color, width, height=Global.DISPLAY[1])
        return cls(id, name, pos, type, color, width)

    @classmethod
    def load(cls, pos, id):
        args = Data.get_cache_processed('data/raw/tile.txt')[id]
        return cls.make(id, args[0], pos, args[1], args[2], args[3])

    @classmethod
    def load_from_name(cls, pos, name):
        args = Data.get_cache_processed('data/raw/tile.txt')
        for k, i in enumerate(args):
            if i[0] == name:
                return cls.make(k, i[0], pos, i[1], i[2], i[3])
        return None
