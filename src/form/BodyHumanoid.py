from src.form.Body import Body


class BodyHumanoid(Body):
    def __init__(self, model_name, host):
        super().__init__(model_name)
        self.host = host

    def set_row(self, row):
        self.row = row
        t = row
        for i in self.order[self.direction - 1]:
            t += 1
            if i >= 0:
                self.organs[i].form.z = t
            elif i == -2:
                if self.host.weapon:
                    self.host.weapon.form.z = t
            elif i == -3:
                if self.host.headgear:
                    self.host.headgear.form.z = t

    def update_perspective(self):
        numeral = Body.TEXTURE_DIRECTION[self.direction] * self.texture_count
        t = self.row
        for i in self.order[self.direction - 1]:
            t += 1
            if i >= 0:
                organ = self.organs[i]
                if organ.texture_num == -1:
                    organ.form.switch(Body.TEXTURE_DIRECTION[self.direction])
                else:
                    organ.form.switch(organ.texture_num + numeral)
                organ.form.reset()
                organ.set(organ.form)
                organ.flip(self.side, self.direction)
                organ.form.z = t
            elif i == -2:
                if self.host.weapon:
                    self.host.weapon.form.z = t
            elif i == -3:
                if self.host.headgear:
                    self.host.headgear.form.z = t
