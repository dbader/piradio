import piradio.fonts as fonts
import piradio.graphics as graphics
import piradio.ui as ui
import piradio.lcd as lcd
import piradio.services as services
from piradio.panels import *

import logging
import os
import time
import json


CONFIG = json.loads(open('config.json').read())
UPDATE_RATE = float(CONFIG['update_rate_hz'])


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
        cwd = os.getcwd()
        fonts.register('tempesta',
                       os.path.join(cwd, 'assets/pf_tempesta_seven.ttf'))
        fonts.register('pixarrows', os.path.join(cwd, 'assets/pixarrows.ttf'))
        fonts.register('climacons', os.path.join(cwd, 'assets/climacons.ttf'))
        fonts.register('helvetica', os.path.join(cwd, 'assets/helvetica.ttf'))

        self.sleeptimer = SleepTimer(CONFIG['sleep_after_minutes'] * 60)
        self.framebuffer = None
        self.prev_keystates = None
        self.font = fonts.get('tempesta', 8)
        self.panels = []
        self.panel_defs = self.read_panels(CONFIG['panels'])
        self.panel_idx = None
        self.active_panel = None
        self.active_panel_fb = None
        self.backing_stores = {}
        self.broker = services.ServiceBroker()

    @staticmethod
    def read_panels(panels):
        ps = []
        for p in panels:
            classname = p[0]
            args = p[1]
            logging.info('Looking up class %s', classname)
            clazz = globals()[classname]
            ps.append((clazz, args))
        return ps

    @property
    def needs_repaint(self):
        if self.active_panel:
            return self.active_panel.needs_repaint
        return False

    def addpanel(self, panel_class, config):
        self.framebuffer.fill(0)
        ui.render_progressbar(self.framebuffer,
                              2, self.framebuffer.height / 2 - 8,
                              self.framebuffer.width - 2 * 2, 16,
                              len(self.panels) / float(len(self.panel_defs)))
        self.framebuffer.center_text(self.font, panel_class.__name__,
                                     rop=graphics.rop_xor)
        self.lcd_update()
        lcd.readkeys()
        logging.info('Initializing %s', panel_class.__name__)
        try:
            instance = self.broker.instantiate(panel_class, config)
            self.panels.append(instance)
            self.backing_stores[instance] = graphics.Surface(lcd.LCD_WIDTH,
                                                             lcd.LCD_HEIGHT)
        except Exception as e:
            logging.error('Failed to initialize panel %s',
                          panel_class.__name__)
            logging.exception(e)

    def run(self):
        try:
            self.sleeptimer.resetsleep()
            lcd.init()
            self.framebuffer = graphics.Surface(lcd.LCD_WIDTH, lcd.LCD_HEIGHT)
            lcd.set_backlight_enabled(True)

            self.broker.register_service(services.clock.ClockService)
            self.broker.register_service(services.weather.WeatherService)
            self.broker.register_service(services.podcast.PodcastService)
            self.broker.register_service(services.audio.AudioService)

            logging.info('Initializing panels %s', self.panel_defs)
            for p, args in self.panel_defs:
                self.addpanel(p, args)
            self.activate_panel(0)

            self.broker.start_bound_services()

            while True:
                services.deliver_pending_notifications()
                self.sleeptimer.update_sleep()
                self.trigger_key_events()
                self.active_panel.update()
                if self.activate_panel:
                    if self.active_panel.paint_if_needed(self.active_panel_fb):
                        logging.debug('Updating LCD (active_panel)')
                        lcd.update(self.active_panel_fb)
                time.sleep(1.0 / UPDATE_RATE)
        finally:
            self.broker.stop_running()

    def lcd_update(self):
        logging.debug('Updating LCD (framebuffer)')
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

    def activate_panel(self, panel_idx):
        logging.debug('Activated panel %s',
                      self.active_panel.__class__.__name__)
        self.panel_idx = panel_idx % len(self.panels)
        if self.active_panel:
            self.active_panel.deactivate()
        self.active_panel = self.panels[self.panel_idx]
        self.active_panel.activate()
        self.active_panel_fb = self.backing_stores[self.active_panel]
        if not self.needs_repaint:
            logging.debug('Updating LCD -- no repaint needed (active_panel)')
            lcd.update(self.active_panel_fb)
        else:
            self.active_panel.paint(self.active_panel_fb)
            lcd.update(self.active_panel_fb)
