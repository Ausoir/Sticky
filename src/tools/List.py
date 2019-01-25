class List(list):
    def __init__(self):
        super().__init__()

    def remove(self, arg):
        if arg in self:
            super().remove(arg)
