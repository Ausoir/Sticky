from src.form.GroupSprite import GroupSprite
from src.interface.GroupInterface import GroupInterface


class Group:
    background = GroupSprite()
    object = GroupSprite()
    unit = GroupSprite()
    gui = GroupSprite()
    interface = GroupInterface()

    @staticmethod
    def remove(arg):
        Group.background.remove(arg)
        Group.object.remove(arg)
        Group.unit.remove(arg)
        Group.gui.remove(arg)

    @staticmethod
    def draw(surface):
        Group.background.draw(surface)
        Group.object.draw(surface)
        Group.unit.draw(surface)
        Group.gui.draw(surface)
