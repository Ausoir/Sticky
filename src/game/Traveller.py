from src.game import Global
from src.game.Camera import Camera
from src.game.Turn import Turn
from src.map.Tile import Tile
from src.tools.Dialog import Dialog


class Traveller:
    def __init__(self, player):
        self.backup = Turn.update
        Turn.update = self.update
        self.control = player.control
        self.visible = 1
        self.moving = [0, 0]
        self.selection = None
        self.next_action = None
        self.delay = 0

    def update(self):
        Global.map_view.overlay.turn()
        self.control.turn()
        Global.player.turn()
        Global.map_view.update_region()
        Global.map_view.update_fog()
        Global.map_view.update()
        if self.delay <= 0:
            if self.action():
                self.delay = 8
                self.next_action = None
            self.move()
        else:
            self.delay -= 1

    def move(self):
        if self.moving[0] != 0 or self.moving[1] != 0:
            front = Camera.target.pos.get_neighbor(self.moving[0], self.moving[1])
            if front and not front.is_land(Tile.CHECK_FIRM):
                time = max(0, -front.get_speed() + 1)
                if Global.player.sleep(time, blackout=False):
                    Camera.target.relocate(to=front)
                else:
                    if Camera.target.tags.get('p') > time * 2:
                        Global.menu.get_prompt(Dialog.get('starve'), Dialog.get('proceed'),
                                               self.starve, param=[time, self.moving])(None)
                    else:
                        Global.menu.get_prompt(Dialog.get('succumb'), Dialog.get('proceed'), self.succumb)(None)
                    self.moving = [0, 0]
                    return
            Global.map_view.update_region()
            Global.map_view.update_fog()
            self.moving = [0, 0]

    def succumb(self, arg):
        Global.menu.display(-1)
        Camera.target.die()

    def starve(self, arg):
        Global.menu.display(-1)
        hunger = Global.player.character.tags.get('hunger')
        Global.player.character.tags.set('hunger', 0)
        self.moving = arg[1]
        self.move()
        Global.player.character.tags.increment('hunger', hunger)
        Global.player.character.decay(arg[0] * 3)

    def remove(self):
        Turn.update = self.backup

    def input(self, action):
        self.next_action = action

    def action(self):
        if self.next_action == 'left':
            self.moving = [-1, 0]
        elif self.next_action == 'up':
            self.moving = [0, -1]
        elif self.next_action == 'right':
            self.moving = [1, 0]
        elif self.next_action == 'down':
            self.moving = [0, 1]
        else:
            return False
        return True
