import base
from .. import graphics
from .. import fonts
import time


class DitherTestPanel(base.Panel):
    def __init__(self):
        self.needs_redraw = True
        self.img = graphics.Surface(filename='assets/dithertest.png')
        self.img.dither()

    def update(self):
        pass

    def paint(self, surface):
        surface.bitblt(self.img, 0, 0)

    def up_pressed(self):
        pass

    def down_pressed(self):
        pass

    def center_pressed(self):
        pass


class AnimationTestPanel(base.Panel):
    def __init__(self):
        self.needs_redraw = True
        self.fps_font = fonts.get('tempesta', 8)
        self.img = fonts.get('tempesta', 16).render('piradio')
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

    def paint(self, surface):
        framestart = time.time()
        surface.fill(0)
        surface.bitblt(self.img, self.x, self.y)
        surface.text(self.fps_font, 0, 0, '%.1f fps' % self.fps)
        frameend = time.time()
        self.fps = 1.0 / (frameend - framestart)

    def up_pressed(self):
        pass

    def down_pressed(self):
        pass

    def center_pressed(self):
        pass
