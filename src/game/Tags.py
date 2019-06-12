class Tags:
    inactive = '!'
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
    armor = 'amr'
    humanoid = 'hum'
    furniture = 'frn'
    flesh = 'if'
    metal = 'im'
    wood = 'iw'
    terrain = 'it'
    jewel = 'ij'
    silver = 'is'
    paper = 'ip'
    fiery = 'ifi'
    sharp = 'ps'
    scribing = 'pw'

    @staticmethod
    def name(tag):
        for k, v in vars(Tags).items():
            if v == tag:
                return k
