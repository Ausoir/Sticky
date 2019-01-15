from src.interface.Window import Window


class Menu:
    window = None

    @staticmethod
    def init():
        Menu.window = Window((400, 300))
        Menu.window.pos.load(100, 100)

    @staticmethod
    def display():
        Menu.window.display()
        Menu.window.hover = lambda x: x + 1
