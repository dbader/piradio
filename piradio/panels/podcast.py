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
        super(RandomPodcastPanel, self).__init__()
        self.font = fonts.get('tempesta', 8)
        logging.info('Loading podcast feed from %s', feed_url)
        self.episodes = podcast.load_podcast(feed_url)
        logging.info('Parsed %i episodes', len(self.episodes))
        self.episode_url = None
        self.episode_title = None
        self.select_random_episode()
        self.lastrefresh = 0

    def select_random_episode(self):
        self.episode_title, self.episode_url = random.choice(self.episodes)

    def update(self):
        if time.time() - self.lastrefresh > 10:
            self.lastrefresh = time.time()
            self.set_needs_repaint()

    def paint(self, surface):
        surface.fill(0)
        surface.center_text(self.font, 'Random Episode', y=2)
        surface.hline(11)

        # Lame multi-line text rendering:
        words = self.episode_title.split()
        line1 = ' '.join(words[:len(words) / 2])
        line2 = ' '.join(words[len(words) / 2:])

        surface.center_text(self.font, line1, y=22)
        surface.center_text(self.font, line2, y=32)

        ui.render_progressbar(surface, 0, 48, surface.width, 14,
                              audio.progress())

    def center_pressed(self):
        self.select_random_episode()
        self.set_needs_repaint()
        audio.playstream(self.episode_url, fade=False)
