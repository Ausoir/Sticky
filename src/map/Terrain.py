from src.entity.Image import Image
from src.game import Global
from src.tools.Data import Data


class Terrain(Image):
    def __init__(self, id, pos, name, image, type, flip):
        super().__init__(pos)
        self.name = name
        self.id = id
        self.form = Data.run_cache(image)
        self.form_name = image
        self.type = type
        if flip == 1:
            self.form.flip(1, 0)
            self.form.resize()

    @classmethod
    def load_from_name(cls, pos, name):
        args = Data.get_cache('tiles')
        for k, i in enumerate(args):
            if i[0] == name:
                return cls(k, pos, i[0], i[1], i[2], i[3])
        return None

    def draw(self, surface):
        self.form.draw(surface, self.vec.x + Global.HALF_BLOCK, self.vec.y + Global.HALF_BLOCK)
