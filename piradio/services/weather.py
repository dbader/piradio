# http://openweathermap.org/wiki/API/JSON_API

from urllib2 import urlopen
import json

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
