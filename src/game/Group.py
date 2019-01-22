from src.form.GroupSprite import GroupSprite
from src.interface.GroupInterface import GroupInterface


class Group:
    background = GroupSprite()
    gui = GroupSprite()
    updates = []
    interface = GroupInterface()

    @staticmethod
    def remove(arg):
        if arg in Group.background:
            Group.background.remove(arg)
        if arg in Group.gui:
            Group.gui.remove(arg)
        if arg in Group.interface:
            Group.interface.remove(arg)
        if arg in Group.updates:
            Group.updates.remove(arg)

    @staticmethod
    def update():
        for i in Group.updates:
            i.update()
