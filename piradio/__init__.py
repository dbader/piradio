#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import piradio.app
import piradio.services


def main():
    # piradio.app.RadioApp().run()
    # return
    while True:
        try:
            logging.info("Booting app")
            piradio.app.RadioApp().run()
        except KeyboardInterrupt:
            logging.info("Shutting down")
            piradio.services.stop_all()
            break
        except Exception as e:
            logging.exception(e)
