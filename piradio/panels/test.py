import base
from .. import graphics
from .. import fontlib
import time


class DitherTestPanel(base.Panel):
    def __init__(self):
        self.needs_redraw = True
        self.img = graphics.Surface(filename='assets/dithertest.png')
        self.img.dither()

    def update(self):
        pass

    def paint(self, framebuffer):
        framebuffer.bitblt(self.img, 0, 0)

    def up_pressed(self):
        pass

    def down_pressed(self):
        pass

    def center_pressed(self):
        pass


class AnimationTestPanel(base.Panel):
    def __init__(self):
        self.needs_redraw = True
        font = fontlib.get('tempesta', 16)
        self.fps_font = fontlib.get('tempesta', 8)
        self.img = font.render('piradio')
        self.x = 0
        self.y = 0
        self.dirx = 3
        self.diry = 3
        self.fps = 0

    def update(self):
        self.x += self.dirx
        self.y += self.diry
        if self.x < -5 or self.x + self.img.width - 5 >= 128:
            self.dirx = -self.dirx
        if self.y < -5 or self.y + self.img.height - 5 >= 64:
            self.diry = -self.diry
        self.needs_redraw = True

    def paint(self, framebuffer):
        framestart = time.time()
        framebuffer.fill(0)
        framebuffer.bitblt(self.img, self.x, self.y)
        framebuffer.text(self.fps_font, 0, 0, '%.1f fps' % self.fps)
        frameend = time.time()
        self.fps = 1.0 / (frameend - framestart)

    def up_pressed(self):
        pass

    def down_pressed(self):
        pass

    def center_pressed(self):
        pass
