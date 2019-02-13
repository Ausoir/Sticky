from src.map.Tile import Tile


class Flee:
    def __init__(self, host):
        self.host = host

    def hunt(self, target):
        dist = self.host.pos[0] - target.pos[0]
        if self.host.get_offset_tile(dir, 0).is_land(Tile.CHECK_LARGE):
            self.host.input('jump', dist.to_list())
        else:
            self.host.input('walk', dist.to_list())


class Melee:
    def __init__(self, host):
        self.host = host

    def hunt(self, target):
        if not self.attack(target):
            if not self.chase(target):
                return 0
        return 1

    def chase(self, target):
        dist = target.pos[0] - self.host.pos[0]
        direction = 1 if dist.x >= 0 else -1
        blocked = self.host.get_offset_tile(direction, 0).is_land(Tile.CHECK_LARGE)
        if not blocked:
            self.host.input('walk', dist.to_list())
            return 1
        jumpblock = self.host.get_offset_tile(direction, -1).is_land(Tile.CHECK_LARGE)
        if blocked:
            if not jumpblock:
                self.host.input('jump', dist.to_list())
                return 1
            elif not self.host.get_offset_tile(-direction, 0).is_land(Tile.CHECK_LARGE):
                self.host.input('walk', (-dist).to_list())
                return 1
            elif not self.host.get_offset_tile(-direction, -1).is_land(Tile.CHECK_LARGE):
                self.host.input('jump', (-dist).to_list())
                return 1
            return 0
        jumpblock_forward = self.host.get_offset_tile(direction*2, -1).is_land(Tile.CHECK_LARGE)
        blocked_forward = self.host.get_offset_tile(direction*2, 0).is_land(Tile.CHECK_LARGE)
        if blocked_forward:
            if not jumpblock_forward:
                if not jumpblock:
                    self.host.input('jump', dist.to_list())
                    return 1
        return 0

    def in_range(self, x):
        for i in self.host.weapon.range:
            if i == x:
                return 1
        return 0

    def attack(self, target):
        dist = target.pos[0] - self.host.pos[0]
        if abs(dist.x) == 1 and 0 <= dist.y <= 1 and 'kick' in self.host.action.skills:
            self.host.input('kick', dist.to_list())
            return 1
        longest_range = 0
        for i in self.host.weapon.range:
            if i > longest_range:
                longest_range = i
        reach = self.host.location.collide_line(self.host.get_interact_pos(), dist.x, dist.y,
                                                distance=longest_range, flag=Tile.CHECK_TERRAIN)
        reach = reach - self.host.get_interact_pos()
        if self.in_range(abs(dist.x)) and abs(reach.x) >= abs(dist.x):
            if -1 <= dist.y <= 1:
                self.host.input('use', dist.to_list())
                return 1
        if -1 <= dist.y <= 0:
            destination = self.host.location.collide_line(self.host.pos[0], dist.x, 0, distance=4, flag=Tile.CHECK_LARGE)
            destination = destination - self.host.pos[0]
            x = min(abs(dist.x), abs(destination.x))
            if x == 1 and 'lunge' in self.host.action.skills:
                self.host.input('lunge', dist.to_list())
                return 1
            if x == 3 and 'dash' in self.host.action.skills:
                self.host.input('dash', dist.to_list())
                return 1
        return 0
