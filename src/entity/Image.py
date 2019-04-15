class Image:
    def __init__(self, vec):
        self.id = '0'
        self.name = None
        self.form = None
        self.form_name = ''
        self.vec = vec

    def __str__(self):
        return str(self.id)

    def load(self, p):
        self.id = p[0]
        return 1
