from src.entity.Object import Object
from src.entity.Space import Space
from src.entity.action.Action import Action
from src.form.Body import Body
from src.game.Turn import Turn


class Unit(Object):
    def __init__(self, form, map):
        super().__init__(form, map)
        Turn.queue.append(self)
        self.action = Action(self)
        self.next_action = 'idle'
        self.next_target = [0, 0]
        self.direction = 1
        self.turn = 0

    def make_form(self, p):
        self.form = Body(self.vec, texture_name=p)

    def update(self):
        old_vec = Space(self.vec)
        super().update()
        self.vec.x = old_vec.x + ((self.vec.x - old_vec.x) * .05)
        if self.vec.y < old_vec.y:
            self.vec.y = old_vec.y + ((self.vec.y - old_vec.y) * .2)
        else:
            self.vec.y = old_vec.y + min(16, self.vec.y - old_vec.y)
        self.form.update()

    def input(self, action, mouse):
        self.next_action = action
        self.next_target = mouse

    def face(self, direction):
        self.direction = direction
        self.form.face(direction)

    def perform(self):
        if self.pos.y < 8:
            self.move(0, 8 - self.pos.y)
            self.next_action = 'hit'
        self.face(1 if self.next_target[0] > self.vec.x else -1)
        continuous = self.action.perform(self.next_action)
        if not continuous:
            self.next_action = 'idle'
