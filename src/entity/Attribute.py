from src.tools.Data import Data
from src.tools.Tag import Tag


class Attribute(Tag):
    ADD_ON = None

    def __init__(self, host):
        super().__init__()
        self.host = host

    def update(self):
        if 'col' in self.attributes:
            self.host.collision_type = self.attributes['col']
        if 'ob' in self.attributes:
            self.host.obstruct_type = self.attributes['ob']
        if 'pivx' in self.attributes:
            self.host.form.image.anchor_x = self.attributes['pivx']
        if 'pivy' in self.attributes:
            self.host.form.image.anchor_y = int(self.host.form.height / 2) + self.attributes['pivy']

    def add_tag(self, host):
        add_tag = self.remove('+')
        if add_tag:
            seed = host.get_seed()
            from src.game import Global
            Global.r_t.reset(seed)
            new_tags = add_tag.split('&')
            for line in new_tags:
                data = Attribute.ADD_ON[line]
                tag = Global.r_t.rand_list(data)
                if tag:
                    if isinstance(tag, list):
                        for one_tag in tag:
                            tag_parts = one_tag.split(':')
                            self.increment(tag_parts[0], Data.parse(tag_parts[1])[0])
                    else:
                        tag_parts = tag.split(':')
                        self.increment(tag_parts[0], Data.parse(tag_parts[1])[0])
            self.add_tag(host)

    def get_level(self):
        return self.get('str', 0) + self.get('sth', 0) + self.get('int', 0) + self.get('cha', 0)
