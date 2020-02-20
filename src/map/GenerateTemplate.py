from src.map.Generator import Generator


class Template(Generator):
    def __init__(self, x, y, seed=0):
        super().__init__(x, y, seed=seed)
        self.background['Lamp'] = '.'

    def run(self):
        pass
