#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import audiolib
import app

try:
    import raspi_lcd as lcd_driver
except OSError:
    import fake_lcd as lcd_driver

app.lcd = lcd_driver

if __name__ == '__main__':
    while True:
        try:
            logging.info("Booting app")
            app.RadioApp().run()
        except KeyboardInterrupt:
            logging.info("Shutting down")
            audiolib.stop()
            break
        except Exception as e:
            logging.exception(e)
