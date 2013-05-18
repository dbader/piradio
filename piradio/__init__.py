#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import piradio.fonts
import piradio.graphics
import piradio.ui
import piradio.panels
import piradio.app


def main():
    logging.basicConfig(level=logging.INFO)
    piradio.app.RadioApp().run()
