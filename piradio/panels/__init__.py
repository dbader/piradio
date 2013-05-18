# __all__ = []

# Possible future panels, by priority:
# wifi-test
# settings
# random images
# twitter
# newsticker
# emails

# import piradio.panels.base
from piradio.panels.alarm import AlarmPanel
from piradio.panels.clock import ClockPanel
from piradio.panels.radio import RadioPanel
from piradio.panels.weather import WeatherPanel
from piradio.panels.public_transport import PublicTransportPanel
from piradio.panels.podcast import RandomPodcastPanel
from piradio.panels.test import DitherTestPanel, AnimationTestPanel
