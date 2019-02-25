from src.form.GroupSprite import GroupSprite


class Group:
    objects = GroupSprite()
    effects = GroupSprite()
    updates = []

    @staticmethod
    def remove(arg):
        if arg in Group.effects:
            Group.effects.remove(arg)
        if arg in Group.objects:
            Group.objects.remove(arg)
        if arg in Group.updates:
            Group.updates.remove(arg)

    @staticmethod
    def update():
        for i in Group.updates:
            i.update()
