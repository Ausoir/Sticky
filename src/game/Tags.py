class Tags:
    inactive = '!'
    interactive = '@'
    climb = 'cli'
    front = 'bf'
    float = 'xg'
    intangible = 'xc'
    indestructible = 'xh'
    back = 'cb'
    fog = 'cf'
    land = 'cd'
    flesh = 'if'
    insubstantial = 'ix'
    metal = 'im'
    wood = 'iw'
    silver = 'is'
    sharp = 'ps'
    combustible = 'pf'
    intelligent = 'ii'
    listener = 'il'
    lightweight = 'ig'

    @staticmethod
    def name(tag):
        for k, v in vars(Tags).items():
            if v == tag:
                return k

    @staticmethod
    def is_property(tag):
        prop_tag = [Tags.flesh, Tags.insubstantial, Tags.metal, Tags.wood, Tags.silver, Tags.sharp]
        return tag in prop_tag

    @staticmethod
    def is_combustible(tags):
        combustibles = [Tags.flesh, Tags.wood, Tags.combustible]
        return any(elem in combustibles for elem in tags)
