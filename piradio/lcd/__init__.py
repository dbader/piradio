"""
Select the LCD driver for the real LCD board (raspi_lcd) or the simulated one (fake_lcd).
"""

import logging

try:
    from raspi_lcd import *
except OSError:
    from fake_lcd import *

logging.info('Using LCD driver %s', init.__module__)
