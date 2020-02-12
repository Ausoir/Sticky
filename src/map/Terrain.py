from src.tools.Data import Data


class Terrain:
    def __init__(self, code, name, image, type, direction):
        self.name = name
        self.id = code
        self.image = Data.get_cache(image)
        self.type = type
        self.direction = direction
        self.joint_neighbors = [0, 0, 0, 0]

    @classmethod
    def load_from_name(cls, name):
        index, v = Data.get_line('raw/tiles.txt', name, row=True)
        if v:
            return cls(index, v[0], v[1], v[2], v[3])
