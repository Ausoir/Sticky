from src.form.GroupSprite import GroupSprite
from src.interface.GroupInterface import GroupInterface


class Group:
    background = GroupSprite()
    object = GroupSprite()
    unit = GroupSprite()
    gui = GroupSprite()
    updates = []
    interface = GroupInterface()

    @staticmethod
    def remove(arg):
        if arg in Group.background:
            Group.background.remove(arg)
        if arg in Group.object:
            Group.object.remove(arg)
        if arg in Group.unit:
            Group.unit.remove(arg)
        if arg in Group.gui:
            Group.gui.remove(arg)
        if arg in Group.interface:
            Group.interface.remove(arg)
        if arg in Group.updates:
            Group.updates.remove(arg)

    @staticmethod
    def draw(surface):
        Group.background.draw(surface)
        Group.object.draw(surface)
        Group.unit.draw(surface)
        Group.gui.draw(surface)

    @staticmethod
    def update():
        for i in Group.updates:
            i.update()
