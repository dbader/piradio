piradio
=======
An internet radio based on the Raspberry Pi.

![Simulator screenshot](https://raw.github.com/dbader/piradio/master/extras/images/simulator.png)


Development Setup (OS X)
------------------------

    $ brew install freetype
    $ brew install mpd
    $ brew install sdl sdl_image sdl_mixer sdl_ttf portmidi
    $ brew install mercurial
    $ gem install mvg-live
    $ cp mpdconf.example.osx ~/.mpdconf
    $ virtualenv venv
    $ . venv/bin/activate
    $ pip install -r requirements.txt
    $ mpd --no-daemon
    $ ./piradio.py


Meta
----

Daniel Bader – [@dbader_org](https://twitter.com/dbader_org>) – mail@dbader.org

Distributed under the MIT license. See ``LICENSE.txt`` for more information.

https://github.com/dbader/piradio
