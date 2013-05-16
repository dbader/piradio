# http://openweathermap.org/wiki/API/JSON_API

from urllib2 import urlopen
import json

import logging
from piradio.services import base
from piradio import commons

FORECAST_CHANGED_EVENT = 'weather_changed'

def weather(city):
    query_url = ('http://openweathermap.org/data/2.1/'
                 'find/name?q=%s&units=metric' % city)
    data = urlopen(query_url)
    cities = json.load(data)
    if cities['count'] > 0:
        city = cities['list'][0]
        return (city['name'], city['main']['temp'],
                city['weather'][0]['description'])


def forecastioweather(apikey, lat, lon):
    forecastio_url = ('https://api.forecast.io/forecast/%s/%f,%f?units=si' %
                      (apikey, lat, lon))
    data = json.load(urlopen(forecastio_url))
    return data['hourly']['icon'], data['hourly']['summary']


class WeatherService(base.AsyncService):
    def __init__(self):
        super(WeatherService, self).__init__(tick_interval=30)
        config = json.loads(open('config.json').read())
        self.apikey = config['forecastio_api_key']
        self.locations = []
        # fixme: how to select locations for which weather should be pulled?

    def tick(self):
        super(WeatherService, self).tick()
        logging.info('%s: Pulling weather data for %i locations',
                     self.__class__.__name__, len(self.locations))
        for lat, lon in self.locations:
            icon, summary = forecastioweather(self.apikey, lat, lon)
            logging.info('%f,%f: %s, %s', lat, lon, icon, summary)

