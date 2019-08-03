class Tags:
    inactive = '!'
    interactive = '@'
    climb = 'cli'
    back = 'bg'
    front = 'bf'
    float = 'xg'
    intangible = 'xc'
    indestructible = 'xh'
    fog = 'cf'
    land = 'cd'
    cover = 'cc'
    support = 'cs'
    humanoid = 'hum'
    flesh = 'if'
    plant = 'iv'
    insubstantial = 'ii'
    metal = 'im'
    wood = 'iw'
    silver = 'is'
    paper = 'ip'
    sharp = 'ps'
    scribing = 'pw'
    workable = 'pc'

    @staticmethod
    def name(tag):
        for k, v in vars(Tags).items():
            if v == tag:
                return k

    @staticmethod
    def is_property(tag):
        prop_tag = [Tags.flesh, Tags.plant, Tags.insubstantial, Tags.metal, Tags.wood, Tags.silver,
                    Tags.paper, Tags.sharp, Tags.scribing]
        return tag in prop_tag

    @staticmethod
    def is_combustible(tags):
        combustibles = [Tags.flesh, Tags.wood, Tags.plant, Tags.paper]
        return any(elem in combustibles for elem in tags)
