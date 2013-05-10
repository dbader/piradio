import bottle
import mpd

STREAMS = {
    'Bayern5': 'http://gffstream.ic.llnwd.net/stream/gffstream_w14b',
    'FM4': 'http://mp3stream1.apasf.apa.at:8000/',
    'M94.5': 'http://stream.m945.mwn.de:80/m945-hq.mp3',
    '1Live': 'http://gffstream.ic.llnwd.net/stream/gffstream_stream_wdr_einslive_b'
}

client = mpd.MPDClient(use_unicode=True)
client.connect("localhost", 6600)

def currentsong():
    currsong = client.currentsong()
    return '%s - %s' % (currsong.get('name'), currsong.get('title'))

@bottle.route('/')
def index():
    streamlinks = '<br>'.join(['<a href="/stream/%s">%s</a>' % (station, station) for station in STREAMS])
    return """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>piradio</title>
    </head>
    <body>
        <h2>%s</h2><br>
        <a href='stop'>Stop</a> | <a href='play'>Play</a><br><br>
        %s
        <p>Bitte nicht ausschalten :D</p>
    </body>
</html>
""" % (currentsong(), streamlinks)

@bottle.route('/stop')
def stop():
    client.stop()
    bottle.redirect('/')

@bottle.route('/play')
def play():
    client.play()
    bottle.redirect('/')

@bottle.route('/stream/<station>')
def stream(station):
    print station
    streamurl = STREAMS.get(station)
    if streamurl:
        client.clear()
        client.add(streamurl)
        client.play()
    bottle.redirect('/')

bottle.run(host='0.0.0.0', port=80)
