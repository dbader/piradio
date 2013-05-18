"""
Needs mvg_json from https://github.com/rmoriz/mvg-live
"""
import subprocess
import json
import base


MVG_JSON_BINARY_PATH = '/usr/local/Cellar/ruby/2.0.0-p0/bin/mvg_json'


def get_data_for_station(station):
    mvg_json = subprocess.check_output([MVG_JSON_BINARY_PATH, station])
    return json.loads(mvg_json)


def get_upcoming_trains(station, min_minutes=3):
    m = get_data_for_station(station)
    return [t for t in m['result_sorted'] if t['minutes'] >= min_minutes]

if __name__ == '__main__':
    for tt in get_upcoming_trains('Studentenstadt')[:5]:
        print tt['line'], tt['destination'], tt['minutes']


class PublicTransportService(base.AsyncService):
    def __init__(self):
        super(PublicTransportService, self).__init__(tick_interval=5*60)

    def tick(self):
        super(PublicTransportService, self).tick()
        for station in self.subscriptions.keys():
            trains = get_upcoming_trains(station)
            self.notify_subscribers(station, trains)
