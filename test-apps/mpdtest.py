import logging
import mpd
import time

logging.basicConfig(level=logging.DEBUG)

client = mpd.MPDClient(use_unicode=True)
client.connect("localhost", 6600)

def printsong():
    currsong = client.currentsong()
    print '%s - %s' % (currsong.get('name'), currsong.get('title'))

def currvolume():
    return int(client.status()['volume'])

def is_playing():
    return float(client.status()['elapsed']) != 0

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

def playstream(url):
    fade_out()
    print 'Playing stream', url
    client.clear()
    client.add(url)
    client.play()
    wait_playing()
    printsong()
    fade_in()

while True:
    playstream('http://stream.m945.mwn.de:80/m945-hq.mp3')
    # time.sleep(1)
    playstream('http://gffstream.ic.llnwd.net/stream/gffstream_w14b')

client.close()
client.disconnect()
