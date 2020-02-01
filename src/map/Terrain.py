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
        args = Data.get_cache('tiles')
        for k, i in enumerate(args):
            if i[0] == name:
                return cls(k, i[0], i[1], i[2], i[3])
        return None
