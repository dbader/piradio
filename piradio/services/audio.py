#sudo pip install python-mpd2
import mpd
import os
from piradio.services import base


class AudioService(base.BaseService):
    PLAYBACK_URL_CHANGED_EVENT = 'playback_url_changed'

    def __init__(self):
        super(AudioService, self).__init__()
        self.mpd_client = mpd.MPDClient(use_unicode=True)

    def start(self):
        super(AudioService, self).start()
        self.mpd_client.connect("localhost", 6600)

    def stop(self):
        super(AudioService, self).stop()
        self.stop_playback()
        self.mpd_client.disconnect()

    def set_volume(self, volume):
        self.mpd_client.setvol(int(100 * volume))

    @property
    def is_playing(self):
        return float(self.mpd_client.status().get('elapsed', 0)) != 0

    @staticmethod
    def playfile(path):
        os.system('mpg321 ' + path)

    def playstream(self, url):
        self.set_volume(1.0)
        self.mpd_client.clear()
        self.mpd_client.add(url)
        self.mpd_client.play()

    def stop_playback(self):
        self.mpd_client.stop()

    @property
    def playback_progress(self):
        if not self.is_playing:
            return 0.0
        done, total = tuple(map(int, client.status()['time'].split(':')))
        if not total:
            return 0.0
        return float(done) / float(total)
