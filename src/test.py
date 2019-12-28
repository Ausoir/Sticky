from pyglet.gl import *
from pyglet.window import key

WINDOW = 400
INCREMENT = 5


class Window(pyglet.window.Window):
    # Cube 3D start rotation
    xRotation = yRotation = 30

    def __init__(self, width, height, title=''):
        super(Window, self).__init__(width, height, title)
        glClearColor(0, 0, 0, 1)
        glEnable(GL_DEPTH_TEST)
        from pyglet.graphics import Batch
        self.batch = Batch()
        from src.form.TextureBindGroup import TextureBindGroup
        texture1 = pyglet.image.load('../data/Error.png').get_texture()
        self.vlist = self.batch.add(4, GL_QUADS, TextureBindGroup(texture1), 'v3f', 't2f')
        self.vlist.vertices = [50,50,50, 50,-50,50, -50,-50,50, -50,50,50]
        self.vlist.tex_coords = [1, 1, 1, 0, 0, 0, 0, 1]
        texture2 = pyglet.image.load('../data/Icon.png').get_texture()
        self.vlist2 = self.batch.add(4, GL_QUADS, TextureBindGroup(texture2), 'v3f', 't2f')
        self.vlist2.vertices = [150,50,50, 150,-50,50, 0,-50,50, 0,50,50]
        self.vlist2.tex_coords = [1, 1, 1, 0, 0, 0, 0, 1]

    def on_draw(self):
        # Clear the current GL Window
        self.clear()
        self.batch.draw()

    def on_resize(self, width, height):
        # set the Viewport
        glViewport(0, 0, width, height)

        # using Projection mode
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        aspectRatio = width / height
        gluPerspective(35, aspectRatio, 1, 1000)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, -400)

    def on_text_motion(self, motion):
        if motion == key.UP:
            self.vlist.vertices[2] += 4
            self.vlist.vertices[5] += 4
        elif motion == key.DOWN:
            self.vlist.vertices[2] -= 4
            self.vlist.vertices[5] -= 4
        elif motion == key.LEFT:
            self.yRotation -= INCREMENT
        elif motion == key.RIGHT:
            self.yRotation += INCREMENT

    def loop(self, dt):
        Window.xRotation += 1
        Window.yRotation += 1


if __name__ == '__main__':
    main = Window(WINDOW, WINDOW, 'Pyglet Colored Cube')
    pyglet.clock.schedule_interval(main.loop, 1)
    pyglet.app.run()
