# __all__ = []


try:
    import lcd
except OSError:
    import fakelcd as lcd

import graphics, fontlib, mvg, podcast, weather, ui, commons, audiolib
import json, os, datetime, logging, random, time

CONFIG = json.loads(open('config.json').read())
GLYPH_PLAYING = '0'

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

class AlarmPanel(Panel):
    def __init__(self):
        self.font = fontlib.get('tempesta', 32)
        self.prev_timestr = None
        self.countdown = 90
        self.alarmtime = None
        self.countdown_str = None
        self.state = 'SET_TIME'

    def fire_alarm(self):
        self.state = 'ALARM'
        self.alarmtime = None

    def countdownstring(self):
        remaining = int(self.alarmtime - time.time() if self.alarmtime else self.countdown)
        minutes = remaining / 60
        seconds = remaining - minutes * 60
        return '%.2i:%.2i' % (minutes, seconds)

    def update(self):
        if self.state == 'COUNTDOWN':
            if self.alarmtime and time.time() >= self.alarmtime:
                self.fire_alarm()
        elif self.state == 'ALARM':
            lcd.set_backlight_enabled(bool(int(time.time()) % 2 == 0))
        if self.countdown_str != self.countdownstring():
            self.countdown_str = self.countdownstring()
            self.needs_redraw = True

    def paint(self, framebuffer):
        framebuffer.fill(0)
        framebuffer.center_text(self.font, self.countdown_str)

    def up_pressed(self):
        self.countdown += 30
        self.needs_redraw = True

    def down_pressed(self):
        self.countdown -= 30
        self.needs_redraw = True

    def center_pressed(self):
        if self.state == 'SET_TIME':
            self.state = 'COUNTDOWN'
            self.alarmtime = time.time() + self.countdown if not self.alarmtime else None
        elif self.state == 'ALARM':
            lcd.set_backlight_enabled(True)
            self.state = 'SET_TIME'
        self.needs_redraw = True

class ClockPanel(Panel):
    def __init__(self):
        self.clock_font = fontlib.get('tempesta', 32)
        self.prev_timestr = None

    def update(self):
        self.timestr = str(datetime.datetime.now().strftime(CONFIG['clock_format']))
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
    def __init__(self, city, lat, lon):
        self.apikey = CONFIG['forecastio_api_key']
        self.city = city
        self.lat, self.lon = lat, lon
        self.font_big = fontlib.get('tempesta', 16)
        self.font = fontlib.get('tempesta', 8)
        self.climacons = fontlib.get('climacons', 32)
        self.load_weather()

    def glyph_for_icon(self, icon):
        GLYPH_FOR_ICON = {
            "clear-day": "I",
            "clear-night": "N",
            "rain": "$",
            "snow": "0",
            "sleet": "3",
            "wind": "B",
            "fog": "?",
            "cloudy": "!",
            "partly-cloudy-day": "\"",
            "partly-cloudy-night": "#",
        }
        return GLYPH_FOR_ICON.get(icon, 'Y')

    def update(self):
        pass

    def paint(self, framebuffer):
        words = self.weather_summary.split()
        line1 = ' '.join(words[:len(words)/2])
        line2 = ' '.join(words[len(words)/2:])

        framebuffer.fill(0)
        framebuffer.center_text(self.font_big, self.city, y=2)
        framebuffer.center_text(self.font, line1, y=20)
        framebuffer.center_text(self.font, line2, y=30)
        framebuffer.center_text(self.climacons, self.weather_glyph, y=40)

    def up_pressed(self):
        pass

    def down_pressed(self):
        pass

    def load_weather(self):
        logging.info('Getting weather for %s', self.city)
        icon, summary = weather.forecastioweather(self.apikey, self.lat, self.lon)

        self.weather_glyph = self.glyph_for_icon(icon)
        self.weather_summary = summary

        self.needs_redraw = True

    def center_pressed(self):
        self.load_weather()

class PublicTransportPanel(Panel):
    def __init__(self, station):
        self.station = station
        self.font = fontlib.get('tempesta', 8)
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
        self.font = fontlib.get('tempesta', 8)
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
        framebuffer.center_text(self.font, 'Random Episode', y=2)
        framebuffer.hline(11)

        words = self.episode_title.split()
        line1 = ' '.join(words[:len(words)/2])
        line2 = ' '.join(words[len(words)/2:])
        framebuffer.center_text(self.font, line1, y=22)
        framebuffer.center_text(self.font, line2, y=32)

        ui.render_progressbar(framebuffer, 0, 48, framebuffer.width, 14, audiolib.progress())


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
        self.font = fontlib.get('tempesta', 8)
        self.glyph_font = fontlib.get('pixarrows', 10)
        self.stations = json.loads(open('stations.json').read())

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
        self.timestr = str(datetime.datetime.now().strftime(CONFIG['clock_format']))
        if self.timestr != self.prev_timestr:
            self.prev_timestr = self.timestr
            logging.debug('Redrawing the clock')
            self.needs_redraw = True