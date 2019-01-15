class GroupInterface(list):
    def __init__(self):
        super().__init__()

    def input(self, arg):
        for x in self:
            x.input(arg)
