import logging
from piradio import fonts
from piradio.panels import base
import piradio.services.weather


class WeatherPanel(base.Panel):
    def __init__(self, city, lat, lon):
        super(WeatherPanel, self).__init__()
        self.city = city
        self.font_big = fonts.get('tempesta', 16)
        self.font = fonts.get('tempesta', 8)
        self.climacons = fonts.get('climacons', 32)
        self.weather_glyph = 'Y'
        self.weather_summary = ''
        weathersvc = piradio.services.weather.instance()
        weathersvc.subscribe((lat, lon), self.on_forecast_changed)

    def on_forecast_changed(self, icon, summary):
        logging.info('Forecast changed: %s, %s', icon, summary)
        self.weather_glyph = self.glyph_for_icon(icon)
        self.weather_summary = summary
        self.set_needs_repaint()

    @staticmethod
    def glyph_for_icon(icon):
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

    def paint(self, surface):
        words = self.weather_summary.split()
        line1 = ' '.join(words[:len(words)/2])
        line2 = ' '.join(words[len(words)/2:])

        surface.fill(0)
        surface.center_text(self.font_big, self.city, y=2)
        surface.center_text(self.font, line1, y=20)
        surface.center_text(self.font, line2, y=30)
        surface.center_text(self.climacons, self.weather_glyph, y=40)
