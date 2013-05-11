import base
import logging
import time
import random
from .. import fonts
from .. import ui
from ..services import audio
from ..services import podcast


class RandomPodcastPanel(base.Panel):
    def __init__(self, feed_url):
        self.font = fonts.get('tempesta', 8)
        logging.info('Loading podcast feed from %s', feed_url)
        self.episodes = podcast.load_podcast(feed_url)
        logging.info('Parsed %i episodes', len(self.episodes))
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

        ui.render_progressbar(framebuffer, 0, 48, framebuffer.width, 14, audio.progress())

    def up_pressed(self):
        pass

    def down_pressed(self):
        pass

    def center_pressed(self):
        self.select_random_episode()
        self.needs_redraw = True
        audio.playstream(self.episode_url, fade=False)
