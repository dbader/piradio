# Possible panels, by priority:
# timer
# wifi-test
# settings
# public transport
# random images
# twitter
# newsticker
# emails

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
import podcast
import random
import mvg

try:
    import lcd
except OSError:
    import fakelcd as lcd

class Panel(object):
    def __init__(self):
        pass

    def update(self):
        pass

    def paint(self, surface):
        pass

    def up_pressed(self):
        pass

    def down_pressed(self):
        pass

    def center_pressed(self):
        pass

class ClockPanel(Panel):
    def __init__(self):
        self.clock_font = fontlib.Font(CLOCK_FONT_PATH, 32)
        self.prev_timestr = None

    def update(self):
        self.timestr = str(datetime.datetime.now().strftime('%H:%M'))
        if self.timestr != self.prev_timestr:
            self.prev_timestr = self.timestr
            logging.debug('Redrawing the clock')
            self.needs_redraw = True

    def paint(self, framebuffer):
        framebuffer.fill(0)
        framebuffer.center_text(self.clock_font, self.timestr)

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
        pass

    def paint(self, framebuffer):
        framebuffer.fill(0)
        framebuffer.center_text(self.font, self.w[0], y=2)
        framebuffer.center_text(self.font, '%.1f C' % self.w[1])

    def up_pressed(self):
        pass

    def down_pressed(self):
        pass

    def center_pressed(self):
        logging.info('Getting weather for %s', self.city)
        self.w = weather.weather(self.city)
        self.needs_redraw = True

class PublicTransportPanel(Panel):
    def __init__(self, station):
        self.station = station
        self.font = fontlib.Font(FONT_PATH, 8)
        self.refresh()

    def refresh(self):
        logging.info('Getting public transport data for station %s', self.station)
        self.upcoming_trains = mvg.get_upcoming_trains(self.station)

    def update(self):
        pass

    def paint(self, framebuffer):
        def format_train(t):
            return '%s %s %s' % (str(t['minutes']).rjust(2, ' '), t['line'].rjust(3, ' '), t['destination'][:16])
        framebuffer.fill(0)
        framebuffer.fillrect(0, 0, framebuffer.width, 10)
        framebuffer.center_text(self.font, self.station, y=0, rop=graphics.rop_xor)
        framebuffer.hline(11)
        trains = map(format_train, self.upcoming_trains[:5])
        ui.render_static_list(framebuffer, 2, 14, self.font, trains, minheight=12)

    def up_pressed(self):
        pass

    def down_pressed(self):
        pass

    def center_pressed(self):
        self.refresh()
        self.needs_redraw = True

class RandomPodcastPanel(Panel):
    def __init__(self, feed_url):
        self.font = fontlib.Font(FONT_PATH, 8)
        logging.info('Loading podcast feed from %s', feed_url)
        self.episodes = podcast.load_podcast(feed_url)
        logging.info('Got %i episodes', len(self.episodes))
        self.select_random_episode()
        self.lastrefresh = 0

    def select_random_episode(self):
        self.episode_title, self.episode_url = random.choice(self.episodes)

    def update(self):
        if time.time() - self.lastrefresh > 10:
            self.lastrefresh = time.time()
            self.needs_redraw = True

    def paint(self, framebuffer):
        framebuffer.fill(0)
        framebuffer.center_text(self.font, self.episode_title)
        ui.render_progressbar(framebuffer, 0, 2, framebuffer.width, 16, audiolib.progress())

    def up_pressed(self):
        pass

    def down_pressed(self):
        pass

    def center_pressed(self):
        self.select_random_episode()
        self.needs_redraw = True
        audiolib.playstream(self.episode_url, fade=False)

class DitherTestPanel(Panel):
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

class AnimationTestPanel(Panel):
    def __init__(self):
        self.needs_redraw = True
        font = fontlib.Font(FONT_PATH, 16)
        self.fps_font = fontlib.Font(FONT_PATH, 8)
        self.img = font.render('piradio')
        self.x = 0
        self.y = 0
        self.dirx = 3
        self.diry = 3
        self.fps = 0

    def update(self):
        self.x += self.dirx
        self.y += self.diry
        if self.x < -5 or self.x + self.img.width -5 >= lcd.LCD_WIDTH:
            self.dirx = -self.dirx
        if self.y < -5 or self.y + self.img.height -5 >= lcd.LCD_HEIGHT:
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
            framebuffer.text(self.glyph_font, -3, -2, GLYPH_PLAYING)
            framebuffer.text(self.font, 7, 2, self.currstation)

        # Draw the clock
        w, h, baseline = self.font.text_extents(self.timestr)
        framebuffer.text(self.font, framebuffer.width - w, 2, self.timestr)

        # Draw separator between the 'status area' and the station selector
        framebuffer.hline(11)

        # Draw the station selector
        ui.render_list(framebuffer, 2, 14, self.font, self.stations.keys(), self.cy, minheight=12, maxvisible=4)

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

LCD_SLEEPTIME = 60 * 60
UPDATE_RATE = 60.0

logger = logging.getLogger('client')
logger.info('Starting up')

class SleepTimer(object):
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

PANELS = [
    (RadioPanel, ()),
    (ClockPanel, ()),
    (PublicTransportPanel, ('Hohenzollernplatz',)),
    (WeatherPanel, ('munich,de',)),
    (WeatherPanel, ('vancouver,ca',)),
    (DitherTestPanel, ()),
    (AnimationTestPanel, ()),
    (RandomPodcastPanel, ('http://domian.alpha-labs.net/domian.rss',)),
    # (RandomPodcastPanel, 'file://' + os.path.join(os.getcwd(),'assets/example.rss'))
]

class RadioApp(object):
    def __init__(self):
        self.sleepmanager = SleepTimer()
        self.framebuffer = None
        self.prev_keystates = None
        self.font = fontlib.Font(FONT_PATH, 8)
        self.panels = []

    @property
    def needs_redraw(self):
        if self.active_panel:
            return self.active_panel.needs_redraw
        return False

    def addpannel(self, pannel_class, *args):
        self.framebuffer.fill(0)
        ui.render_progressbar(self.framebuffer,
                              2, self.framebuffer.height / 2 - 8,
                              self.framebuffer.width - 2 * 2, 16,
                              len(self.panels) / float(len(PANELS)))
        self.framebuffer.center_text(self.font, pannel_class.__name__, rop=graphics.rop_xor)
        self.lcd_update()
        lcd.readkeys()
        try:
            self.panels.append(pannel_class(*args))
        except Exception as e:
            logging.error('Failed to initialize panel %s', pannel_class.__name__)
            logging.exception(e)

    def run(self):
        self.sleepmanager.resetsleep()
        audiolib.stop()
        lcd.init()
        self.framebuffer = graphics.Surface(lcd.LCD_WIDTH, lcd.LCD_HEIGHT)
        lcd.set_backlight_enabled(True)

        logging.info('Initializing panels')
        for p, args in PANELS:
            self.addpannel(p, *args)
        self.activate_panel(0)

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
        self.panel_idx = commons.clamp(panel_idx, 0, len(self.panels) - 1)
        self.active_panel = self.panels[self.panel_idx]
        self.active_panel.needs_redraw = True
        logging.debug('Activated panel %s', self.active_panel.__class__.__name__)

if __name__ == '__main__':
    RadioApp().run()
    # while True:
    #     try:
    #         logging.info("Booting app")
    #         app = RadioApp()
    #         app.run()
    #     except KeyboardInterrupt:
    #         logging.info('Shutting down')
    #         audiolib.stop()
    #         break
    #     except Exception as e:
    #         logging.exception(e)
