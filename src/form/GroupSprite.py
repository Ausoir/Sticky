class GroupSprite(list):
    def __init__(self):
        super().__init__()

    def add(self, arg):
        for k, v in enumerate(self):
            if arg.depth <= v.depth:
                self.insert(k, arg)
                return
        self.append(arg)

    def draw(self, surface):
        for i in self:
            if i.visible == 1:
                i.draw(surface)
