#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import piradio.services.audio as audio
import piradio.app


def main():
    while True:
        try:
            logging.info("Booting app")
            piradio.app.RadioApp().run()
        except KeyboardInterrupt:
            logging.info("Shutting down")
            audio.stop()
            break
        except Exception as e:
            logging.exception(e)
