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
        pass

    def paint(self, surface):
        pass

    def down_pressed(self):
        pass

    def up_pressed(self):
        pass

class RadioPanel(Panel):
    def __init__(self):
        pass

    def paint(self, surface):
        pass

    def down_pressed(self):
        pass

    def up_pressed(self):
        pass

FONT_PATH = os.path.join(os.getcwd(), 'assets/font.ttf')
GLYPHFONT_PATH = os.path.join(os.getcwd(), 'assets/pixarrows.ttf')
CLOCK_FONT_PATH = os.path.join(os.getcwd(), 'assets/font.ttf')
GLYPH_PLAYING = '0'#unichr(9654)

LCD_SLEEPTIME = 5
UPDATE_RATE = 60.0

PANELS = [RadioPanel(), ClockPanel()]
active_panel = PANELS[0]

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
        self.needs_redraw = True

        self.font = fontlib.Font(FONT_PATH, 8)
        self.glyph_font = fontlib.Font(GLYPHFONT_PATH, 10)
        self.stations = json.loads(open('stations.json').read())['stations']
        print self.stations

        self.cy = 0
        self.needs_redraw = True
        self.currstation = ''
        self.prev_timestr = ''

    def run(self):
        self.sleepmanager.resetsleep()
        audiolib.stop()
        self.framebuffer = graphics.Surface(lcd.LCD_WIDTH, lcd.LCD_HEIGHT)
        lcd.init()

        while True:
            self.sleepmanager.update_sleep()
            self.trigger_key_events()
            self.update_clock()

            if self.needs_redraw:
                self.redraw()
                self.needs_redraw = False

            time.sleep(1.0 / UPDATE_RATE)

    def lcd_update(self):
        # framebuffer.apply(lambda pixel: 0 if pixel else 1)
        # framebuffer.apply(lambda pixel: pixel * 200)
        # framebuffer.dither()
        # print repr(self.framebuffer)
        logging.debug('Updating LCD')
        lcd.update(self.framebuffer)

    def trigger_key_events(self):
        keystates = lcd.readkeys()
        if keystates != self.prev_keystates:
            for i in range(len(keystates)):
                if keystates[i]:
                    self.on_key_down(i)
        self.prev_keystates = keystates

    def dither_test(self):
        img = graphics.Surface(filename='assets/dithertest.png')
        img.dither()
        self.framebuffer.bitblt(img, 0, 0)
        self.lcd_update()
        time.sleep(5)

    def big_clock(self):
        time_of_day = str(datetime.datetime.now().strftime('%H:%M'))
        clock_font = fontlib.Font(CLOCK_FONT_PATH, 40)
        self.framebuffer.fill(0)
        self.framebuffer.center_text(clock_font, time_of_day)
        self.lcd_update()
        time.sleep(5)

    def on_key_down(self, key):
        self.sleepmanager.resetsleep()
        if key == lcd.K_UP:
            self.cy -= 1
            self.cy = commons.clamp(self.cy, 0, len(self.stations)-1)
        if key == lcd.K_DOWN:
            self.cy += 1
            self.cy = commons.clamp(self.cy, 0, len(self.stations)-1)
        if key == lcd.K_RIGHT:
            self.dither_test()
        if key == lcd.K_LEFT:
            self.big_clock()
        if key == lcd.K_CENTER:
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

    def redraw(self):
        # Clear the framebuffer
        self.framebuffer.fill(0)

        # If necessary, draw the 'playing' icon and the name of the current station
        if self.currstation:
            w, h, baseline = self.glyph_font.text_extents(self.currstation)
            self.framebuffer.text(self.glyph_font, 0, -baseline-1, GLYPH_PLAYING)

            w, h, baseline = self.font.text_extents(self.currstation)
            self.framebuffer.text(self.font, 10, 2 - baseline, self.currstation)

        # Draw the clock
        w, h, baseline = self.font.text_extents(self.timestr)
        self.framebuffer.text(self.font, self.framebuffer.width - w - 2, 2-baseline, self.timestr)

        # Draw separator between the 'status area' and the station selector
        self.framebuffer.hline(11)

        # Draw the station selector
        ui.render_list(self.framebuffer, 2, 14, self.font, self.stations.keys(), self.cy, minheight=12)

        self.lcd_update()

if __name__ == '__main__':
    app = RadioApp()
    app.run()