from src.tools.Tag import Tag


class Attribute(Tag):
    def __init__(self, host):
        super().__init__()
        self.host = host

    def update(self):
        if 'p' in self.attributes:
            self.host.hittable = 1
        else:
            self.host.hittable = 0
        if 'col' in self.attributes:
            cols = []
            for i in str(self.attributes['col']):
                cols.append(int(i))
            self.host.collision_type = cols
        if 'ob' in self.attributes:
            self.host.obstruct_type = self.attributes['ob']
        if 'pivx' in self.attributes:
            self.host.form.image.anchor_x = self.attributes['pivx']
        if 'pivy' in self.attributes:
            self.host.form.image.anchor_y = int(self.host.form.height / 2) + self.attributes['pivy']
        if 'seed' in self.attributes:
            from src.game import Global
            if self.attributes['seed'] == -1:
                seed = Global.r.rand_int(1, 9999)
                self.attributes['seed'] = seed
                Global.r_t.reset(seed)
            add_tag = self.remove('+')
            if add_tag:
                new_tags = add_tag.split('&')
                from src.tools.Data import Data
                for line in new_tags:
                    data = Data.get_line('attributes.txt', line)[1]
                    tag = Global.r_t.rand_list(data)
                    if tag:
                        if isinstance(tag, list):
                            for one_tag in tag:
                                tag_parts = one_tag.split(':')
                                self.increment(tag_parts[0], Data.parse(tag_parts[1])[0])
                        else:
                            tag_parts = tag.split(':')
                            self.increment(tag_parts[0], Data.parse(tag_parts[1])[0])

    def get_carry_over(self):
        permanent = ['money', 'seed', 'full']
        return (lambda keys: {x: self.attributes[x] for x in keys})(permanent)
