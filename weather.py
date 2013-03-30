# http://openweathermap.org/wiki/API/JSON_API

from json import load
from urllib2 import urlopen
from pprint import pprint

def weather(city):
    data = urlopen('http://openweathermap.org/data/2.1/find/name?q=%s&units=metric' % city)
    cities = load(data)
    if cities['count'] > 0:
        city = cities['list'][0]
        return (city['name'], city['main']['temp'], city['weather'][0]['description'])
