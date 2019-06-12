def none(arg, loc, objects):
    pass


def field(arg, loc, objects):
    new = []
    for obj in objects:
        if obj.name == 'Estate':
            obj.remove()
            new += obj.build('field')
        else:
            new.append(obj)
    return new


def hostile(loc, arg):
    pass
