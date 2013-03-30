import logging
import os
import fontlib
import datetime
import audiolib
import time
import graphics
import json
import commons
import ui
import weather

import fakelcd as lcd
# import lcd

class Panel(object):
    def __init__(self):
        pass

    def paint(self, surface):
        pass

    def down_pressed(self):
        pass

    def up_pressed(self):
        pass

class ClockPanel(Panel):
    def __init__(self):
        self.needs_redraw = True
        self.clock_font = fontlib.Font(CLOCK_FONT_PATH, 40)

    def update(self):
        self.needs_redraw = True

    def paint(self, framebuffer):
        time_of_day = str(datetime.datetime.now().strftime('%H:%M'))
        framebuffer.fill(0)
        framebuffer.center_text(self.clock_font, time_of_day)
        self.needs_redraw = True

    def up_pressed(self):
        pass

    def down_pressed(self):
        pass

    def center_pressed(self):
        pass

class WeatherPanel(Panel):
    def __init__(self, city):
        self.city = city
        self.font = fontlib.Font(FONT_PATH, 16)
        logging.info('Getting weather for %s', self.city)
        self.w = weather.weather(self.city)

    def update(self):
        self.needs_redraw = True

    def paint(self, framebuffer):
        framebuffer.fill(0)
        framebuffer.text(self.font, 0, 0, self.w[0])
        framebuffer.center_text(self.font, '%.1f C' % self.w[1])

    def up_pressed(self):
        pass

    def down_pressed(self):
        pass

    def center_pressed(self):
        pass

class DitherTestPanel(Panel):
    def __init__(self):
        self.needs_redraw = True
        self.img = graphics.Surface(filename='assets/dithertest.png')
        self.img.dither()

    def update(self):
        self.needs_redraw = True

    def paint(self, framebuffer):
        framebuffer.bitblt(self.img, 0, 0)
        self.needs_redraw = True

    def up_pressed(self):
        pass

    def down_pressed(self):
        pass

    def center_pressed(self):
        pass

class AnimationTestPanel(Panel):
    def __init__(self):
        self.needs_redraw = True
        font = fontlib.Font(FONT_PATH, 16)
        self.img = font.render('piradio')
        self.x = 0
        self.y = 0
        self.dirx = 1
        self.diry = 1

    def update(self):
        self.x += self.dirx
        self.y += self.diry
        if self.x < -5 or self.x + self.img.width -5 >= lcd.LCD_WIDTH:
            self.dirx = -self.dirx
        if self.y < -5 or self.y + self.img.height -5 >= lcd.LCD_HEIGHT:
            self.diry = -self.diry
        self.needs_redraw = True

    def paint(self, framebuffer):
        framebuffer.fill(0)
        framebuffer.bitblt(self.img, self.x, self.y)
        self.needs_redraw = True

    def up_pressed(self):
        pass

    def down_pressed(self):
        pass

    def center_pressed(self):
        pass

class RadioPanel(Panel):
    def __init__(self):
        self.font = fontlib.Font(FONT_PATH, 8)
        self.glyph_font = fontlib.Font(GLYPHFONT_PATH, 10)
        self.stations = json.loads(open('stations.json').read())['stations']
        print self.stations

        self.cy = 0
        self.currstation = ''
        self.prev_timestr = ''
        self.needs_redraw = True

    def update(self):
        self.update_clock()

    def paint(self, framebuffer):
        # Clear the framebuffer
        framebuffer.fill(0)

        # If necessary, draw the 'playing' icon and the name of the current station
        if self.currstation:
            w, h, baseline = self.glyph_font.text_extents(self.currstation)
            framebuffer.text(self.glyph_font, 0, -baseline-1, GLYPH_PLAYING)

            w, h, baseline = self.font.text_extents(self.currstation)
            framebuffer.text(self.font, 10, 2 - baseline, self.currstation)

        # Draw the clock
        w, h, baseline = self.font.text_extents(self.timestr)
        framebuffer.text(self.font, framebuffer.width - w - 2, 2-baseline, self.timestr)

        # Draw separator between the 'status area' and the station selector
        framebuffer.hline(11)

        # Draw the station selector
        ui.render_list(framebuffer, 2, 14, self.font, self.stations.keys(), self.cy, minheight=12)

    def up_pressed(self):
        self.cy -= 1
        self.cy = commons.clamp(self.cy, 0, len(self.stations)-1)
        self.needs_redraw = True

    def down_pressed(self):
        self.cy += 1
        self.cy = commons.clamp(self.cy, 0, len(self.stations)-1)
        self.needs_redraw = True

    def center_pressed(self):
        if self.currstation == self.stations.keys()[self.cy]:
            logging.debug('Stopping playback')
            audiolib.stop()
            self.currstation = ''
        else:
            logging.debug('Switching station')
            audiolib.playstream(self.stations.values()[self.cy], fade=False)
            self.currstation = self.stations.keys()[self.cy]
        self.needs_redraw = True

    def update_clock(self):
        self.timestr = str(datetime.datetime.now().strftime('%H:%M'))
        if self.timestr != self.prev_timestr:
            self.prev_timestr = self.timestr
            logging.debug('Redrawing the clock')
            self.needs_redraw = True

