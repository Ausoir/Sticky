class GroupInterface(list):
    def __init__(self):
        super().__init__()

    def input(self, arg):
        for x in self:
            if x.input(arg) == 1:
                return
