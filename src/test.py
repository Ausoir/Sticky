from src.entity.Space import Space


class Travel:
    class Node:
        def __init__(self, parent, node):
            self.parent = parent
            self.node = node
            self.g = 0
            self.h = 0
            self.f = self.g + self.h

        def set_h(self, destination):
            self.h = (self.node - destination).distance()

        def __str__(self):
            return self.node.__str__()+'/'+str(self.f)

    def __init__(self):
        self.destination = Space(end)
        self.counter = 0
        self.open = []
        self.closed = []
        self.open.append(Travel.Node(None, Space(start)))

    def iterate(self, node):
        index = 0
        for k, v in enumerate(self.open):
            if v.f < node.f:
                index = k
                node = v
        self.open.pop(index)
        self.closed.append(node)
        if node.node == self.destination:
            return node
        options = [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (1, -1)]
        for new_pos in options:
            new_pos = Space(node.node.x + new_pos[0], node.node.y + new_pos[1])
            if self.is_blocked(new_pos):
                continue
            if self.check_loop(self.closed, new_pos):
                continue
            conflict = self.check_loop(self.open, new_pos)
            if conflict:
                # if node.g + 1 <= conflict.g:
                #     conflict.g = node.g + 1
                #     conflict.set_h(self.destination)
                #     conflict.f = conflict.h + conflict.g
                continue
            self.counter += 1
            new = Travel.Node(node, new_pos)
            new.g = node.g + 1
            new.set_h(self.destination)
            new.f = new.h + new.g
            self.open.append(new)

    def check_loop(self, loop, pos):
        for i in loop:
            if i.node == pos:
                return i

    def is_blocked(self, pos):
        return maze[pos.y][pos.x] == 1

    def perform(self):
        done = 0
        while not done and self.counter < 500:
            done = self.iterate(self.open[0])
        if done:
            while done.parent:
                print(done.node)
                done = done.parent
        print(self.counter)


maze = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 1, 1, 1, 0, 1],
        [1, 0, 0, 2, 1, 0, 0, 0, 0, 1],
        [1, 0, 0, 2, 1, 0, 0, 0, 0, 1],
        [1, 0, 0, 2, 1, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

start = (1, 8)
end = (5, 8)

path = Travel()
path.perform()
