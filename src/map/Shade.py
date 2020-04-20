from src.form.Shape import Shape
from src.game import Global


class Shade:
    zero = (0, 0, 0, 0)
    wall_shade_color = (0, 0, 0, 120)
    wall_shade_meta = ((wall_shade_color, zero, zero, wall_shade_color),
                       (wall_shade_color, wall_shade_color, zero, zero),
                       (wall_shade_color, zero, zero, wall_shade_color),
                       (wall_shade_color, wall_shade_color, zero, zero))

    def __init__(self):
        self.overlay = Shape(0, 0, 600, Global.draw_group.group_overlay,
                             width=Global.BLOCK, height=Global.BLOCK, color=Shade.zero)
        self.shades = []
        quarter = int(Global.BLOCK / 8)
        for i in [(-quarter, Global.BLOCK), (Global.BLOCK, -quarter), (quarter, Global.BLOCK), (Global.BLOCK, quarter)]:
            shade = Shape(0, 0, 0, Global.draw_group.group_shade, width=i[0], height=i[1], color=Shade.zero)
            self.shades.append(shade)
        self.wall_shaders = [0, 0, 0, 0]
        self.overlay.add_batch()

    def remove(self):
        self.overlay.remove_batch()
        self.remove_shades()

    def remove_shades(self):
        for i in range(4):
            if self.wall_shaders[i] == 1:
                self.shades[i].remove_batch()
                self.wall_shaders[i] = 0

    def show(self, visible):
        self.overlay.show(visible)
        self.show_shades(visible)

    def show_shades(self, visible):
        for shade in self.shades:
            shade.show(visible)

    def update(self, x, y):
        self.overlay.update(x, y)
        if self.wall_shaders[0] == 1:
            self.shades[0].update(x, y)
        if self.wall_shaders[1] == 1:
            self.shades[1].update(x, y)
        if self.wall_shaders[2] == 1:
            self.shades[2].update(x + Global.BLOCK, y)
        if self.wall_shaders[3] == 1:
            self.shades[3].update(x, y + Global.BLOCK)

    def set_color(self, color):
        self.overlay.set_solid_color(color)

    def shade_walls(self, joint_neighbors):
        for k, v in enumerate(Shade.wall_shade_meta):
            if self.wall_shaders[k] == 0 and joint_neighbors[k] == 1:
                if self.shades[k].add_batch():
                    self.shades[k].set_gradient(v[0], v[1], v[2], v[3])
            elif self.wall_shaders[k] == 1 and joint_neighbors[k] == 0:
                self.shades[k].remove_batch()
            self.wall_shaders[k] = joint_neighbors[k]
