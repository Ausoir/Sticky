from src.tools.Dialog import Dialog


class Tag:
    def __init__(self):
        self.attributes = {}

    def __str__(self):
        return Dialog.dict(self.attributes)

    def load(self, arg):
        for i in arg:
            strings = i.split(':')
            if len(strings) > 1:
                if strings[1][0].isdigit() or strings[1][0] == '-':
                    self.attributes[strings[0]] = int(strings[1])
                else:
                    self.attributes[strings[0]] = strings[1]

    def remove(self, tag, default=None):
        if tag in self.attributes:
            r = self.attributes[tag]
            del self.attributes[tag]
            return r
        return default

    def get(self, tag, default=None):
        if tag in self.attributes:
            return self.attributes[tag]
        return default

    def set(self, tag, arg, add=True):
        if tag in self.attributes or add:
            self.attributes[tag] = arg
            return True

    def increment(self, tag, arg, remove=None, default=0):
        if isinstance(arg, int):
            if tag in self.attributes:
                self.attributes[tag] += arg
                if remove is not None and self.attributes[tag] == remove:
                    del self.attributes[tag]
                    return remove
                else:
                    return self.attributes[tag]
            elif arg != 0:
                self.attributes[tag] = default + arg
                return self.attributes[tag]
        else:
            self.set(tag, arg)

    def sync(self, tag, target, ratio=1):
        if target and target != 0:
            self.increment(tag, target * ratio, remove=0)

    def minmax(self, tag, minimum, maximum):
        if tag in self.attributes:
            self.attributes[tag] = max(minimum, min(maximum, self.attributes[tag]))

    def require(self, tag, arg, cost=True):
        if tag in self.attributes:
            if self.attributes[tag] >= arg:
                if cost:
                    self.attributes[tag] -= arg
                return True
