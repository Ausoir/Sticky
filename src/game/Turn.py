class Turn:
    queue = None
    fast_queue = None
    remove_queue = None
    frame = 0
    queue_turn = 0

    @staticmethod
    def init():
        Turn.queue = [[], [], [], [], [], [], [], [], [], []]
        Turn.fast_queue = []
        Turn.remove_queue = []
        Turn.frame = 0
        Turn.queue_turn = 0

    @staticmethod
    def update():
        while Turn.remove_queue:
            item = Turn.remove_queue.pop()
            for queue in Turn.queue:
                queue = filter(lambda x: x != item, queue)
            Turn.fast_queue = filter(lambda x: x != item, Turn.fast_queue)
        for i in Turn.queue[Turn.frame]:
            i()
        for i in Turn.fast_queue:
            i()
        Turn.frame += 1
        if Turn.frame >= 10:
            Turn.frame = 0

    @staticmethod
    def add(arg):
        Turn.queue[Turn.queue_turn].append(arg)
        Turn.queue_turn += 1
        if Turn.queue_turn >= 10:
            Turn.queue_turn = 0

    @staticmethod
    def remove(arg):
        for i in Turn.queue:
            if arg in i:
                i.remove(arg)
