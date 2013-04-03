#!/usr/bin/env python
# -*- coding: utf-8 -*-
import freetype
import graphics
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('fonts')

class Font(object):
    def __init__(self, filename, size):
        logger.info('Loading font %s, size %ipx', filename, size)
        self._filename = filename
        self._face = freetype.Face(filename)
        self.set_size(size)

    def __repr__(self):
        return '%s("%s", %i)' % (self.__class__.__name__, self._filename, self.size)

    @property
    def size(self):
        """The font's size in pixels."""
        return self._size

    def set_size(self, size):
        """Set the font's size in pixels."""
        self._face.set_pixel_sizes(0, size)
        self._glyphcache = {}
        self._size = size

    def _load_glyph(self, c):
        logger.debug('Loading glyph "%s"' % c)

        self._face.load_char(c, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_MONO)
        glyph = self._face.glyph

        bitmap = glyph.bitmap
        pixels = self._unpack_mono_bitmap(bitmap)
        surface = graphics.Surface(width=bitmap.width, height=bitmap.rows, pixels=pixels)
        top, left = glyph.bitmap_top, glyph.bitmap_left
        advance_x = glyph.advance.x / 64

        return (surface, advance_x, top, left)

    def _unpack_mono_bitmap(self, bitmap):
        """
        Unpack a freetype FT_LOAD_TARGET_MONO glyph bitmap into a bytearray where each pixel
        is represented by a single byte.
        """
        # Allocate a bytearray of sufficient size to hold the glyph bitmap.
        data = bytearray(bitmap.rows * bitmap.width)

        # Iterate over every byte in the glyph bitmap. Note that we're not
        # iterating over every pixel in the resulting unpacked bitmap --
        # we're iterating over the packed bytes in the input bitmap.
        for y in range(bitmap.rows):
            for byte_index in range(bitmap.pitch):

                # Read the byte that contains the packed pixel data.
                byte_value = bitmap.buffer[y * bitmap.pitch + byte_index]

                # We've processed this many bits (=pixels) so far. This determines
                # where we'll read the next batch of pixels from.
                num_bits_done = byte_index * 8

                # Pre-compute where we should write the pixels that we're going
                # to unpack from the current byte in the glyph bitmap.
                rowstart = y * bitmap.width + byte_index * 8

                # Iterate over every bit (=pixel) that's still a part of the output bitmap.
                # Sometimes we're only unpacking a fraction of a byte because glyphs may
                # not always fit on a byte boundary. So we make sure to stop if we unpack
                # past the current row of pixels.
                for bit_index in range(0, min(8, bitmap.width - num_bits_done)):

                    # Unpack the next pixel from the current glyph byte.
                    bit = byte_value & (1 << (7 - bit_index))

                    # Write the pixel to the output bytearray. We ensure that `off` pixels
                    # have a value of 0 and `on` pixels have a value of 1.
                    data[rowstart + bit_index] = 1 if bit else 0

        return data

    def _get_glyph(self, c):
        cached_glyph = self._glyphcache.get(c)

        if cached_glyph:
            return cached_glyph

        glyph = self._load_glyph(c)
        self._glyphcache[c] = glyph
        return glyph

    def text_extents(self, text):
        """Return (width, height, baseline) of `text` rendered in the current font."""
        slot = self._face.glyph
        width, height, baseline = 0, 0, 0
        previous = None

        for c in text:
            surf, advance_x, top, left = self._get_glyph(c)
            height = max(height, surf.height + max (0, surf.height - top))
            baseline = max(baseline, max(0, surf.height - top))
            kerning = self._face.get_kerning(previous, c)
            width += advance_x + (kerning.x / 64)
            previous = c

        return (width, height + baseline, baseline)

    def render(self, text, width=None, height=None, baseline=None):
        """
        Render the given `text` into a new surface and return it.
        If `width`, `height`, and `baseline` are not specified they will be computed using
        the `text_extents' function.
        """
        if width is None or height is None or baseline is None:
            width, height, baseline = self.text_extents(text)

        outbuffer = graphics.Surface(width, height)
        slot = self._face.glyph
        x, y = 0, 0
        previous = 0

        for c in text:
            surface, advance_x, top, left = self._get_glyph(c)
            y = height - baseline - top
            kerning = self._face.get_kerning(previous, c)
            x += (kerning.x / 64)
            outbuffer.bitblt_fast(surface, x, y)
            x += advance_x
            previous = c

        return outbuffer

if __name__ == '__main__':
    f = Font('test-apps/font4.ttf', 16)
    text = u'22:50'
    # text = 'T,'
    width, height, baseline = f.text_extents(text)
    print '"%s": width=%i height=%i baseline=%i' % (text, width, height, baseline)
    print f
    print repr(f.render(text))
    print f.size

    # global unpack_mono_bitmap
    # global unpack_mono_bitmapX
    # tmp = unpack_mono_bitmap
    # unpack_mono_bitmap = unpack_mono_bitmapX
    # unpack_mono_bitmapX = tmp
    # f = Font('test-apps/font4.ttf', 16)
    # print repr(f.render(text))

    import random
    import string
    def random_string(l):
        return ''.join( random.choice(string.ascii_letters + string.digits) for n in xrange(l) )

    def benchmark():
        # for c in string.ascii_letters + string.digits:
        #     f.render(c)
        for i in xrange(500):
            f.render(random_string(30))

    import cProfile
    import pstats
    cProfile.run('benchmark()', 'fontbench.profile')
    p = pstats.Stats('fontbench.profile')
    print p.sort_stats('cumulative').print_stats(20)
    print p.sort_stats('time').print_stats(20)