FONT_PATH = os.path.join(os.getcwd(), 'assets/font.ttf')
GLYPHFONT_PATH = os.path.join(os.getcwd(), 'assets/pixarrows.ttf')
CLOCK_FONT_PATH = os.path.join(os.getcwd(), 'assets/font.ttf')
GLYPH_PLAYING = '0'#unichr(9654)

LCD_SLEEPTIME = 5 * 60
UPDATE_RATE = 60.0

# Possible panels, by priority:
# wheather
# timer
# wifi-test
# settings
# public transport
# random images
# twitter
# newsticker
# emails
PANELS = [RadioPanel(), ClockPanel(), WeatherPanel('munich,de'), DitherTestPanel(), AnimationTestPanel()]

logger = logging.getLogger('client')
logger.info('Starting up')

class SleepManager(object):
    def __init__(self):
        self.sleeptime = None
        self.sleeping = False

    def shouldsleep(self):
        return time.time() > self.sleeptime

    def resetsleep(self):
        self.sleeptime = time.time() + LCD_SLEEPTIME
        logging.debug('Sleeptime set to %f', self.sleeptime)

    def sleep(self):
        logging.info('Going to sleep')
        lcd.set_backlight_enabled(False)
        self.sleeping = True
        global UPDATE_RATE
        UPDATE_RATE /= 4

    def wakeup(self):
        logging.info('Waking up')
        lcd.set_backlight_enabled(True)
        self.sleeping = False
        global UPDATE_RATE
        UPDATE_RATE *= 4

    def update_sleep(self):
        if not self.sleeping and self.shouldsleep():
            self.sleep()
        elif self.sleeping and not self.shouldsleep():
            self.wakeup()
            self.resetsleep()

class RadioApp(object):
    def __init__(self):
        self.sleepmanager = SleepManager()
        self.framebuffer = None
        self.prev_keystates = None
        self.activate_panel(0)

    @property
    def needs_redraw(self):
        if self.active_panel:
            return self.active_panel.needs_redraw
        return False

    def run(self):
        self.sleepmanager.resetsleep()
        self.framebuffer = graphics.Surface(lcd.LCD_WIDTH, lcd.LCD_HEIGHT)
        audiolib.stop()
        lcd.init()

        while True:
            self.sleepmanager.update_sleep()
            self.trigger_key_events()
            self.active_panel.update()

            if self.needs_redraw:
                self.redraw()
                self.active_panel.needs_redraw = False

            time.sleep(1.0 / UPDATE_RATE)

    def lcd_update(self):
        logging.debug('Updating LCD')
        lcd.update(self.framebuffer)

    def trigger_key_events(self):
        keystates = lcd.readkeys()
        if keystates != self.prev_keystates:
            for i in range(len(keystates)):
                if keystates[i]:
                    self.on_key_down(i)
        self.prev_keystates = keystates

    def on_key_down(self, key):
        self.sleepmanager.resetsleep()

        # Forward up, down, and center button presses to the active panel.
        if key == lcd.K_UP:
            self.active_panel.up_pressed()
        if key == lcd.K_DOWN:
            self.active_panel.down_pressed()
        if key == lcd.K_CENTER:
            self.active_panel.center_pressed()

        # Left and right button presses switch to another panel.
        if key == lcd.K_LEFT:
            self.activate_panel(self.panel_idx - 1)
        if key == lcd.K_RIGHT:
            self.activate_panel(self.panel_idx + 1)

    def redraw(self):
        self.active_panel.paint(self.framebuffer)
        self.lcd_update()

    def activate_panel(self, panel_idx):
        self.panel_idx = commons.clamp(panel_idx, 0, len(PANELS) - 1)
        self.active_panel = PANELS[self.panel_idx]
        self.active_panel.needs_redraw = True
        logging.debug('Activated panel %s', self.active_panel.__class__.__name__)

if __name__ == '__main__':
    app = RadioApp()
    app.run()