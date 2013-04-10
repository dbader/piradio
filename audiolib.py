#sudo pip install python-mpd2
import logging
import mpd
import time
import os

logging.basicConfig(level=logging.DEBUG)

client = mpd.MPDClient(use_unicode=True)
client.connect("localhost", 6600)

def printsong():
    logging.info('Current song: %s', currentsong())

def currentsong():
    currsong = client.currentsong()
    return u'%s - %s' % (currsong.get('name'), currsong.get('title'))

def currentstation():
    return client.currentsong().get('name', '')

def currvolume():
    return int(client.status()['volume'])

def is_playing():
    return float(client.status().get('elapsed', 0)) != 0

def wait_playing(timeout=10):
    print 'waiting for new song to start playing'
    while not is_playing() and timeout > 0:
        time.sleep(0.1)
        timeout -= 0.1

def fade_out():
    startvolume = currvolume()
    if not startvolume or not is_playing():
        # We're not playing. Fade out instantly.
        client.setvol(0)
        return

    print 'fading out from %i to 0' % startvolume
    for v in range(startvolume, -1, -10):
        client.setvol(v)
        time.sleep(0.25)
    time.sleep(1)
    print ('fade - done')

def fade_in():
    startvolume = currvolume()
    print 'fading in from %i to 100' % startvolume
    for v in range(startvolume, 101, 10):
        client.setvol(v)
        time.sleep(0.25)
    time.sleep(1)
    print ('fade - done')

def nextsong():
    fade_out()
    print '>> next'
    client.next()
    wait_playing()
    printsong()
    fade_in()

def stop():
    client.stop()

def playstream(url, fade=True):
    if fade:
        fade_out()
    logging.info('Playing stream %s', url)
    client.setvol(100)
    client.clear()
    client.add(url)
    client.play()
    if fade:
        wait_playing()
        printsong()
        fade_in()

    # client.close()
    # client.disconnect()
    # client = None

def progress():
    if not is_playing():
        return 0.0
    done, total = tuple(map(int, client.status()['time'].split(':')))
    if not total:
        return 0.0
    return float(done) / float(total)

def playfile(path):
    os.system('mpg321 ' + path)

if __name__ == '__main__':
    print progress()
    print is_playing()