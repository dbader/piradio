#!/usr/bin/env python
# -*- coding: utf-8 -*-
import freetype
import graphics
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('fonts')

# 0.27
def unpack_mono_bitmap(bitmap):
    """Unpack a freetype FT_LOAD_TARGET_MONO bitmap into a list that has one element per pixel."""

    def bits(x):
        """Unpack the bits of am 8bit word into a list."""
        data = []
        for i in range(8):
            data.insert(0, int((x & 1) == 1))
            x = x >> 1
        return data

    data = []
    for i in range(bitmap.rows):
        row = []
        for j in range(bitmap.pitch):
            row.extend(bits(bitmap.buffer[i*bitmap.pitch+j]))
        data.extend(row[:bitmap.width])
    return data

def bits(x):
    """Unpack the bits of am 8bit word into a list."""
    data = []
    for i in range(8):
        data.insert(0, int((x & 1) == 1))
        x = x >> 1
    return data

# 1.0
def unpack_mono_bitmap(bitmap):
    data = bytearray(bitmap.rows * bitmap.width)
    for y in range(bitmap.rows):
        for x in range(bitmap.width):
            byte_index = x / 8
            byte_value = bitmap.buffer[y * bitmap.pitch + byte_index]
            bit_index = x - (byte_index * 8)
            data[y * bitmap.width + x] = 1 if (  byte_value & (1 << (7 - bit_index)) ) else 0
            # Correct:
            # data[y * bitmap.width + x] = bits(byte_value)[bit_index]
    return data

# 0.24
def unpack_mono_bitmap(bitmap):
    data = bytearray(bitmap.rows * bitmap.width)

    for y in range(bitmap.rows):
        for byte_index in range(bitmap.pitch):
            byte_value = bitmap.buffer[y * bitmap.pitch + byte_index]
            num_bits_done = byte_index * 8
            rowstart = y * bitmap.width + byte_index * 8
            for bit_index in range(0, min(8, bitmap.width - num_bits_done)):
                data[rowstart + bit_index] = 1 if (  byte_value & (1 << (7 - bit_index)) ) else 0

    return data


def buf2str(pixels, width, height):
    bstr = ''
    for i in range(height):
        rowstr = ''
        for j in range(width):
            rowstr += '#' if pixels[i * width + j] else '.'
        bstr += rowstr + '\n'
    return bstr

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
        surface = graphics.Surface(width=bitmap.width, height=bitmap.rows, pixels=unpack_mono_bitmap(bitmap))
        top, left = glyph.bitmap_top, glyph.bitmap_left
        advance_x = (glyph.advance.x >> 6)
        return (surface, advance_x, top, left)

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
        previous = 0
        for c in text:
            self._face.load_char(c, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_MONO)
            bitmap = slot.bitmap
            height = max(height, bitmap.rows + max (0, -(slot.bitmap_top - bitmap.rows)))
            baseline = max(baseline, max(0, -(slot.bitmap_top - bitmap.rows)))
            kerning = self._face.get_kerning(previous, c)
            width += (slot.advance.x >> 6) + (kerning.x >> 6)
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
            x += (kerning.x >> 6)
            outbuffer.bitblt_fast(surface, x, y)
            x += advance_x
            previous = c
        return outbuffer

if __name__ == '__main__':
    f = Font('test-apps/font4.ttf', 32)
    text = u'hello, world.'
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
        for c in string.ascii_letters + string.digits:
            f.render(c)

    import cProfile
    import pstats
    cProfile.run('benchmark()', 'fontbench.profile')
    p = pstats.Stats('fontbench.profile')
    print p.sort_stats('cumulative').print_stats(20)
    print p.sort_stats('time').print_stats(20)