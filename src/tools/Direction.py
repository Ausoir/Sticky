numeral = {1: 1, 2: 2, 3: 1, 4: 0}
coord = {1: [-1, 0], 2: [0, -1], 3: [1, 0], 4: [0, 1]}
side = {1: -1, 2: -1, 3: 1, 4: 1}
opposite = {1: 3, 2: 4, 3: 1, 4: 2}


def add(direction, offset):
    r = (direction + offset) % 4
    if r == 0:
        return 4
    return r


def get_direction_toward(diff):
    horizontal = abs(diff[0]) >= abs(diff[1])
    if horizontal:
        if diff[0] < 0:
            return 1
        else:
            return 3
    else:
        if diff[1] < 0:
            return 2
        else:
            return 4
