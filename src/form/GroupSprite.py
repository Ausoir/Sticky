class GroupSprite(list):
    def __init__(self):
        super().__init__()

    def draw(self, surface):
        for x in self:
            if x.visible == 1:
                x.draw(surface)
