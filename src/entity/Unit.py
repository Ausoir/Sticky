from src.entity.Object import Object
from src.entity.action.Action import Action
from src.form.Body import Body
from src.map.Tile import Tile


# has Body form, is movable
class Unit(Object):
    def __init__(self, form, map):
        super().__init__(form, map)
        self.action = Action(self)
        self.next_action = 'idle'
        self.next_target = [0, 0]
        self.direction = 1

    def make_form(self, p):
        self.form = Body(texture_name=p)

    def draw(self, surface, pos):
        super().draw(surface, pos)
        self.form.update()

    def input(self, action, mouse):
        self.next_action = action
        self.next_target = mouse

    def face(self, direction):
        self.direction = direction
        self.form.face(direction)

    def turn(self):
        super().turn()
        if self.delay == 0:
            self.face(1 if self.next_target[0] > self.pos.x * Tile.BLOCK else -1)
            continuous = self.action.perform(self.next_action)
            if not continuous:
                self.next_action = 'idle'

    def on_fall(self):
        self.action.perform('hit')
