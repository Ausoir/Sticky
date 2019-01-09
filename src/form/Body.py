from src.other import Data


class Body:
    def __init__(self, texture_name='Error'):
        data = Data.get_cache_clip(texture_name).copy()
        self.model = data[0]
        self.property = data[1]
        self.animation = data[2]
        self.motion = data[3]
        self.organs = []

    def draw(self, surface, pos):
        pass
