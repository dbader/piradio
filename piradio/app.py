import logging
import os
import fontlib
import services.audio
import time
import graphics
import json
import ui

from panels import *


CONFIG = json.loads(open('config.json').read())
UPDATE_RATE = float(CONFIG['update_rate_hz'])

logger = logging.getLogger('client')
logger.info('Starting up')


class SleepTimer(object):
    def __init__(self, sleep_after_minutes):
        self.sleep_after_minutes = sleep_after_minutes
        self.sleeptime = None
        self.sleeping = False

    def shouldsleep(self):
        return time.time() > self.sleeptime

    def resetsleep(self):
        self.sleeptime = time.time() + self.sleep_after_minutes

    def sleep(self):
        logging.info('Going to sleep')
        lcd.set_backlight_enabled(False)
        self.sleeping = True
        global UPDATE_RATE
        UPDATE_RATE = float(CONFIG['update_rate_sleep_hz'])

    def wakeup(self):
        logging.info('Waking up')
        lcd.set_backlight_enabled(True)
        self.sleeping = False
        global UPDATE_RATE
        UPDATE_RATE = float(CONFIG['update_rate_hz'])

    def update_sleep(self):
        if not self.sleeping and self.shouldsleep():
            self.sleep()
        elif self.sleeping and not self.shouldsleep():
            self.wakeup()
            self.resetsleep()


class RadioApp(object):
    def __init__(self):
        assert lcd, 'app.lcd must be set externally to a valid LCD driver'

        fontlib.register('tempesta', os.path.join(os.getcwd(), 'assets/pf_tempesta_seven.ttf'))
        fontlib.register('pixarrows', os.path.join(os.getcwd(), 'assets/pixarrows.ttf'))
        fontlib.register('climacons', os.path.join(os.getcwd(), 'assets/climacons.ttf'))
        fontlib.register('helvetica', os.path.join(os.getcwd(), 'assets/helvetica.ttf'))

        self.sleeptimer = SleepTimer(CONFIG['sleep_after_minutes'] * 60)
        self.framebuffer = None
        self.prev_keystates = None
        self.font = fontlib.get('tempesta', 8)
        self.panels = []

    def read_panels(self, panels):
        ps = []
        for p in panels:
            classname = p[0]
            args = p[1:]
            logging.info('Looking up class %s', classname)
            clazz = globals()[classname]
            ps.append((clazz, args))
        return ps

    @property
    def needs_redraw(self):
        if self.active_panel:
            return self.active_panel.needs_redraw
        return False

    def addpanel(self, panel_class, *args):
        self.framebuffer.fill(0)
        ui.render_progressbar(self.framebuffer,
                              2, self.framebuffer.height / 2 - 8,
                              self.framebuffer.width - 2 * 2, 16,
                              len(self.panels) / float(len(self.panel_defs)))
        self.framebuffer.center_text(self.font, panel_class.__name__, rop=graphics.rop_xor)
        self.lcd_update()
        lcd.readkeys()
        logging.info('Initializing %s', panel_class.__name__)
        try:
            self.panels.append(panel_class(*args))
        except Exception as e:
            logging.error('Failed to initialize panel %s', panel_class.__name__)
            logging.exception(e)

    def run(self):
        self.sleeptimer.resetsleep()
        services.audio.stop()
        lcd.init()
        self.framebuffer = graphics.Surface(lcd.LCD_WIDTH, lcd.LCD_HEIGHT)
        lcd.set_backlight_enabled(True)

        logging.info('Initializing panels')
        self.panel_defs = self.read_panels(CONFIG['panels'])
        for p, args in self.panel_defs:
            self.addpanel(p, *args)
        self.activate_panel(0)

        while True:
            self.sleeptimer.update_sleep()
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
        self.sleeptimer.resetsleep()

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
        self.panel_idx = panel_idx % len(self.panels)
        self.active_panel = self.panels[self.panel_idx]
        self.active_panel.needs_redraw = True
        logging.debug('Activated panel %s', self.active_panel.__class__.__name__)
