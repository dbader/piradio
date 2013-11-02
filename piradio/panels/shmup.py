import time
import piradio.fonts as fonts
import piradio.graphics as graphics
from . import base


class ShootEmUpGamePanel(base.Panel):
    def __init__(self):
        super(ShootEmUpGamePanel, self).__init__()

        self.fps = 0
        self.bg_scroll_offset = 0
        self.fg_scroll_offset = 0
        self.ship_x = 5
        self.ship_y = 24
        self.shots = []

        # Load assets
        self.fps_font = fonts.get('tempesta', 8)
        self.background_img = graphics.Surface(
            filename='assets/shmup/background.png',
            dither=True
        )
        self.foreground_img = graphics.Surface(
            filename='assets/shmup/foreground.png',
            dither=True
        )
        self.ship_img = graphics.Surface(
            filename='assets/shmup/ship.png',
        )

    def update(self):
        self.bg_scroll_offset += 1
        self.fg_scroll_offset += 2

        if (self.bg_scroll_offset >= self.background_img.width - 128 or
            self.fg_scroll_offset >= self.foreground_img.width - 128):
            self.bg_scroll_offset = 0
            self.fg_scroll_offset = 0

        gc_shots = []
        for shot in self.shots:
            shot[0] += 4
            if shot[0] < 128 and shot[1] < 64:
                gc_shots.append(shot)

        self.shots = gc_shots

        self.set_needs_repaint()

    def up_pressed(self):
        self.ship_y -= 1

    def down_pressed(self):
        self.ship_y += 1

    def center_pressed(self):
        self.shots.append([self.ship_x, self.ship_y+2])
        self.shots.append([self.ship_x, self.ship_y+14])

    def paint(self, surface):
        framestart = time.time()

        surface.bitblt_scrolled(
            self.background_img,
            self.bg_scroll_offset
        )

        surface.bitblt(
            self.ship_img,
            self.ship_x,
            self.ship_y,
            op=graphics.rop_or
        )

        for shot in self.shots:
            surface.setpixel(shot[0], shot[1])
            surface.setpixel(shot[0]+1, shot[1])
            surface.setpixel(shot[0]+2, shot[1])
            surface.setpixel(shot[0]+3, shot[1])

        surface.bitblt_scrolled(
            self.foreground_img,
            self.fg_scroll_offset,
            op=graphics.rop_or
        )

        # surface.text(self.fps_font, 0, 0, '%.1f fps' % self.fps)
        frameend = time.time()
        self.fps = 1.0 / (frameend - framestart)
