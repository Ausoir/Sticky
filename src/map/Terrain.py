from src.entity.Image import Image
from src.game import Global
from src.tools.Data import Data


class Terrain(Image):
    def __init__(self, id, pos, name, image, type, flip_x, flip_y, background):
        super().__init__(pos)
        self.name = name
        self.id = id
        self.form = Data.run_cache(image)
        self.form_name = image
        self.type = type
        self.background = background
        if flip_x == 1 or flip_y == 1:
            self.form.direction = (1 if flip_x == 0 else 0, flip_y)
            self.form.resize()

    @classmethod
    def load_from_name(cls, pos, name):
        args = Data.get_cache('tiles')
        for k, i in enumerate(args):
            if i[0] == name:
                return cls(k, pos, i[0], i[1], i[2], i[3], i[4], i[5])
        return None

    def draw(self, surface):
        self.form.draw(surface, self.vec.x + Global.HALF_BLOCK, self.vec.y + Global.HALF_BLOCK)
