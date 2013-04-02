"""
Needs mvg_json from https://github.com/rmoriz/mvg-live
"""
import subprocess
import json

MVG_JSON_BINARY_PATH = '/usr/local/Cellar/ruby/2.0.0-p0/bin/mvg_json'

def get_data_for_station(station):
    mvg_json = subprocess.check_output([MVG_JSON_BINARY_PATH, station])
    return json.loads(mvg_json)

def get_upcoming_trains(station, min_minutes=3):
    m = get_data_for_station(station)
    return [t for t in m['result_sorted'] if t['minutes'] >= min_minutes]

if __name__ == '__main__':
    for t in get_upcoming_trains('Studentenstadt')[:5]:
        print t['line'], t['destination'], t['minutes']